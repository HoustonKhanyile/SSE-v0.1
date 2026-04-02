import importlib
from sse.api.app import SemanticsRequest, _build_prediction_payload, semantics
from sse.phenomenon import PhenomenonContext

api_app_module = importlib.import_module("sse.api.app")


def test_prediction_payload_includes_general_query_mode_by_default():
    payload = _build_prediction_payload("A student considers cheating during an exam.")
    assert payload["query_mode"] == "general"
    assert payload["phenomenon_tag"] == ""


def test_prediction_payload_extracts_phenomenon_tag(monkeypatch):
    def _stub_context(raw_text: str, tag: str) -> PhenomenonContext:
        return PhenomenonContext(
            tag=tag,
            normalized_query="why this term emerged",
            summary="stub summary",
            hypotheses=["h1"],
            evidence=[],
            enriched_text=f"{raw_text} stub enrichment",
        )

    monkeypatch.setattr(api_app_module, "build_phenomenon_context", _stub_context)
    payload = _build_prediction_payload(
        "In modern slang, why does @language shift quickly in online communities?",
        query_mode="phenomenon",
    )
    assert payload["query_mode"] == "phenomenon"
    assert payload["phenomenon_tag"] == "language"
    assert payload["phenomenon"]["module"] == "language"


def test_semantics_returns_query_mode_and_tag(monkeypatch):
    def _stub_context(raw_text: str, tag: str) -> PhenomenonContext:
        return PhenomenonContext(
            tag=tag,
            normalized_query="why terminology spreads",
            summary="stub summary",
            hypotheses=["h1"],
            evidence=[],
            enriched_text=f"{raw_text} stub enrichment",
        )

    monkeypatch.setattr(api_app_module, "build_phenomenon_context", _stub_context)
    result = semantics(
        SemanticsRequest(
            situation="Why does @terminology spread faster in certain industries?",
            query_mode="phenomenon",
        )
    )
    assert result["query_mode"] == "phenomenon"
    assert result["phenomenon_tag"] == "terminology"
