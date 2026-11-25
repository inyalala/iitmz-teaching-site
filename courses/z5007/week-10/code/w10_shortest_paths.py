"""Week 10 Reference Module: Weighted Shortest Paths (Dijkstra and Bellman-Ford)."""

from __future__ import annotations

import heapq
import math
from typing import Hashable


WeightedAdj = dict[Hashable, list[tuple[Hashable, float]]]


def dijkstra(adj: WeightedAdj, source: Hashable) -> tuple[dict[Hashable, float], dict[Hashable, Hashable | None]]:
    """Compute single-source shortest paths for non-negative edge weights in O((V + E) log V)."""
    dist: dict[Hashable, float] = {u: math.inf for u in adj}
    parent: dict[Hashable, Hashable | None] = {u: None for u in adj}
    dist[source] = 0.0
    pq: list[tuple[float, int, Hashable]] = [(0.0, 0, source)]
    counter = 0

    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if w < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                parent[v] = u
                counter += 1
                heapq.heappush(pq, (nd, counter, v))
    return dist, parent


def bellman_ford(
    vertices: list[Hashable],
    edges: list[tuple[Hashable, Hashable, float]],
    source: Hashable,
) -> tuple[dict[Hashable, float], dict[Hashable, Hashable | None], bool]:
    """Compute shortest paths allowing negative weights; returns (dist, parent, has_negative_cycle)."""
    dist: dict[Hashable, float] = {u: math.inf for u in vertices}
    parent: dict[Hashable, Hashable | None] = {u: None for u in vertices}
    dist[source] = 0.0

    for _ in range(len(vertices) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True
        if not updated:
            break

    has_neg_cycle = any(
        dist[u] != math.inf and dist[u] + w < dist[v] for u, v, w in edges
    )
    return dist, parent, has_neg_cycle


def build_path(parent: dict[Hashable, Hashable | None], target: Hashable) -> list[Hashable]:
    path: list[Hashable] = []
    cur: Hashable | None = target
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    return path


def run_tests() -> None:
    adj: WeightedAdj = {
        "StoneTown": [("Mbweni", 6.0), ("Fumba", 18.0), ("Bububu", 9.0)],
        "Mbweni": [("Bweleo", 11.0), ("Fumba", 14.0)],
        "Bububu": [("Mahonda", 16.0)],
        "Fumba": [("Bweleo", 5.0)],
        "Bweleo": [("Kizimkazi", 38.0)],
        "Mahonda": [("Nungwi", 33.0)],
        "Kizimkazi": [],
        "Nungwi": [],
    }
    dist, parent = dijkstra(adj, "StoneTown")
    assert dist["Bweleo"] == 17.0
    assert build_path(parent, "Bweleo") == ["StoneTown", "Mbweni", "Bweleo"]

    # Compare with Bellman-Ford on same graph
    verts = list(adj.keys())
    edges = [(u, v, w) for u, nbrs in adj.items() for v, w in nbrs]
    bf_dist, _, neg = bellman_ford(verts, edges, "StoneTown")
    assert not neg and bf_dist == dist

    # Negative edge without cycle
    v2 = ["S", "A", "B", "C"]
    e2 = [("S", "A", 4.0), ("S", "B", 5.0), ("B", "A", -3.0), ("A", "C", 2.0)]
    d2, _, neg2 = bellman_ford(v2, e2, "S")
    assert not neg2 and d2["A"] == 2.0 and d2["C"] == 4.0

    # Negative cycle detection
    e3 = [("S", "A", 1.0), ("A", "B", -2.0), ("B", "A", -1.0)]
    _, _, neg3 = bellman_ford(["S", "A", "B"], e3, "S")
    assert neg3
    print("W10 self-tests passed.")


if __name__ == "__main__":
    run_tests()
