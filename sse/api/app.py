from __future__ import annotations

from pathlib import Path

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sse.orchestrator import RunConfig, run_sse_with_trace
from sse.profiles import create_profile, get_profile, list_profiles, resolve_profiles_in_text, update_profile
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
    depth: str = "default"
    alternatives: bool = False


class CompareRequest(BaseModel):
    base_situation: str
    variant_situation: str
    depth: str = "default"
    alternatives: bool = False


class TimelineCheckpoint(BaseModel):
    label: str
    situation: str


class TimelineRequest(BaseModel):
    base_situation: str
    checkpoints: list[TimelineCheckpoint]
    depth: str = "default"
    alternatives: bool = False


class SemanticsRequest(BaseModel):
    situation: str


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


def _build_prediction_payload(
    raw_situation: str,
    depth: str = "default",
    include_alternatives: bool = False,
) -> dict:
    resolved_situation, profiles_used = resolve_profiles_in_text(raw_situation)
    result, trace = run_sse_with_trace(
        resolved_situation,
        RunConfig(depth=depth, include_alternatives=include_alternatives),
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
    payload["profiles_used"] = [{"tag": p["tag"], "name": p["name"]} for p in profiles_used]
    return payload


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    return _build_prediction_payload(
        raw_situation=request.situation,
        depth=request.depth,
        include_alternatives=request.alternatives,
    )


@app.post("/api/compare")
def compare(request: CompareRequest) -> dict:
    base_payload = _build_prediction_payload(
        raw_situation=request.base_situation,
        depth=request.depth,
        include_alternatives=request.alternatives,
    )
    variant_payload = _build_prediction_payload(
        raw_situation=request.variant_situation,
        depth=request.depth,
        include_alternatives=request.alternatives,
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
    steps: list[dict] = []
    inflections: list[dict] = []

    ordered = [TimelineCheckpoint(label="T0", situation=request.base_situation)] + request.checkpoints
    prev_payload: dict | None = None

    for idx, checkpoint in enumerate(ordered):
        payload = _build_prediction_payload(
            raw_situation=checkpoint.situation,
            depth=request.depth,
            include_alternatives=request.alternatives,
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
    resolved_situation, profiles_used = resolve_profiles_in_text(request.situation)
    parsed = parse_situation(resolved_situation)
    return {
        "raw_text": request.situation,
        "resolved_situation": parsed.raw_text,
        "mode": parsed.mode,
        "domain": parsed.domain,
        "conflict": parsed.conflict,
        "actors": parsed.actors,
        "institutions": parsed.institutions,
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
