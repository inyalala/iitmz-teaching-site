"""Z2004 Lab 07: Query Optimization, Join Cost Models, and SQLite EXPLAIN QUERY PLAN."""

from __future__ import annotations

import math
import sqlite3
import tempfile
from pathlib import Path


def cost_block_nested_loop(b_outer: int, b_inner: int, mem_pages: int) -> int:
    """Estimate page I/Os for Block Nested-Loop Join with M buffer pages."""
    if mem_pages < 3:
        raise ValueError("Need at least 3 buffer pages (M-2 outer, 1 inner, 1 output)")
    chunks = math.ceil(b_outer / (mem_pages - 2))
    return b_outer + chunks * b_inner


def cost_sort_merge_join(b_r: int, b_s: int, mem_pages: int) -> int:
    """Estimate page I/Os for two-pass External Sort-Merge Join (when M >= sqrt(max(B_R, B_S)))."""
    if mem_pages < 3:
        raise ValueError("Need at least 3 buffer pages")
    # Two-pass external merge sort reads/writes each relation twice plus 1 join read pass = 3*(B_R + B_S)
    # when max(B_R, B_S) <= mem_pages * (mem_pages - 1); otherwise compute explicit merge passes.
    passes_r = 1 + math.ceil(math.log(max(1, math.ceil(b_r / mem_pages)), max(2, mem_pages - 1)))
    passes_s = 1 + math.ceil(math.log(max(1, math.ceil(b_s / mem_pages)), max(2, mem_pages - 1)))
    return 2 * passes_r * b_r + 2 * passes_s * b_s - (b_r + b_s)


def cost_grace_hash_join(b_r: int, b_s: int, mem_pages: int) -> int:
    """Estimate page I/Os for Grace Hash Join (partition + probe)."""
    if mem_pages < 3:
        raise ValueError("Need at least 3 buffer pages")
    # Partition phase: read + write both; Probe phase: read both -> 3*(B_R + B_S)
    # Valid when smallest partition fits in M-2 pages (approx min(B_R, B_S) <= (M-1)*(M-2))
    return 3 * (b_r + b_s)


def explain_sqlite_join_plans(db_path: Path) -> dict[str, list[str]]:
    """Compare SQLite EXPLAIN QUERY PLAN before and after adding selective indexes."""
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE Students (sid INTEGER PRIMARY KEY, major TEXT, gpa REAL);
        CREATE TABLE Enrollments (eid INTEGER PRIMARY KEY, sid INTEGER, cid TEXT, grade REAL);
        """
    )
    conn.executemany(
        "INSERT INTO Students VALUES (?, ?, ?)",
        [(i, "DSAI" if i % 5 == 0 else "CS", 2.5 + (i % 15) * 0.1) for i in range(1, 501)],
    )
    conn.executemany(
        "INSERT INTO Enrollments VALUES (?, ?, ?, ?)",
        [(i, (i % 500) + 1, f"Z{3000 + ((i // 5) % 10)}", 65.0 + (i % 35)) for i in range(1, 2001)],
    )
    query = (
        "SELECT s.sid, e.cid, e.grade FROM Students s "
        "JOIN Enrollments e ON s.sid = e.sid WHERE s.major = 'DSAI' AND e.cid = 'Z3003'"
    )
    plan_no_idx = [row[3] for row in conn.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()]
    conn.execute("CREATE INDEX idx_enroll_sid_cid ON Enrollments(sid, cid)")
    conn.execute("CREATE INDEX idx_students_major ON Students(major)")
    conn.execute("ANALYZE")
    plan_with_idx = [row[3] for row in conn.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()]
    rows = conn.execute(query).fetchall()
    conn.close()
    return {
        "no_index": plan_no_idx,
        "with_index": plan_with_idx,
        "result_count": [str(len(rows))],
    }


def run_tests() -> None:
    bnl = cost_block_nested_loop(b_outer=1000, b_inner=500, mem_pages=52)
    smj = cost_sort_merge_join(b_r=1000, b_s=500, mem_pages=52)
    ghj = cost_grace_hash_join(b_r=1000, b_s=500, mem_pages=52)
    # BNL = 1000 + ceil(1000/50)*500 = 11000; SMJ & GHJ = 3*(1000+500) = 4500
    assert bnl == 11000, f"Unexpected BNL cost: {bnl}"
    assert ghj == 4500, f"Unexpected GHJ cost: {ghj}"
    assert smj == 4500, f"Unexpected SMJ cost: {smj}"
    assert ghj < bnl and smj < bnl

    with tempfile.TemporaryDirectory() as tmp:
        plans = explain_sqlite_join_plans(Path(tmp) / "opt.db")
        joined_no_idx = " ".join(plans["no_index"])
        joined_idx = " ".join(plans["with_index"])
        assert "SCAN" in joined_no_idx
        assert "SEARCH" in joined_idx
        assert int(plans["result_count"][0]) > 0
    print(f"DB07 self-tests passed (BNL={bnl}, SMJ={smj}, GHJ={ghj} pages; indexed SEARCH verified).")


if __name__ == "__main__":
    run_tests()
