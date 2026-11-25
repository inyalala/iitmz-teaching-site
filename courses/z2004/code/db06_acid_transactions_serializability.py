"""Z2004 Lab 06: ACID Transactions, Rollback Atomicity, WAL Isolation, and Conflict Serializability."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path


def is_conflict_serializable(schedule: list[tuple[str, str, str]]) -> tuple[bool, list[str]]:
    """Test conflict serializability via precedence (serialization) graph cycle check.

    Each operation is (txn_id, 'R'|'W', item).
    """
    txns = sorted({t for t, _, _ in schedule})
    adj: dict[str, set[str]] = {t: set() for t in txns}
    for i in range(len(schedule)):
        t1, op1, item1 = schedule[i]
        for j in range(i + 1, len(schedule)):
            t2, op2, item2 = schedule[j]
            if t1 != t2 and item1 == item2 and (op1 == "W" or op2 == "W"):
                adj[t1].add(t2)

    indeg = {t: 0 for t in txns}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    q = [t for t in txns if indeg[t] == 0]
    order: list[str] = []
    while q:
        u = q.pop(0)
        order.append(u)
        for v in sorted(adj[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return len(order) == len(txns), order


def run_tests() -> None:
    # Serializable vs non-serializable schedule check
    s_ok = [("T1", "R", "A"), ("T1", "W", "A"), ("T2", "R", "A"), ("T2", "W", "A"), ("T1", "R", "B"), ("T2", "R", "B")]
    ok, order = is_conflict_serializable(s_ok)
    assert ok and order == ["T1", "T2"]

    s_cycle = [("T1", "R", "A"), ("T2", "R", "A"), ("T1", "W", "A"), ("T2", "W", "A")]
    ok2, _ = is_conflict_serializable(s_cycle)
    assert not ok2

    # SQLite ACID atomicity & rollback on failure
    with tempfile.TemporaryDirectory() as tmp:
        db_file = Path(tmp) / "acid_test.db"
        conn = sqlite3.connect(db_file)
        conn.execute("CREATE TABLE Accounts (id TEXT PRIMARY KEY, bal INTEGER CHECK (bal >= 0))")
        conn.execute("INSERT INTO Accounts VALUES ('Asha', 100), ('Omar', 50)")
        conn.commit()

        # Failed transfer (overdraft) must roll back completely
        try:
            with conn:
                conn.execute("UPDATE Accounts SET bal = bal - 150 WHERE id = 'Asha'")
                conn.execute("UPDATE Accounts SET bal = bal + 150 WHERE id = 'Omar'")
        except sqlite3.IntegrityError:
            pass
        bals = dict(conn.execute("SELECT id, bal FROM Accounts").fetchall())
        assert bals == {"Asha": 100, "Omar": 50}
        conn.close()
    print("DB06 self-tests passed (Conflict serializability & ACID rollback verified).")


if __name__ == "__main__":
    run_tests()
