from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

GuardrailMode = Literal["off", "audit", "enforce"]


@dataclass(frozen=True)
class GuardrailDecision:
    flagged: bool
    category: str
    reason: str
    safe_reframe: str


_CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "violence": (
        r"\b(kill|murder|shoot|stab|bomb|explosive|poison|arson|attack)\b",
    ),
    "crime": (
        r"\b(steal|rob|burglary|fraud|scam|counterfeit|blackmail|extort|hack(ing)?|break into)\b",
    ),
    "self_harm": (
        r"\b(suicide|self[- ]?harm|kill myself|cut myself|overdose)\b",
    ),
    "sexual_exploitation": (
        r"\b(groom(ing)?|sex traffick(ing)?|child sexual|minor sexual|rape)\b",
    ),
}

_STRONG_OPERATIONAL_PATTERNS: tuple[str, ...] = (
    r"\bhow to\b",
    r"\btell me how to\b",
    r"\bshow me how to\b",
    r"\bbest way to\b",
    r"\bways? to\b",
    r"\bsteps? to\b",
    r"\bstep[- ]by[- ]step\b",
    r"\binstructions?\b",
    r"\btutorial\b",
    r"\bguide to\b",
    r"\brecipe for\b",
)

_WEAK_OPERATIONAL_PATTERNS: tuple[str, ...] = (
    r"\bwithout getting caught\b",
    r"\bavoid getting caught\b",
    r"\bget away with\b",
    r"\bbypass\b",
    r"\bevade\b",
    r"\bbuild\b",
    r"\bmake\b",
    r"\bcreate\b",
)

_REQUEST_CUE_PATTERNS: tuple[str, ...] = (
    r"\b(give|show|tell|provide|write|list)\b",
    r"^can you\b",
    r"^could you\b",
)

_INTENT_CUE_PATTERNS: tuple[str, ...] = (
    r"\bi want to\b",
    r"\bi need to\b",
    r"\bi am trying to\b",
    r"\bi'm trying to\b",
)

_ANALYTICAL_FRAMING_PATTERNS: tuple[str, ...] = (
    r"\bwhy does\b",
    r"\bwhy do\b",
    r"\bhistory of\b",
    r"\bimpact of\b",
    r"\bpolicy impact\b",
    r"\banaly(sis|ze|zing)\b",
    r"\bresearch\b",
    r"\bmodel(ing)?\b",
    r"\bsimulat(e|ion|ing)\b",
    r"\bscenario planning\b",
    r"\bforecast(ing)?\b",
    r"\bpredict(ion|ive)?\b",
)

_PREVENTIVE_FRAMING_PATTERNS: tuple[str, ...] = (
    r"\bhow to prevent\b",
    r"\bprevent\b",
    r"\bprevention\b",
    r"\bmitigate\b",
    r"\breduce harm\b",
    r"\bsafety\b",
    r"\bde-escalat(e|ion)\b",
    r"\bincident response\b",
    r"\bresponse plan\b",
    r"\brisk assessment\b",
    r"\bdefensive\b",
    r"\bprotection\b",
    r"\bsafeguard(ing)?\b",
    r"\bcompliance\b",
)

_EVASION_PATTERNS: tuple[str, ...] = (
    r"\bwithout getting caught\b",
    r"\bavoid getting caught\b",
    r"\bget away with\b",
    r"\bevade\b",
)

_SAFE_REFRAME_BY_CATEGORY: dict[str, str] = {
    "violence": "Reframe toward prevention, de-escalation, or policy analysis of violence risk.",
    "crime": "Reframe toward prevention, legal compliance, or incident-response best practices.",
    "self_harm": "Reframe toward safety support, prevention resources, or crisis intervention planning.",
    "sexual_exploitation": "Reframe toward safeguarding, reporting pathways, and prevention protocols.",
    "unknown": "Reframe toward safety, prevention, or non-operational policy analysis.",
}


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _detect_category(text: str) -> str:
    for category, patterns in _CATEGORY_PATTERNS.items():
        if _contains_any(text, patterns):
            return category
    return "unknown"


def evaluate_situation_text(text: str) -> GuardrailDecision:
    normalized = " ".join((text or "").strip().lower().split())
    if not normalized:
        return GuardrailDecision(
            flagged=False,
            category="unknown",
            reason="No operational harmful-use pattern detected.",
            safe_reframe=_SAFE_REFRAME_BY_CATEGORY["unknown"],
        )

    category = _detect_category(normalized)
    if category == "unknown":
        return GuardrailDecision(
            flagged=False,
            category="unknown",
            reason="No operational harmful-use pattern detected.",
            safe_reframe=_SAFE_REFRAME_BY_CATEGORY["unknown"],
        )

    strong_operational = _contains_any(normalized, _STRONG_OPERATIONAL_PATTERNS)
    weak_operational = _contains_any(normalized, _WEAK_OPERATIONAL_PATTERNS)
    request_cue = _contains_any(normalized, _REQUEST_CUE_PATTERNS)
    intent_cue = _contains_any(normalized, _INTENT_CUE_PATTERNS)
    analytical_framing = _contains_any(normalized, _ANALYTICAL_FRAMING_PATTERNS)
    preventive_framing = _contains_any(normalized, _PREVENTIVE_FRAMING_PATTERNS)
    evasive = _contains_any(normalized, _EVASION_PATTERNS)
    operational = strong_operational or evasive or (weak_operational and (request_cue or intent_cue))
    safe_context = (preventive_framing and not evasive) or (
        analytical_framing and not evasive and not strong_operational
    )

    if operational and not safe_context:
        return GuardrailDecision(
            flagged=True,
            category=category,
            reason=f"Operational request matched harmful-use category '{category}'.",
            safe_reframe=_SAFE_REFRAME_BY_CATEGORY[category],
        )

    return GuardrailDecision(
        flagged=False,
        category=category,
        reason="Harmful domain mentioned without operational harmful-use intent.",
        safe_reframe=_SAFE_REFRAME_BY_CATEGORY[category],
    )
