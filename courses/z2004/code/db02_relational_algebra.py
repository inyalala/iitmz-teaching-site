"""Z2004 Lab 02: Relational Algebra Engine in Python (Select, Project, Join, Set Ops, Division)."""

from __future__ import annotations

from typing import Callable, Iterable


Row = dict[str, object]
Relation = list[Row]


def select(rel: Relation, pred: Callable[[Row], bool]) -> Relation:
    return [dict(r) for r in rel if pred(r)]


def project(rel: Relation, cols: list[str]) -> Relation:
    seen: set[tuple[object, ...]] = set()
    out: Relation = []
    for r in rel:
        tup = tuple(r[c] for c in cols)
        if tup not in seen:
            seen.add(tup)
            out.append({c: r[c] for c in cols})
    return out


def natural_join(r1: Relation, r2: Relation) -> Relation:
    if not r1 or not r2:
        return []
    shared = [k for k in r1[0] if k in r2[0]]
    out: Relation = []
    for a in r1:
        for b in r2:
            if all(a[k] == b[k] for k in shared):
                merged = dict(a)
                merged.update(b)
                out.append(merged)
    return out


def division(r_xy: Relation, s_y: Relation, x_cols: list[str], y_cols: list[str]) -> Relation:
    """Compute R(X, Y) / S(Y): X values paired with EVERY tuple in S(Y)."""
    required = {tuple(s[c] for c in y_cols) for s in s_y}
    groups: dict[tuple[object, ...], set[tuple[object, ...]]] = {}
    for row in r_xy:
        xk = tuple(row[c] for c in x_cols)
        yk = tuple(row[c] for c in y_cols)
        groups.setdefault(xk, set()).add(yk)
    return [dict(zip(x_cols, xk)) for xk, yset in groups.items() if required.issubset(yset)]


def run_tests() -> None:
    students: Relation = [
        {"SID": 1, "Name": "Asha", "Dept": "CSE"},
        {"SID": 2, "Name": "Omar", "Dept": "CSE"},
        {"SID": 3, "Name": "Zahra", "Dept": "EEE"},
    ]
    enrol: Relation = [
        {"SID": 1, "CID": "DB101"},
        {"SID": 1, "CID": "CS102"},
        {"SID": 2, "CID": "DB101"},
        {"SID": 3, "CID": "EE105"},
    ]
    core_courses: Relation = [{"CID": "DB101"}, {"CID": "CS102"}]

    cse_names = project(select(students, lambda r: r["Dept"] == "CSE"), ["Name"])
    assert cse_names == [{"Name": "Asha"}, {"Name": "Omar"}]

    joined = natural_join(students, enrol)
    assert len(joined) == 4

    # Relational division: students enrolled in ALL core_courses
    all_core_sids = division(enrol, core_courses, ["SID"], ["CID"])
    assert all_core_sids == [{"SID": 1}]
    print("DB02 self-tests passed (Relational Algebra select, project, natural join, division).")


if __name__ == "__main__":
    run_tests()
