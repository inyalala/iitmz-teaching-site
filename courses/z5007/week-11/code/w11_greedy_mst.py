"""Week 11 Reference Module: Greedy Algorithms, Disjoint Set Union, Kruskal MST, and Prim MST."""

from __future__ import annotations

import heapq
import random
from typing import Hashable


class DisjointSet:
    """Union-Find with path compression and union by rank."""

    def __init__(self, items: list[Hashable]) -> None:
        self.parent: dict[Hashable, Hashable] = {x: x for x in items}
        self.rank: dict[Hashable, int] = {x: 0 for x in items}

    def find(self, x: Hashable) -> Hashable:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: Hashable, b: Hashable) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal_mst(
    vertices: list[Hashable],
    edges: list[tuple[Hashable, Hashable, float]],
) -> tuple[float, list[tuple[Hashable, Hashable, float]]]:
    """Build a Minimum Spanning Tree in O(E log E) using sorted edges + DSU."""
    dsu = DisjointSet(vertices)
    mst: list[tuple[Hashable, Hashable, float]] = []
    total = 0.0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if dsu.union(u, v):
            mst.append((u, v, w))
            total += w
            if len(mst) == len(vertices) - 1:
                break
    return total, mst


def prim_mst(
    adj: dict[Hashable, list[tuple[Hashable, float]]],
    start: Hashable,
) -> tuple[float, list[tuple[Hashable, Hashable, float]]]:
    """Build a Minimum Spanning Tree in O((V + E) log V) via a priority queue."""
    visited: set[Hashable] = {start}
    pq: list[tuple[float, int, Hashable, Hashable]] = []
    counter = 0
    for v, w in adj[start]:
        counter += 1
        heapq.heappush(pq, (w, counter, start, v))
    mst: list[tuple[Hashable, Hashable, float]] = []
    total = 0.0
    while pq and len(visited) < len(adj):
        w, _, u, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        total += w
        for nxt, nw in adj[v]:
            if nxt not in visited:
                counter += 1
                heapq.heappush(pq, (nw, counter, v, nxt))
    return total, mst


def interval_scheduling(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Earliest-finish-time greedy algorithm maximizing non-overlapping intervals."""
    chosen: list[tuple[float, float]] = []
    last_end = -float("inf")
    for start, end in sorted(intervals, key=lambda x: (x[1], x[0])):
        if start >= last_end:
            chosen.append((start, end))
            last_end = end
    return chosen


def fractional_knapsack(capacity: float, items: list[tuple[float, float]]) -> float:
    """Maximize value given (value, weight) items using value-per-weight greedy order."""
    rem = capacity
    total_val = 0.0
    for val, wt in sorted(items, key=lambda x: x[0] / x[1], reverse=True):
        if rem <= 0:
            break
        take = min(wt, rem)
        total_val += val * (take / wt)
        rem -= take
    return total_val


def run_tests() -> None:
    verts = ["A", "B", "C", "D", "E"]
    edges = [
        ("A", "B", 1.0),
        ("A", "C", 4.0),
        ("B", "C", 2.0),
        ("B", "D", 6.0),
        ("C", "D", 3.0),
        ("C", "E", 5.0),
        ("D", "E", 2.0),
    ]
    adj: dict[Hashable, list[tuple[Hashable, float]]] = {v: [] for v in verts}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    kw, kmst = kruskal_mst(verts, edges)
    pw, pmst = prim_mst(adj, "A")
    assert kw == pw == 8.0 and len(kmst) == len(pmst) == 4

    # Random connected graph parity test between Kruskal and Prim
    rng = random.Random(11)
    for _ in range(25):
        n = 12
        vs = list(range(n))
        es: list[tuple[Hashable, Hashable, float]] = [(i, i + 1, float(rng.randint(1, 20))) for i in range(n - 1)]
        for _ in range(18):
            u, v = rng.sample(vs, 2)
            es.append((u, v, float(rng.randint(1, 20))))
        radj: dict[Hashable, list[tuple[Hashable, float]]] = {v: [] for v in vs}
        for u, v, w in es:
            radj[u].append((v, w))
            radj[v].append((u, w))
        assert kruskal_mst(vs, es)[0] == prim_mst(radj, 0)[0]

    sched = interval_scheduling([(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11)])
    assert len(sched) == 3
    assert abs(fractional_knapsack(50.0, [(60, 10), (100, 20), (120, 30)]) - 240.0) < 1e-9
    print("W11 self-tests passed.")


if __name__ == "__main__":
    run_tests()
