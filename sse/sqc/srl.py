from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from sse.ess import EssSnapshot
from sse.mcm import McmPriors
from sse.ssm import SituationSemantics


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class BeliefState:
    beliefs_about_others: Dict[str, float]
    perceived_intent: Dict[str, float]
    credibility_scores: Dict[str, float]
    perceived_constraints: Dict[str, List[str]]


@dataclass(frozen=True)
class InstitutionAgent:
    enforcement_capacity: float
    legitimacy_threshold: float
    strategic_tolerance: float
    policy_flexibility: float


@dataclass(frozen=True)
class SignalProfile:
    cost: float
    audience_scope: str
    reversibility: str
    credibility_impact: float


@dataclass(frozen=True)
class StrategicAction:
    id: str
    label: str
    action_class: str
    signal: Optional[SignalProfile] = None


@dataclass(frozen=True)
class StrategicResult:
    belief_shift_summary: str
    signal_evaluation_summary: str
    coalition_likelihood: float
    recursion_depth_used: int
    chosen_action: str
    institution_response: str
    cascade_state: bool
    score_adjustment: float


def infer_recursion_depth(semantics: SituationSemantics, override: Optional[int] = None) -> int:
    if override is not None:
        return max(0, min(3, int(override)))

    lower = semantics.raw_text.lower()
    if any(k in lower for k in ("negotiat", "bargain", "deal", "precommit", "hostage")):
        return 2
    if any(k in lower for k in ("politic", "election", "protest")):
        return 2
    if semantics.mode == "C":
        return 2
    if semantics.mode == "B":
        return 1
    return 0


def _build_targets(semantics: SituationSemantics, ess: EssSnapshot) -> List[str]:
    targets: List[str] = []
    targets.extend(semantics.actors)
    targets.extend(ess.institutions)
    if not targets:
        targets = ["counterparty"]
    if len(targets) == 1:
        targets.append("counterparty")
    return list(dict.fromkeys(targets))


def initialize_belief_state(semantics: SituationSemantics, ess: EssSnapshot, priors: McmPriors) -> BeliefState:
    base_intent = 0.62 if semantics.conflict else 0.42
    base_cred = _clamp(0.45 + (priors.conformity * 0.3) - (0.05 if semantics.conflict else 0.0))
    targets = _build_targets(semantics, ess)
    return BeliefState(
        beliefs_about_others={target: base_intent for target in targets},
        perceived_intent={target: base_intent for target in targets},
        credibility_scores={target: base_cred for target in targets},
        perceived_constraints={target: list(ess.constraints) for target in targets},
    )


def _institution_agent(semantics: SituationSemantics) -> InstitutionAgent:
    if semantics.mode == "C":
        return InstitutionAgent(0.78, 0.46, 0.42, 0.48)
    if semantics.mode == "B":
        return InstitutionAgent(0.58, 0.5, 0.55, 0.58)
    return InstitutionAgent(0.45, 0.55, 0.62, 0.65)


def _baseline_coalition(semantics: SituationSemantics, priors: McmPriors, avg_credibility: float) -> float:
    shared_value_alignment = _clamp(0.35 + (priors.conformity * 0.45) + (0.12 if semantics.mode == "C" else 0.0))
    coordination_cost = _clamp(0.55 - (0.07 if semantics.mode == "C" else 0.0) + (0.08 if semantics.mode == "B" else 0.0))
    external_pressure = _clamp(0.28 + (0.22 if semantics.conflict else 0.0) + (0.2 if semantics.mode == "C" else 0.0))
    score = (0.35 * shared_value_alignment) + (0.3 * avg_credibility) + (0.2 * external_pressure) - (0.25 * coordination_cost)
    return _clamp(score)


def _deception_detection_risk(semantics: SituationSemantics, ess: EssSnapshot) -> float:
    risk = 0.16
    if semantics.conflict:
        risk += 0.2
    if semantics.mode == "C":
        risk += 0.18
    if ess.institutions:
        risk += 0.2
    return _clamp(risk)


