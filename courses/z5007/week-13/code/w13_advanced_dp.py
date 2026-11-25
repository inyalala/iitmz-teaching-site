"""Week 13 Reference Module: Advanced Dynamic Programming (MCM, LIS O(n log n), Rod Cutting, Bitmask TSP)."""

from __future__ import annotations

import bisect
import math


def matrix_chain_order(dims: list[int]) -> tuple[int, str]:
    """Return (min_scalar_multiplications, optimal_parenthesization) for matrix chain dims."""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = math.inf  # type: ignore[assignment]
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k

    def _fmt(i: int, j: int) -> str:
        if i == j:
            return f"A{i + 1}"
        k = split[i][j]
        return f"({_fmt(i, k)} x {_fmt(k + 1, j)})"

    return int(dp[0][n - 1]), _fmt(0, n - 1)


def lis_nlogn(seq: list[int]) -> int:
    """Compute Longest Increasing Subsequence length in O(n log n) using patience tails."""
    tails: list[int] = []
    for x in seq:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)


def rod_cutting(prices: list[int], length: int) -> tuple[int, list[int]]:
    """Return (max_revenue, cut_lengths) for rod of given length; prices[i] is price for length i+1."""
    dp = [0] * (length + 1)
    first_cut = [0] * (length + 1)
    for j in range(1, length + 1):
        best = -1
        for i in range(1, min(j, len(prices)) + 1):
            cand = prices[i - 1] + dp[j - i]
            if cand > best:
                best = cand
                first_cut[j] = i
        dp[j] = best
    cuts: list[int] = []
    rem = length
    while rem > 0:
        cuts.append(first_cut[rem])
        rem -= first_cut[rem]
    return dp[length], cuts


def held_karp_tsp(dist: list[list[float]]) -> float:
    """Exact bitmask DP Traveling Salesperson tour cost starting/ending at vertex 0 in O(n^2 2^n)."""
    n = len(dist)
    full = 1 << n
    dp = [[math.inf] * n for _ in range(full)]
    dp[1][0] = 0.0
    for mask in range(1, full):
        if not (mask & 1):
            continue
        for u in range(n):
            if dp[mask][u] == math.inf:
                continue
            for v in range(1, n):
                if not (mask & (1 << v)):
                    nxt = mask | (1 << v)
                    cand = dp[mask][u] + dist[u][v]
                    if cand < dp[nxt][v]:
                        dp[nxt][v] = cand
    return min(dp[full - 1][u] + dist[u][0] for u in range(1, n))


def run_tests() -> None:
    cost, parens = matrix_chain_order([30, 35, 15, 5, 10, 20, 25])
    assert cost == 15125 and "A1" in parens
    assert lis_nlogn([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    rev, cuts = rod_cutting([1, 5, 8, 9, 10, 17, 17, 20], 8)
    assert rev == 22 and sum(cuts) == 8
    tsp_cost = held_karp_tsp([[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]])
    assert tsp_cost == 80.0
    print(f"W13 self-tests passed (MCM cost={cost}, LIS=4, Held-Karp TSP={tsp_cost:.0f}).")


if __name__ == "__main__":
    run_tests()
