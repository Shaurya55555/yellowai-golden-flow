"""Golden Flow: weather-aware delivery-delay checker.

What it does
------------
1. Reads orders from a local JSON file (the "database").
2. Fetches the current weather for every order's city CONCURRENTLY
   (asyncio.gather + httpx.AsyncClient), never one-by-one.
3. If the weather "main" is Rain, Snow or Extreme, the order status is
   updated to "Delayed" and a personalised, weather-aware apology is attached.
4. A bad city (e.g. "InvalidCity123") is logged and skipped - the run still
   finishes and processes every other city.
5. The updated orders are written back to disk.

The API key is read from a .env file (OPENWEATHER_API_KEY) - never hardcoded.

Usage
-----
    python weather_delay.py                 # real API, updates orders.json in place
    python weather_delay.py --output out.json
    python weather_delay.py --mock          # deterministic offline demo, no key needed
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from apology import generate_apology

OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

# Per the assignment spec, only these "main" values trigger a delay.
DELAY_CONDITIONS = {"Rain", "Snow", "Extreme"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("golden-flow")


class CityNotFoundError(Exception):
    """Raised when OpenWeatherMap does not recognise a city (HTTP 404)."""


# --------------------------------------------------------------------------- #
# Weather fetching                                                            #
# --------------------------------------------------------------------------- #
async def fetch_weather(client: httpx.AsyncClient, city: str, api_key: str) -> dict:
    """Fetch current weather for one city. Raises on failure."""
    log.info("-> requesting weather for %-16s", city)
    resp = await client.get(
        OWM_URL,
        params={"q": city, "appid": api_key, "units": "metric"},
        timeout=15,
    )
    if resp.status_code == 404:
        raise CityNotFoundError(f"OpenWeatherMap does not recognise city '{city}'")
    resp.raise_for_status()
    data = resp.json()
    weather = (data.get("weather") or [{}])[0]
    result = {
        "city": city,
        "main": weather.get("main", "Unknown"),
        "description": weather.get("description", ""),
        "temp_c": data.get("main", {}).get("temp"),
    }
    log.info("<- got %-16s -> %s (%s)", city, result["main"], result["description"])
    return result


def _load_mock_fixtures() -> dict:
    return json.loads(Path("fixtures/mock_weather.json").read_text(encoding="utf-8"))


async def fetch_weather_mock(client: httpx.AsyncClient, city: str, api_key: str) -> dict:
    """Offline stand-in used by --mock so the demo is deterministic."""
    fixtures = _load_mock_fixtures()
    log.info("-> requesting weather for %-16s (mock)", city)
    await asyncio.sleep(0.4)  # pretend network latency so concurrency is visible
    if city not in fixtures:
        raise CityNotFoundError(f"OpenWeatherMap does not recognise city '{city}'")
    entry = fixtures[city]
    result = {
        "city": city,
        "main": entry["main"],
        "description": entry.get("description", ""),
        "temp_c": entry.get("temp_c"),
    }
    log.info("<- got %-16s -> %s (%s)", city, result["main"], result["description"])
    return result


# --------------------------------------------------------------------------- #
# Per-order processing                                                        #
# --------------------------------------------------------------------------- #
async def process_order(client, order: dict, api_key: str, fetcher) -> dict:
    """Resolve weather for a single order. Never raises - errors are captured."""
    city = order.get("city", "")
    try:
        weather = await fetcher(client, city, api_key)
        return {"order": order, "weather": weather, "error": None}
    except CityNotFoundError as exc:
        log.warning("SKIP  order %s: %s", order.get("order_id"), exc)
        return {"order": order, "weather": None, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        log.warning(
            "SKIP  order %s: HTTP %s from weather API",
            order.get("order_id"),
            exc.response.status_code,
        )
        return {"order": order, "weather": None, "error": f"HTTP {exc.response.status_code}"}
    except (httpx.RequestError, asyncio.TimeoutError) as exc:
        log.warning("SKIP  order %s: network error: %s", order.get("order_id"), exc)
        return {"order": order, "weather": None, "error": f"network error: {exc}"}


# --------------------------------------------------------------------------- #
# Golden Flow                                                                 #
# --------------------------------------------------------------------------- #
def apply_golden_flow(results: list[dict]) -> list[dict]:
    """Mutate orders in place based on their resolved weather. Returns orders."""
    orders: list[dict] = []
    for item in results:
        order = item["order"]
        weather = item["weather"]
        error = item["error"]

        # Drop any fields from a previous run so re-runs are idempotent.
        for stale in ("weather", "weather_description", "apology", "weather_error"):
            order.pop(stale, None)

        if error is not None:
            order["status"] = "Pending"
            order["weather_error"] = error
        elif weather["main"] in DELAY_CONDITIONS:
            order["status"] = "Delayed"
            order["weather"] = weather["main"]
            order["weather_description"] = weather["description"]
            order["apology"] = generate_apology(
                order.get("customer", ""),
                order.get("city", ""),
                weather["main"],
                weather["description"],
            )
        else:
            order["status"] = "Processing"
            order["weather"] = weather["main"]
            order["weather_description"] = weather["description"]

        orders.append(order)
    return orders


async def run(orders_path: Path, output_path: Path, use_mock: bool) -> None:
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not use_mock and not api_key:
        raise SystemExit(
            "OPENWEATHER_API_KEY is not set. Copy .env.example to .env and add your "
            "free OpenWeatherMap key, or run with --mock for an offline demo."
        )

    orders = json.loads(orders_path.read_text(encoding="utf-8"))
    log.info("Loaded %d orders from %s", len(orders), orders_path)

    fetcher = fetch_weather_mock if use_mock else fetch_weather
    started = time.perf_counter()

    async with httpx.AsyncClient() as client:
        # asyncio.gather => all city lookups are in flight at the same time.
        results = await asyncio.gather(
            *(process_order(client, order, api_key, fetcher) for order in orders)
        )

    elapsed = time.perf_counter() - started
    log.info("Fetched %d cities concurrently in %.2fs", len(orders), elapsed)

    updated = apply_golden_flow(results)
    output_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")

    delayed = [o for o in updated if o["status"] == "Delayed"]
    errored = [o for o in updated if "weather_error" in o]

    print("\n================ SUMMARY ================")
    for o in updated:
        line = f"  {o['order_id']}  {o['customer']:<15}  {o['city']:<14}  -> {o['status']}"
        if "weather_error" in o:
            line += f"   [{o['weather_error']}]"
        print(line)
    print("----------------------------------------")
    print(f"  Delayed: {len(delayed)}   Errors handled: {len(errored)}   Total: {len(updated)}")
    for o in delayed:
        print(f"\n  Apology for {o['order_id']}:\n    {o['apology']}")
    print("========================================")
    print(f"\nWrote updated orders -> {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Weather-aware delivery-delay checker")
    parser.add_argument("--orders", default="orders.json", help="input orders JSON")
    parser.add_argument(
        "--output",
        default=None,
        help="where to write updated orders (default: overwrite the input file)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="use local fixtures instead of the live API (no key needed)",
    )
    args = parser.parse_args()

    orders_path = Path(args.orders)
    output_path = Path(args.output) if args.output else orders_path
    asyncio.run(run(orders_path, output_path, args.mock))


if __name__ == "__main__":
    main()
