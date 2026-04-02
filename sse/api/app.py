from __future__ import annotations

from pathlib import Path
import re

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sse.api.forecasting import (
    build_daily_use_forecast,
    build_reputation_summary,
    build_reflection_response,
    _build_sse_prompt,
)
from sse.config import get_guardrail_mode
from sse.guardrails import GuardrailDecision, GuardrailMode, evaluate_situation_text
from sse.orchestrator import RunConfig, run_sse_with_trace
from sse.phenomenon import SUPPORTED_PHENOMENA, build_phenomenon_context
from sse.profiles import create_profile, get_profile, list_profiles, resolve_profiles_in_text, update_profile
from sse.queries import create_query_item, get_query_item, list_query_items, reflect_query_item, search_query_items
from sse.ssm import parse_situation
from sse.tracking import (
    create_tracking_item,
    ensure_dummy_tracking_item,
    get_tracking_item,
    list_tracking_items,
    vote_tracking_item,
)

app = FastAPI(title="SSE API", version="0.1.0")

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
_INDEX_FILE = _FRONTEND_DIR / "index.html"

if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")


@app.on_event("startup")
async def startup_seed_tracking() -> None:
    ensure_dummy_tracking_item()


@app.middleware("http")
async def no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


class PredictRequest(BaseModel):
    situation: str
    query_mode: str = "general"
    depth: str = "default"
    alternatives: bool = False
    strategic_depth: int | None = None
    feature_type: str = "situation_check"
    intended_move: str = ""
    intended_timing: str = ""
    desired_outcome: str = ""
    role_tags: list[str] | None = None
    urgency: str = "normal"


class CompareRequest(BaseModel):
    base_situation: str
    variant_situation: str
    query_mode: str = "general"
    depth: str = "default"
    alternatives: bool = False
    strategic_depth: int | None = None


class TimelineCheckpoint(BaseModel):
    label: str
    situation: str


class TimelineRequest(BaseModel):
    base_situation: str
    checkpoints: list[TimelineCheckpoint]
    query_mode: str = "general"
    depth: str = "default"
    alternatives: bool = False
    strategic_depth: int | None = None


class SemanticsRequest(BaseModel):
    situation: str
    query_mode: str = "general"


class TrackingCreateRequest(BaseModel):
    situation: str
    prediction: dict
    started_at: str | None = None
    expected_at: str | None = None


class TrackingVoteRequest(BaseModel):
    vote: str
    actual_outcome: str | None = None
    actual_at: str | None = None


class ProfileCreateRequest(BaseModel):
    name: str
    profile_type: str
    description: str = ""
    attributes: dict[str, str] | None = None
    tag: str | None = None


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    profile_type: str | None = None
    description: str | None = None
    attributes: dict[str, str] | None = None


class QueryCreateRequest(BaseModel):
    situation: str
    query_mode: str = "general"
    prediction: dict


class ReflectionRequest(BaseModel):
    outcome_summary: str
    forecast_accuracy: str
    action_taken: str


def _normalize_query_mode(raw: str) -> str:
    if (raw or "").strip().lower() == "phenomenon":
        return "phenomenon"
    return "general"


def _extract_first_tag(text: str) -> str:
    match = re.search(r"@([A-Za-z0-9_-]+)", text)
    return match.group(1).lower() if match else ""


def _assert_non_phenomenon_endpoint(query_mode: str) -> None:
    if _normalize_query_mode(query_mode) == "phenomenon":
        raise HTTPException(
            status_code=400,
            detail="Phenomenon mode supports only Run SSE and Semantics.",
        )


def _evaluate_guardrail_for_text(raw_situation: str) -> tuple[GuardrailMode, GuardrailDecision]:
    mode = get_guardrail_mode()
    if mode == "off":
        return mode, GuardrailDecision(
            flagged=False,
            category="unknown",
            reason="Guardrails disabled by configuration.",
            safe_reframe="Reframe toward safety, prevention, or non-operational policy analysis.",
        )
    return mode, evaluate_situation_text(raw_situation)


