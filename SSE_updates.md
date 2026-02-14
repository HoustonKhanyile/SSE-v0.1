# SSE Updates

This document captures updates made after the original v0.1 prototype spec in `readme_md_sse_minimal_runnable_prototype_v_0.md`.

## Scope
The system has been extended from a minimal deterministic prototype into a richer interactive demo platform with:
- profile-aware inference (`@tag` references)
- counterfactual comparison
- timeline replay simulation
- tracked prediction evaluation
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

## Frontend Updates

### 1. Main Interface (`frontend/index.html`, `frontend/app.js`, `frontend/styles.css`)
Added:
- profile icon (`P`) and tracking icon (`T`) in top-right
- profile mention chips under situation input for detected `@tags`
- semantics panel with editable values and add/remove user variables
- compare mode panel + result section (base/variant side-by-side)
- timeline replay panel with checkpoint rows (`T1`, `T2`, ...), read-only labels, plus-button add
- factor sidebar with clickable expand/collapse role explanations
- metadata rendering improvements
- glossary updates for all new concepts
- centered disclaimer with scope link

### 2. Profile Pages
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

### 3. Tracking Pages
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

### 4. About / Documentation UI
Added:
- `frontend/about.html`

Purpose:
- explain what SSE is
- explain how SSE works
- explain what SSE does not do

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

## Status
SSE v0.1 now behaves as an extended prototype platform with deterministic core simulation plus scenario tools, profile context injection, and post-hoc evaluation workflows.
