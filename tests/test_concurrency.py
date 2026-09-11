"""Proves the weather fetches run concurrently, through the real gather path.

The point is concurrent-vs-sequential behaviour, not benchmarking. With N fake
fetchers each sleeping FAKE_DELAY, a sequential run takes N * FAKE_DELAY; a
concurrent one takes ~FAKE_DELAY plus event-loop / client overhead. The
threshold sits at half the sequential time, which no amount of machine jitter
turns a genuinely sequential run into.
"""

import asyncio
import time

from weather_delay import gather_weather

FAKE_DELAY = 0.5
N = 6


async def _slow_fetcher(client, city, api_key):
    await asyncio.sleep(FAKE_DELAY)
    return {"city": city, "main": "Clear", "description": "clear sky", "temp_c": 20.0}


def test_orders_are_fetched_concurrently():
    orders = [
        {"order_id": str(1000 + i), "customer": "Test User", "city": f"City{i}", "status": "Pending"}
        for i in range(N)
    ]

    start = time.perf_counter()
    results = asyncio.run(gather_weather(orders, "dummy-key", _slow_fetcher))
    elapsed = time.perf_counter() - start

    sequential = N * FAKE_DELAY  # 3.0s
    assert elapsed < sequential * 0.5, (
        f"took {elapsed:.2f}s vs sequential {sequential:.2f}s - not concurrent"
    )

    # gather preserves order and returns one result per order
    assert len(results) == N
    assert [r.order["order_id"] for r in results] == [o["order_id"] for o in orders]
    assert all(r.ok and r.error is None for r in results)
