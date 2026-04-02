# SSE Daily-Use Product Spec
## Consumer Forecast Layer for the Social Simulation Engine

## Document Purpose
This spec defines the daily-use product layer for SSE as a human forecast utility. It focuses on the functional structure the Codex agent should implement around forecast metrics, user journeys, feature behavior, onboarding, and the Signal Sprint-to-SSE funnel.

This spec intentionally excludes homepage/product positioning because the SSE UI already exists and placement decisions will be handled within the existing interface system.

---

# 1. Product Objective

## 1.1 Core Goal
SSE should become a daily-use human forecast utility that people consult before making consequential social decisions.

The core behavioral habit is:

**Before making the move, check SSE.**

## 1.2 Product Function
At the consumer level, SSE should help users:
- read a situation
- forecast likely interpersonal or group dynamics
- assess risk and receptiveness
- choose a better behavioral posture
- improve decision quality over time

## 1.3 Product Promise
SSE helps users avoid misreading important situations by forecasting the likely direction of human dynamics before they act.

---

# 2. Product Philosophy

The product should feel:
- fast
- clear
- intelligent
- advisory rather than authoritarian
- useful in real situations
- repeatable as a daily habit

SSE should not feel like a research tool at the consumer layer.
It should feel like a practical forecast utility for human situations.

---

# 3. Core User Loop

## 3.1 Primary Loop
The core loop is:

1. **Read** — user describes a situation
2. **Forecast** — SSE estimates likely social dynamics
3. **Decide** — SSE recommends a posture or likely best move
4. **Act** — user carries out the decision in real life
5. **Learn** — user compares outcome to forecast and builds trust

## 3.2 Product Principle
Every major interaction in the product should support this loop.
If a feature does not strengthen this loop, it should be considered secondary.

---

# 4. Forecast Metrics Definitions

These metrics form the public grammar of SSE. They are the behavioral equivalent of weather indicators.

## 4.1 Situation Stability
**Definition:** Measures how stable or fragile the current situation is.

**Purpose:** Helps users understand whether conditions are calm, uncertain, or structurally volatile.

**Suggested Output Format:**
- High
- Medium
- Low

**Interpretation:**
- High = conditions are relatively stable
- Medium = the situation contains mixed signals or latent tension
- Low = the situation is fragile and susceptible to disruption

## 4.2 Escalation Risk
**Definition:** Probability that the interaction will worsen if the user proceeds.

**Purpose:** Warns users when conflict, defensiveness, backlash, or social deterioration is likely.

**Suggested Output Format:**
- percentage score
- qualitative label: Low / Moderate / High

**Interpretation:**
- Low = unlikely to worsen materially
- Moderate = notable chance of resistance or friction
- High = user should proceed very carefully or delay

## 4.3 Receptiveness Score
**Definition:** Likelihood that the target person or group is currently open to influence, persuasion, or cooperation.

**Purpose:** Helps users judge whether an ask, proposal, or emotional approach is likely to land.

**Suggested Output Format:**
- percentage score
- qualitative label: Closed / Mixed / Open

## 4.4 Trust Fragility
**Definition:** Measures how easily trust could be damaged in the current situation.

**Purpose:** Helps users understand whether the relationship is resilient or sensitive.

**Suggested Output Format:**
- Low
- Medium
- High

**Interpretation:**
- Low = trust can tolerate some friction
- Medium = careful framing is needed
- High = trust can be harmed quickly by missteps

## 4.5 Pressure Index
**Definition:** Measures how much emotional, social, strategic, or reputational pressure is present.

**Purpose:** Identifies situations where behavior is more likely to be distorted by stress or stakes.

**Suggested Output Format:**
- 0–100 scale
- qualitative label: Light / Elevated / Heavy

## 4.6 Timing Quality
**Definition:** Measures whether now is a good moment to act.

**Purpose:** Helps users distinguish between good timing, premature action, and delay-worthy conditions.

**Suggested Output Format:**
- Good
- Mixed
- Poor

## 4.7 Recommended Posture
**Definition:** Advises the user on the best broad stance to take.

**Approved posture types:**
- Push
- Wait
- Soften
- Clarify
- Reframe
- De-escalate
- Avoid

**Purpose:** Converts forecast into immediate behavioral guidance.

## 4.8 Likely Outcome Direction
**Definition:** Summarizes the most probable trajectory if the user proceeds as currently intended.

**Purpose:** Gives users a simple directional forecast.

**Example output:**
- Likely positive if framed collaboratively
- Likely defensive resistance if pushed now
- Likely no movement without more trust-building
- Likely escalation if confrontation is direct

