# Golden Flow - Weather-Aware Delivery-Delay Checker

Yellow.ai AI Intern assignment 2.

A script that reads a local `orders.json`, checks the current weather for every
order's city **concurrently**, flags orders as `Delayed` when the weather is bad
(Rain / Snow / Extreme), and attaches a personalised, weather-aware apology. A
bad city is logged and skipped without crashing the run.

## Features mapped to the brief

| Requirement | Where |
| --- | --- |
| Parallel fetching (`asyncio.gather`) | `weather_delay.py` -> `run()` builds one task per order and awaits them together via `asyncio.gather` |
| Golden Flow logic (Rain/Snow/Extreme -> `Delayed`) | `weather_delay.py` -> `DELAY_CONDITIONS` + `apply_golden_flow()` |
| AI Challenge - Weather-Aware Apology function | `apology.py` -> `generate_apology()` (drafted with an AI tool, see `AI_LOG.md`) |
| Resilience - handle `InvalidCity123`, keep going | `process_order()` catches `CityNotFoundError` / HTTP / network errors, logs, returns an error record |
| Security - no hardcoded key | key read from `.env` via `python-dotenv`; `.env` is git-ignored, `.env.example` is committed |

## Setup

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your free key from https://home.openweathermap.org/api_keys
```

## Run

```bash
# live API - updates orders.json in place
python weather_delay.py

# write to a separate file instead of overwriting
python weather_delay.py --output orders.result.json

# offline deterministic demo (no API key needed) - forces New York=Rain, London=Snow
python weather_delay.py --mock
```

Reset the input between runs with `cp orders.seed.json orders.json`.

## Example output (`--mock`)

```
-> requesting weather for New York         (mock)
-> requesting weather for Mumbai           (mock)
-> requesting weather for London           (mock)
-> requesting weather for InvalidCity123   (mock)
<- got New York         -> Rain (heavy intensity rain)
<- got Mumbai           -> Clouds (broken clouds)
<- got London           -> Snow (light snow)
WARNING SKIP  order 1004: OpenWeatherMap does not recognise city 'InvalidCity123'
Fetched 4 cities concurrently in 0.41s

================ SUMMARY ================
  1001  Alice Smith      New York        -> Delayed
  1002  Bob Jones        Mumbai          -> Processing
  1003  Charlie Green    London          -> Delayed
  1004  InvalidCity123   InvalidCity123  -> Pending   [OpenWeatherMap does not recognise city 'InvalidCity123']
----------------------------------------
  Delayed: 2   Errors handled: 1   Total: 4

  Apology for 1001:
    Hi Alice, your order to New York is delayed due to heavy intensity rain. We appreciate your patience!
```

The `-> requesting ...` lines all print before any `<- got ...` line, which shows
the four calls really are in flight together (total time ~= one request, not four).

## Tests

```bash
pytest -q
```

Covers the apology text, the delay-condition set, the delay/skip/idempotency
behaviour of `apply_golden_flow()` - all without touching the network.

## Files

```
weather_delay.py        main async script
apology.py              Weather-Aware Apology function
test_logic.py           unit tests for the pure logic
orders.json             the "database" (mutated in place by a run)
orders.seed.json        pristine copy of the input, for resetting
fixtures/mock_weather.json   canned weather used by --mock
.env.example            template for the API key
AI_LOG.md               prompts used to build the parallel + error-handling logic
```
