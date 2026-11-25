"""Week 02 Reference Module: Static Arrays, Binary Search, Dynamic Arrays, and Simple Sorts."""

from __future__ import annotations

import random
from typing import Any, Optional


class StaticArray:
    """Fixed-capacity contiguous slot array supporting O(1) indexed access and O(n) shift edits."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._data: list[Any] = [None] * capacity
        self._size = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Any:
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        return self._data[index]

    def set(self, index: int, value: Any) -> None:
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        self._data[index] = value

    def insert(self, index: int, value: Any) -> None:
        if self._size == len(self._data):
            raise OverflowError("static array is full")
        if not 0 <= index <= self._size:
            raise IndexError("index out of range")
        for j in range(self._size, index, -1):
            self._data[j] = self._data[j - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index: int) -> Any:
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        removed = self._data[index]
        for j in range(index, self._size - 1):
            self._data[j] = self._data[j + 1]
        self._data[self._size - 1] = None
        self._size -= 1
        return removed


class DynamicArray:
    """Resizable array with geometric doubling on growth and halving at 1/4 occupancy."""

    def __init__(self, initial_capacity: int = 2) -> None:
        if initial_capacity <= 0:
            raise ValueError("initial_capacity must be positive")
        self._data: list[Any] = [None] * initial_capacity
        self._size = 0
        self.resize_events = 0
        self.total_copies = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)

    def _resize(self, new_cap: int) -> None:
        new_block: list[Any] = [None] * new_cap
        for i in range(self._size):
            new_block[i] = self._data[i]
            self.total_copies += 1
        self._data = new_block
        self.resize_events += 1

    def append(self, value: Any) -> None:
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        self._data[self._size] = value
        self._size += 1

    def pop(self) -> Any:
        if self._size == 0:
            raise IndexError("pop from empty DynamicArray")
        val = self._data[self._size - 1]
        self._data[self._size - 1] = None
        self._size -= 1
        if 0 < self._size <= len(self._data) // 4 and len(self._data) > 2:
            self._resize(len(self._data) // 2)
        return val

    def to_list(self) -> list[Any]:
        return [self._data[i] for i in range(self._size)]


def binary_search(arr: list[int], target: int) -> int:
    """Return index of target in sorted arr, or -1 if absent."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(arr: list[int], target: int) -> int:
    """Return first index i such that arr[i] >= target (or len(arr))."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def bubble_sort(arr: list[int]) -> tuple[int, int]:
    """In-place stable Bubble Sort returning (comparisons, swaps)."""
    n = len(arr)
    comps = swaps = 0
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            comps += 1
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return comps, swaps


def selection_sort(arr: list[int]) -> tuple[int, int]:
    """In-place Selection Sort returning (comparisons, swaps)."""
    n = len(arr)
    comps = swaps = 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comps += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
    return comps, swaps


def run_tests() -> None:
    sa = StaticArray(4)
    sa.insert(0, 10)
    sa.insert(1, 30)
    sa.insert(1, 20)
    assert [sa.get(i) for i in range(len(sa))] == [10, 20, 30]
    assert sa.delete(1) == 20 and len(sa) == 2

    da = DynamicArray(2)
    for k in range(100):
        da.append(k)
    assert da.to_list() == list(range(100))
    # Geometric doubling copies fewer than 2n elements total
    assert da.total_copies < 2 * 100
    for _ in range(90):
        da.pop()
    assert da.capacity <= 32

    sorted_vals = [2, 4, 4, 4, 9, 15]
    assert binary_search(sorted_vals, 9) == 4
    assert lower_bound(sorted_vals, 4) == 1
    assert lower_bound(sorted_vals, 5) == 4

    rng = random.Random(2026)
    for _ in range(100):
        xs = [rng.randint(0, 50) for _ in range(30)]
        a, b = xs[:], xs[:]
        bubble_sort(a)
        selection_sort(b)
        assert a == sorted(xs) and b == sorted(xs)
    assert bubble_sort([1, 2, 3, 4, 5]) == (4, 0)
    assert selection_sort(list(range(10, 0, -1)))[0] == 45
    print("W02 self-tests passed.")


if __name__ == "__main__":
    run_tests()
