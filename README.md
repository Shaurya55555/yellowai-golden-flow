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
python weather_delay.py                                # live API, updates orders.json in place
python weather_delay.py --output updated_orders.json   # write elsewhere, keep orders.json untouched
python weather_delay.py --mock --output orders.mock.result.json   # offline deterministic demo
```

The brief asks for "the updated `orders.json`", so the default **writes `orders.json`
in place**. To reset it to the pristine assignment data:
`cp orders.seed.json orders.json`.

## Order files

| File | Role |
| --- | --- |
| `orders.json` | **both** the exact assignment input and, after a run, the required deliverable - "the updated `orders.json` (showing which orders were marked as Delayed)". Which orders are `Delayed` in the committed copy depends on the real weather at the last live run; re-run before submitting for a fresh capture. |
| `orders.seed.json` | pristine backup of the original 4 `Pending` orders, for resetting `orders.json`. |
| `orders.live.json` | a preserved snapshot of a live run, kept alongside `orders.json` in case the latter gets overwritten by a later `--mock` or test run. |
| `orders.mock.result.json` | a `python weather_delay.py --mock` run against `fixtures/mock_weather.json` (New York = Rain, London = Snow). Deterministic, weather-independent proof of the `Rain/Snow/Extreme -> Delayed` branch and the apology function, for whenever the live weather doesn't cooperate. |

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
  with 8 fake fetchers each sleeping 0.6s and asserts the batch finishes in
  under half the 4.8s a sequential run would take.

## Files

```
weather_delay.py          main async script
apology.py                Weather-Aware Apology function
tests/                     test_logic.py, test_concurrency.py
pytest.ini                 pythonpath so tests import weather_delay
orders.json                 assignment input AND the deliverable (updated in place by default)
orders.seed.json            pristine backup of the 4 Pending orders
orders.live.json            a preserved live-run snapshot
orders.mock.result.json     deterministic --mock run (weather-independent Delayed proof)
fixtures/mock_weather.json  canned weather used by --mock
.env.example               template for the API key
AI_LOG.md                  prompts used to build the parallel + error-handling logic
```
