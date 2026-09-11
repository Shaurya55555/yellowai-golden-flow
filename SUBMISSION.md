# Assignment 2 - Submission Checklist

| Deliverable | File / action | Status |
| --- | --- | --- |
| Source code | this repo (`weather_delay.py`, `apology.py`, `tests/`) | done |
| The updated `orders.json` (showing which orders were marked as Delayed) | `orders.json` - the brief's exact wording, taken literally: input and output are the same file | done (see note) |
| "AI Log" with the prompts used | `AI_LOG.md` | done |
| Demo recording | script below | to record |

## Note on the order files

The brief says *"Save as `orders.json`"* and asks for *"the updated `orders.json`
(showing which orders were marked as Delayed)"* - read literally, that means one
file, updated in place. So:

- **`orders.json`** - the exact assignment input, **and**, after a run, the
  required deliverable. `python weather_delay.py` (no `--output`) writes it in
  place. Which orders are `Delayed` in the committed copy depends on the real
  weather at the last live run - **re-run right before submitting** for a fresh
  capture.
- **`orders.seed.json`** - a pristine backup of the original 4 `Pending`
  orders. Reset with `cp orders.seed.json orders.json`.
- **`orders.live.json`** - a preserved snapshot of a live run, so there is
  always a live-API artifact even if `orders.json` later gets overwritten by a
  test or mock run.
- **`orders.mock.result.json`** - a `--mock` run against
  `fixtures/mock_weather.json` (New York = Rain, London = Snow). Deterministic,
  weather-independent proof that the `Rain/Snow/Extreme -> Delayed` branch and
  the apology function work, regardless of what the sky is doing on submission
  day. **If the live `orders.json` shows zero `Delayed` orders at submission
  time** (possible - real weather is not guaranteed to cooperate), point to
  this file as the proof the logic works, alongside the honest live capture.

All logic (concurrency, error handling, classification, file writing) is
identical on the live and `--mock` paths - only the weather source differs.

## Demo recording script (2-3 min)

1. Show `.env.example`; the real key lives in `.env` (git-ignored).
2. `pytest -q` -> **7 passed**. Call out `tests/test_concurrency.py` - it runs
   the real `gather_weather` path with fake delays and proves the batch is
   concurrent, not sequential.
3. `python weather_delay.py` (LIVE API, updates `orders.json` in place):
   - all four `-> requesting ...` lines print before any `<- got ...` line =
     concurrent (`asyncio.gather`), plus the "Fetched 4 cities concurrently in
     X.XXs" timing line.
   - `WARNING SKIP order 1004` = `InvalidCity123` handled, the run still
     completes and writes output.
   - `cat orders.json` -> real weather per city; any `Rain/Snow/Extreme` city is
     `Delayed` with an apology. If nothing is `Delayed` this run, say so plainly
     and move to step 4.
4. `python weather_delay.py --mock --output orders.mock.result.json` -> SUMMARY
   shows 2 `Delayed` (New York, London), 1 error handled, and the two apology
   messages - the deterministic proof of the branch.
5. Open `weather_delay.py` and point at `is_delivery_delay()` -
   `{"Rain", "Snow", "Extreme"}`, exactly the brief.
6. Show `AI_LOG.md`.

## Push to GitHub

Already at https://github.com/Shaurya55555/yellowai-golden-flow (branch `main`).
