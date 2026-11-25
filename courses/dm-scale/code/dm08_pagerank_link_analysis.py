"""Z3003 Module 08: PageRank Power Iteration, Dead-End Teleportation, and HITS Hubs/Authorities."""

from __future__ import annotations

import numpy as np


def pagerank(
    adj: dict[str, list[str]],
    beta: float = 0.85,
    tol: float = 1e-10,
    max_iter: int = 200,
) -> tuple[dict[str, float], int]:
    """Compute PageRank via power iteration with dead-end handling and random teleportation."""
    nodes = sorted(adj.keys())
    n = len(nodes)
    idx = {u: i for i, u in enumerate(nodes)}
    M = np.zeros((n, n), dtype=float)
    for u, nbrs in adj.items():
        if nbrs:
            for v in nbrs:
                M[idx[v], idx[u]] += 1.0 / len(nbrs)
        else:
            # Dead end distributes mass uniformly to avoid rank leak
            M[:, idx[u]] = 1.0 / n

    r = np.full(n, 1.0 / n, dtype=float)
    teleport = (1.0 - beta) / n
    iters = 0
    for iters in range(1, max_iter + 1):
        r_next = beta * (M @ r) + teleport
        if float(np.sum(np.abs(r_next - r))) < tol:
            r = r_next
            break
        r = r_next
    return {u: float(r[idx[u]]) for u in nodes}, iters


def hits_scores(adj: dict[str, list[str]], iters: int = 30) -> tuple[dict[str, float], dict[str, float]]:
    """Compute normalized HITS hub and authority vectors."""
    nodes = sorted(adj.keys())
    n = len(nodes)
    idx = {u: i for i, u in enumerate(nodes)}
    L = np.zeros((n, n), dtype=float)
    for u, nbrs in adj.items():
        for v in nbrs:
            L[idx[u], idx[v]] = 1.0
    h = np.ones(n)
    a = np.ones(n)
    for _ in range(iters):
        a = L.T @ h
        a /= max(float(np.linalg.norm(a)), 1e-12)
        h = L @ a
        h /= max(float(np.linalg.norm(h)), 1e-12)
    return {u: float(h[idx[u]]) for u in nodes}, {u: float(a[idx[u]]) for u in nodes}


def run_tests() -> None:
    # Classic MMDS Ch. 5 web graph with spider trap D->D
    web = {
        "A": ["B", "C", "D"],
        "B": ["A", "D"],
        "C": ["A"],
        "D": ["D"],  # spider trap!
    }
    pr_leak, _ = pagerank(web, beta=1.0, max_iter=150)
    pr_tele, iters = pagerank(web, beta=0.85)
    assert abs(sum(pr_tele.values()) - 1.0) < 1e-8
    # Teleportation keeps non-trap nodes positive instead of 0
    assert pr_tele["A"] > 0.05 and pr_leak["D"] > 0.99

    hubs, auths = hits_scores({"H1": ["A1", "A2"], "H2": ["A1"], "A1": [], "A2": []})
    assert auths["A1"] > auths["A2"] and hubs["H1"] > hubs["H2"]
    print(f"DM08 self-tests passed (PageRank converged in {iters} iters; sum={sum(pr_tele.values()):.6f}).")


if __name__ == "__main__":
    run_tests()
