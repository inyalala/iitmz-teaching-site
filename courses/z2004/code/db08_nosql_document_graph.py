"""Z2004 Lab 08: Document Store and Property Graph Patterns vs. Relational SQLite Parity."""

from __future__ import annotations

import json
import sqlite3
from collections import deque


def build_document_store(orders: list[dict]) -> dict[str, dict]:
    """Index embedded order documents by order_id for single-lookup document access."""
    return {doc["order_id"]: doc for doc in orders}


def document_revenue_by_region(doc_store: dict[str, dict]) -> dict[str, float]:
    """Aggregate line-item revenue directly from nested JSON order documents."""
    totals: dict[str, float] = {}
    for doc in doc_store.values():
        region = doc["customer"]["region"]
        order_total = sum(item["qty"] * item["price"] for item in doc["items"])
        totals[region] = totals.get(region, 0.0) + order_total
    return totals


def graph_shortest_path_hops(edges: list[tuple[str, str]], start: str, goal: str) -> list[str] | None:
    """Compute shortest path in an undirected collaboration/citation property graph via BFS."""
    adj: dict[str, list[str]] = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    q = deque([[start]])
    seen = {start}
    while q:
        path = q.popleft()
        node = path[-1]
        if node == goal:
            return path
        for nxt in sorted(adj.get(node, [])):
            if nxt not in seen:
                seen.add(nxt)
                q.append(path + [nxt])
    return None


def sqlite_parity_check(orders: list[dict], edges: list[tuple[str, str]]) -> tuple[dict[str, float], int]:
    """Verify exact numeric parity between NoSQL document/graph queries and SQLite SQL/CTE queries."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE OrderDocs (order_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    conn.executemany(
        "INSERT INTO OrderDocs VALUES (?, ?)",
        [(o["order_id"], json.dumps(o)) for o in orders],
    )
    sql_rev = dict(
        conn.execute(
            """
            SELECT json_extract(d.payload, '$.customer.region') AS region,
                   SUM(json_extract(j.value, '$.qty') * json_extract(j.value, '$.price')) AS rev
            FROM OrderDocs d, json_each(d.payload, '$.items') j
            GROUP BY region
            """
        ).fetchall()
    )

    conn.execute("CREATE TABLE GraphEdges (src TEXT, dst TEXT)")
    for u, v in edges:
        conn.execute("INSERT INTO GraphEdges VALUES (?, ?), (?, ?)", (u, v, v, u))
    hops_row = conn.execute(
        """
        WITH RECURSIVE Walk(node, depth, visited) AS (
            SELECT 'Asha', 0, ',Asha,'
            UNION ALL
            SELECT e.dst, w.depth + 1, w.visited || e.dst || ','
            FROM Walk w
            JOIN GraphEdges e ON e.src = w.node
            WHERE w.depth < 6 AND instr(w.visited, ',' || e.dst || ',') = 0
        )
        SELECT MIN(depth) FROM Walk WHERE node = 'Zuri'
        """
    ).fetchone()
    conn.close()
    return sql_rev, int(hops_row[0])


def run_tests() -> None:
    orders = [
        {
            "order_id": "ORD-101",
            "customer": {"name": "Amina", "region": "Unguja"},
            "items": [{"sku": "CLV-1", "qty": 2, "price": 15.0}, {"sku": "SEA-4", "qty": 1, "price": 20.0}],
        },
        {
            "order_id": "ORD-102",
            "customer": {"name": "Hassan", "region": "Pemba"},
            "items": [{"sku": "CLV-1", "qty": 4, "price": 15.0}],
        },
        {
            "order_id": "ORD-103",
            "customer": {"name": "Fatma", "region": "Unguja"},
            "items": [{"sku": "SP-2", "qty": 3, "price": 10.0}],
        },
    ]
    edges = [("Asha", "Bakari"), ("Bakari", "Chidi"), ("Chidi", "Zuri"), ("Asha", "Dalia"), ("Dalia", "Zuri")]

    doc_store = build_document_store(orders)
    doc_rev = document_revenue_by_region(doc_store)
    path = graph_shortest_path_hops(edges, "Asha", "Zuri")
    sql_rev, sql_hops = sqlite_parity_check(orders, edges)

    assert doc_rev == {"Unguja": 80.0, "Pemba": 60.0}
    assert doc_rev == sql_rev
    assert path == ["Asha", "Dalia", "Zuri"]
    assert len(path) - 1 == sql_hops == 2
    print("DB08 self-tests passed (Document aggregation and Graph BFS match SQLite JSON1/CTE parity).")


if __name__ == "__main__":
    run_tests()
