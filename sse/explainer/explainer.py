from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sse.ess import EssSnapshot
from sse.mcm import McmPriors
from sse.ssm import SituationSemantics


@dataclass(frozen=True)
class FactorInsight:
    name: str
    role: str
    category: str


@dataclass(frozen=True)
class ExplanationTrace:
    summary: str
    factors: List[FactorInsight]


def generate_explanation(
    semantics: SituationSemantics,
    ess: EssSnapshot,
    priors: McmPriors,
    outcome_label: str,
    depth: str,
    recursion_depth_used: int = 0,
    strategic_action: str = "",
    institution_response: str = "",
) -> ExplanationTrace:
    factors: List[FactorInsight] = []
    factors.extend(
        [
            FactorInsight(
                name=constraint,
                role=(
                    "This acts as a hard boundary that limits which actions are safe "
                    "or institutionally acceptable."
                ),
                category="constraint",
            )
            for constraint in ess.constraints
        ]
    )
    factors.extend(
        [
            FactorInsight(
                name=affordance,
                role=(
                    "This creates a practical opening that makes the predicted behavior "
                    "more available in the current environment."
                ),
                category="affordance",
            )
            for affordance in ess.affordances
        ]
    )
    factors.extend(
        [
            FactorInsight(
                name=tendency,
                role=(
                    "This prior biases decision-making and increases the likelihood of "
                    "the dominant response pattern."
                ),
                category="prior",
            )
            for tendency in priors.tendencies
        ]
    )

    if depth == "deep":
        summary = (
            "This outcome follows from institutional constraints, observed affordances, "
            "and psychological priors that shape behavior in this context."
        )
    else:
        summary = "This outcome is most likely given the constraints and priors in the situation."

    summary = f"{outcome_label} {summary}"
    summary += f" Strategic recursion depth D={recursion_depth_used} was used for opponent modeling."
    if strategic_action:
        factors.append(
            FactorInsight(
                name=f"strategic action: {strategic_action}",
                role="This strategic action maximized deterministic multi-agent payoff under bounded recursion.",
                category="strategic",
            )
        )
    if institution_response:
        factors.append(
            FactorInsight(
                name=f"institution response: {institution_response}",
                role="Institutional response altered second-order incentives and final outcome confidence.",
                category="strategic",
            )
        )

    return ExplanationTrace(summary=summary, factors=factors)
