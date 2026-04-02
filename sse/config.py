from __future__ import annotations

import os
from typing import cast

from sse.guardrails import GuardrailMode

_DEFAULT_GUARDRAIL_MODE: GuardrailMode = "enforce"
_VALID_GUARDRAIL_MODES = {"off", "audit", "enforce"}


def get_guardrail_mode() -> GuardrailMode:
    raw_value = (os.getenv("SSE_GUARDRAIL_MODE") or "").strip().lower()
    if raw_value in _VALID_GUARDRAIL_MODES:
        return cast(GuardrailMode, raw_value)
    return _DEFAULT_GUARDRAIL_MODE
