from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from sse.contracts import Outcome
from sse.ess import EssSnapshot
from sse.mcm import McmPriors
from sse.ssm import SituationSemantics
from .srl import StrategicResult, run_strategic_reasoning


@dataclass(frozen=True)
class ScoredOutcome:
    outcome: Outcome
    score: float


_EXAMPLE_OUTCOMES = {
    "exam_cheating": Outcome(
        id="no_cheat_internal_conflict",
        label="The student does not cheat but experiences internal conflict.",
        confidence=0.72,
        rationale=["risk aversion", "norm compliance"],
    ),
    "workplace_promotion": Outcome(
        id="quiet_job_search",
        label="The employee quietly searches for another job while maintaining performance.",
        confidence=0.68,
        rationale=["career preservation", "avoid open conflict"],
    ),
    "manager_confrontation": Outcome(
        id="cautious_raise_issue",
        label="The employee raises the issue cautiously rather than aggressively.",
        confidence=0.66,
        rationale=["risk management", "institutional awareness"],
    ),
    "public_tax_policy": Outcome(
        id="dissatisfaction_protest",
        label="Widespread dissatisfaction and short-term protest activity among affected groups.",
        confidence=0.64,
        rationale=["collective grievance", "cost shock"],
    ),
    "platform_algorithm_change": Outcome(
        id="creator_migration_criticism",
        label="Gradual creator migration and increased public criticism of the platform.",
        confidence=0.62,
        rationale=["platform skepticism", "audience maintenance"],
    ),
}


def _default_outcome(semantics: SituationSemantics, priors: McmPriors) -> Outcome:
    if semantics.domain == "education":
        return Outcome(
            id="no_cheat_internal_conflict",
            label="The student does not cheat but experiences internal conflict.",
            confidence=0.6 + (priors.risk_aversion * 0.2),
            rationale=["risk aversion", "norm compliance"],
        )
    if semantics.domain == "workplace":
        return Outcome(
            id="quiet_job_search",
            label="The employee quietly searches for another job while maintaining performance.",
            confidence=0.58 + (priors.risk_aversion * 0.2),
            rationale=["career preservation", "avoid open conflict"],
        )
    if semantics.domain == "policy":
        return Outcome(
            id="dissatisfaction_protest",
            label="Widespread dissatisfaction and short-term protest activity among affected groups.",
            confidence=0.55 + ((1 - priors.risk_aversion) * 0.2),
            rationale=["collective grievance", "cost shock"],
        )
    if semantics.domain == "media":
        return Outcome(
            id="creator_migration_criticism",
            label="Gradual creator migration and increased public criticism of the platform.",
            confidence=0.54 + ((1 - priors.conformity) * 0.2),
            rationale=["platform skepticism", "audience maintenance"],
        )

    return Outcome(
        id="cautious_compliance",
        label="The actor proceeds cautiously while staying within norms.",
        confidence=0.55,
        rationale=["risk aversion", "norm alignment"],
    )


def _default_alternatives(semantics: SituationSemantics) -> List[Outcome]:
    if semantics.domain == "education":
        return [
            Outcome(
                id="cheat_short_term",
                label="The student cheats, gains a short-term advantage, but risks consequences.",
                confidence=0.28,
                rationale=["opportunity", "short-term gain"],
            )
        ]
    if semantics.domain == "workplace":
        return [
            Outcome(
                id="direct_confrontation",
                label="The employee confronts management directly, escalating tension.",
                confidence=0.3,
                rationale=["frustration", "perceived unfairness"],
            )
        ]
    if semantics.domain == "policy":
        return [
            Outcome(
                id="quiet_acceptance",
                label="Most people accept the change without organized protest.",
                confidence=0.3,
                rationale=["adaptation", "cost absorption"],
            )
        ]
    if semantics.domain == "media":
        return [
            Outcome(
                id="platform_adaptation",
                label="Creators adapt content strategy to the new algorithm.",
                confidence=0.32,
                rationale=["audience retention", "platform dependence"],
            )
        ]

    return [
        Outcome(
            id="status_quo",
            label="No meaningful change occurs in the short term.",
            confidence=0.3,
            rationale=["inertia"],
        )
    ]


def compute_outcomes(
    semantics: SituationSemantics,
    ess: EssSnapshot,
    priors: McmPriors,
    example_id: Optional[str] = None,
) -> List[Outcome]:
    outcomes, _strategic = compute_outcomes_with_strategy(
        semantics=semantics,
        ess=ess,
        priors=priors,
        example_id=example_id,
        strategic_depth_override=None,
    )
    return outcomes


def compute_outcomes_with_strategy(
    semantics: SituationSemantics,
    ess: EssSnapshot,
    priors: McmPriors,
    example_id: Optional[str] = None,
    strategic_depth_override: Optional[int] = None,
) -> Tuple[List[Outcome], StrategicResult]:
    if example_id and example_id in _EXAMPLE_OUTCOMES:
        primary = _EXAMPLE_OUTCOMES[example_id]
    else:
        primary = _default_outcome(semantics, priors)

    alternatives = _default_alternatives(semantics)
    strategic = run_strategic_reasoning(
        semantics=semantics,
        ess=ess,
        priors=priors,
        strategic_depth_override=strategic_depth_override,
    )

    adjusted_confidence = max(0.05, min(0.95, round(primary.confidence + strategic.score_adjustment, 4)))
    strategic_rationale = f"strategic:{strategic.chosen_action}"
    if strategic.cascade_state:
        strategic_rationale += ";cascade=true"
    if strategic_rationale not in primary.rationale:
        rationale = list(primary.rationale) + [strategic_rationale]
    else:
        rationale = list(primary.rationale)

    adjusted_primary = Outcome(
        id=primary.id,
        label=primary.label,
        confidence=adjusted_confidence,
        rationale=rationale,
    )
    return [adjusted_primary] + alternatives, strategic
