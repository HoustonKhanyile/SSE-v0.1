# SSE Updates

This document captures updates made after the original v0.1 prototype spec in `readme_md_sse_minimal_runnable_prototype_v_0.md`.

## Scope
The system has been extended from a minimal deterministic prototype into a richer interactive demo platform with:
- profile-aware inference (`@tag` references)
- counterfactual comparison
- timeline replay simulation
- tracked prediction evaluation
- persistent query history with search and detail views
- phenomenon query mode (`General` vs `Phenomenon`)
- expanded frontend UX and documentation surfaces

## Backend Updates

### 1. Profile System
Added persistent actor profiles for `individual`, `group`, and `population`.

New module:
- `sse/profiles/store.py`
- `sse/profiles/__init__.py`

Capabilities:
- create profile
- list profiles
- get profile by tag
- update profile by tag
- resolve `@profile_tag` mentions in situation text and inject profile context for inference

Profile data store:
- `sse/data/profiles_store.json` (local runtime data)

### 2. Tracking System
Added persistent tracking for predicted situations and post-outcome evaluation.

Module:
- `sse/tracking/store.py`
- `sse/tracking/__init__.py`

Capabilities:
- create tracking item
- list tracking items
- get tracking item
- vote accurate/inaccurate
- capture actual observed outcome notes
- seed dummy item when store is empty

Tracking data store:
- `sse/data/tracking_store.json`

### 3. Compare Mode API
Added side-by-side counterfactual comparison endpoint.

Endpoint:
- `POST /api/compare`

Returns:
- base prediction payload
- variant prediction payload
- confidence delta
- dominant outcome changed flag
- mode changed flag
- added/removed/shared factor diff

### 4. Timeline Replay API
Added stepwise replay across checkpoints.

Endpoint:
- `POST /api/timeline`

Returns:
- ordered timeline steps (T0 + checkpoints)
- prediction per step
- per-step deltas (confidence, outcome/mode change, factor add/remove)
- confidence trend
- inflection points (where outcome/mode changes)

### 5. Profile-aware Predict/Semantics
Existing endpoints now resolve profile mentions before processing:
- `POST /api/predict`
- `POST /api/semantics`

Extended response metadata includes:
- `resolved_situation`
- `profiles_used`

### 6. API Surface Summary
Current expanded API includes:
- `POST /api/predict`
- `POST /api/compare`
- `POST /api/timeline`
- `POST /api/semantics`
- `POST /api/profiles`
- `GET /api/profiles`
- `GET /api/profiles/{tag}`
- `POST /api/profiles/{tag}/update`
- `POST /api/tracking`
- `GET /api/tracking`
- `GET /api/tracking/{item_id}`
- `POST /api/tracking/{item_id}/vote`
- `POST /api/queries`
- `GET /api/queries`
- `GET /api/queries/{item_id}`

### 7. Phenomenon Query Mode
Added a dedicated `query_mode` flow with two values:
- `general`
- `phenomenon`

Phenomenon behavior:
- requires a phenomenon tag in input text
- supported tags:
  - `@language`
  - `@trend`
  - `@behavior`
- routes to phenomenon module logic before SSE inference
- still uses SSE core pipeline (`SSM`, `ESS`, `MCM`, `SQC`, `Explainer`) by enriching situation text with module context

New module package:
- `sse/phenomenon/modules.py`
- `sse/phenomenon/__init__.py`

Phenomenon module outputs:
- normalized phenomenon query
- module summary
- hypotheses
- evidence list
- enriched text used for downstream inference

Internet-enabled enrichment:
- phenomenon modules perform targeted web lookup (DuckDuckGo Instant Answer API) for evidence extraction
- fallback behavior remains deterministic if network results are unavailable

API contract updates:
- `POST /api/predict` accepts `query_mode`
- `POST /api/semantics` accepts `query_mode`
- responses include:
  - `query_mode`
  - `phenomenon_tag`
  - `phenomenon` payload (module/query/summary/hypotheses/evidence)
  - `pipeline` marker showing SSE components used
