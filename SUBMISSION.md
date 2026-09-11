# Assignment 2 - Submission Checklist

| Deliverable | File / action | Status |
| --- | --- | --- |
| Source code | this repo (`weather_delay.py`, `apology.py`, `tests/`) | done |
| Updated order output showing which orders became `Delayed` | `updated_orders.json` (+ `orders.live.json` for the real run) | done (see note) |
| "AI Log" with the prompts used | `AI_LOG.md` | done |
| Demo recording | script below | to record |

## Note on the order files

- **`orders.json`** - the exact assignment input, 4 orders all `Pending`. A
  default run never touches it.
- **`updated_orders.json`** - the script's output. The committed copy is from
  `python weather_delay.py --mock`, which swaps only the HTTP call for
  `fixtures/mock_weather.json` (New York = Rain, London = Snow). It shows the
  `Rain/Snow/Extreme -> Delayed` branch and two Weather-Aware Apologies.
  **Re-run `python weather_delay.py` before submitting** to regenerate this from
  the live API - if any real city has bad weather that day it will show a
  genuine `Delayed`.
- **`orders.live.json`** - a real OpenWeatherMap run. Proves the live API
  integration and that `InvalidCity123` is caught and logged while the other
  three cities finish. On a clear-weather day every valid city is `Processing`;
  that is the honest live output, and `updated_orders.json` demonstrates the
  delay logic that the weather didn't trigger.

All logic (concurrency, error handling, classification, file writing) is
identical on the live and `--mock` paths - only the weather source differs.

## Demo recording script (2-3 min)

1. Show `.env.example`; the real key lives in `.env` (git-ignored).
2. `pytest -q` -> **7 passed**. Call out `tests/test_concurrency.py` - it runs
   the real `gather_weather` path with fake delays and proves the batch is
   concurrent, not sequential.
3. `python weather_delay.py` (LIVE API, writes `orders.live.json`... actually
   `updated_orders.json` by default - use `--output orders.live.json` if you
   want to keep the mock copy):
   - all four `-> requesting ...` lines print before any `<- got ...` line =
     concurrent (`asyncio.gather`), plus the "Fetched 4 cities concurrently in
     X.XXs" timing line.
   - `WARNING SKIP order 1004` = `InvalidCity123` handled, the run still
     completes and writes output.
4. `python weather_delay.py --mock` -> SUMMARY shows 2 `Delayed`, 1 error
   handled, and the two apology messages. `cat updated_orders.json`.
5. Open `weather_delay.py` and point at `is_delivery_delay()` -
   `{"Rain", "Snow", "Extreme"}`, exactly the brief.
6. Show `AI_LOG.md`.

## Push to GitHub

Already at https://github.com/Shaurya55555/yellowai-golden-flow (branch `main`).
