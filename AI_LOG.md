# AI Log

Tool used: Claude (Sonnet 5) via Claude Code. Below are the actual prompts used
to build the three pieces the brief calls out.

## 1. Parallel fetching

> "In Python, I have a list of orders each with a `city`. I need to fetch the
> current weather for every city from the OpenWeatherMap API at the same time,
> not sequentially. Show me the `asyncio` + `httpx.AsyncClient` pattern using
> `asyncio.gather`, with one coroutine per city, sharing a single client."

Follow-up:

> "Add lightweight logging that prints a line right before each request is
> awaited and right after each response, so that when I record the demo the
> interleaved output visibly proves the calls overlap. Also time the whole
> `gather` block and log 'Fetched N cities concurrently in X.XXs'."

Result: `run()` creates `process_order(...)` coroutines for every order and
awaits them with a single `asyncio.gather(...)` inside one `httpx.AsyncClient`
context. The `-> requesting` / `<- got` log lines interleave, and elapsed time
is roughly one request instead of four.

## 2. Error handling / resilience

> "One of the cities is `InvalidCity123`. OpenWeatherMap returns HTTP 404 for
> it. I need the script to log that error and carry on processing the other
> cities - it must not crash and must not abort the `gather`. What's the clean
> way to do this?"

Follow-up:

> "Give each task its own try/except so a single failure can't take down
> `asyncio.gather`. Catch a custom `CityNotFoundError` for the 404, plus
> `httpx.HTTPStatusError`, `httpx.RequestError` and timeouts separately, and
> return a structured record `{order, weather, error}` in every branch so the
> caller can tell success from failure without exceptions leaking out."

Result: `fetch_weather()` raises `CityNotFoundError` on 404; `process_order()`
wraps the call and converts every failure mode into an `error` record that is
logged at WARNING level. `apply_golden_flow()` then leaves errored orders as
`Pending` and adds a `weather_error` field. The run always finishes and always
writes the output file.

## 3. AI Challenge - Weather-Aware Apology function

> "Write a small deterministic Python function `generate_apology(customer, city,
> weather_main, description=None)` that returns a message like: 'Hi Alice, your
> order to New York is delayed due to heavy rain. We appreciate your patience!'
> Use the customer's first name only, prefer the API's human `description`
> string when present, and fall back to a per-condition phrase map
> (Rain -> 'heavy rain', Snow -> 'snowfall', Extreme -> 'extreme weather
> conditions') otherwise. No network calls, so it stays unit-testable."

Result: `apology.py` -> `generate_apology()`, covered by `test_logic.py`.
