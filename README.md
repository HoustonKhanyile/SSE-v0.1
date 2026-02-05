# Social Simulation Engine (SSE)

This repository implements the **Minimal Runnable Prototype (MRP v0.1)** as described in:
`readme_md_sse_minimal_runnable_prototype_v_0.md`.

If you want the full spec, open:
`readme_md_sse_minimal_runnable_prototype_v_0.md`

## Project Breakdown

```
sse/
  contracts/        # Authoritative data contracts (PredictionResult, Outcome, etc.)
  ssm/              # Situation Semantics Mapper
  ess/              # Objective context snapshot (constraints, affordances)
  mcm/              # Psychological & sociological priors (stub)
  sqc/              # Cognition & outcome scoring (stub)
  explainer/        # Explanation layer (trace-based)
  orchestrator/     # Deterministic execution pipeline
  demo/             # CLI runner + demo situations
  tests/            # Contract, mode, and end-to-end tests
```

## Quickstart

```bash
pip install -e .
python -m sse.demo --example workplace_promotion
```

## Custom Situation

```bash
python -m sse.demo --situation "A student is tempted to cheat during an exam" --depth default
```

## Example Output

```json
{
  "predicted_outcome": {
    "id": "quiet_job_search",
    "label": "The employee quietly searches for another job while maintaining performance.",
    "confidence": 0.68,
    "rationale": [
      "career preservation",
      "avoid open conflict"
    ]
  },
  "explanation": "The employee quietly searches for another job while maintaining performance. This outcome is most likely given the constraints and priors in the situation.",
  "horizon": "days",
  "mode": "B"
}
```

## Tests

```bash
pytest
```

## Frontend (Static)

Open `frontend/index.html` in a browser to use the single-page UI.

## API Server (Local)

```bash
pip install -e .
python -m sse.api
```

Then open:
`http://127.0.0.1:8000/`

The frontend calls:
`http://127.0.0.1:8000/api/predict`
