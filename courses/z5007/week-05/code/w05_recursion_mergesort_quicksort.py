"""Week 05 Reference Module: Recursion, Merge Sort, Inversions, Quicksort, and Quickselect."""

from __future__ import annotations

import random


def merge_sort_and_count(arr: list[int]) -> tuple[list[int], int]:
    """Return (sorted_copy, inversion_count) in O(n log n) time."""
    if len(arr) <= 1:
        return arr[:], 0
    mid = len(arr) // 2
    left, inv_l = merge_sort_and_count(arr[:mid])
    right, inv_r = merge_sort_and_count(arr[mid:])
    merged: list[int] = []
    i = j = 0
    invs = inv_l + inv_r
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            invs += len(left) - i
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, invs


def _partition_hoare_random(arr: list[int], lo: int, hi: int, rng: random.Random) -> int:
    pivot_idx = rng.randint(lo, hi)
    pivot = arr[pivot_idx]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        j -= 1
        while arr[j] > pivot:
            j -= 1
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]


def quicksort(arr: list[int], seed: int = 0) -> None:
    """In-place randomized Hoare Quicksort."""
    rng = random.Random(seed)

    def _sort(lo: int, hi: int) -> None:
        if lo < hi:
            p = _partition_hoare_random(arr, lo, hi, rng)
            _sort(lo, p)
            _sort(p + 1, hi)

    _sort(0, len(arr) - 1)


def quickselect(arr: list[int], k: int, seed: int = 0) -> int:
    """Return the k-th smallest element (0-indexed) in expected O(n) time."""
    if not 0 <= k < len(arr):
        raise IndexError("k out of range")
    a = arr[:]
    rng = random.Random(seed)
    lo, hi = 0, len(a) - 1
    while lo < hi:
        p = rng.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot = a[hi]
        store = lo
        for i in range(lo, hi):
            if a[i] < pivot:
                a[store], a[i] = a[i], a[store]
                store += 1
        a[store], a[hi] = a[hi], a[store]
        if store == k:
            return a[store]
        if k < store:
            hi = store - 1
        else:
            lo = store + 1
    return a[lo]


def run_tests() -> None:
    rng = random.Random(5007)
    for _ in range(100):
        xs = [rng.randint(-100, 100) for _ in range(40)]
        sorted_xs, inv = merge_sort_and_count(xs)
        assert sorted_xs == sorted(xs)
        brute_inv = sum(1 for i in range(len(xs)) for j in range(i + 1, len(xs)) if xs[i] > xs[j])
        assert inv == brute_inv

        qs = xs[:]
        quicksort(qs, seed=7)
        assert qs == sorted(xs)

        k = rng.randrange(len(xs))
        assert quickselect(xs, k, seed=7) == sorted(xs)[k]
    print("W05 self-tests passed.")


if __name__ == "__main__":
    run_tests()
