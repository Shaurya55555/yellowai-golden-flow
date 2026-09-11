"""Proves the weather fetches run concurrently, through the real gather path.

The point is concurrent-vs-sequential behaviour, not benchmarking: with 4 fake
fetchers each sleeping 0.3s, a sequential run would take ~1.2s and a concurrent
one ~0.3s, so the threshold sits comfortably between the two.
"""

import asyncio
import time

from weather_delay import gather_weather

FAKE_DELAY = 0.3
N = 4


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

    # sequential would be N * FAKE_DELAY = 1.2s; concurrent is ~FAKE_DELAY
    assert elapsed < 0.8, f"took {elapsed:.2f}s - looks sequential, not concurrent"

    # gather preserves order and returns one result per order
    assert len(results) == N
    assert [r["order"]["order_id"] for r in results] == [o["order_id"] for o in orders]
    assert all(r["error"] is None for r in results)
