from __future__ import annotations

from typing import Any


POSTURES = ["Push", "Wait", "Soften", "Clarify", "Reframe", "De-escalate", "Avoid"]

HIGH_PRESSURE_WORDS = {
    "urgent",
    "deadline",
    "high-stakes",
    "fired",
    "promotion",
    "divorce",
    "confront",
    "conflict",
    "lawsuit",
    "crisis",
}
TRUST_SENSITIVE_WORDS = {
    "partner",
    "friend",
    "trust",
    "manager",
    "team",
    "client",
    "family",
    "relationship",
}
COLLABORATIVE_WORDS = {
    "align",
    "support",
    "collaborative",
    "together",
    "clarify",
    "understand",
    "help",
    "cooperate",
}
ESCALATION_WORDS = {
    "accuse",
    "blame",
    "threat",
    "ultimatum",
    "push",
    "confront",
    "attack",
    "angry",
    "escalate",
}


def _label_from_score(score: int, low_cutoff: int, high_cutoff: int, labels: tuple[str, str, str]) -> str:
    if score < low_cutoff:
        return labels[0]
    if score < high_cutoff:
        return labels[1]
    return labels[2]


def _contains_any(text: str, words: set[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in words)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _summarize_text(text: str, limit: int = 150) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def _build_sse_prompt(
    situation: str,
    feature_type: str,
    intended_move: str = "",
    intended_timing: str = "",
    desired_outcome: str = "",
    role_tags: list[str] | None = None,
    urgency: str = "normal",
) -> str:
    fragments = [situation.strip()]
    if intended_move.strip():
        fragments.append(f"Intended move: {intended_move.strip()}.")
    if intended_timing.strip():
        fragments.append(f"Timing context: {intended_timing.strip()}.")
    if desired_outcome.strip():
        fragments.append(f"Desired outcome: {desired_outcome.strip()}.")
    if role_tags:
        cleaned = [tag.strip() for tag in role_tags if tag.strip()]
        if cleaned:
            fragments.append(f"Relevant roles: {', '.join(cleaned)}.")
    if urgency and urgency != "normal":
        fragments.append(f"Urgency level: {urgency}.")
    if feature_type and feature_type != "situation_check":
        fragments.append(f"Forecast focus: {feature_type.replace('_', ' ')}.")
    return " ".join(part for part in fragments if part)


def build_daily_use_forecast(
    payload: dict[str, Any],
    *,
    original_situation: str,
    feature_type: str,
    intended_move: str = "",
    intended_timing: str = "",
    desired_outcome: str = "",
    role_tags: list[str] | None = None,
    urgency: str = "normal",
) -> dict[str, Any]:
    text = " ".join(
        [
            original_situation or "",
            intended_move or "",
            intended_timing or "",
            desired_outcome or "",
            payload.get("explanation", ""),
            payload.get("predicted_outcome", {}).get("label", ""),
        ]
    ).lower()
    confidence = float(payload.get("predicted_outcome", {}).get("confidence", 0.5) or 0.5)
    factors = payload.get("factors", [])
    factor_names = " ".join(str(f.get("name", "")) for f in factors).lower()
    constraint_count = sum(1 for factor in factors if factor.get("category") == "constraint")
    strategic_count = sum(1 for factor in factors if factor.get("category") == "strategic")
    pressure_bonus = 18 if urgency == "high" else 10 if urgency == "medium" else 0
    if _contains_any(text, HIGH_PRESSURE_WORDS):
        pressure_bonus += 18
    if strategic_count:
        pressure_bonus += 8
    pressure_index = int(_clamp(round(25 + (1 - confidence) * 28 + constraint_count * 9 + pressure_bonus), 0, 100))
    stability_score = int(_clamp(round(confidence * 100 - pressure_index * 0.28 + 18), 0, 100))
    escalation_score = int(
        _clamp(
            round(
                22
                + (1 - confidence) * 36
                + pressure_index * 0.24
                + (16 if _contains_any(text, ESCALATION_WORDS) else 0)
                + (10 if "defens" in text or "resistan" in text else 0)
                - (10 if _contains_any(text, COLLABORATIVE_WORDS) else 0)
            ),
            0,
            100,
        )
    )
    receptiveness_score = int(
        _clamp(
            round(
                58
                + confidence * 18
                - escalation_score * 0.38
                - pressure_index * 0.16
                + (10 if _contains_any(text, COLLABORATIVE_WORDS) else 0)
            ),
            0,
            100,
        )
    )
    trust_score = int(
        _clamp(
            round(
                24
                + escalation_score * 0.44
                + (18 if _contains_any(text + " " + factor_names, TRUST_SENSITIVE_WORDS) else 0)
                - confidence * 8
            ),
            0,
            100,
        )
    )

    if escalation_score >= 72:
        posture = ["De-escalate", "Wait"]
    elif receptiveness_score < 40:
        posture = ["Wait", "Clarify"]
    elif pressure_index >= 70:
        posture = ["Soften", "Reframe"]
    elif intended_move and _contains_any(intended_move, ESCALATION_WORDS):
        posture = ["Clarify", "Soften"]
    elif receptiveness_score >= 68 and stability_score >= 62:
        posture = ["Push"]
    else:
        posture = ["Clarify", "Reframe"]

    timing_quality = "Poor" if pressure_index >= 78 or escalation_score >= 75 else "Mixed" if pressure_index >= 55 or receptiveness_score < 55 else "Good"
    likely_direction = (
        "Likely escalation if the move is direct."
        if escalation_score >= 72
        else "Likely limited movement without better framing."
        if receptiveness_score < 45
        else "Likely better response if framed collaboratively."
        if receptiveness_score >= 60
        else "Likely mixed response unless expectations are clarified."
    )
    reasoning_summary = _summarize_text(payload.get("explanation", ""))
    next_step = {
        "Push": "Make the ask directly, but keep it specific and collaborative.",
        "Wait": "Delay the move briefly and gather one more signal before acting.",
        "Soften": "Reduce intensity and lead with context before the main ask.",
        "Clarify": "State your objective and constraints explicitly before pushing for an outcome.",
        "Reframe": "Anchor the move around mutual benefit rather than personal pressure.",
        "De-escalate": "Lower the temperature first and avoid a binary confrontation.",
        "Avoid": "Do not make this move in its current form.",
    }[posture[0]]
    warning = None
    if escalation_score >= 68 or trust_score >= 72 or pressure_index >= 72:
        warning = {
            "label": "Escalation warning",
            "explanation": "Conditions suggest heightened resistance or trust damage if you push too hard now.",
            "safer_alternative_posture": posture[-1],
        }

    move_evaluator = {
        "likely_reception": _label_from_score(receptiveness_score, 40, 68, ("Closed", "Mixed", "Open")),
        "posture_rating": "Needs revision" if escalation_score >= 65 else "Usable with care" if pressure_index >= 55 else "Well-positioned",
        "recommended_modifications": next_step,
    }
    timing_details = {
        "timing_quality": timing_quality,
        "time_sensitivity_note": "Conditions appear volatile, so timing matters more than usual."
        if pressure_index >= 65
        else "Timing is not perfect, but the move is viable with better framing."
        if timing_quality == "Mixed"
        else "Current conditions appear workable.",
        "recommended_timing_posture": posture[0],
    }
    framing_details = {
        "suggested_framing_angle": "Frame around shared objectives and reduced friction."
        if posture[0] in {"Soften", "Reframe", "Clarify"}
        else "Use direct but calm language anchored in concrete next steps.",
        "tone_recommendation": "Calm, specific, and non-accusatory.",
        "posture_refinement": " + ".join(posture),
        "revised_language_guidance": "Lead with the situation, name the shared interest, then make one clear ask.",
    }

    return {
        "feature_type": feature_type,
        "situation_summary": _summarize_text(original_situation, 120),
        "forecast_metrics": {
            "situation_stability": {
                "score": stability_score,
                "label": _label_from_score(stability_score, 45, 70, ("Low", "Medium", "High")),
            },
            "escalation_risk": {
                "score": escalation_score,
                "label": _label_from_score(escalation_score, 35, 70, ("Low", "Moderate", "High")),
            },
            "receptiveness_score": {
                "score": receptiveness_score,
                "label": _label_from_score(receptiveness_score, 40, 68, ("Closed", "Mixed", "Open")),
            },
            "trust_fragility": {
                "score": trust_score,
                "label": _label_from_score(trust_score, 38, 68, ("Low", "Medium", "High")),
            },
            "pressure_index": {
                "score": pressure_index,
                "label": _label_from_score(pressure_index, 40, 70, ("Light", "Elevated", "Heavy")),
            },
            "timing_quality": timing_quality,
        },
        "recommended_posture": posture,
        "likely_outcome_direction": likely_direction,
        "reasoning_summary": reasoning_summary,
        "next_step_suggestion": next_step,
        "warning": warning,
        "move_evaluator": move_evaluator,
        "timing_checker": timing_details,
        "framing_optimizer": framing_details,
        "confidence_note": "Confidence is calibrated and directional, not deterministic.",
    }


def build_reflection_response(
    *,
    forecast: dict[str, Any],
    outcome_summary: str,
    forecast_accuracy: str,
    action_taken: str,
) -> dict[str, Any]:
    posture = (forecast.get("recommended_posture") or ["Clarify"])[0]
    trust_recap = (
        "This builds trust if the forecast helped you slow down and choose a better posture."
        if forecast_accuracy == "accurate"
        else "Trust improves when misses are logged clearly and used to tighten future judgment."
    )
    learning = (
        f"The forecast appears directionally correct. Keep using the `{posture}` posture in similar conditions."
        if forecast_accuracy == "accurate"
        else f"The forecast missed the outcome. Re-check timing, hidden pressures, and whether `{posture}` was actually used."
    )
    comparison = (
        f"Forecast: {forecast.get('likely_outcome_direction', 'n/a')} Actual: {_summarize_text(outcome_summary, 120)}."
    )
    return {
        "reflective_comparison": comparison,
        "trust_building_recap": trust_recap,
        "learning_insight": learning,
        "action_taken": _summarize_text(action_taken, 120),
        "forecast_accuracy": forecast_accuracy,
    }


def build_reputation_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    reflected = [item for item in items if item.get("reflection")]
    accurate = sum(1 for item in reflected if item["reflection"].get("forecast_accuracy") == "accurate")
    total = len(reflected)
    accuracy_rate = round((accurate / total) * 100, 1) if total else 0.0
    dimensions = {
        "consistency_of_judgment": min(100.0, round(35 + total * 9 + accuracy_rate * 0.35, 1)) if total else 0.0,
        "foresight_quality": accuracy_rate,
        "restraint_quality": min(100.0, round(42 + accurate * 8 - max(total - accurate, 0) * 3, 1)) if total else 0.0,
        "framing_quality": min(100.0, round(40 + accurate * 7, 1)) if total else 0.0,
        "escalation_avoidance": min(100.0, round(38 + accurate * 6, 1)) if total else 0.0,
        "timing_quality": min(100.0, round(36 + accurate * 7, 1)) if total else 0.0,
    }
    return {
        "cases_reflected": total,
        "accuracy_rate": accuracy_rate,
        "public_summary": "Judgment history is still forming." if not total else "Judgment profile is improving through repeated reflection." if accuracy_rate >= 60 else "Judgment profile is active, but still volatile.",
        "dimensions": dimensions,
    }
