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


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    resolved_situation, profiles_used = resolve_profiles_in_text(request.situation)
    result, trace = run_sse_with_trace(
        resolved_situation,
        RunConfig(depth=request.depth, include_alternatives=request.alternatives),
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
