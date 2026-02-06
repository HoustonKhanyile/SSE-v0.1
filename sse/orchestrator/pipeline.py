from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sse.contracts import PredictionResult, validate_prediction_result
from sse.ess import build_snapshot
from sse.explainer import ExplanationTrace, generate_explanation
from sse.mcm import synthesize_priors
from sse.sqc import compute_outcomes
from sse.ssm import parse_situation


@dataclass(frozen=True)
class RunConfig:
    depth: str = "default"
    include_alternatives: bool = False
    example_id: Optional[str] = None


def _infer_horizon(mode: str) -> str:
    if mode == "C":
        return "weeks"
    if mode == "B":
        return "days"
    return "hours"


def run_sse_with_trace(
    situation_text: str, config: Optional[RunConfig] = None
) -> tuple[PredictionResult, ExplanationTrace]:
    config = config or RunConfig()

    semantics = parse_situation(situation_text)
    ess = build_snapshot(semantics)
    priors = synthesize_priors(semantics)

    outcomes = compute_outcomes(semantics, ess, priors, example_id=config.example_id)
    primary = outcomes[0]

    explanation_trace = generate_explanation(
        semantics=semantics,
        ess=ess,
        priors=priors,
        outcome_label=primary.label,
        depth=config.depth,
    )

    explanation = explanation_trace.summary
    if config.depth == "deep":
        factor_names = [factor.name for factor in explanation_trace.factors]
        explanation += " Factors: " + "; ".join(factor_names) + "."

    horizon = _infer_horizon(semantics.mode)
    alternatives = outcomes[1:] if config.include_alternatives else []

    result = PredictionResult(
        predicted_outcome=primary,
        explanation=explanation,
        horizon=horizon,
        mode=semantics.mode,
        alternatives=alternatives,
    )
    validate_prediction_result(result)
    return result, explanation_trace


def run_sse(situation_text: str, config: Optional[RunConfig] = None) -> PredictionResult:
    result, _trace = run_sse_with_trace(situation_text, config)
    return result