def _guardrail_payload(status: str, mode: GuardrailMode, decision: GuardrailDecision) -> dict:
    return {
        "status": status,
        "mode": mode,
        "category": decision.category,
        "reason": decision.reason,
        "safe_reframe": decision.safe_reframe,
    }


def _build_soft_block_payload(
    raw_situation: str,
    query_mode: str,
    mode: GuardrailMode,
    decision: GuardrailDecision,
) -> dict:
    normalized_query_mode = _normalize_query_mode(query_mode)
    phenomenon_tag = _extract_first_tag(raw_situation)
    resolved_situation, profiles_used = resolve_profiles_in_text(raw_situation)
    explanation = (
        "This request was blocked by safety guardrails because it appears operationally harmful. "
        f"{decision.safe_reframe}"
    )
    return {
        "predicted_outcome": {
            "id": "guardrail_blocked",
            "label": "Request blocked for safety constraints.",
            "confidence": 1.0,
            "rationale": ["guardrail_enforced"],
        },
        "explanation": explanation,
        "horizon": "n/a",
        "mode": "A",
        "belief_shift_summary": "",
        "signal_evaluation_summary": "",
        "coalition_likelihood": 0.0,
        "recursion_depth_used": 0,
        "factors": [],
        "trace": "guardrail:block",
        "source": "backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resolved_situation": resolved_situation,
        "sse_input_situation": resolved_situation,
        "profiles_used": [{"tag": p["tag"], "name": p["name"]} for p in profiles_used],
        "query_mode": normalized_query_mode,
        "phenomenon_tag": phenomenon_tag,
        "pipeline": ["Guardrail"],
        "guardrail": _guardrail_payload(status="blocked", mode=mode, decision=decision),
    }


