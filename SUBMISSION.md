# Assignment 2 - Submission Checklist

| Deliverable | File / action | Status |
| --- | --- | --- |
| Source code | this repo (`weather_delay.py`, `apology.py`, `tests/`) | done |
| Updated order output showing which orders became `Delayed` | `updated_orders.json` (live) + `orders.mock.result.json` (deterministic) | done (see note) |
| "AI Log" with the prompts used | `AI_LOG.md` | done |
| Demo recording | script below | to record |

## Note on the order files

- **`orders.json`** - the exact assignment input, 4 orders all `Pending`. A
  default run never touches it.
- **`updated_orders.json`** - the deliverable, from a **live**
  `python weather_delay.py` run. The committed copy was captured with Mumbai
  actually raining, so order `1002` is `Delayed` with a real apology and `1004`
  is error-handled. Which cities delay depends on the weather at run time -
  **re-run before submitting** for a fresh capture.
- **`orders.mock.result.json`** - a `--mock` run against
  `fixtures/mock_weather.json` (New York = Rain, London = Snow). Deterministic,
  weather-independent proof that the `Rain/Snow/Extreme -> Delayed` branch and
  the apology function work, regardless of what the sky is doing on submission
  day.

All logic (concurrency, error handling, classification, file writing) is
identical on the live and `--mock` paths - only the weather source differs.

## Demo recording script (2-3 min)

1. Show `.env.example`; the real key lives in `.env` (git-ignored).
2. `pytest -q` -> **7 passed**. Call out `tests/test_concurrency.py` - it runs
   the real `gather_weather` path with fake delays and proves the batch is
   concurrent, not sequential.
3. `python weather_delay.py` (LIVE API -> `updated_orders.json`):
   - all four `-> requesting ...` lines print before any `<- got ...` line =
     concurrent (`asyncio.gather`), plus the "Fetched 4 cities concurrently in
     X.XXs" timing line.
   - `WARNING SKIP order 1004` = `InvalidCity123` handled, the run still
     completes and writes output.
   - `cat updated_orders.json` -> real weather per city; any `Rain/Snow/Extreme`
     city is `Delayed` with an apology.
4. `python weather_delay.py --mock --output orders.mock.result.json` -> SUMMARY
   shows 2 `Delayed` (New York, London), 1 error handled, and the two apology
   messages - the deterministic proof of the branch.
5. Open `weather_delay.py` and point at `is_delivery_delay()` -
   `{"Rain", "Snow", "Extreme"}`, exactly the brief.
6. Show `AI_LOG.md`.

## Push to GitHub

Already at https://github.com/Shaurya55555/yellowai-golden-flow (branch `main`).