- compare/timeline endpoints reject phenomenon mode:
  - `POST /api/compare` -> `400` for `query_mode=phenomenon`
  - `POST /api/timeline` -> `400` for `query_mode=phenomenon`

### 8. Query Persistence and Retrieval
Added persistent query history using local JSON storage (no database required).

New module package:
- `sse/queries/store.py`
- `sse/queries/__init__.py`

Query data store:
- `sse/data/queries_store.json`

Capabilities:
- save query input + query mode + prediction payload
- list query history (most recent first)
- search query history by text (`situation`, `query_mode`, predicted outcome label)
- fetch a single saved query by id

Endpoints:
- `POST /api/queries`
- `GET /api/queries` (supports search via `?q=...`)
- `GET /api/queries/{item_id}`

### 9. Guardrails v0.1.1 (Utility-Preserving, Configurable)
Added a deterministic, local guardrail layer at the API prediction boundary to reduce harmful operational misuse while preserving normal analytical utility.

New modules:
- `sse/guardrails/policy.py`
- `sse/guardrails/__init__.py`
- `sse/config.py`

Guardrail mode configuration:
- env var: `SSE_GUARDRAIL_MODE`
- supported values:
  - `off`
  - `audit`
  - `enforce`
- default/fallback: `enforce`

Guardrail behavior:
- `off`:
  - prediction runs normally
  - response includes `guardrail` metadata with `status="clear"`
- `audit`:
  - prediction runs normally
  - flagged requests include `guardrail.status="flagged"`
- `enforce`:
  - flagged requests return a soft-block payload (HTTP `200`) with prediction-compatible schema
  - payload uses synthetic outcome:
    - `predicted_outcome.id = "guardrail_blocked"`
    - `trace = "guardrail:block"`
    - `factors = []`

New response field (predict/compare/timeline payloads):
- `guardrail` object with:
  - `status` (`blocked` | `flagged` | `clear`)
  - `mode` (`off` | `audit` | `enforce`)
  - `category`
  - `reason`
  - `safe_reframe`

Current enforcement scope:
- enabled on:
  - `POST /api/predict`
  - `POST /api/compare`
  - `POST /api/timeline`
- intentionally not enforced on:
  - `POST /api/semantics`

Policy design notes:
- rule-based (no external moderation service)
- deterministic and local-only
- tuned to minimize false positives for:
  - analytical framing (`analysis`, `simulation`, `forecast`, policy framing)
  - preventive/defensive framing (`prevent`, `mitigate`, `incident response`, `compliance`)
- still blocks clear operational harmful intent (e.g., step-by-step or evasive instruction requests)

Test coverage added:
- `tests/test_guardrails_policy.py`
- `tests/test_guardrails_config.py`
- `tests/test_guardrails_api.py`

## Frontend Updates

### 1. Main Interface (`frontend/index.html`, `frontend/app.js`, `frontend/styles.css`)
Added:
- profile icon (`P`) and tracking icon (`T`) in top-right
- query search bar in top-right (next to profile/tracking icons)
- left-side query menu icon (`Q`) opening a dedicated saved-queries sidebar
- profile mention chips under situation input for detected `@tags`
- semantics panel with editable values and add/remove user variables
- compare mode panel + result section (base/variant side-by-side)
- timeline replay panel with checkpoint rows (`T1`, `T2`, ...), read-only labels, plus-button add
- factor sidebar with clickable expand/collapse role explanations
- metadata rendering improvements
- glossary updates for all new concepts
- centered disclaimer with scope link

Query history behavior:
- successful `Run SSE` responses are persisted into query history
- top-right search filters saved queries
- search results render in left query sidebar
- clicking a saved query opens dedicated query detail page:
  - `/static/query.html?id=<query_id>`

### 2. Phenomenon Mode UI (`frontend/index.html`, `frontend/app.js`, `frontend/styles.css`)
Added:
- query-mode selector (`General` / `Phenomenon`) next to primary action controls
- phenomenon-aware hints and validation messaging
- supported phenomenon tags surfaced in UI behavior:
  - `@language`
  - `@trend`
  - `@behavior`

