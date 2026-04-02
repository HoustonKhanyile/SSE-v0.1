from sse.config import get_guardrail_mode


def test_default_guardrail_mode_is_enforce(monkeypatch):
    monkeypatch.delenv("SSE_GUARDRAIL_MODE", raising=False)
    assert get_guardrail_mode() == "enforce"


def test_valid_modes_are_normalized(monkeypatch):
    monkeypatch.setenv("SSE_GUARDRAIL_MODE", " AUDIT ")
    assert get_guardrail_mode() == "audit"

    monkeypatch.setenv("SSE_GUARDRAIL_MODE", "off")
    assert get_guardrail_mode() == "off"

    monkeypatch.setenv("SSE_GUARDRAIL_MODE", "ENFORCE")
    assert get_guardrail_mode() == "enforce"


def test_invalid_mode_falls_back_to_enforce(monkeypatch):
    monkeypatch.setenv("SSE_GUARDRAIL_MODE", "invalid")
    assert get_guardrail_mode() == "enforce"
