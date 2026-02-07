from __future__ import annotations

from pathlib import Path

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sse.orchestrator import RunConfig, run_sse_with_trace
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


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    result, trace = run_sse_with_trace(
        request.situation,
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
    return payload


@app.post("/api/semantics")
def semantics(request: SemanticsRequest) -> dict:
    parsed = parse_situation(request.situation)
    return {
        "raw_text": parsed.raw_text,
        "mode": parsed.mode,
        "domain": parsed.domain,
        "conflict": parsed.conflict,
        "actors": parsed.actors,
        "institutions": parsed.institutions,
        "source": "backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


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
