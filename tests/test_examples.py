from sse.demo.examples import EXAMPLES
from sse.orchestrator import RunConfig, run_sse


def test_examples_produce_valid_prediction_result():
    for example in EXAMPLES.values():
        result = run_sse(
            example.situation,
            RunConfig(depth="default", include_alternatives=False, example_id=example.id),
        )
        assert result.predicted_outcome.id == example.expected_outcome_id
        assert result.mode == example.expected_mode
        assert result.explanation
