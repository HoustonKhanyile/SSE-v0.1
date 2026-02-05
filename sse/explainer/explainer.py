from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sse.ess import EssSnapshot
from sse.mcm import McmPriors
from sse.ssm import SituationSemantics


@dataclass(frozen=True)
class ExplanationTrace:
    summary: str
    factors: List[str]


def generate_explanation(
    semantics: SituationSemantics,
    ess: EssSnapshot,
    priors: McmPriors,
    outcome_label: str,
    depth: str,
) -> ExplanationTrace:
    factors = []
    factors.extend(ess.constraints)
    factors.extend(ess.affordances)
    factors.extend(priors.tendencies)

    if depth == "deep":
        summary = (
            "This outcome follows from institutional constraints, observed affordances, "
            "and psychological priors that shape behavior in this context."
        )
    else:
        summary = "This outcome is most likely given the constraints and priors in the situation."

    summary = f"{outcome_label} {summary}"

    return ExplanationTrace(summary=summary, factors=factors)
