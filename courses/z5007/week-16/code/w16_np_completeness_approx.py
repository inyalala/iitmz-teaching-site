"""Week 16 Reference Module: NP-Completeness, 3-SAT Reductions, and 2-Approximation Algorithms."""

from __future__ import annotations

from typing import Optional


def eval_cnf(clauses: list[tuple[int, ...]], assignment: dict[int, bool]) -> bool:
    """Evaluate a CNF formula where positive int x is x and -x is NOT x."""
    for clause in clauses:
        if not any((assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)]) for lit in clause):
            return False
    return True


def solve_sat_backtracking(num_vars: int, clauses: list[tuple[int, ...]]) -> Optional[dict[int, bool]]:
    """Backtracking DPLL-style exact SAT solver."""
    assign: dict[int, bool] = {}

    def _can_satisfy() -> bool:
        for clause in clauses:
            undecided = False
            satisfied = False
            for lit in clause:
                v = abs(lit)
                if v not in assign:
                    undecided = True
                elif (lit > 0 and assign[v]) or (lit < 0 and not assign[v]):
                    satisfied = True
                    break
            if not satisfied and not undecided:
                return False
        return True

    def _dfs(var: int) -> bool:
        if not _can_satisfy():
            return False
        if var > num_vars:
            return True
        for val in (True, False):
            assign[var] = val
            if _dfs(var + 1):
                return True
            del assign[var]
        return False

    return assign if _dfs(1) else None


def reduce_3sat_to_independent_set(clauses: list[tuple[int, int, int]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Construct the classic polynomial reduction graph G=(V,E) with target k = len(clauses).

    Vertices are (clause_idx, literal_idx) pairs. Edges connect:
    1) all 3 literals inside each clause triangle, and
    2) complementary literals (x, -x) across distinct clauses.
    """
    nodes = [(ci, li) for ci in range(len(clauses)) for li in range(3)]
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for ci in range(len(clauses)):
        edges.append(((ci, 0), (ci, 1)))
        edges.append(((ci, 1), (ci, 2)))
        edges.append(((ci, 0), (ci, 2)))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            c1, l1 = nodes[i]
            c2, l2 = nodes[j]
            if c1 != c2 and clauses[c1][l1] == -clauses[c2][l2]:
                edges.append((nodes[i], nodes[j]))
    return [(ci * 3 + li, 0) for ci, li in nodes], [(c1 * 3 + l1, c2 * 3 + l2) for (c1, l1), (c2, l2) in edges]


def vertex_cover_2approx(vertices: list[int], edges: list[tuple[int, int]]) -> set[int]:
    """2-approximation for Minimum Vertex Cover via maximal matching."""
    cover: set[int] = set()
    for u, v in edges:
        if u not in cover and v not in cover:
            cover.add(u)
            cover.add(v)
    assert all(u in cover or v in cover for u, v in edges)
    return cover


def run_tests() -> None:
    clauses = [(1, -2, 3), (-1, 2, 3), (-1, -2, -3)]
    sol = solve_sat_backtracking(3, clauses)
    assert sol is not None and eval_cnf(clauses, sol)

    unsat = [(1,), (-1,)]
    assert solve_sat_backtracking(1, unsat) is None

    v_pairs, red_edges = reduce_3sat_to_independent_set(clauses)
    assert len(v_pairs) == 9 and len(red_edges) >= 9

    vc = vertex_cover_2approx([0, 1, 2, 3, 4], [(0, 1), (1, 2), (2, 3), (3, 4)])
    assert len(vc) <= 4
    print(f"W16 self-tests passed (3-SAT solution={sol}, 2-approx Vertex Cover size={len(vc)}).")


if __name__ == "__main__":
    run_tests()
