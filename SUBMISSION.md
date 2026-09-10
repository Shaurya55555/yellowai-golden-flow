# Assignment 2 - Submission Checklist

| Deliverable | File / action | Status |
| --- | --- | --- |
| Source code | this repo (`weather_delay.py`, `apology.py`, `test_logic.py`) | done |
| Updated `orders.json` | `orders.json` (live API run) + `orders.mock.result.json` (Delayed path) | done (see note) |
| "AI Log" with the prompts used | `AI_LOG.md` | done |
| Demo recording | steps below | to record |

## Note on `orders.json` - live run vs the `Delayed` path

Two result files are committed:

- **`orders.json`** - produced by a real `python weather_delay.py` run against
  the live OpenWeatherMap API. At run time New York / Mumbai / London all had
  Clear or Clouds weather, so no order legitimately flipped to `Delayed`; every
  valid city shows its real `weather` / `weather_description`, and
  `InvalidCity123` is caught and marked with `weather_error` while the run
  finishes normally. This is the honest current-weather output.

- **`orders.mock.result.json`** - produced by `python weather_delay.py --mock`,
  which swaps only the HTTP call for `fixtures/mock_weather.json`
  (New York = Rain, London = Snow). This exercises the `Rain/Snow/Extreme ->
  Delayed` branch and the Weather-Aware Apology function, which the live run
  couldn't show because the weather simply wasn't bad. All other logic
  (concurrency, error handling, file writing) is identical on both paths.

`orders.seed.json` is the untouched input. Regenerate the live file any time with:

```bash
cp orders.seed.json orders.json && python weather_delay.py
```

## Demo recording script (2-3 min)

1. Show `.env.example` and mention the real key lives in `.env` (git-ignored).
2. `pytest -q`  -> 5 passing logic tests, no network.
3. `cp orders.seed.json orders.json && python weather_delay.py`  (LIVE API)
   - all four `-> requesting ...` lines print before any `<- got ...` line =
     the calls run concurrently (`asyncio.gather`).
   - `WARNING SKIP order 1004` = `InvalidCity123` handled, run continues.
   - `cat orders.json` -> real weather per city, `weather_error` on 1004.
4. `python weather_delay.py --mock`  (forces Rain/Snow to show the Golden Flow)
   - SUMMARY: 2 Delayed, 1 error handled, plus the two apology messages.
   - `cat orders.mock.result.json` isn't needed; the run writes `orders.json`.
     Use `--output orders.mock.result.json` if you want to keep both side by side.

## Push to GitHub

```bash
git remote add origin https://github.com/Shaurya55555/yellowai-golden-flow.git
git branch -M main
git push -u origin main
```
