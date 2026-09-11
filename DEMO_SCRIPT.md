# Assignment 2 demo recording script

Target: 2:00-2:30. Start your recorder, open a terminal in
`D:\Projects\yellowai-golden-flow`, and follow this top to bottom. Lines in
`>` are what you say; commands are what you type.

---

### 0:00-0:15 - Intro

> "This is the Golden Flow assignment: check weather for each order concurrently,
> flag delivery delays, write a personalised apology, and never crash on a bad
> city."

```bash
cat orders.json
```

> "These are the four required orders - New York, Mumbai, London, and the
> deliberately invalid `InvalidCity123` - straight from the brief."

---

### 0:15-0:40 - Code, 15 seconds on the two things that matter most

Open `weather_delay.py` in your editor. Scroll to `gather_weather`:

```python
async def gather_weather(orders, api_key, fetcher):
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(
            *(process_order(client, order, api_key, fetcher) for order in orders)
        )
```

> "One shared client, one `asyncio.gather` - every city is requested at the same
> time, not in a loop."

Scroll to `is_delivery_delay`:

```python
def is_delivery_delay(weather_main):
    return weather_main in DELAY_CONDITIONS   # {"Rain", "Snow", "Extreme"}
```

> "The delay rule, exactly the three conditions the brief names."

---

### 0:40-0:55 - Tests

```bash
pytest -q
```

> "Seven tests. One of them - `test_concurrency` - runs this exact `gather_weather`
> function with fake delays and proves the batch finishes in a fraction of what
> a sequential run would take, not just that `asyncio.gather` exists somewhere
> in the file."

Expected output: `7 passed`.

---

### 0:55-1:35 - Live run

```bash
python weather_delay.py
```

While it runs, narrate over the log lines:

> "Watch the order: all four `-> requesting` lines print before any `<- got`
> line comes back - that's the four calls genuinely overlapping in flight."

Point at:
```
WARNING  SKIP  order 1004: OpenWeatherMap does not recognise city 'InvalidCity123'
```
> "The invalid city fails, gets logged, and the run keeps going - it doesn't
> abort the other three."

Point at the timing line:
```
INFO     Fetched 4 cities concurrently in 0.8Xs
```
> "About one request's worth of time for four cities."

```bash
cat orders.json
```

**If any city shows `"status": "Delayed"`:**
> "Real weather flagged this order and generated a real apology - `[read the
> apology line aloud]`."

**If nothing is Delayed this run** (weather can go either way):
> "Right now all three cities have clear weather, so nothing's flagged - that's
> expected and honest, it's live data. The logic itself is proven next."

---

### 1:35-2:05 - Deterministic proof of the Delayed branch

```bash
python weather_delay.py --mock --output orders.mock.result.json
```

> "This swaps only the HTTP call for a fixed fixture - New York gets rain,
> London gets snow - so the Delayed branch and the apology function are proven
> regardless of what the sky is doing right now."

```bash
cat orders.mock.result.json
```

> "Two orders delayed, two personalised apologies, `InvalidCity123` still
> handled the same way. Same concurrency, same error handling, same code path -
> only the weather source changed."

---

### 2:05-2:25 - AI Log and wrap

```bash
cat AI_LOG.md
```

> "The AI Log - the actual prompts I used to design the concurrent-fetching and
> error-handling logic, plus the apology function. The apology itself is
> deterministic at runtime, no extra API key or quota, so it's fully
> reproducible and unit-tested - that's a deliberate choice, explained in the
> log."

> "The key comes from a `.env` file, never hardcoded - it's git-ignored, and
> httpx's own logging is silenced so it never leaks into these logs either."

Stop recording.

---

## Pre-flight checklist (do before hitting record)

- [ ] `python weather_delay.py` once, fresh, so `orders.json` reflects current weather
- [ ] `.env` has your real `OPENWEATHER_API_KEY` (check with `cat .env.example` to remember the var name, don't `cat .env` on camera)
- [ ] Terminal font large enough to read on screen
- [ ] `AI_LOG.md` and `weather_delay.py` open in tabs, ready to switch to