Behavior changes in `Phenomenon` mode:
- compare and timeline controls are hidden
- compare and timeline panels/outputs are closed/hidden if active
- `Run SSE` and `Semantics` remain available

Output card changes:
- default output title remains `PredictionResult` in general mode
- phenomenon mode output title is `Breakdown`
- breakdown section renders:
  - module
  - question
  - summary
  - hypotheses
  - evidence
- phenomenon card removes:
  - horizon display
  - confidence display
  - `AlternativeOutcomeSet` entry path (sidebar toggle hidden, alternatives block hidden)

### 3. Profile Pages
Added/updated:
- `frontend/create-profile.html` (create/list profiles)
- `frontend/profiles.js`
- `frontend/profiles.css`
- `frontend/profile.html` (single profile detail/update)
- `frontend/profile.js`
- `frontend/profiles.html` now acts as redirect to `create-profile.html`

Behavior:
- saved profiles are clickable links to profile detail page
- profile detail page supports updates

### 4. Tracking Pages
Added:
- `frontend/tracking.html`
- `frontend/tracking.js`
- `frontend/tracking-detail.html`
- `frontend/tracking-detail.js`
- `frontend/tracking.css`

Behavior:
- list tracked situations
- open detail
- vote accurate/inaccurate
- inaccurate flow requires actual-outcome note

### 5. About / Documentation UI
Added:
- `frontend/about.html`

Purpose:
- explain what SSE is
- explain how SSE works
- explain what SSE does not do

### 6. Query Detail Page UI
Added:
- `frontend/query.html`
- `frontend/query.js`
- `frontend/query.css`

Behavior:
- loads one saved query by id via `GET /api/queries/{item_id}`
- shows core query details (situation, mode, saved timestamp, predicted outcome, confidence, horizon)
- for `general` queries, includes full reasoning card sections:
  - `Primary Factors`
  - `AlternativeOutcomeSet`
  - `Trace`
  - `Metadata` (prediction source and timestamp)

## Accessibility and UX Improvements
- sidebar open/close behavior adjusted to avoid `aria-hidden` focus issue
- use of `inert` for non-interactive hidden sidebar state
- focus return behavior improved
- cache-busting query parameters added for static assets during iterative updates

## Local-only / Repo Hygiene Updates
Updated `.gitignore` to keep local tooling artifacts out of pushes:
- `node_modules/`
- `artifacts/`
- `playwright-report/`
- `test-results/`
- `sse/data/profiles_store.json`

## Practical Usage Notes

### Profile tagging in queries
Example:
- `How will @city_commuters react to the tax change?`

### Phenomenon queries
Examples:
- `@language: how did the term "aura farming" come to be?`
- `@trend: why did this behavior spread so quickly?`
- `@behavior: why do users keep doomscrolling at night?`

Notes:
- use `Phenomenon` mode in the dropdown
- include one supported phenomenon tag in the text
- compare/timeline are intentionally unavailable in this mode

### Compare Mode
Use base + variant to get:
- confidence delta
- factor diff
- outcome/mode changes

### Timeline Replay
Use checkpoint rows (`T1`, `T2`, ...):
- labels are read-only
- situations are editable
- plus button adds next checkpoint

### Tracking
Track a prediction from run-time to observed outcome and vote accuracy later.

### Query History and Search
- run `Run SSE` to persist a query snapshot
- use top-right search to filter saved history
- open left query sidebar with the `Q` button
- click a result to open dedicated saved query detail page

## Status
SSE v0.1 now behaves as an extended prototype platform with deterministic core simulation plus scenario tools, profile context injection, persistent query-memory and retrieval workflows, post-hoc evaluation features, a dedicated phenomenon analysis path with internet-assisted evidence enrichment, and configurable API guardrails that preserve utility while reducing harmful operational misuse.
