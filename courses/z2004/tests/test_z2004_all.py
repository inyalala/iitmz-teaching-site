"""Automated unittest self-test suite verifying all 8 Z2004 DBMS modules and School SQL DDL."""

from __future__ import annotations

import importlib.util
import io
import sqlite3
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent


def _load_module(py_path: Path):
    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[py_path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


class TestZ2004DBMS(unittest.TestCase):
    """Run all DB01-DB08 SQLite/Python modules and validate SQL schema execution."""

    def test_all_db_modules_pass(self) -> None:
        scripts = sorted((COURSE_ROOT / "code").glob("db*.py"))
        self.assertEqual(len(scripts), 8, f"Expected 8 db scripts, found {len(scripts)}")
        for script in scripts:
            with self.subTest(module=script.name):
                mod = _load_module(script)
                self.assertTrue(hasattr(mod, "run_tests"), f"{script.name} missing run_tests()")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    mod.run_tests()
                self.assertIn("passed", buf.getvalue().lower())

    def test_school_sql_schema_loads_cleanly(self) -> None:
        sql_path = COURSE_ROOT / "code/z2004_school_schema.sql"
        self.assertTrue(sql_path.exists())
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(sql_path.read_text(encoding="utf-8"))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertGreaterEqual(len(tables), 3)
        conn.close()

    def test_normalization_and_serializability(self) -> None:
        db04 = _load_module(COURSE_ROOT / "code/db04_normalization_fd_checker.py")
        fds = [(frozenset("A"), frozenset("B")), (frozenset("BC"), frozenset("D")), (frozenset("D"), frozenset("E"))]
        keys = db04.find_candidate_keys(frozenset("ABCDE"), fds)
        self.assertEqual(keys, [frozenset("AC")])

        db07 = _load_module(COURSE_ROOT / "code/db07_query_optimization_joins.py")
        self.assertEqual(db07.cost_block_nested_loop(1000, 500, 52), 11000)
        self.assertEqual(db07.cost_grace_hash_join(1000, 500, 52), 4500)


if __name__ == "__main__":
    unittest.main()
