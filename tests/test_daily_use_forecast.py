from sse.api.app import PredictRequest, ReflectionRequest, get_query_endpoint, predict, reflect_query_endpoint
from sse.queries import create_query_item


def test_predict_returns_daily_use_forecast():
    payload = predict(
        PredictRequest(
            situation="I need to ask my manager for more flexibility during a high-pressure week.",
            feature_type="move_evaluator",
            intended_move="I want to send a message asking for deadline flexibility.",
            urgency="high",
            role_tags=["manager"],
            alternatives=True,
        )
    )
    assert "daily_use" in payload
    assert payload["daily_use"]["feature_type"] == "move_evaluator"
    assert payload["daily_use"]["forecast_metrics"]["escalation_risk"]["label"] in {"Low", "Moderate", "High"}
    assert payload["daily_use"]["recommended_posture"]
    assert payload["daily_use"]["move_evaluator"]["likely_reception"] in {"Closed", "Mixed", "Open"}


def test_reflection_endpoint_persists_feedback():
    payload = predict(
        PredictRequest(
            situation="I am deciding whether to confront a teammate about missed work.",
            feature_type="timing_checker",
        )
    )
    saved = get_query_endpoint(
        create_query_item(
            situation="I am deciding whether to confront a teammate about missed work.",
            query_mode="general",
            prediction=payload,
        )["id"]
    )
    updated = reflect_query_endpoint(
        saved["id"],
        ReflectionRequest(
            action_taken="I delayed the conversation until after the deadline meeting.",
            outcome_summary="The teammate was more receptive once the pressure dropped.",
            forecast_accuracy="accurate",
        ),
    )
    assert updated["reflection"]["forecast_accuracy"] == "accurate"
    assert "reflective_comparison" in updated["reflection"]
