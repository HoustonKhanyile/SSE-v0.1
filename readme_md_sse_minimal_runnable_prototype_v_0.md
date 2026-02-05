# Social Simulation Engine (SSE)

## Minimal Runnable Prototype (MRP v0.1)

This repository implements a **deterministic, end-to-end prototype** of the Social Simulation Engine (SSE).

The purpose of v0.1 is **not realism**, but **architectural proof**:

- arbitrary situation input
- automatic situation understanding
- context compilation
- cognition-driven behavior simulation
- dominant outcome selection
- explanation by default

If this runs end-to-end and produces a valid `PredictionResult`, the system is working.

---

## What SSE Does (v0.1)

Given a user-provided situation, SSE:

1. Parses the semantics of the situation (SSM)
2. Infers the relevant context radius (A / B / C)
3. Compiles environmental and institutional constraints (ESS snapshot)
4. Synthesizes psychological and sociological priors (MCM stub)
5. Simulates cognition and action selection (SQC stub)
6. Selects the dominant realized outcome
7. Explains **why this outcome occurs**

The default output answers:

> **This is what will most likely happen — and why.**

---

## Repository Structure

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

---

## How to Run the Demo

### 1. Install (local)

```bash
pip install -e .
```

### 2. Run a demo situation

```bash
python -m sse.demo --example workplace_promotion
```

### 3. Provide a custom situation

```bash
python -m sse.demo --situation "A student is tempted to cheat during an exam" \
                   --depth default
```

### 4. Request deeper analysis

```bash
python -m sse.demo --example public_tax_policy --depth deep
```

---

## Execution Pipeline (v0.1)

```
Situation Text
   ↓
SSM (parse → graph → mode select)
   ↓
ESS Snapshot + MCM Priors
   ↓
PRΔ Computation
   ↓
SQC Cognition & Outcome Scoring
   ↓
Dominant Outcome Selection
   ↓
Explanation Generation
   ↓
PredictionResult (JSON)
```

All steps are deterministic in v0.1.

---

## Authoritative Output Contract

Every run returns a valid **PredictionResult** object:

- `predicted_outcome` (mandatory)
- `explanation` (mandatory)
- `horizon` (inferred by default)
- `mode` (A / B / C)

Alternative outcomes and trajectories are returned **only when requested**.

---

## Demo Situation Set (Canonical)

The following demo situations are included for testing and demonstration. Each is designed to exercise a different inference mode.

### Mode A — Single-Actor Behavior

**ID:** `exam_cheating`

> *A student notices that the invigilator has stepped out briefly during an exam and considers whether to cheat.*

Expected dominant outcome:
- The student does not cheat but experiences internal conflict.

---

### Mode B — Multi-Actor Interaction

**ID:** `workplace_promotion`

> *An employee who has consistently exceeded performance targets has been denied a promotion without a clear explanation and is deciding how to respond.*

Expected dominant outcome:
- The employee begins quietly searching for another job while maintaining performance.

---

### Mode B — Interpersonal Conflict

**ID:** `manager_confrontation`

> *An employee confronts their manager about unpaid overtime while knowing HR may become involved.*

Expected dominant outcome:
- The employee raises the issue cautiously rather than aggressively.

---

### Mode C — Population Response

**ID:** `public_tax_policy`

> *A government announces a sudden increase in fuel taxes, affecting commuters and small businesses.*

Expected dominant outcome:
- Widespread dissatisfaction and short-term protest activity among affected groups.

---

### Mode C — Cultural Shift

**ID:** `platform_algorithm_change`

> *A social media platform changes its algorithm, reducing visibility for independent creators.*

Expected dominant outcome:
- Gradual creator migration and increased public criticism of the platform.

---

## Testing Expectations

Minimum tests to pass for v0.1:

- identical input produces identical output
- every demo returns a valid PredictionResult
- inference mode matches expected A/B/C
- explanation is always present

---

## What v0.1 Is Not

- It is not predictive ground truth
- It is not a trained cognition model
- It is not a full societal simulator

It is a **working skeleton** that proves SSE’s architecture and philosophy.

---

## Upgrade Path

Once v0.1 is stable:

- replace rule-based SSM with learned semantics
- replace MCM heuristics with music-driven priors
- replace SQC scoring with trained cognition model
- extend ESS snapshots into multi-step environments

The **PredictionResult API remains stable throughout**.

---

## Final Note

If this prototype runs end-to-end and produces explanations that feel *structurally correct*, SSE is already doing something meaningful.

Everything else is scale.