---

# 5. Forecast Output Structure

## 5.1 Standard Forecast Card
Every forecast should be rendered in a compact, scannable structure.

### Required sections
1. Situation summary
2. Forecast metrics
3. Recommended posture
4. Likely outcome direction
5. Reasoning summary
6. Optional next-step suggestion

## 5.2 Example Forecast Structure

**Situation Summary**
Asking a manager for more flexibility during a high-pressure period.

**Forecast**
- Stability: Medium
- Escalation Risk: 28% (Low)
- Receptiveness: 54% (Mixed)
- Trust Fragility: Medium
- Pressure Index: 71 (Heavy)
- Timing Quality: Mixed
- Recommended Posture: Soften + Reframe
- Likely Outcome: Better response if framed around team efficiency rather than personal strain

**Why This Forecast**
The relationship appears workable, but pressure conditions raise the chance of defensive interpretation. The request is more likely to succeed if aligned with mutual benefit.

## 5.3 Compression Rule
Forecasts must be concise first. Deeper reasoning should be available behind an optional expansion, not forced into the first view.

---

# 6. Consumer Feature Set

## 6.1 Situation Check
**Purpose:** Fast forecast for a described scenario.

**User input:**
- free-text description of the situation
- optional role tags (manager, partner, friend, audience, client, team)
- optional urgency indicator

**System output:**
- full forecast card
- recommended posture
- likely outcome direction

**Priority:** Core launch feature

---

## 6.2 Move Evaluator
**Purpose:** Lets the user test a proposed action before taking it.

**User input:**
- situation description
- intended move or message

**System output:**
- likely reception
- escalation risk
- posture rating
- recommended modifications

**Example use:**
“Here is the text I want to send. How is it likely to land?”

**Priority:** Core launch feature

---

## 6.3 Timing Checker
**Purpose:** Assesses whether the user should act now, delay, or prepare further.

**User input:**
- situation description
- intended timing

**System output:**
- timing quality
- time-sensitivity note
- recommended timing posture

**Priority:** High

---

## 6.4 Framing Optimizer
**Purpose:** Recommends how a move should be framed for the best result.

**User input:**
- situation description
- desired outcome
- optional draft message or approach

**System output:**
- suggested framing angle
- tone recommendation
- posture refinement
- optional revised language guidance

**Priority:** High

---

## 6.5 Escalation Warning
**Purpose:** Flags when the user’s intended move is likely to create unnecessary resistance or conflict.

**Trigger condition:**
- escalation risk above defined threshold
- trust fragility high
- pressure index elevated

**System output:**
- warning label
- explanation
- safer alternative posture

**Priority:** High

---

## 6.6 Outcome Reflection
**Purpose:** Lets users log the real-world result and compare it against the forecast.

**User input:**
- outcome summary
- whether forecast felt accurate
- what action was taken

**System output:**
- reflective comparison
- trust-building recap
- optional learning insight

**Priority:** Medium, but strategically important for retention

---

## 6.7 Reputation Tracker
**Purpose:** Measures the user’s demonstrated judgment quality over time.

**Role in ecosystem:**
This feature connects the serious utility layer of SSE with the status and reputation logic introduced through Signal Sprint.

**Potential internal dimensions:**
- consistency of judgment
- foresight quality
- restraint quality
- framing quality
- escalation avoidance
- timing quality

**Public-facing output should remain simple.**

**Priority:** Medium

---

# 7. User Journey Design

## 7.1 First-Time User Journey

### Objective
Convert curiosity into first practical use.

### Flow
1. User enters SSE
2. System introduces a simple premise: describe a situation
3. User submits first situation
4. SSE returns a forecast card
5. User is shown one actionable takeaway
6. User is encouraged to return after acting to reflect on the result

### First-use design principle
The first experience must produce useful clarity within one short interaction.

---

## 7.2 Returning User Journey

### Objective
Build habit and trust.

### Flow
1. User returns with a new situation
2. SSE recognizes repeat usage pattern
3. Forecast is delivered quickly
4. Outcome reflection from past cases remains accessible
5. Reputation/judgment history gradually becomes visible

### Returning-user principle
The experience should feel faster and more natural over time.

---

## 7.3 High-Stakes User Journey

### Objective
Support emotionally charged or strategically important situations.

### Flow
1. User flags situation as high-stakes
2. SSE increases emphasis on risk metrics
3. Forecast highlights escalation risk, trust fragility, and timing quality
4. Recommended posture is made especially explicit
5. Optional alternative-action suggestions are provided

