from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from sse.orchestrator import RunConfig, run_sse

app = FastAPI(title="SSE API", version="0.1.0")


class PredictRequest(BaseModel):
    situation: str
    depth: str = "default"
    alternatives: bool = False


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    result = run_sse(
        request.situation,
        RunConfig(depth=request.depth, include_alternatives=request.alternatives),
    )
    return result.to_dict()


def create_app() -> FastAPI:
    return app


def main() -> None:
    import uvicorn

    uvicorn.run("sse.api.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
