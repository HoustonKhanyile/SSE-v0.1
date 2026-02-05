from sse.orchestrator import RunConfig, run_sse


def test_deterministic_output():
    situation = "A student considers cheating during an exam when the invigilator leaves."
    result1 = run_sse(situation, RunConfig())
    result2 = run_sse(situation, RunConfig())

    assert result1.to_dict() == result2.to_dict()
