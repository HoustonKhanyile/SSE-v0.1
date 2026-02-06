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

    return ExplanationTrace(summary=summary, factors=factors)
