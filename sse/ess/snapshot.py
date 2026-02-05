from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from sse.ssm import SituationSemantics


@dataclass(frozen=True)
class EssSnapshot:
    constraints: List[str]
    affordances: List[str]
    institutions: List[str]

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "constraints": list(self.constraints),
            "affordances": list(self.affordances),
            "institutions": list(self.institutions),
        }


def build_snapshot(semantics: SituationSemantics) -> EssSnapshot:
    constraints: List[str] = []
    affordances: List[str] = []

    if semantics.domain == "education":
        constraints.append("exam integrity policy")
        affordances.append("temporary invigilator absence")
    elif semantics.domain == "workplace":
        constraints.append("performance review process")
        affordances.append("job market mobility")
    elif semantics.domain == "policy":
        constraints.append("tax enforcement")
        affordances.append("public protest channels")
    elif semantics.domain == "media":
        constraints.append("platform ranking rules")
        affordances.append("creator migration")
    else:
        constraints.append("social norms")
        affordances.append("individual discretion")

    return EssSnapshot(
        constraints=constraints,
        affordances=affordances,
        institutions=list(semantics.institutions),
    )
