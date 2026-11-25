"""Z2004 Lab 04: Functional Dependency Closure, Candidate Keys, 3NF/BCNF Checker, and Lossless Join."""

from __future__ import annotations

from itertools import combinations


FD = tuple[frozenset[str], frozenset[str]]


def attribute_closure(attrs: frozenset[str], fds: list[FD]) -> frozenset[str]:
    """Compute X+ under Armstrong's axioms."""
    closure = set(attrs)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if lhs.issubset(closure) and not rhs.issubset(closure):
                closure.update(rhs)
                changed = True
    return frozenset(closure)


def find_candidate_keys(relation: frozenset[str], fds: list[FD]) -> list[frozenset[str]]:
    """Find all minimal superkeys for relation."""
    keys: list[frozenset[str]] = []
    cols = sorted(relation)
    for size in range(1, len(cols) + 1):
        for comb in combinations(cols, size):
            cand = frozenset(comb)
            if any(k.issubset(cand) for k in keys):
                continue
            if attribute_closure(cand, fds) == relation:
                keys.append(cand)
    return keys


def is_bcnf(relation: frozenset[str], fds: list[FD]) -> tuple[bool, list[FD]]:
    """Return (is_bcnf, violating_fds) for relation."""
    violations: list[FD] = []
    for lhs, rhs in fds:
        if lhs.issubset(relation) and rhs.issubset(relation) and not rhs.issubset(lhs):
            if not relation.issubset(attribute_closure(lhs, fds)):
                violations.append((lhs, rhs))
    return len(violations) == 0, violations


def is_lossless_binary_split(r1: frozenset[str], r2: frozenset[str], fds: list[FD]) -> bool:
    """Chase / intersection rule: R1 & R2 -> R1 or R1 & R2 -> R2."""
    inter = r1 & r2
    if not inter:
        return False
    cl = attribute_closure(inter, fds)
    return r1.issubset(cl) or r2.issubset(cl)


def run_tests() -> None:
    # Classic R(A, B, C, D) with A -> B, B -> C (not in BCNF or 3NF)
    rel = frozenset({"A", "B", "C", "D"})
    fds: list[FD] = [(frozenset({"A"}), frozenset({"B"})), (frozenset({"B"}), frozenset({"C"}))]
    keys = find_candidate_keys(rel, fds)
    assert keys == [frozenset({"A", "D"})]
    ok, viols = is_bcnf(rel, fds)
    assert not ok and len(viols) == 2

    # Lossless BCNF decomposition check: R1(B, C), R2(A, B, D) -> common B -> C -> R1
    r1, r2 = frozenset({"B", "C"}), frozenset({"A", "B", "D"})
    assert is_lossless_binary_split(r1, r2, fds)
    print("DB04 self-tests passed (FD closure, candidate keys, BCNF checker, lossless join).")


if __name__ == "__main__":
    run_tests()
