"""Automated unittest self-test suite verifying all 17 Z5007 Python reference modules (Weeks 1-17)."""

from __future__ import annotations

import importlib.util
import io
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


class TestZ5007Weeks01To17(unittest.TestCase):
    """Run every Week 1-17 reference module self-test plus targeted invariant checks."""

    def test_all_weekly_modules_pass(self) -> None:
        week_scripts = sorted(COURSE_ROOT.glob("week-*/code/w*.py"))
        self.assertEqual(len(week_scripts), 17, f"Expected 17 weekly scripts, found {len(week_scripts)}")
        for script in week_scripts:
            with self.subTest(module=script.name):
                mod = _load_module(script)
                self.assertTrue(hasattr(mod, "run_tests"), f"{script.name} missing run_tests()")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    mod.run_tests()
                self.assertIn("passed", buf.getvalue().lower())

    def test_core_algorithm_contracts(self) -> None:
        w02 = _load_module(COURSE_ROOT / "week-02/code/w02_arrays_binary_search_sorts.py")
        self.assertEqual(w02.binary_search([2, 5, 8, 12, 16, 23], 23), 5)
        self.assertEqual(w02.binary_search([2, 5, 8, 12, 16, 23], 99), -1)

        w07 = _load_module(COURSE_ROOT / "week-07/code/w07_avl_trees.py")
        root = None
        for k in [10, 20, 30, 40, 50, 25]:
            root = w07.avl_insert(root, k)
        w07.verify_avl(root)
        self.assertEqual(w07.avl_inorder(root), [10, 20, 25, 30, 40, 50])

        w12 = _load_module(COURSE_ROOT / "week-12/code/w12_dynamic_programming.py")
        items = [(3, 2), (4, 3), (5, 4), (6, 5)]  # (value, weight)
        val, chosen = w12.knapsack_01(5, items)
        self.assertEqual(val, 7)
        self.assertEqual(sum(items[i][1] for i in chosen), 5)

        w14 = _load_module(COURSE_ROOT / "week-14/code/w14_string_matching_tries.py")
        self.assertEqual(w14.compute_lps("ABABAC"), [0, 0, 1, 2, 3, 0])
        self.assertEqual(w14.kmp_search("ABABABAC", "ABABAC"), [2])

    def test_project_benchmark_starter_passes(self) -> None:
        proj = _load_module(COURSE_ROOT / "project/p01_project_benchmark_starter.py")
        buf = io.StringIO()
        with redirect_stdout(buf):
            proj.run_tests()
        self.assertIn("passed", buf.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
