"""Unit tests for the pure logic (no network)."""

from apology import generate_apology
from weather_delay import DELAY_CONDITIONS, apply_golden_flow, is_delivery_delay


def test_apology_uses_first_name_and_description():
    msg = generate_apology("Alice Smith", "New York", "Rain", "heavy intensity rain")
    assert msg == (
        "Hi Alice, your order to New York is delayed due to heavy intensity rain. "
        "We appreciate your patience!"
    )


def test_apology_falls_back_when_no_description():
    msg = generate_apology("Bob", "London", "Snow", "")
    assert "Hi Bob," in msg
    assert "snowfall" in msg


def test_delay_conditions_match_spec():
    assert DELAY_CONDITIONS == {"Rain", "Snow", "Extreme"}


def test_is_delivery_delay_only_rain_snow_extreme():
    assert all(is_delivery_delay(w) for w in ("Rain", "Snow", "Extreme"))
    for w in ("Clear", "Clouds", "Drizzle", "Thunderstorm", "Mist", "Fog", None):
        assert not is_delivery_delay(w)


def _order(oid, city="X"):
    return {"order_id": oid, "customer": "Test User", "city": city, "status": "Pending"}


def test_golden_flow_marks_rain_as_delayed():
    results = [
        {"order": _order("1"), "weather": {"main": "Rain", "description": "light rain"}, "error": None},
        {"order": _order("2"), "weather": {"main": "Clear", "description": "clear sky"}, "error": None},
        {"order": _order("3"), "weather": None, "error": "unknown city 'Nowhere'"},
    ]
    out = apply_golden_flow(results)
    assert out[0]["status"] == "Delayed"
    assert "apology" in out[0]
    assert out[1]["status"] == "Processing"
    assert out[2]["status"] == "Pending"
    assert out[2]["weather_error"] == "unknown city 'Nowhere'"


def test_golden_flow_is_idempotent():
    results = [
        {"order": _order("1"), "weather": {"main": "Snow", "description": "light snow"}, "error": None},
    ]
    first = apply_golden_flow(results)[0]
    # feed the already-mutated order back in
    second = apply_golden_flow(
        [{"order": first, "weather": {"main": "Clear", "description": "clear sky"}, "error": None}]
    )[0]
    assert second["status"] == "Processing"
    assert "apology" not in second
    assert "weather_error" not in second
