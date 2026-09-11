# Golden Flow - Weather-Aware Delivery-Delay Checker

Yellow.ai AI Intern assignment 2.

A script that reads a local `orders.json`, checks the current weather for every
order's city **concurrently**, flags orders as `Delayed` when the weather is bad
(Rain / Snow / Extreme), and attaches a personalised, weather-aware apology. A
bad city is logged and skipped without crashing the run.

## Features mapped to the brief

| Requirement | Where |
| --- | --- |
| Parallel fetching (`asyncio.gather`) | `weather_delay.py` -> `gather_weather()` fires one `process_order` coroutine per order through a single `asyncio.gather`; `run()` calls it. Proven by `tests/test_concurrency.py`. |
| Golden Flow logic (Rain/Snow/Extreme -> `Delayed`) | `weather_delay.py` -> `is_delivery_delay()` + `apply_golden_flow()` |
| AI Challenge - Weather-Aware Apology function | `apology.py` -> `generate_apology()`. AI was used during development to design and refine it (prompts in `AI_LOG.md`); the runtime implementation is deterministic so the behaviour is reproducible and offline-testable. |
| Resilience - handle `InvalidCity123`, keep going | `process_order()` catches `CityNotFoundError` / HTTP / network errors per task, logs, returns an error record; `asyncio.gather` is never poisoned |
| Security - no hardcoded key | key read from `.env` via `python-dotenv`; `.env` is git-ignored, `.env.example` is committed |

## Setup

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate       macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your free key from https://home.openweathermap.org/api_keys
```

## Run

```bash
python weather_delay.py                       # live API -> updated_orders.json
python weather_delay.py --output orders.json   # update the input file in place
python weather_delay.py --mock                 # offline deterministic demo, no key
```

`orders.json` is never modified by a default run. To reset it after an in-place
run: `git checkout orders.json`.

## Order files

| File | Role |
| --- | --- |
| `orders.json` | the exact assignment input - 4 orders, all `Pending`. Never written to by a default run. |
| `updated_orders.json` | script output. The committed copy is from `python weather_delay.py --mock` (deterministic fixture weather: New York = Rain, London = Snow), so it shows the `Delayed` branch. Re-run `python weather_delay.py` to regenerate it from the live API. |
| `orders.live.json` | a real OpenWeatherMap run - proves the live API integration and the `InvalidCity123` handling. May show every valid city as `Processing` when the real weather is clear. |

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

The `-> requesting ...` lines all print before any `<- got ...` line: the four
calls are in flight together (total time ~= one request, not four).

## Tests

```bash
pytest -q          # 7 passed
```

- `tests/test_logic.py` - apology text, the exact `{Rain, Snow, Extreme}` rule
  via `is_delivery_delay`, and the delay / skip / idempotency behaviour of
  `apply_golden_flow()`. No network.
- `tests/test_concurrency.py` - runs `gather_weather` (the real aggregation path)
  with 4 fake fetchers each sleeping 0.3s and asserts the batch finishes in
  well under the ~1.2s a sequential run would take.

## Files

```
weather_delay.py          main async script
apology.py                Weather-Aware Apology function
tests/                     test_logic.py, test_concurrency.py
pytest.ini                 pythonpath so tests import weather_delay
orders.json                assignment input (4 Pending orders)
updated_orders.json        script output (committed copy is the --mock run)
orders.live.json           a real OpenWeatherMap run
fixtures/mock_weather.json  canned weather used by --mock
.env.example               template for the API key
AI_LOG.md                  prompts used to build the parallel + error-handling logic
```
