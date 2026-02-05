from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SituationSemantics:
    raw_text: str
    actors: List[str]
    institutions: List[str]
    conflict: bool
    domain: str
    mode: str


def _tokenize(text: str) -> List[str]:
    return [t.strip(".,!?;:\"'()[]").lower() for t in text.split() if t.strip()]


def infer_mode(tokens: List[str]) -> str:
    mode_c_markers = {
        "government",
        "policy",
        "tax",
        "public",
        "population",
        "platform",
        "algorithm",
        "commuters",
        "businesses",
        "society",
        "community",
    }
    if any(t in mode_c_markers for t in tokens):
        return "C"

    interpersonal_markers = {
        "manager",
        "employee",
        "coworker",
        "hr",
        "promotion",
        "confronts",
        "confront",
        "partner",
        "friend",
        "team",
    }
    if any(t in interpersonal_markers for t in tokens):
        return "B"

    return "A"


def parse_situation(text: str) -> SituationSemantics:
    tokens = _tokenize(text)

    actors = []
    for t in tokens:
        if t in {"student", "employee", "manager", "government", "creators", "commuters"}:
            if t not in actors:
                actors.append(t)

    institutions = []
    for t in tokens:
        if t in {"hr", "government", "platform", "school", "exam", "company"}:
            if t not in institutions:
                institutions.append(t)

    conflict = any(t in {"denied", "conflict", "confronts", "cheat", "unpaid"} for t in tokens)

    domain = "general"
    if any(t in {"exam", "student", "cheat"} for t in tokens):
        domain = "education"
    elif any(t in {"employee", "manager", "promotion", "hr"} for t in tokens):
        domain = "workplace"
    elif any(t in {"tax", "government", "commuters", "businesses"} for t in tokens):
        domain = "policy"
    elif any(t in {"platform", "algorithm", "creators"} for t in tokens):
        domain = "media"

    mode = infer_mode(tokens)
    return SituationSemantics(
        raw_text=text,
        actors=actors,
        institutions=institutions,
        conflict=conflict,
        domain=domain,
        mode=mode,
    )