def _build_prediction_payload(
    raw_situation: str,
    query_mode: str = "general",
    depth: str = "default",
    include_alternatives: bool = False,
    strategic_depth: int | None = None,
    feature_type: str = "situation_check",
    intended_move: str = "",
    intended_timing: str = "",
    desired_outcome: str = "",
    role_tags: list[str] | None = None,
    urgency: str = "normal",
) -> dict:
    normalized_query_mode = _normalize_query_mode(query_mode)
    phenomenon_tag = _extract_first_tag(raw_situation)
    guardrail_mode, guardrail_decision = _evaluate_guardrail_for_text(raw_situation)
    composed_situation = _build_sse_prompt(
        raw_situation,
        feature_type=feature_type,
        intended_move=intended_move,
        intended_timing=intended_timing,
        desired_outcome=desired_outcome,
        role_tags=role_tags,
        urgency=urgency,
    )
    if guardrail_mode == "enforce" and guardrail_decision.flagged:
        payload = _build_soft_block_payload(
            raw_situation=raw_situation,
            query_mode=query_mode,
            mode=guardrail_mode,
            decision=guardrail_decision,
        )
        payload["daily_use"] = build_daily_use_forecast(
            payload,
            original_situation=raw_situation,
            feature_type=feature_type,
            intended_move=intended_move,
            intended_timing=intended_timing,
            desired_outcome=desired_outcome,
            role_tags=role_tags,
            urgency=urgency,
        )
        payload["input_context"] = {
            "feature_type": feature_type,
            "intended_move": intended_move,
            "intended_timing": intended_timing,
            "desired_outcome": desired_outcome,
            "role_tags": role_tags or [],
            "urgency": urgency,
        }
        return payload

    resolved_situation, profiles_used = resolve_profiles_in_text(composed_situation)
    phenomenon_payload = None
    sse_input_situation = resolved_situation
    if normalized_query_mode == "phenomenon":
        if not phenomenon_tag:
            raise HTTPException(
                status_code=400,
                detail="Phenomenon mode requires a module tag such as @language or @trend.",
            )
        if phenomenon_tag not in SUPPORTED_PHENOMENA:
            supported = ", ".join([f"@{tag}" for tag in sorted(SUPPORTED_PHENOMENA)])
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported phenomenon tag '@{phenomenon_tag}'. Supported tags: {supported}.",
            )
        try:
            context = build_phenomenon_context(
                raw_text=resolved_situation,
                tag=phenomenon_tag,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        sse_input_situation = context.enriched_text
        phenomenon_payload = {
            "module": context.tag,
            "query": context.normalized_query,
            "summary": context.summary,
            "hypotheses": context.hypotheses,
            "evidence": [
                {
                    "source": item.source,
                    "title": item.title,
                    "snippet": item.snippet,
                    "url": item.url,
                }
                for item in context.evidence
            ],
        }

    result, trace = run_sse_with_trace(
        sse_input_situation,
        RunConfig(
            depth=depth,
            include_alternatives=include_alternatives,
            strategic_depth=strategic_depth,
        ),
    )
    payload = result.to_dict()
    payload["factors"] = [
        {"name": factor.name, "role": factor.role, "category": factor.category}
        for factor in trace.factors
    ]
    payload["trace"] = trace.summary
    payload["source"] = "backend"
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    payload["resolved_situation"] = resolved_situation
    payload["sse_input_situation"] = sse_input_situation
    payload["profiles_used"] = [{"tag": p["tag"], "name": p["name"]} for p in profiles_used]
    payload["query_mode"] = normalized_query_mode
    payload["phenomenon_tag"] = phenomenon_tag
    payload["pipeline"] = ["SSM", "ESS", "MCM", "SQC", "Explainer"]
    if guardrail_mode == "audit" and guardrail_decision.flagged:
        guardrail_status = "flagged"
    else:
        guardrail_status = "clear"
    payload["guardrail"] = _guardrail_payload(
        status=guardrail_status,
        mode=guardrail_mode,
        decision=guardrail_decision,
    )
    if phenomenon_payload:
        payload["phenomenon"] = phenomenon_payload
    payload["daily_use"] = build_daily_use_forecast(
        payload,
        original_situation=raw_situation,
        feature_type=feature_type,
        intended_move=intended_move,
        intended_timing=intended_timing,
        desired_outcome=desired_outcome,
        role_tags=role_tags,
        urgency=urgency,
    )
    payload["input_context"] = {
        "feature_type": feature_type,
        "intended_move": intended_move,
        "intended_timing": intended_timing,
        "desired_outcome": desired_outcome,
        "role_tags": role_tags or [],
        "urgency": urgency,
    }
    return payload


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    return _build_prediction_payload(
        raw_situation=request.situation,
        query_mode=request.query_mode,
        depth=request.depth,
        include_alternatives=request.alternatives,
        strategic_depth=request.strategic_depth,
        feature_type=request.feature_type,
        intended_move=request.intended_move,
        intended_timing=request.intended_timing,
        desired_outcome=request.desired_outcome,
        role_tags=request.role_tags,
        urgency=request.urgency,
    )


@app.post("/api/compare")
def compare(request: CompareRequest) -> dict:
    _assert_non_phenomenon_endpoint(request.query_mode)
    base_payload = _build_prediction_payload(
        raw_situation=request.base_situation,
        query_mode=request.query_mode,
        depth=request.depth,
        include_alternatives=request.alternatives,
        strategic_depth=request.strategic_depth,
    )
    variant_payload = _build_prediction_payload(
        raw_situation=request.variant_situation,
        query_mode=request.query_mode,
        depth=request.depth,
        include_alternatives=request.alternatives,
        strategic_depth=request.strategic_depth,
    )

    base_factors = {f["name"] for f in base_payload.get("factors", [])}
    variant_factors = {f["name"] for f in variant_payload.get("factors", [])}
    base_confidence = float(base_payload["predicted_outcome"]["confidence"])
    variant_confidence = float(variant_payload["predicted_outcome"]["confidence"])

    return {
        "base": base_payload,
        "variant": variant_payload,
        "comparison": {
            "confidence_delta": round(variant_confidence - base_confidence, 4),
            "dominant_changed": (
                base_payload["predicted_outcome"]["id"] != variant_payload["predicted_outcome"]["id"]
            ),
            "mode_changed": base_payload["mode"] != variant_payload["mode"],
            "added_factors": sorted(list(variant_factors - base_factors)),
            "removed_factors": sorted(list(base_factors - variant_factors)),
            "shared_factors": sorted(list(base_factors & variant_factors)),
        },
    }


@app.post("/api/timeline")
def timeline(request: TimelineRequest) -> dict:
    _assert_non_phenomenon_endpoint(request.query_mode)
    steps: list[dict] = []
    inflections: list[dict] = []

    ordered = [TimelineCheckpoint(label="T0", situation=request.base_situation)] + request.checkpoints
    prev_payload: dict | None = None

    for idx, checkpoint in enumerate(ordered):
        payload = _build_prediction_payload(
            raw_situation=checkpoint.situation,
            query_mode=request.query_mode,
            depth=request.depth,
            include_alternatives=request.alternatives,
            strategic_depth=request.strategic_depth,
        )
        step = {
            "index": idx,
            "label": checkpoint.label or f"T{idx}",
            "situation": checkpoint.situation,
            "prediction": payload,
            "delta": None,
        }

        if prev_payload is not None:
            prev_confidence = float(prev_payload["predicted_outcome"]["confidence"])
            curr_confidence = float(payload["predicted_outcome"]["confidence"])
            prev_factors = {f["name"] for f in prev_payload.get("factors", [])}
            curr_factors = {f["name"] for f in payload.get("factors", [])}
            outcome_changed = prev_payload["predicted_outcome"]["id"] != payload["predicted_outcome"]["id"]
            mode_changed = prev_payload["mode"] != payload["mode"]

            step["delta"] = {
                "confidence_delta": round(curr_confidence - prev_confidence, 4),
                "outcome_changed": outcome_changed,
                "mode_changed": mode_changed,
                "added_factors": sorted(list(curr_factors - prev_factors)),
                "removed_factors": sorted(list(prev_factors - curr_factors)),
            }

            if outcome_changed or mode_changed:
                inflections.append(
                    {
                        "at_step": step["label"],
                        "reason": "outcome_changed" if outcome_changed else "mode_changed",
                        "from_outcome": prev_payload["predicted_outcome"]["id"],
                        "to_outcome": payload["predicted_outcome"]["id"],
                        "from_mode": prev_payload["mode"],
                        "to_mode": payload["mode"],
                    }
                )

        steps.append(step)
        prev_payload = payload

    trend = [float(step["prediction"]["predicted_outcome"]["confidence"]) for step in steps]
    return {"steps": steps, "confidence_trend": trend, "inflections": inflections}


@app.post("/api/semantics")
def semantics(request: SemanticsRequest) -> dict:
    normalized_query_mode = _normalize_query_mode(request.query_mode)
    phenomenon_tag = _extract_first_tag(request.situation)
    resolved_situation, profiles_used = resolve_profiles_in_text(request.situation)
    parsed = parse_situation(resolved_situation)
    phenomenon_payload = None
    if normalized_query_mode == "phenomenon" and phenomenon_tag in SUPPORTED_PHENOMENA:
        try:
            context = build_phenomenon_context(
                raw_text=resolved_situation,
                tag=phenomenon_tag,
            )
            phenomenon_payload = {
                "module": context.tag,
                "query": context.normalized_query,
                "summary": context.summary,
                "hypotheses": context.hypotheses,
                "evidence": [
                    {
                        "source": item.source,
                        "title": item.title,
                        "snippet": item.snippet,
                        "url": item.url,
                    }
                    for item in context.evidence
                ],
            }
        except ValueError:
            phenomenon_payload = None
    return {
        "raw_text": request.situation,
        "resolved_situation": parsed.raw_text,
        "mode": parsed.mode,
        "domain": parsed.domain,
        "conflict": parsed.conflict,
        "actors": parsed.actors,
        "institutions": parsed.institutions,
        "query_mode": normalized_query_mode,
        "phenomenon_tag": phenomenon_tag,
        "supported_phenomenon_tags": sorted(list(SUPPORTED_PHENOMENA)),
        "phenomenon": phenomenon_payload,
        "profiles_used": [{"tag": p["tag"], "name": p["name"]} for p in profiles_used],
        "source": "backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/profiles")
def create_profile_endpoint(request: ProfileCreateRequest) -> dict:
    if request.profile_type not in {"individual", "group", "population"}:
        return {"error": "invalid_profile_type"}
    if not request.name.strip():
        return {"error": "name_required"}
    return create_profile(
        name=request.name,
        profile_type=request.profile_type,
        description=request.description,
        attributes=request.attributes,
        tag=request.tag,
    )


@app.get("/api/profiles")
def list_profiles_endpoint() -> list[dict]:
    return list_profiles()


@app.get("/api/profiles/{tag}")
def get_profile_endpoint(tag: str) -> dict:
    item = get_profile(tag)
    if item is None:
        return {"error": "not_found"}
    return item


@app.post("/api/profiles/{tag}/update")
def update_profile_endpoint(tag: str, request: ProfileUpdateRequest) -> dict:
    if request.profile_type is not None and request.profile_type not in {"individual", "group", "population"}:
        return {"error": "invalid_profile_type"}
    item = update_profile(
        tag=tag,
        name=request.name,
        profile_type=request.profile_type,
        description=request.description,
        attributes=request.attributes,
    )
    if item is None:
        return {"error": "not_found"}
    return item


@app.post("/api/tracking")
def create_tracking(request: TrackingCreateRequest) -> dict:
    return create_tracking_item(
        situation=request.situation,
        prediction=request.prediction,
        started_at=request.started_at,
        expected_at=request.expected_at,
    )


@app.get("/api/tracking")
def list_tracking() -> list[dict]:
    ensure_dummy_tracking_item()
    return list_tracking_items()


@app.get("/api/tracking/{item_id}")
def get_tracking(item_id: str) -> dict:
    item = get_tracking_item(item_id)
    if item is None:
        return {"error": "not_found"}
    return item


@app.post("/api/tracking/{item_id}/vote")
def vote_tracking(item_id: str, request: TrackingVoteRequest) -> dict:
    if request.vote not in {"accurate", "inaccurate"}:
        return {"error": "invalid_vote"}
    if request.vote == "inaccurate" and not (request.actual_outcome or "").strip():
        return {"error": "actual_outcome_required"}
    item = vote_tracking_item(
        item_id=item_id,
        vote=request.vote,
        actual_outcome=request.actual_outcome,
        actual_at=request.actual_at,
    )
    if item is None:
        return {"error": "not_found"}
    return item


@app.post("/api/queries")
def create_query_endpoint(request: QueryCreateRequest) -> dict:
    if not request.situation.strip():
        return {"error": "situation_required"}
    return create_query_item(
        situation=request.situation,
        query_mode=request.query_mode,
        prediction=request.prediction,
    )


@app.get("/api/queries")
def list_queries_endpoint(q: str = Query(default="")) -> list[dict]:
    if (q or "").strip():
        return search_query_items(q)
    return list_query_items()


@app.get("/api/queries/{item_id}")
def get_query_endpoint(item_id: str) -> dict:
    item = get_query_item(item_id)
    if item is None:
        return {"error": "not_found"}
    return item


@app.post("/api/queries/{item_id}/reflect")
def reflect_query_endpoint(item_id: str, request: ReflectionRequest) -> dict:
    item = get_query_item(item_id)
    if item is None:
        return {"error": "not_found"}
    if request.forecast_accuracy not in {"accurate", "inaccurate"}:
        return {"error": "invalid_forecast_accuracy"}
    reflection = build_reflection_response(
        forecast=item.get("prediction", {}).get("daily_use", {}),
        outcome_summary=request.outcome_summary,
        forecast_accuracy=request.forecast_accuracy,
        action_taken=request.action_taken,
    )
    reflection["outcome_summary"] = request.outcome_summary
    updated = reflect_query_item(item_id, reflection)
    if updated is None:
        return {"error": "not_found"}
    return updated


@app.get("/api/reputation")
def reputation_endpoint() -> dict:
    return build_reputation_summary(list_query_items())


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_INDEX_FILE)


@app.get("/index.html")
def index_html() -> FileResponse:
    return FileResponse(_INDEX_FILE)


def create_app() -> FastAPI:
    return app


def main() -> None:
    import uvicorn

    uvicorn.run("sse.api.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