### Principle
High-stakes mode should feel more cautious, sober, and protective.

---

# 8. Onboarding Flow

## 8.1 Onboarding Goal
Teach the user one core behavior:

**Use SSE before acting in important human situations.**

## 8.2 Onboarding Requirements
Onboarding should communicate:
- SSE reads situations, not just words
- SSE is advisory, not absolute
- SSE is best used before consequential action
- the user can start with a real-life situation immediately

## 8.3 Suggested Onboarding Sequence

### Step 1: Core premise
Present the product as a situation forecast tool.

### Step 2: Use-case examples
Show simple example prompts such as:
- “I need to send a difficult message.”
- “I want to ask for something important.”
- “I think this conversation could go badly.”
- “I want to know whether to push or wait.”

### Step 3: First live input
Prompt user to enter a real scenario.

### Step 4: Forecast education
After the first forecast, briefly explain metric meanings.

### Step 5: Habit prompt
Encourage the user to come back before their next important move.

## 8.4 Onboarding Principle
Onboarding should be short and action-oriented. The fastest route to understanding is using the system on a real situation.

---

# 9. Signal Sprint -> SSE Funnel Architecture

## 9.1 Funnel Objective
Signal Sprint and the game-show ecosystem should create familiarity with behavioral intelligence and channel users into SSE as the serious daily-use utility.

## 9.2 Functional Relationship

### Signal Sprint does the following:
- introduces situational judgment as a desirable skill
- makes reading human dynamics entertaining
- creates identity and status around good judgment
- normalizes the language of signals, reputation, and influence

### SSE does the following:
- operationalizes real-world forecasting
- supports actual decisions
- deepens trust through repeated utility
- becomes the daily-use layer users graduate into

## 9.3 Funnel Stages
1. **Entertainment** — user encounters Signal Sprint or the show
2. **Curiosity** — user becomes interested in judgment, influence, and social reading
3. **Identity** — user begins valuing behavioral intelligence
4. **Utility** — user enters SSE for real-life decisions
5. **Dependence** — user consults SSE habitually before important moves

## 9.4 Product Design Implication
The ecosystem should preserve consistent language across both layers.

Examples of shared concepts:
- signal
- judgment
- reputation
- influence
- read the situation
- make the move

This continuity helps the funnel feel natural rather than disconnected.

---

# 10. Feature Prioritization

## Phase 1 — Core Utility Launch
Must include:
- Situation Check
- Move Evaluator
- Timing Checker
- Framing Optimizer
- Escalation Warning
- standard forecast card
- lightweight onboarding

## Phase 2 — Trust and Retention
Should include:
- Outcome Reflection
- forecast history
- user pattern memory
- simplified judgment tracking

## Phase 3 — Ecosystem Convergence
Can include:
- Reputation Tracker
- Signal Sprint-linked status logic
- identity/profile overlays
- deeper longitudinal behavior insights

---

# 11. UX Behavior Rules

## 11.1 First View Rule
The first view must show concise forecast outputs, not dense explanation.

## 11.2 Advisory Rule
Language should guide rather than command.
Use phrases like:
- likely
- may
- higher chance
- recommended posture

Avoid absolute, deterministic phrasing.

## 11.3 Actionability Rule
Every forecast should lead to a concrete takeaway.
The user should not leave without knowing what posture or action is suggested.

## 11.4 Confidence Rule
When uncertainty is high, the system should communicate that clearly.
Confidence should be calibrated, not overstated.

## 11.5 Reusability Rule
The experience must be easy to repeat frequently.
Inputs and outputs should be lightweight enough for everyday use.

---

# 12. Trust-Building Principles

For SSE to become infrastructure-like, users must develop trust.
Trust should be built through:
- consistent usefulness
- calibrated language
- meaningful postures
- visible reflection loops
- repeated directionally correct guidance

The product should avoid pretending to be infallible.
Its trust should come from practical helpfulness, not omniscience.

---

# 13. Success Criteria

The daily-use layer is working if users begin to:
- consult SSE before important conversations or decisions
- return after acting to compare outcomes
- rely on posture guidance during uncertain situations
- perceive SSE as improving judgment, not merely entertaining them
- associate good decisions with checking the signal first

---

# 14. Strategic Definition

SSE at the consumer layer is:

**A human forecast utility that helps people read situations, anticipate likely outcomes, and choose better moves before acting.**

The repeatable habit is:

**Before making a consequential move, check SSE.**

That is the product logic this spec is designed to operationalize.

