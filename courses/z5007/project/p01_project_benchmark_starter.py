"""Z5007 Course Project Starter Benchmark: Custom From-Scratch Data Structures vs. Naive Baselines."""

from __future__ import annotations

import math
import random
import time


class BinaryMinHeap:
    """From-scratch binary min-heap supporting O(log n) push and pop (no heapq dependency)."""

    def __init__(self) -> None:
        self._data: list[tuple[float, object]] = []

    def __len__(self) -> int:
        return len(self._data)

    def push(self, priority: float, item: object) -> None:
        self._data.append((priority, item))
        i = len(self._data) - 1
        while i > 0:
            p = (i - 1) // 2
            if self._data[p][0] <= self._data[i][0]:
                break
            self._data[p], self._data[i] = self._data[i], self._data[p]
            i = p

    def pop(self) -> tuple[float, object]:
        if not self._data:
            raise IndexError("pop from empty BinaryMinHeap")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            i, n = 0, len(self._data)
            while True:
                left, right, smallest = 2 * i + 1, 2 * i + 2, i
                if left < n and self._data[left][0] < self._data[smallest][0]:
                    smallest = left
                if right < n and self._data[right][0] < self._data[smallest][0]:
                    smallest = right
                if smallest == i:
                    break
                self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
                i = smallest
        return top


def build_synthetic_route_graph(
    n_nodes: int = 600, avg_degree: int = 4, seed: int = 5007
) -> tuple[dict[int, list[tuple[int, float]]], dict[int, tuple[float, float]]]:
    """Generate a connected weighted 2D route graph (>= 500 nodes, >= 2000 directed edges)."""
    rng = random.Random(seed)
    coords = {u: (rng.uniform(0.0, 100.0), rng.uniform(0.0, 100.0)) for u in range(n_nodes)}
    adj: dict[int, list[tuple[int, float]]] = {u: [] for u in range(n_nodes)}

    def dist(u: int, v: int) -> float:
        dx = coords[u][0] - coords[v][0]
        dy = coords[u][1] - coords[v][1]
        return math.hypot(dx, dy)

    # Backbone chain guarantees reachability across all nodes
    for u in range(n_nodes - 1):
        w = round(dist(u, u + 1), 3)
        adj[u].append((u + 1, w))
        adj[u + 1].append((u, w))

    for u in range(n_nodes):
        for _ in range(avg_degree):
            v = rng.randrange(n_nodes)
            if v != u:
                w = round(dist(u, v) * rng.uniform(1.0, 1.25), 3)
                adj[u].append((v, w))
    return adj, coords


def dijkstra_array_naive(adj: dict[int, list[tuple[int, float]]], src: int, dst: int) -> float:
    """O(V^2) array-scan baseline for shortest-path distance."""
    n = len(adj)
    dist = [math.inf] * n
    done = [False] * n
    dist[src] = 0.0
    for _ in range(n):
        u, best = -1, math.inf
        for cand in range(n):
            if not done[cand] and dist[cand] < best:
                u, best = cand, dist[cand]
        if u == -1 or u == dst:
            break
        done[u] = True
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist[dst]


def astar_heap(
    adj: dict[int, list[tuple[int, float]]],
    coords: dict[int, tuple[float, float]],
    src: int,
    dst: int,
) -> tuple[float, int]:
    """From-scratch BinaryMinHeap A* search returning (distance, settled_nodes)."""
    tx, ty = coords[dst]
    dist: dict[int, float] = {src: 0.0}
    pq = BinaryMinHeap()
    pq.push(math.hypot(coords[src][0] - tx, coords[src][1] - ty), src)
    settled = 0
    seen: set[int] = set()
    while len(pq) > 0:
        _, u_obj = pq.pop()
        u = int(u_obj)
        if u in seen:
            continue
        seen.add(u)
        settled += 1
        if u == dst:
            return dist[u], settled
        du = dist[u]
        for v, w in adj[u]:
            nd = du + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                h = math.hypot(coords[v][0] - tx, coords[v][1] - ty)
                pq.push(nd + h, v)
    return math.inf, settled


def benchmark_inverted_index_recommender(
    n_items: int = 1000, top_k: int = 5, seed: int = 5007
) -> tuple[list[tuple[float, int]], list[tuple[float, int]], float, float]:
    """Compare custom InvertedIndex + bounded MinHeap Top-K vs. brute-force full-catalog scan."""
    rng = random.Random(seed)
    vocab = [f"tag_{t}" for t in range(80)]
    catalog: dict[int, set[str]] = {
        item_id: set(rng.sample(vocab, k=5)) for item_id in range(n_items)
    }
    inverted: dict[str, list[int]] = {}
    for item_id, tags in catalog.items():
        for tag in tags:
            inverted.setdefault(tag, []).append(item_id)

    query_tags = {"tag_0", "tag_5", "tag_12", "tag_27"}

    # Naive O(N) full scan over all 1,000 items + full sort
    t0 = time.perf_counter()
    naive_scores: list[tuple[float, int]] = []
    for item_id, tags in catalog.items():
        inter = len(tags & query_tags)
        if inter > 0:
            score = inter / len(tags | query_tags)
            naive_scores.append((score, -item_id))
    naive_scores.sort(reverse=True)
    naive_top = [(round(s, 6), -neg_id) for s, neg_id in naive_scores[:top_k]]
    t_naive = time.perf_counter() - t0

    # Custom InvertedIndex + size-K BinaryMinHeap
    t1 = time.perf_counter()
    counts: dict[int, int] = {}
    for tag in query_tags:
        for item_id in inverted.get(tag, ()):
            counts[item_id] = counts.get(item_id, 0) + 1
    top_heap = BinaryMinHeap()
    for item_id, inter in counts.items():
        score = inter / (len(catalog[item_id]) + len(query_tags) - inter)
        key = (score, -item_id)
        if len(top_heap) < top_k:
            top_heap.push(key, item_id)
        else:
            min_key, _ = top_heap._data[0]
            if key > min_key:
                top_heap.pop()
                top_heap.push(key, item_id)
    idx_top: list[tuple[float, int]] = []
    while len(top_heap) > 0:
        min_key, item_id = top_heap.pop()
        idx_top.append((round(float(min_key[0]), 6), int(item_id)))
    idx_top.reverse()
    t_idx = time.perf_counter() - t1
    return naive_top, idx_top, t_naive, t_idx


def run_tests() -> None:
    adj, coords = build_synthetic_route_graph(n_nodes=600, avg_degree=4, seed=5007)
    edge_count = sum(len(nbrs) for nbrs in adj.values())
    assert len(adj) == 600 and edge_count >= 2400

    t0 = time.perf_counter()
    d_naive = dijkstra_array_naive(adj, 0, 599)
    dt_naive = time.perf_counter() - t0

    t1 = time.perf_counter()
    d_astar, settled = astar_heap(adj, coords, 0, 599)
    dt_astar = time.perf_counter() - t1

    assert abs(d_naive - d_astar) < 1e-6 and math.isfinite(d_astar)
    assert settled <= len(adj)

    naive_top, idx_top, t_scan, t_inv = benchmark_inverted_index_recommender()
    assert naive_top == idx_top and len(idx_top) == 5
    print(
        f"P01 project benchmark tests passed (V=600, E={edge_count}, dist={d_astar:.2f}, "
        f"A*={dt_astar*1000:.2f}ms vs O(V^2)={dt_naive*1000:.2f}ms; Top-5 recommender parity OK)."
    )


if __name__ == "__main__":
    run_tests()
