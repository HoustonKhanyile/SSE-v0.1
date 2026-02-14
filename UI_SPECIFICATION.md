# SSE UI Detailed Specification

This document defines the current SSE demo UI in implementation-level detail so it can be replicated exactly in another project.

## Framework Requirement
- The replicated UI implementation must use a Node.js framework/runtime for frontend delivery and behavior.
- Acceptable implementation pattern: Node.js-driven web app (for example, a React/Next.js, Vue/Nuxt, SvelteKit, or equivalent Node.js-based stack).
- The goal is parity of UI/UX and behavior while keeping the implementation in the Node.js ecosystem.

## 1. Global Visual System

### 1.1 Typography
- Primary UI font: `Space Grotesk`
- Secondary/body/explanation font: `Source Serif 4`
- Fallbacks:
  - Sans: `"Segoe UI", sans-serif`
  - Serif: `"Times New Roman", serif`

### 1.2 Core Color Tokens
Defined in `frontend/styles.css`:
- `--bg: #0c0f1a`
- `--panel: rgba(18, 23, 38, 0.92)`
- `--panel-strong: #131a2e`
- `--accent: #ffb347`
- `--accent-2: #48d7ff`
- `--text: #f5f7ff`
- `--muted: #a6b0c8`
- `--border: rgba(255, 255, 255, 0.12)`
- `--shadow: 0 30px 80px rgba(4, 10, 24, 0.6)`

### 1.3 Global Canvas
- Body uses dark atmospheric background with animated orb layers and subtle masked grid.
- Main app container width: `max-width: 980px`
- Main page padding: `64px 24px 120px`
- Panel shape: rounded (`24px`) with translucent dark background and border.

## 2. Main Application Page (`frontend/index.html`)

## 2.1 Top-right Utility Icons
Container: `.top-links`
- Fixed at top-right (`top: 18px; right: 18px`)
- Horizontal icon row with `8px` gap.

Icons:
- Profile icon: `P`
  - Link target: `/static/create-profile.html`
  - Style variant uses `--accent` tint.
- Tracking icon: `T`
  - Link target: `/static/tracking.html`
  - Style variant uses `--accent-2` tint.

Icon style:
- 38x38 circular chip
- translucent dark background
- outlined border
- centered single-letter label

## 2.2 Hero Header
- Kicker text: `Social Simulation Engine`
- Main heading: `Situation-to-Outcome Prototype`
- Supporting line explains dominant outcome + explanation behavior.

## 2.3 Primary Input Panel

Elements (top-down):
1. Label: `Situation Text`
2. Main textarea `#situation`
   - Rounded, dark field
   - Placeholder: exam-cheating example
3. Profile mention chips container `#profile-mentions`
   - Auto-populated from `@tag` mentions in textarea
   - Each chip links to `/static/profile.html?tag=<tag>`
4. Action row `.actions`
   - `Run SSE` button `#run`
   - `Compare Mode` button `#compare-toggle`
   - `Timeline Replay` button `#timeline-toggle`
   - `Semantics` button `#semantics-toggle`
   - Hint text: profile tag guidance

## 2.4 Compare Mode Panel (`#compare-panel`)
Hidden by default; toggled by `#compare-toggle`.

Contains:
- Label: `Variant Situation`
- Variant textarea `#variant-situation`
- `Run Compare` button `#run-compare`

Purpose:
- Compare base situation (`#situation`) vs variant situation.

## 2.5 Timeline Replay Panel (`#timeline-panel`)
Hidden by default; toggled by `#timeline-toggle`.

Contains:
- Header title: `Timeline Checkpoints`
- Plus button `#timeline-add`
- Row container `#timeline-rows`
- `Run Timeline` button `#run-timeline`

Row behavior:
- Default one row exists: `T1`
- Each row has:
  - read-only checkpoint label input (`T1`, `T2`, ...)
  - editable checkpoint situation input
- Plus button appends next checkpoint label.

## 2.6 Semantics Panel (`#semantics-panel`)
Hidden by default; toggled by `#semantics-toggle`.

Contains:
- Header title: `Situation Semantics`
- Plus button `#semantics-add`
- Run button `#semantics-run`
- Row container `#semantics-rows`

Row behavior:
- System semantic keys (mode/domain/conflict/actors/institutions): read-only key input, editable value.
- User variables: key/value editable and deletable via `x` button.

## 2.7 Prediction Output Panel (`#output`)
Hidden until `Run SSE`.

Sections:
- Header: `PredictionResult` + mode pill `#mode`
- Dominant outcome text `#outcome`
- Explanation text `#explanation`
- Meta row:
  - `#horizon`
  - `#confidence`
  - `Track Situation` button `#track-situation`
- Right-aligned sidebar toggle: `>` link `#toggle`

## 2.8 Counterfactual Compare Output (`#compare-output`)
Hidden until `Run Compare`.

Sections:
- Header: `Counterfactual Compare` + delta badge `#compare-delta`
- Two-card comparison grid:
  - Base card:
    - `#compare-base-outcome`
    - `#compare-base-meta`
  - Variant card:
    - `#compare-variant-outcome`
    - `#compare-variant-meta`
- Factor diff block:
  - Added factors `#compare-added`
  - Removed factors `#compare-removed`
  - Shared factors `#compare-shared`

## 2.9 Timeline Replay Output (`#timeline-output`)
Hidden until `Run Timeline`.

