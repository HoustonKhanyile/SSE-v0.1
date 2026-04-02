from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import List
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


SUPPORTED_PHENOMENA = {"language", "trend", "behavior"}


@dataclass(frozen=True)
class PhenomenonEvidence:
    source: str
    title: str
    snippet: str
    url: str


@dataclass(frozen=True)
class PhenomenonContext:
    tag: str
    normalized_query: str
    summary: str
    hypotheses: List[str]
    evidence: List[PhenomenonEvidence]
    enriched_text: str


def _clean_query(raw_text: str, tag: str) -> str:
    without_tag = re.sub(rf"@{re.escape(tag)}\b", "", raw_text, count=1, flags=re.IGNORECASE)
    without_prefix = re.sub(r"^\s*[:\-]\s*", "", without_tag.strip())
    return without_prefix.strip()


def _http_get_json(url: str, timeout: float = 3.0) -> dict | list | None:
    req = Request(url, headers={"User-Agent": "SSE-Phenomenon/0.1"})
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        return json.loads(raw)
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def _duckduckgo_search(query: str, limit: int = 3) -> List[PhenomenonEvidence]:
    url = (
        "https://api.duckduckgo.com/"
        f"?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
    )
    payload = _http_get_json(url)
    if not isinstance(payload, dict):
        return []

    items: List[PhenomenonEvidence] = []
    abstract = (payload.get("AbstractText") or "").strip()
    abstract_url = (payload.get("AbstractURL") or "").strip()
    heading = (payload.get("Heading") or "").strip() or "DuckDuckGo Result"
    if abstract and abstract_url:
        items.append(
            PhenomenonEvidence(
                source="duckduckgo",
                title=heading,
                snippet=abstract,
                url=abstract_url,
            )
        )

    related = payload.get("RelatedTopics") or []
    for topic in related:
        if len(items) >= limit:
            break
        if not isinstance(topic, dict):
            continue
        text = (topic.get("Text") or "").strip()
        first_url = (topic.get("FirstURL") or "").strip()
        if text and first_url:
            items.append(
                PhenomenonEvidence(
                    source="duckduckgo",
                    title=text.split(" - ")[0][:120],
                    snippet=text[:220],
                    url=first_url,
                )
            )
    return items[:limit]


def _language_hypotheses(query: str) -> List[str]:
    lower = query.lower()
    hypotheses = [
        "Novel terms usually begin as in-group signals, then spread once they become identity markers.",
        "Language change accelerates when short, vivid phrases fit platform constraints and meme formats.",
    ]
    if any(token in lower for token in ("tiktok", "x", "twitter", "instagram", "youtube", "reddit")):
        hypotheses.append("Algorithmic amplification likely accelerated adoption across communities.")
    if any(token in lower for token in ("origin", "come to be", "etymology", "coined")):
        hypotheses.append("Earliest use likely came from a niche creator community before mainstream pickup.")
    return hypotheses


def _trend_hypotheses(query: str) -> List[str]:
    lower = query.lower()
    hypotheses = [
        "Trends often follow diffusion stages: novelty, imitation, platform reinforcement, and saturation.",
        "Observable growth can be caused by social proof loops rather than intrinsic utility alone.",
    ]
    if any(token in lower for token in ("market", "sales", "adoption", "consumer")):
        hypotheses.append("Price signals and accessibility likely interacted with social signaling effects.")
    if any(token in lower for token in ("policy", "regulation", "law")):
        hypotheses.append("Institutional changes may have altered incentives and visibility.")
    return hypotheses


def _behavior_hypotheses(query: str) -> List[str]:
    lower = query.lower()
    hypotheses = [
        "Behavioral patterns often emerge from repeated reinforcement in stable environments.",
        "Observed behavior can reflect bounded rationality under social and institutional constraints.",
    ]
    if any(token in lower for token in ("habit", "routine", "daily", "repeat")):
        hypotheses.append("Habit loops likely contributed through cue-routine-reward dynamics.")
    if any(token in lower for token in ("group", "peer", "community", "norm")):
        hypotheses.append("Norm pressure and social imitation likely increased behavioral convergence.")
    return hypotheses


def _build_enriched_text(
    raw_text: str,
    tag: str,
    summary: str,
    hypotheses: List[str],
    evidence: List[PhenomenonEvidence],
) -> str:
    evidence_line = "; ".join(
        f"{item.title}: {item.snippet[:140]}"
        for item in evidence[:2]
    )
    hypotheses_line = "; ".join(hypotheses[:3])
    return (
        f"{raw_text} "
        f"Phenomenon focus={tag}. "
        f"Interpretation summary: {summary} "
        f"Hypotheses: {hypotheses_line}. "
        f"Observed evidence: {evidence_line if evidence_line else 'No external evidence retrieved.'}"
    )


def build_phenomenon_context(raw_text: str, tag: str) -> PhenomenonContext:
    normalized_tag = tag.strip().lower()
    if normalized_tag not in SUPPORTED_PHENOMENA:
        raise ValueError("unsupported_phenomenon_tag")

    query = _clean_query(raw_text, normalized_tag)
    if not query:
        raise ValueError("empty_phenomenon_query")

    if normalized_tag == "language":
        summary = (
            "Language phenomena are explained through lexical innovation, social identity signaling, and "
            "platform-mediated diffusion."
        )
        hypotheses = _language_hypotheses(query)
        evidence = _duckduckgo_search(f"{query} slang origin terminology")
    elif normalized_tag == "trend":
        summary = (
            "Trend phenomena are explained through adoption dynamics, incentive structure, and social contagion."
        )
        hypotheses = _trend_hypotheses(query)
        evidence = _duckduckgo_search(f"{query} trend origin adoption drivers")
    else:
        summary = (
            "Behavior phenomena are explained through reinforcement dynamics, social norms, and constrained decision-making."
        )
        hypotheses = _behavior_hypotheses(query)
        evidence = _duckduckgo_search(f"{query} behavior pattern causes psychology sociology")

    enriched_text = _build_enriched_text(
        raw_text=raw_text,
        tag=normalized_tag,
        summary=summary,
        hypotheses=hypotheses,
        evidence=evidence,
    )
    return PhenomenonContext(
        tag=normalized_tag,
        normalized_query=query,
        summary=summary,
        hypotheses=hypotheses,
        evidence=evidence,
        enriched_text=enriched_text,
    )
