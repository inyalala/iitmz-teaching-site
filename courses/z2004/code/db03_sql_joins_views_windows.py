"""Z2004 Lab 03: Complex SQL Joins, Subqueries, CTEs, Window Functions, and Views in SQLite."""

from __future__ import annotations

import sqlite3


def run_tests() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE Students (StudentID TEXT PRIMARY KEY, Name TEXT, Year INT, Hostel TEXT);
        CREATE TABLE FoodItems (ItemID TEXT PRIMARY KEY, Name TEXT UNIQUE, Category TEXT, Price REAL);
        CREATE TABLE Orders (OrderID INT PRIMARY KEY, StudentID TEXT, ItemName TEXT, Qty INT);

        INSERT INTO Students VALUES
            ('S1', 'Asha', 2, 'Kizingo'),
            ('S2', 'Omar', 2, 'Kizingo'),
            ('S3', 'Zahra', 3, 'Mbweni'),
            ('S4', 'Juma', 1, 'Mbweni');

        INSERT INTO FoodItems VALUES
            ('F1', 'Pilau', 'Main', 5.50),
            ('F2', 'Urojo', 'Snack', 2.00),
            ('F3', 'Chai', 'Drink', 1.00);

        INSERT INTO Orders VALUES
            (1, 'S1', 'Pilau', 2),
            (2, 'S1', 'Chai', 3),
            (3, 'S2', 'Urojo', 4),
            (4, 'S3', 'Pilau', 1);

        CREATE VIEW StudentSpend AS
        SELECT s.StudentID, s.Name, s.Hostel,
               COALESCE(SUM(o.Qty * f.Price), 0.0) AS TotalSpend
        FROM Students s
        LEFT JOIN Orders o ON s.StudentID = o.StudentID
        LEFT JOIN FoodItems f ON o.ItemName = f.Name
        GROUP BY s.StudentID, s.Name, s.Hostel;
        """
    )

    spend = dict(conn.execute("SELECT Name, TotalSpend FROM StudentSpend").fetchall())
    assert spend == {"Asha": 14.0, "Omar": 8.0, "Zahra": 5.5, "Juma": 0.0}

    # Window function ranking inside Hostel
    ranked = conn.execute(
        """
        WITH SpendCTE AS (SELECT * FROM StudentSpend)
        SELECT Name, Hostel, TotalSpend,
               RANK() OVER (PARTITION BY Hostel ORDER BY TotalSpend DESC) AS HostelRank
        FROM SpendCTE
        ORDER BY Hostel, HostelRank, Name
        """
    ).fetchall()
    assert ranked[0][:2] == ("Asha", "Kizingo") and ranked[0][3] == 1
    print("DB03 self-tests passed (LEFT JOIN, View, CTE, and Window RANK verified).")


if __name__ == "__main__":
    run_tests()
