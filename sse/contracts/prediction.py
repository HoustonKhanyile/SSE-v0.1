from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class Outcome:
    id: str
    label: str
    confidence: float
    rationale: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "confidence": self.confidence,
            "rationale": list(self.rationale),
        }


@dataclass(frozen=True)
class PredictionResult:
    predicted_outcome: Outcome
    explanation: str
    horizon: str
    mode: str
    alternatives: List[Outcome] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "predicted_outcome": self.predicted_outcome.to_dict(),
            "explanation": self.explanation,
            "horizon": self.horizon,
            "mode": self.mode,
        }
        if self.alternatives:
            data["alternatives"] = [o.to_dict() for o in self.alternatives]
        return data


def validate_prediction_result(result: PredictionResult) -> None:
    if not result.predicted_outcome:
        raise ValueError("PredictionResult.predicted_outcome is required")
    if not result.explanation:
        raise ValueError("PredictionResult.explanation is required")
    if result.mode not in {"A", "B", "C"}:
        raise ValueError("PredictionResult.mode must be A, B, or C")
    if not result.horizon:
        raise ValueError("PredictionResult.horizon is required")
