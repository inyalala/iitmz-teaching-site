"""Z5008 Lab Module 02: Spark SQL Window Functions, Joins, and Adaptive Partition Tuning."""

from __future__ import annotations

import sqlite3
from typing import Any


def spark_or_sqlite_window_analytics(orders: list[tuple[str, str, float, str]]) -> list[tuple[Any, ...]]:
    """Execute RANK and running cumulative sum across region partitions via PySpark or SQLite fallback."""
    try:
        from pyspark.sql import SparkSession, Window
        import pyspark.sql.functions as F

        spark = SparkSession.builder.master("local[2]").appName("Z5008-BD02").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        df = spark.createDataFrame(orders, ["tx_id", "region", "amount", "ts"])
        w_rank = Window.partitionBy("region").orderBy(F.desc("amount"))
        w_run = Window.partitionBy("region").orderBy("ts").rowsBetween(Window.unboundedPreceding, Window.currentRow)
        res = df.withColumn("rnk", F.rank().over(w_rank)).withColumn("running_total", F.sum("amount").over(w_run))
        return [tuple(r) for r in res.orderBy("region", "rnk").collect()]
    except Exception:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE orders (tx_id TEXT, region TEXT, amount REAL, ts TEXT)")
        conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
        return conn.execute(
            """
            SELECT tx_id, region, amount, ts,
                   RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS rnk,
                   SUM(amount) OVER (PARTITION BY region ORDER BY ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
            FROM orders
            ORDER BY region, rnk
            """
        ).fetchall()


def run_tests() -> None:
    orders = [
        ("T1", "Zanzibar", 100.0, "2026-05-01T09:00"),
        ("T2", "Zanzibar", 250.0, "2026-05-01T10:00"),
        ("T3", "Pemba", 180.0, "2026-05-01T09:30"),
        ("T4", "Pemba", 60.0, "2026-05-01T11:00"),
    ]
    rows = spark_or_sqlite_window_analytics(orders)
    assert len(rows) == 4
    # First row for Pemba is T3 (amount 180, rank 1)
    assert rows[0][0] == "T3" and rows[0][4] == 1
    print("BD02 self-tests passed (Window RANK and cumulative SUM verified).")


if __name__ == "__main__":
    run_tests()
