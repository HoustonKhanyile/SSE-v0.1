from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from sse.ssm import SituationSemantics


@dataclass(frozen=True)
class McmPriors:
    tendencies: List[str]
    risk_aversion: float
    conformity: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "tendencies": list(self.tendencies),
            "risk_aversion": self.risk_aversion,
            "conformity": self.conformity,
        }


def synthesize_priors(semantics: SituationSemantics) -> McmPriors:
    if semantics.domain == "education":
        tendencies = ["rule compliance", "anxiety under evaluation"]
        return McmPriors(tendencies=tendencies, risk_aversion=0.7, conformity=0.6)
    if semantics.domain == "workplace":
        tendencies = ["career preservation", "status sensitivity"]
        return McmPriors(tendencies=tendencies, risk_aversion=0.6, conformity=0.55)
    if semantics.domain == "policy":
        tendencies = ["collective grievance", "cost sensitivity"]
        return McmPriors(tendencies=tendencies, risk_aversion=0.4, conformity=0.5)
    if semantics.domain == "media":
        tendencies = ["audience maintenance", "platform skepticism"]
        return McmPriors(tendencies=tendencies, risk_aversion=0.45, conformity=0.35)

    tendencies = ["self preservation", "norm alignment"]
    return McmPriors(tendencies=tendencies, risk_aversion=0.5, conformity=0.5)
