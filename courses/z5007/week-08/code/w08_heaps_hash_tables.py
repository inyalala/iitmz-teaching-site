"""Week 08 Reference Module: Max-Heaps, Priority Queues, and Hash Tables (Chaining vs. Linear Probing)."""

from __future__ import annotations

import random
from typing import Any, Optional


class MaxHeap:
    """Array-backed binary max-heap with O(n) Floyd heapify and O(log n) push/pop."""

    def __init__(self, items: Optional[list[Any]] = None) -> None:
        self._a: list[Any] = list(items) if items else []
        if len(self._a) > 1:
            for i in range(len(self._a) // 2 - 1, -1, -1):
                self._sift_down(i)

    def __len__(self) -> int:
        return len(self._a)

    def peek(self) -> Any:
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def push(self, val: Any) -> None:
        self._a.append(val)
        self._sift_up(len(self._a) - 1)

    def pop(self) -> Any:
        if not self._a:
            raise IndexError("pop from empty heap")
        top = self._a[0]
        last = self._a.pop()
        if self._a:
            self._a[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self._a[idx] > self._a[parent]:
                self._a[idx], self._a[parent] = self._a[parent], self._a[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self._a)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest = idx
            if left < n and self._a[left] > self._a[largest]:
                largest = left
            if right < n and self._a[right] > self._a[largest]:
                largest = right
            if largest == idx:
                break
            self._a[idx], self._a[largest] = self._a[largest], self._a[idx]
            idx = largest


def heapsort(items: list[Any]) -> list[Any]:
    """Return ascending sorted list using MaxHeap extraction."""
    h = MaxHeap(items)
    out = [None] * len(h)
    for i in range(len(h) - 1, -1, -1):
        out[i] = h.pop()
    return out


class ChainingHashTable:
    """Hash table resolving collisions via per-bucket linked lists (Python lists) and dynamic rehashing."""

    def __init__(self, capacity: int = 8) -> None:
        self._buckets: list[list[tuple[Any, Any]]] = [[] for _ in range(capacity)]
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def load_factor(self) -> float:
        return self._size / len(self._buckets)

    def _rehash(self, new_cap: int) -> None:
        items = [kv for b in self._buckets for kv in b]
        self._buckets = [[] for _ in range(new_cap)]
        self._size = 0
        for k, v in items:
            self.put(k, v)

    def put(self, key: Any, value: Any) -> int:
        if self.load_factor() >= 0.75:
            self._rehash(2 * len(self._buckets))
        idx = hash(key) % len(self._buckets)
        bucket = self._buckets[idx]
        probes = 1
        for i, (k, _) in enumerate(bucket):
            probes += 1
            if k == key:
                bucket[i] = (key, value)
                return probes
        bucket.append((key, value))
        self._size += 1
        return probes

    def get(self, key: Any) -> tuple[Optional[Any], int]:
        idx = hash(key) % len(self._buckets)
        probes = 0
        for k, v in self._buckets[idx]:
            probes += 1
            if k == key:
                return v, probes
        return None, max(1, probes)

    def delete(self, key: Any) -> bool:
        idx = hash(key) % len(self._buckets)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return True
        return False


_TOMBSTONE = object()


class LinearProbingHashTable:
    """Open-addressing hash table with linear probing and tombstone deletion."""

    def __init__(self, capacity: int = 8) -> None:
        self._keys: list[Any] = [None] * capacity
        self._vals: list[Any] = [None] * capacity
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def load_factor(self) -> float:
        return self._size / len(self._keys)

    def _rehash(self, new_cap: int) -> None:
        old_k, old_v = self._keys, self._vals
        self._keys = [None] * new_cap
        self._vals = [None] * new_cap
        self._size = 0
        for k, v in zip(old_k, old_v):
            if k is not None and k is not _TOMBSTONE:
                self.put(k, v)

    def put(self, key: Any, value: Any) -> int:
        if self.load_factor() >= 0.65:
            self._rehash(2 * len(self._keys))
        cap = len(self._keys)
        idx = hash(key) % cap
        first_tomb = -1
        probes = 0
        while True:
            probes += 1
            cur = self._keys[idx]
            if cur is None:
                target = first_tomb if first_tomb != -1 else idx
                self._keys[target] = key
                self._vals[target] = value
                self._size += 1
                return probes
            if cur is _TOMBSTONE:
                if first_tomb == -1:
                    first_tomb = idx
            elif cur == key:
                self._vals[idx] = value
                return probes
            idx = (idx + 1) % cap

    def get(self, key: Any) -> tuple[Optional[Any], int]:
        cap = len(self._keys)
        idx = hash(key) % cap
        probes = 0
        while probes < cap:
            probes += 1
            cur = self._keys[idx]
            if cur is None:
                return None, probes
            if cur is not _TOMBSTONE and cur == key:
                return self._vals[idx], probes
            idx = (idx + 1) % cap
        return None, probes

    def delete(self, key: Any) -> bool:
        cap = len(self._keys)
        idx = hash(key) % cap
        steps = 0
        while steps < cap:
            cur = self._keys[idx]
            if cur is None:
                return False
            if cur is not _TOMBSTONE and cur == key:
                self._keys[idx] = _TOMBSTONE
                self._vals[idx] = None
                self._size -= 1
                return True
            idx = (idx + 1) % cap
            steps += 1
        return False


def run_tests() -> None:
    rng = random.Random(8)
    data = [rng.randint(0, 500) for _ in range(100)]
    assert heapsort(data) == sorted(data)

    h = MaxHeap()
    for x in (10, 40, 20, 5, 60):
        h.push(x)
    assert [h.pop() for _ in range(5)] == [60, 40, 20, 10, 5]

    for tbl in (ChainingHashTable(), LinearProbingHashTable()):
        ref: dict[str, int] = {}
        for i in range(150):
            k = f"farm_{i}"
            tbl.put(k, i * 10)
            ref[k] = i * 10
        for i in range(0, 150, 3):
            k = f"farm_{i}"
            assert tbl.delete(k)
            del ref[k]
        for k, v in ref.items():
            got, _ = tbl.get(k)
            assert got == v
        assert tbl.get("farm_0")[0] is None
    print("W08 self-tests passed.")


if __name__ == "__main__":
    run_tests()
