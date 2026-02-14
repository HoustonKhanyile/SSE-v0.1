from sse.orchestrator import RunConfig, run_sse


def test_srl_depth_inference_by_mode():
    mode_a = run_sse("A student considers cheating during an exam.", RunConfig())
    mode_b = run_sse("An employee confronts their manager about overtime.", RunConfig())
    mode_c = run_sse("A government raises fuel taxes for commuters.", RunConfig())

    assert mode_a.recursion_depth_used == 0
    assert mode_b.recursion_depth_used == 1
    assert mode_c.recursion_depth_used == 2


def test_srl_depth_override_and_extensions_present():
    result = run_sse(
        "A manager and employee negotiate a performance deal with HR oversight.",
        RunConfig(strategic_depth=3),
    )

    assert result.recursion_depth_used == 3
    assert result.belief_shift_summary
    assert result.signal_evaluation_summary
    assert 0.0 <= result.coalition_likelihood <= 1.0

