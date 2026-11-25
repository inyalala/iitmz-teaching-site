"""Week 09 Reference Module: Graph Representations, BFS, DFS, Connected Components, and Topological Sort."""

from __future__ import annotations

from collections import deque
from typing import Hashable


class Graph:
    """Adjacency-list graph supporting directed and undirected edges."""

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self.adj: dict[Hashable, list[Hashable]] = {}

    def add_vertex(self, u: Hashable) -> None:
        if u not in self.adj:
            self.adj[u] = []

    def add_edge(self, u: Hashable, v: Hashable) -> None:
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append(v)
        if not self.directed:
            self.adj[v].append(u)

    def to_adjacency_matrix(self) -> tuple[list[Hashable], list[list[int]]]:
        nodes = sorted(self.adj, key=str)
        idx = {u: i for i, u in enumerate(nodes)}
        n = len(nodes)
        mat = [[0] * n for _ in range(n)]
        for u, nbrs in self.adj.items():
            for v in nbrs:
                mat[idx[u]][idx[v]] = 1
        return nodes, mat


def bfs_shortest_paths(graph: Graph, start: Hashable) -> tuple[list[Hashable], dict[Hashable, int], dict[Hashable, Hashable | None]]:
    """Run BFS from start, returning (visit_order, hop_distances, parents)."""
    dist: dict[Hashable, int] = {start: 0}
    parent: dict[Hashable, Hashable | None] = {start: None}
    order: list[Hashable] = []
    q: deque[Hashable] = deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph.adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return order, dist, parent


def reconstruct_path(parent: dict[Hashable, Hashable | None], target: Hashable) -> list[Hashable]:
    if target not in parent:
        return []
    path: list[Hashable] = []
    cur: Hashable | None = target
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def dfs_timestamps(graph: Graph) -> tuple[list[Hashable], dict[Hashable, int], dict[Hashable, int], bool]:
    """Full DFS recording discovery/finish times and directed cycle detection."""
    color: dict[Hashable, int] = {u: 0 for u in graph.adj}  # 0=white, 1=gray, 2=black
    disc: dict[Hashable, int] = {}
    fin: dict[Hashable, int] = {}
    order: list[Hashable] = []
    has_cycle = False
    clock = 0

    def _visit(u: Hashable) -> None:
        nonlocal clock, has_cycle
        clock += 1
        disc[u] = clock
        color[u] = 1
        order.append(u)
        for v in graph.adj.get(u, []):
            if color[v] == 0:
                _visit(v)
            elif color[v] == 1:
                has_cycle = True
        color[u] = 2
        clock += 1
        fin[u] = clock

    for u in graph.adj:
        if color[u] == 0:
            _visit(u)
    return order, disc, fin, has_cycle


def topological_sort_kahn(graph: Graph) -> list[Hashable]:
    """Kahn's O(V + E) in-degree topological ordering; raises ValueError on cycle."""
    if not graph.directed:
        raise ValueError("topological sort requires a directed graph")
    indeg: dict[Hashable, int] = {u: 0 for u in graph.adj}
    for u in graph.adj:
        for v in graph.adj[u]:
            indeg[v] += 1
    q: deque[Hashable] = deque([u for u, d in indeg.items() if d == 0])
    topo: list[Hashable] = []
    while q:
        u = q.popleft()
        topo.append(u)
        for v in graph.adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(topo) != len(graph.adj):
        raise ValueError("graph contains a directed cycle")
    return topo


def connected_components(graph: Graph) -> list[list[Hashable]]:
    """Find connected components in an undirected graph."""
    visited: set[Hashable] = set()
    comps: list[list[Hashable]] = []
    for start in graph.adj:
        if start not in visited:
            order, _, _ = bfs_shortest_paths(graph, start)
            visited.update(order)
            comps.append(order)
    return comps


def run_tests() -> None:
    g = Graph(directed=False)
    for u, v in [("StoneTown", "Fumba"), ("Fumba", "Bweleo"), ("StoneTown", "Bububu"), ("Bububu", "Mkokotoni"), ("Chake", "Wete")]:
        g.add_edge(u, v)
    comps = connected_components(g)
    assert len(comps) == 2

    _, dist, parent = bfs_shortest_paths(g, "StoneTown")
    assert dist["Bweleo"] == 2
    assert reconstruct_path(parent, "Bweleo") == ["StoneTown", "Fumba", "Bweleo"]

    dag = Graph(directed=True)
    for u, v in [("IntroPython", "Z5007"), ("DiscreteMath", "Z5007"), ("Z5007", "Algorithms"), ("Z5007", "DataMining"), ("Algorithms", "Capstone"), ("DataMining", "Capstone")]:
        dag.add_edge(u, v)
    topo = topological_sort_kahn(dag)
    pos = {node: i for i, node in enumerate(topo)}
    for u, nbrs in dag.adj.items():
        for v in nbrs:
            assert pos[u] < pos[v]
    _, _, _, cyc = dfs_timestamps(dag)
    assert not cyc

    dag.add_edge("Capstone", "Z5007")
    _, _, _, cyc2 = dfs_timestamps(dag)
    assert cyc2
    print("W09 self-tests passed.")


if __name__ == "__main__":
    run_tests()