def _candidate_actions(
    semantics: SituationSemantics,
    baseline_credibility: float,
    detection_risk: float,
) -> List[StrategicAction]:
    actions: List[StrategicAction] = [
        StrategicAction(id="reactive_response", label="Reactive best response", action_class="reactive"),
        StrategicAction(
            id="reassurance_signal",
            label="Issue reassurance signal",
            action_class="signaling",
            signal=SignalProfile(cost=0.28, audience_scope="targeted", reversibility="high", credibility_impact=0.08),
        ),
        StrategicAction(
            id="public_commitment",
            label="Make public commitment",
            action_class="commitment",
            signal=SignalProfile(cost=0.62, audience_scope="public", reversibility="low", credibility_impact=0.15),
        ),
    ]
    if semantics.mode in {"B", "C"}:
        actions.append(
            StrategicAction(
                id="coalition_proposal",
                label="Propose coalition coordination",
                action_class="coalition",
                signal=SignalProfile(cost=0.5, audience_scope="targeted", reversibility="medium", credibility_impact=0.1),
            )
        )

    if baseline_credibility > 0.5 and detection_risk < 0.55:
        actions.append(
            StrategicAction(
                id="strategic_concealment",
                label="Use strategic concealment",
                action_class="deception",
                signal=SignalProfile(cost=0.2, audience_scope="targeted", reversibility="high", credibility_impact=-0.1),
            )
        )
    return actions


def _recursive_pressure(depth: int, base_intent: float) -> float:
    if depth <= 0:
        return _clamp(base_intent)
    prior = _recursive_pressure(depth - 1, base_intent)
    return _clamp((0.62 * prior) + (0.38 * base_intent) + (0.03 * depth))


def _signal_consistency(action: StrategicAction) -> float:
    if action.signal is None:
        return 0.55
    consistency = 0.5 + (action.signal.cost * 0.22)
    if action.action_class == "commitment":
        consistency += 0.16
    if action.action_class == "deception":
        consistency -= 0.24
    return _clamp(consistency, 0.05, 0.95)


def _bayes_like_update(prior: float, consistency: float) -> float:
    numerator = prior * consistency
    denominator = numerator + ((1 - prior) * (1 - consistency))
    if denominator == 0:
        return prior
    return _clamp(numerator / denominator)


