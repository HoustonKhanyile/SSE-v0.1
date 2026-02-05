from sse.ssm import parse_situation


def test_mode_inference():
    a = parse_situation("A student considers cheating during an exam.")
    b = parse_situation("An employee confronts their manager about overtime.")
    c = parse_situation("A government raises fuel taxes for commuters.")

    assert a.mode == "A"
    assert b.mode == "B"
    assert c.mode == "C"
