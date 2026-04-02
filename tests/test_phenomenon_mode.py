import importlib
import pytest
from fastapi import HTTPException

from sse.api.app import (
    CompareRequest,
    PredictRequest,
    SemanticsRequest,
    TimelineCheckpoint,
    TimelineRequest,
    compare,
    predict,
    semantics,
    timeline,
)
from sse.phenomenon import PhenomenonContext

api_app_module = importlib.import_module("sse.api.app")


def test_compare_rejects_phenomenon_mode():
    with pytest.raises(HTTPException) as exc:
        compare(
            CompareRequest(
                base_situation="@language: why did this term emerge?",
                variant_situation="@language: why did this term spread?",
                query_mode="phenomenon",
            )
        )
    assert exc.value.status_code == 400


def test_timeline_rejects_phenomenon_mode():
    with pytest.raises(HTTPException) as exc:
        timeline(
            TimelineRequest(
                base_situation="@trend: why is this trend growing?",
                checkpoints=[TimelineCheckpoint(label="T1", situation="@trend: why now?")],
                query_mode="phenomenon",
            )
        )
    assert exc.value.status_code == 400


def test_predict_phenomenon_requires_supported_tag():
    with pytest.raises(HTTPException) as exc:
        predict(PredictRequest(situation="@unknown: explain this pattern", query_mode="phenomenon"))
    assert exc.value.status_code == 400


def test_semantics_includes_phenomenon_module_payload(monkeypatch):
    def _stub_context(raw_text: str, tag: str) -> PhenomenonContext:
        return PhenomenonContext(
            tag=tag,
            normalized_query="how it emerged",
            summary="stub summary",
            hypotheses=["h1", "h2"],
            evidence=[],
            enriched_text=f"{raw_text} enriched",
        )

    monkeypatch.setattr(api_app_module, "build_phenomenon_context", _stub_context)
    payload = semantics(
        SemanticsRequest(
            situation='@language: how did "aura farming" come to be?',
            query_mode="phenomenon",
        )
    )
    assert payload["query_mode"] == "phenomenon"
    assert payload["phenomenon_tag"] == "language"
    assert payload["phenomenon"]["module"] == "language"


def test_predict_supports_behavior_module(monkeypatch):
    def _stub_context(raw_text: str, tag: str) -> PhenomenonContext:
        return PhenomenonContext(
            tag=tag,
            normalized_query="why this behavior persists",
            summary="behavior summary",
            hypotheses=["h1"],
            evidence=[],
            enriched_text=f"{raw_text} enriched",
        )

    monkeypatch.setattr(api_app_module, "build_phenomenon_context", _stub_context)
    payload = predict(
        PredictRequest(
            situation="@behavior: why do users keep doomscrolling at night?",
            query_mode="phenomenon",
        )
    )
    assert payload["query_mode"] == "phenomenon"
    assert payload["phenomenon_tag"] == "behavior"
    assert payload["phenomenon"]["module"] == "behavior"
