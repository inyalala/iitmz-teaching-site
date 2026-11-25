"""Z2004 Lab 01: ER-to-Relational DDL Schema, Integrity Constraints, and Foreign Key Cascades."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def build_school_db(conn: sqlite3.Connection) -> None:
    """Create Student, Course, and Enrolment tables with PK, FK, UNIQUE, and CHECK constraints."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(
        """
        DROP TABLE IF EXISTS Enrolment;
        DROP TABLE IF EXISTS Course;
        DROP TABLE IF EXISTS Student;

        CREATE TABLE Student (
            SID   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name  TEXT NOT NULL,
            Dept  TEXT NOT NULL,
            GPA   REAL CHECK (GPA IS NULL OR (GPA BETWEEN 0.00 AND 4.00)),
            Email TEXT UNIQUE
        );
        CREATE TABLE Course (
            CID     TEXT PRIMARY KEY,
            CName   TEXT NOT NULL,
            Credits INTEGER NOT NULL DEFAULT 3 CHECK (Credits IN (1, 2, 3, 4))
        );
        CREATE TABLE Enrolment (
            SID   INTEGER NOT NULL,
            CID   TEXT NOT NULL,
            Grade TEXT CHECK (Grade IN ('A', 'B', 'C', 'D', 'F') OR Grade IS NULL),
            PRIMARY KEY (SID, CID),
            FOREIGN KEY (SID) REFERENCES Student(SID) ON DELETE CASCADE,
            FOREIGN KEY (CID) REFERENCES Course(CID) ON DELETE CASCADE
        );
        """
    )
    conn.executemany(
        "INSERT INTO Student (Name, Dept, GPA, Email) VALUES (?, ?, ?, ?)",
        [
            ("Asha Ali", "CSE", 3.80, "asha.ali@iitmz.example"),
            ("Omar Said", "CSE", 3.20, "omar.said@iitmz.example"),
            ("Zahra Musa", "EEE", None, "zahra.musa@iitmz.example"),
        ],
    )
    conn.executemany(
        "INSERT INTO Course (CID, CName, Credits) VALUES (?, ?, ?)",
        [("DB101", "Database Management Systems", 3), ("CS102", "Data Structures", 4)],
    )
    conn.executemany(
        "INSERT INTO Enrolment (SID, CID, Grade) VALUES (?, ?, ?)",
        [(1, "DB101", "A"), (1, "CS102", "A"), (2, "DB101", "B")],
    )
    conn.commit()


def run_tests() -> None:
    conn = sqlite3.connect(":memory:")
    build_school_db(conn)

    # Check GPA constraint violation
    try:
        conn.execute("INSERT INTO Student (Name, Dept, GPA, Email) VALUES ('Bad', 'CSE', 4.9, 'x@y.z')")
        raise AssertionError("Expected IntegrityError for GPA > 4.00")
    except sqlite3.IntegrityError:
        pass

    # Check Foreign Key rejection
    try:
        conn.execute("INSERT INTO Enrolment (SID, CID, Grade) VALUES (999, 'DB101', 'A')")
        raise AssertionError("Expected IntegrityError for nonexistent SID")
    except sqlite3.IntegrityError:
        pass

    # Check ON DELETE CASCADE
    conn.execute("DELETE FROM Student WHERE SID = 1")
    rem = conn.execute("SELECT COUNT(*) FROM Enrolment WHERE SID = 1").fetchone()[0]
    assert rem == 0
    print("DB01 self-tests passed (DDL constraints and ON DELETE CASCADE verified).")


if __name__ == "__main__":
    run_tests()
