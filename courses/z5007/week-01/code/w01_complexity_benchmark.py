"""Week 01 Reference Module: Empirical Complexity and Big-O Benchmarking.

Implements step-counted and wall-clock benchmarks across O(1), O(log n), O(n),
O(n log n), and O(n^2) growth regimes, plus Python list vs. set lookup scaling.
"""

from __future__ import annotations

import math
import random
import time
from typing import Callable


def constant_lookup(arr: list[int], index: int) -> tuple[int, int]:
    """Return (arr[index], step_count) in O(1) time."""
    if not 0 <= index < len(arr):
        raise IndexError("index out of range")
    return arr[index], 1


def binary_search_counted(sorted_arr: list[int], target: int) -> tuple[int, int]:
    """Return (index_or_minus_one, comparisons) in O(log n) time."""
    lo, hi = 0, len(sorted_arr) - 1
    steps = 0
    while lo <= hi:
        steps += 1
        mid = (lo + hi) // 2
        if sorted_arr[mid] == target:
            return mid, steps
        if sorted_arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps


def linear_max_counted(arr: list[int]) -> tuple[int, int]:
    """Return (max_value, comparisons) in O(n) time."""
    if not arr:
        raise ValueError("array must be non-empty")
    best = arr[0]
    steps = 0
    for val in arr[1:]:
        steps += 1
        if val > best:
            best = val
    return best, steps


def mergesort_counted(arr: list[int]) -> tuple[list[int], int]:
    """Sort a copy of arr using Merge Sort and count key comparisons in O(n log n)."""
    if len(arr) <= 1:
        return arr[:], 0
    mid = len(arr) // 2
    left, c_left = mergesort_counted(arr[:mid])
    right, c_right = mergesort_counted(arr[mid:])
    merged: list[int] = []
    i = j = 0
    comps = c_left + c_right
    while i < len(left) and j < len(right):
        comps += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, comps


def count_inversions_quadratic(arr: list[int]) -> tuple[int, int]:
    """Count pairs i < j with arr[i] > arr[j] in O(n^2) time."""
    n = len(arr)
    inversions = 0
    steps = 0
    for i in range(n):
        for j in range(i + 1, n):
            steps += 1
            if arr[i] > arr[j]:
                inversions += 1
    return inversions, steps


def estimate_log_log_slope(sizes: list[int], times_sec: list[float]) -> float:
    """Estimate empirical exponent b in T(n) ~ c * n^b via least squares in log-log space."""
    xs = [math.log(n) for n in sizes]
    ys = [math.log(max(t, 1e-12)) for t in times_sec]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den > 0 else 0.0


def time_call(fn: Callable[[], object], repeats: int = 3) -> float:
    """Return median wall-clock duration in seconds across repeats."""
    durations: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - t0)
    durations.sort()
    return durations[len(durations) // 2]


def run_tests() -> None:
    """Run unit assertions and scaling checks."""
    arr = [10, 20, 30, 40, 50]
    assert constant_lookup(arr, 3) == (40, 1)
    idx, steps = binary_search_counted(list(range(1024)), 777)
    assert idx == 777 and steps <= 11
    assert binary_search_counted(arr, 99)[0] == -1
    assert linear_max_counted([3, 19, 7, 2])[0] == 19

    rng = random.Random(42)
    sample = [rng.randint(0, 1000) for _ in range(200)]
    sorted_sample, comps = mergesort_counted(sample)
    assert sorted_sample == sorted(sample)
    assert comps <= 200 * math.ceil(math.log2(200))

    inv, qsteps = count_inversions_quadratic([4, 3, 2, 1])
    assert inv == 6 and qsteps == 6

    # Empirical log-log slope check for quadratic inversion counter
    sizes = [150, 300, 600, 1200]
    timings = []
    for n in sizes:
        data = [rng.randint(0, 10000) for _ in range(n)]
        timings.append(time_call(lambda d=data: count_inversions_quadratic(d), repeats=3))
    slope = estimate_log_log_slope(sizes, timings)
    assert 1.6 <= slope <= 2.4, f"Expected quadratic slope near 2.0, got {slope:.2f}"
    print(f"W01 self-tests passed (quadratic log-log slope = {slope:.2f}).")


if __name__ == "__main__":
    run_tests()
