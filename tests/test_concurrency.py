"""Proves the weather fetches run concurrently, through the real gather path.

The point is concurrent-vs-sequential behaviour, not benchmarking. With 8 fake
fetchers each sleeping 0.6s, a sequential run takes 4.8s; a concurrent one takes
~0.6s plus event-loop / httpx client overhead (well under a second on a normal
machine). The threshold sits at half the sequential time - a genuinely
sequential run can never come in under that no matter the machine jitter.
"""

import asyncio
import time

from weather_delay import gather_weather

FAKE_DELAY = 0.6
N = 8


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

    sequential = N * FAKE_DELAY  # 4.8s
    assert elapsed < sequential * 0.5, (
        f"took {elapsed:.2f}s vs {sequential:.2f}s sequential - not concurrent"
    )

    # gather preserves order and returns one result per order
    assert len(results) == N
    assert [r.order["order_id"] for r in results] == [o["order_id"] for o in orders]
    assert all(r.ok and r.error is None for r in results)