def run_strategic_reasoning(
    semantics: SituationSemantics,
    ess: EssSnapshot,
    priors: McmPriors,
    strategic_depth_override: Optional[int] = None,
) -> StrategicResult:
    depth = infer_recursion_depth(semantics, strategic_depth_override)
    belief_state = initialize_belief_state(semantics, ess, priors)
    avg_credibility = sum(belief_state.credibility_scores.values()) / len(belief_state.credibility_scores)
    baseline_coalition = _baseline_coalition(semantics, priors, avg_credibility)
    detection_risk = _deception_detection_risk(semantics, ess)
    institution = _institution_agent(semantics)

    best_action = "reactive_response"
    best_signal_summary = "No strategic signal evaluated."
    best_belief_delta = 0.0
    best_coalition = baseline_coalition
    best_cascade = False
    best_response = "public_framing"
    best_score = -1.0

    actions = _candidate_actions(semantics, avg_credibility, detection_risk)
    for action in actions:
        consistency = _signal_consistency(action)
        updated_intent = {}
        updated_credibility = {}
        intent_deltas: List[float] = []
        cred_deltas: List[float] = []
        for target, prior_intent in belief_state.perceived_intent.items():
            posterior_intent = _bayes_like_update(prior_intent, consistency)
            updated_intent[target] = posterior_intent
            intent_deltas.append(posterior_intent - prior_intent)

            prior_cred = belief_state.credibility_scores[target]
            cred_delta = 0.0
            if action.signal is not None:
                cred_delta = action.signal.credibility_impact + (0.1 * action.signal.cost) + (0.1 * (consistency - 0.5))
            if action.action_class == "deception":
                cred_delta -= 0.2
            updated_cred = _clamp(prior_cred + cred_delta)
            updated_credibility[target] = updated_cred
            cred_deltas.append(updated_cred - prior_cred)

        mean_intent_delta = sum(intent_deltas) / len(intent_deltas)
        mean_credibility = sum(updated_credibility.values()) / len(updated_credibility)
        opponent_pressure = _recursive_pressure(depth, _clamp(sum(updated_intent.values()) / len(updated_intent)))

        coalition = _baseline_coalition(semantics, priors, mean_credibility)
        if action.action_class == "coalition":
            coalition = _clamp(coalition + 0.14)
        if action.action_class == "deception":
            coalition = _clamp(coalition - 0.1)

        legitimacy = _clamp(mean_credibility - (0.18 if semantics.conflict else 0.0))
        if action.action_class == "commitment":
            legitimacy = _clamp(legitimacy + 0.08)
        if action.action_class == "deception":
            legitimacy = _clamp(legitimacy - 0.15)

        if legitimacy < institution.legitimacy_threshold and institution.policy_flexibility > 0.45:
            institution_response = "preemptive_concession"
            institution_bonus = 0.08
        elif action.action_class == "deception":
            institution_response = "selective_enforcement"
            institution_bonus = -0.04
        elif semantics.conflict and institution.enforcement_capacity > 0.55:
            institution_response = "deterrence_escalation"
            institution_bonus = -0.06
        else:
            institution_response = "public_framing"
            institution_bonus = 0.03

        coordination_level = coalition + (0.1 if action.action_class == "coalition" else 0.0)
        cascade = legitimacy < 0.42 or coordination_level > 0.78

        value_satisfaction = _clamp(0.42 + (0.33 * (1 - opponent_pressure)) + (0.1 if action.action_class == "commitment" else 0.04))
        emotional_stability = _clamp(
            0.36 + (0.36 * priors.risk_aversion) - (0.22 if semantics.conflict else 0.0) + (0.08 if action.action_class == "signaling" else 0.0)
        )
        survival_security = _clamp(
            0.35 + (0.45 * priors.risk_aversion) + (0.1 if action.action_class == "commitment" else 0.0) - (0.18 if action.action_class == "deception" else 0.0)
        )
        reputational_impact = mean_credibility

        score = (
            (0.3 * value_satisfaction)
            + (0.24 * emotional_stability)
            + (0.26 * survival_security)
            + (0.2 * reputational_impact)
            + (0.14 * (coalition - baseline_coalition))
            + institution_bonus
            - (0.08 if cascade else 0.0)
        )

        if score > best_score:
            best_score = score
            best_action = action.id
            best_coalition = coalition
            best_cascade = cascade
            best_response = institution_response
            best_belief_delta = mean_intent_delta
            mean_cred_delta = sum(cred_deltas) / len(cred_deltas)
            if action.signal is None:
                best_signal_summary = "No costly signal selected; credibility remained stable."
            else:
                best_signal_summary = (
                    f"Selected {action.action_class} signal with cost={action.signal.cost:.2f}, "
                    f"consistency={consistency:.2f}, credibility_delta={mean_cred_delta:.3f}."
                )

    belief_shift_summary = f"Average inferred intent shift across modeled agents: {best_belief_delta:+.3f}."
    score_adjustment = round((best_score - 0.5) * 0.18 + (0.03 * depth), 4)
    return StrategicResult(
        belief_shift_summary=belief_shift_summary,
        signal_evaluation_summary=best_signal_summary,
        coalition_likelihood=round(best_coalition, 4),
        recursion_depth_used=depth,
        chosen_action=best_action,
        institution_response=best_response,
        cascade_state=best_cascade,
        score_adjustment=score_adjustment,
    )
