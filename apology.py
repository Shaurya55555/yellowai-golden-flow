"""Weather-Aware Apology generator.

This function was drafted with the help of an AI tool (see AI_LOG.md). It is
kept deterministic on purpose: no network call, no API key, fully testable.
Given the customer, destination city and the weather that caused the delay, it
returns a short, personalised apology line.
"""

from __future__ import annotations

# Fallback phrasing when the API does not give us a human description.
_CONDITION_PHRASES = {
    "Rain": "heavy rain",
    "Snow": "snowfall",
    "Extreme": "extreme weather conditions",
    "Thunderstorm": "a thunderstorm",
    "Drizzle": "persistent drizzle",
}


def _first_name(customer: str) -> str:
    customer = (customer or "").strip()
    if not customer:
        return "there"
    return customer.split()[0]


def generate_apology(
    customer: str,
    city: str,
    weather_main: str,
    description: str | None = None,
) -> str:
    """Return a personalised, weather-aware apology message.

    Example:
        >>> generate_apology("Alice Smith", "New York", "Rain", "heavy intensity rain")
        'Hi Alice, your order to New York is delayed due to heavy intensity rain. We appreciate your patience!'
    """
    name = _first_name(customer)
    reason = (description or "").strip()
    if not reason:
        reason = _CONDITION_PHRASES.get(
            weather_main, f"{str(weather_main).lower()} conditions"
        )
    return (
        f"Hi {name}, your order to {city} is delayed due to {reason}. "
        f"We appreciate your patience!"
    )
