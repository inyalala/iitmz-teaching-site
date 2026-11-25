"""Week 17 Reference Module: Capstone Synthesis & Randomized/Parallel Algorithm Patterns."""

from __future__ import annotations

import heapq
import math
import random


def monte_carlo_pi(samples: int, seed: int = 5007) -> float:
    """Estimate pi via randomized dart throwing in [0, 1]^2."""
    rng = random.Random(seed)
    inside = 0
    for _ in range(samples):
        x, y = rng.random(), rng.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return 4.0 * inside / samples


def parallel_prefix_sum(arr: list[int]) -> list[int]:
    """Blelloch-style work-efficient scan illustration (up-sweep + down-sweep on power-of-2 length)."""
    n = 1
    while n < len(arr):
        n *= 2
    buf = arr[:] + [0] * (n - len(arr))
    # Up-sweep (reduce)
    step = 1
    while step < n:
        for i in range(0, n, 2 * step):
            buf[i + 2 * step - 1] += buf[i + step - 1]
        step *= 2
    # Down-sweep (exclusive scan -> convert to inclusive by shifting)
    total = buf[n - 1]
    buf[n - 1] = 0
    step //= 2
    while step >= 1:
        for i in range(0, n, 2 * step):
            t = buf[i + step - 1]
            buf[i + step - 1] = buf[i + 2 * step - 1]
            buf[i + 2 * step - 1] += t
        step //= 2
    inclusive = [buf[i + 1] for i in range(len(arr) - 1)] + ([total] if arr else [])
    return inclusive[: len(arr)]


def zanzibar_dispatch_pipeline(
    roads: dict[str, list[tuple[str, float]]],
    cargo_items: list[tuple[str, int, int]],
    truck_capacity: int,
    depot: str,
    destination: str,
) -> tuple[float, int, list[str]]:
    """End-to-end synthesis: Dijkstra shortest route + 0/1 Knapsack cargo selection."""
    dist = {u: math.inf for u in roads}
    dist[depot] = 0.0
    pq: list[tuple[float, str]] = [(0.0, depot)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in roads[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))

    n = len(cargo_items)
    dp = [[0] * (truck_capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        _, val, wt = cargo_items[i - 1]
        for w in range(truck_capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if wt <= w and dp[i - 1][w - wt] + val > dp[i][w]:
                dp[i][w] = dp[i - 1][w - wt] + val
    chosen: list[str] = []
    w = truck_capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(cargo_items[i - 1][0])
            w -= cargo_items[i - 1][2]
    chosen.reverse()
    return dist[destination], dp[n][truck_capacity], chosen


def run_tests() -> None:
    pi_est = monte_carlo_pi(20_000)
    assert abs(pi_est - math.pi) < 0.05

    arr = [3, 1, 4, 1, 5, 9, 2]
    ps = parallel_prefix_sum(arr)
    expected = [sum(arr[: i + 1]) for i in range(len(arr))]
    assert ps == expected

    roads = {
        "StoneTown": [("Mbweni", 6.0), ("Fumba", 18.0)],
        "Mbweni": [("Bweleo", 11.0)],
        "Fumba": [("Bweleo", 5.0)],
        "Bweleo": [],
    }
    cargo = [("Cloves", 180, 20), ("Seedlings", 120, 15), ("Sensors", 210, 25)]
    route_km, cargo_val, picked = zanzibar_dispatch_pipeline(roads, cargo, 40, "StoneTown", "Bweleo")
    assert route_km == 17.0 and cargo_val == 330 and picked == ["Seedlings", "Sensors"]
    print(f"W17 self-tests passed (pi_est={pi_est:.4f}, dispatch route={route_km:.0f} km, cargo={cargo_val}).")


if __name__ == "__main__":
    run_tests()
