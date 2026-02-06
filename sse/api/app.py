from __future__ import annotations

from pathlib import Path

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sse.orchestrator import RunConfig, run_sse_with_trace
from sse.ssm import parse_situation

app = FastAPI(title="SSE API", version="0.1.0")

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
_INDEX_FILE = _FRONTEND_DIR / "index.html"

if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")


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