Sections:
- Header: `Timeline Replay` + trend badge `#timeline-trend`
- Step list container `#timeline-steps-list`
  - one card per step (T0 + checkpoints)
  - includes situation, dominant outcome, mode/horizon/confidence, delta summary
- Inflection section:
  - `#timeline-inflections` showing outcome/mode change points

## 2.10 Sidebar (`#sidebar`)
Right slide-over panel, closed by default.

Header:
- Title: `AlternativeOutcomeSet`
- `Close` button `#close`

Content blocks:
1. Primary Factors (`#factors`)
   - each factor is a clickable row
   - expands to role explanation
2. Alternatives (`#alternatives`)
3. Trace (`#trace`)
4. Metadata:
   - `#meta-source`
   - `#meta-time`

Overlay:
- Scrim `#scrim` visible when sidebar open

Accessibility behavior:
- Sidebar uses `aria-hidden` and `inert` when closed
- Focus moves to close button on open
- Focus returns to `#toggle` on close
- `Esc` closes sidebar

## 2.11 Glossary Control
Bottom-left floating info control:
- Button `.glossary-btn` (`i` in circle)
- Hover/focus opens `.glossary-panel`

Glossary includes:
- core engine terms (SSE, SSM, ESS, MCM, SQC, PredictionResult, Mode A/B/C, etc.)
- profile system concepts
- compare mode concepts
- timeline concepts
- tracking/evaluation concepts

## 2.12 Disclaimer Footer
Bottom-centered fine print:
- Two-line disclaimer text
- Link: `Read full SSE scope.` -> `/static/about.html`

## 3. Create Profile Page (`frontend/create-profile.html`)

Purpose:
- Create and list actor profiles.

Header:
- Title: `Create Profile`
- Back link to `/`

Create form fields:
- Name `#name`
- Tag `#tag` (optional)
- Type `#profile-type` (`individual`, `group`, `population`)
- Description `#description`
- Attributes `#attributes` (key:value per line)
- Submit button

Status:
- `#status` shows save result/failures.

Saved profiles list:
- Container `#profiles`
- Each item shows:
  - Name (clickable link)
  - `@tag`
  - profile type
  - description
  - attributes summary
  - direct `Open profile` link

Link target:
- `/static/profile.html?tag=<tag>`

## 4. Profile Detail Page (`frontend/profile.html`)

Purpose:
- View and update one profile.

Header:
- Title: `Profile`
- Back link to create page

Form fields:
- Name (editable)
- Tag (read-only)
- Type (editable select)
- Description (editable)
- Attributes (editable multiline key:value)
- `Update Profile` button

Behavior:
- Reads tag from URL query (`?tag=`)
- Loads profile from API
- Submits updates to API and shows status message

## 5. Tracking Pages

## 5.1 Tracking List (`frontend/tracking.html`)
- Title: `Tracked Situations`
- Back link to simulator
- List container `#list`
- Each list item links to detail page with query id

## 5.2 Tracking Detail (`frontend/tracking-detail.html`)
- Title: `Situation Detail`
- Back link to list
- Detail card `#detail` (situation, prediction, timeline fields, vote status)
- Accuracy vote section:
  - `#vote-accurate`
  - `#vote-inaccurate`
- Inaccurate dropdown panel `#inaccurate-panel`:
  - textarea `#actual-outcome`
  - submit button `#submit-inaccurate`
- Vote result text `#vote-status`

## 6. About Page (`frontend/about.html`)

Purpose:
- Explain scope and limits.

Sections:
- What SSE is
- How it works
- What it does not do
- Why transparency matters
- Back link to simulator

## 7. Responsiveness

Breakpoint: `max-width: 720px`
- Meta row stacks vertically
- Action row stacks vertically
- Compare cards collapse to single column
- Top-right icon cluster shifts inward
- Glossary/disclaimer dimensions adjusted for narrow viewports

## 8. Motion and Interaction

Animations:
- Orb float background animation
- Output fade-in animation

Interactive surfaces:
- Buttons and icon chips use hover/active cues
- Factor rows toggle open/closed detail panels
- Panels toggle via dedicated controls:
  - compare
  - timeline
  - semantics
  - sidebar

## 9. API Binding Matrix (UI -> Backend)

Main app:
- `Run SSE` -> `POST /api/predict`
- `Semantics` panel load -> `POST /api/semantics`
- `Run Compare` -> `POST /api/compare`
- `Run Timeline` -> `POST /api/timeline`
- `Track Situation` -> `POST /api/tracking`

Profiles:
- Create form -> `POST /api/profiles`
- Saved profile list -> `GET /api/profiles`
- Detail load -> `GET /api/profiles/{tag}`
- Update -> `POST /api/profiles/{tag}/update`

Tracking:
- List -> `GET /api/tracking`
- Detail -> `GET /api/tracking/{item_id}`
- Vote -> `POST /api/tracking/{item_id}/vote`

## 10. Required Fidelity Checklist

To reproduce this UI exactly, preserve:
- color tokens and typography choices
- rounded panel geometry and translucency
- top-right profile/tracking icon behavior
- profile mention chips under situation input
- structured semantics and timeline row systems
- side-by-side compare and timeline outputs
- factor-expansion sidebar mechanics
- glossary hover panel and centered disclaimer
- page set:
  - main (`index.html`)
  - create profile
  - profile detail
  - tracking list/detail
  - about
- endpoint wiring and response-dependent rendering paths

This spec is authoritative for matching current demo UX behavior and visual structure.
