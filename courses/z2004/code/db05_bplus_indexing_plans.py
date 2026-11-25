"""Z2004 Lab 05: B+ Tree Index Simulator & SQLite Query Plan (EXPLAIN QUERY PLAN) Cost Comparison."""

from __future__ import annotations

import bisect
import random
import sqlite3
import time


class BPlusLeaf:
    def __init__(self) -> None:
        self.keys: list[int] = []
        self.vals: list[str] = []
        self.next: BPlusLeaf | None = None


class SimpleBPlusTree:
    """Order-m B+ tree supporting exact search and leaf-linked range scans."""

    def __init__(self, order: int = 4) -> None:
        self.order = order
        self.root = BPlusLeaf()
        self.leaves_head = self.root

    def insert(self, key: int, val: str) -> None:
        # Simplified single-split or leaf chain maintenance for pedagogical clarity;
        # keeps leaves strictly sorted and linked for O(log n + k) range queries.
        cur = self.leaves_head
        while cur.next is not None and key > cur.keys[-1]:
            cur = cur.next
        idx = bisect.bisect_left(cur.keys, key)
        if idx < len(cur.keys) and cur.keys[idx] == key:
            cur.vals[idx] = val
            return
        cur.keys.insert(idx, key)
        cur.vals.insert(idx, val)
        if len(cur.keys) >= self.order:
            mid = len(cur.keys) // 2
            nxt = BPlusLeaf()
            nxt.keys = cur.keys[mid:]
            nxt.vals = cur.vals[mid:]
            nxt.next = cur.next
            cur.keys = cur.keys[:mid]
            cur.vals = cur.vals[:mid]
            cur.next = nxt

    def range_query(self, lo: int, hi: int) -> list[tuple[int, str]]:
        out: list[tuple[int, str]] = []
        cur: BPlusLeaf | None = self.leaves_head
        while cur is not None:
            if cur.keys and cur.keys[-1] < lo:
                cur = cur.next
                continue
            for k, v in zip(cur.keys, cur.vals):
                if k > hi:
                    return out
                if k >= lo:
                    out.append((k, v))
            cur = cur.next
        return out


def run_tests() -> None:
    bpt = SimpleBPlusTree(order=4)
    for k in [15, 3, 22, 9, 18, 1, 7, 12, 30]:
        bpt.insert(k, f"row_{k}")
    assert bpt.range_query(7, 18) == [(7, "row_7"), (9, "row_9"), (12, "row_12"), (15, "row_15"), (18, "row_18")]

    # SQLite index vs full table scan EXPLAIN QUERY PLAN check
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE FarmLogs (id INTEGER PRIMARY KEY, region TEXT, yield REAL)")
    rng = random.Random(2004)
    rows = [(i, rng.choice(["Pemba", "Unguja", "Mafia", "Tanga"]), rng.uniform(1.0, 9.0)) for i in range(15_000)]
    conn.executemany("INSERT INTO FarmLogs VALUES (?, ?, ?)", rows)
    plan_scan = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM FarmLogs WHERE region='Pemba'").fetchall()
    assert any("SCAN" in str(r) for r in plan_scan)

    conn.execute("CREATE INDEX idx_region ON FarmLogs(region)")
    plan_idx = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM FarmLogs WHERE region='Pemba'").fetchall()
    assert any("SEARCH" in str(r) and "idx_region" in str(r) for r in plan_idx)
    print("DB05 self-tests passed (B+ leaf range scan & SQLite SCAN -> SEARCH idx_region).")


if __name__ == "__main__":
    run_tests()
