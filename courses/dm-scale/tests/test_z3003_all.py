"""Automated unittest self-test suite verifying all Z3003 Data Mining modules and Mini-Project starter."""

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


class TestZ3003DataMining(unittest.TestCase):
    """Run all DM01-DM09 modules and MP01 Mini-Project starter pipeline."""

    def test_all_dm_and_starter_modules_pass(self) -> None:
        scripts = sorted(list((COURSE_ROOT / "code").glob("dm*.py")) + list((COURSE_ROOT / "code").glob("mp*.py")))
        self.assertEqual(len(scripts), 10, f"Expected 9 dm + 1 mp scripts, found {len(scripts)}")
        for script in scripts:
            with self.subTest(module=script.name):
                mod = _load_module(script)
                self.assertTrue(hasattr(mod, "run_tests"), f"{script.name} missing run_tests()")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    mod.run_tests()
                self.assertIn("passed", buf.getvalue().lower())

    def test_key_dm_formulas(self) -> None:
        dm05 = _load_module(COURSE_ROOT / "code/dm05_lsh_minhash.py")
        self.assertAlmostEqual(dm05.jaccard({"a", "b", "c"}, {"b", "c", "d", "e"}), 0.4, places=6)
        self.assertAlmostEqual(dm05.s_curve_probability(0.5, bands=20, rows=5), 1.0 - (1.0 - 0.5**5) ** 20, places=6)

        dm08 = _load_module(COURSE_ROOT / "code/dm08_pagerank_link_analysis.py")
        ranks, _ = dm08.pagerank({"A": ["B"], "B": ["C"], "C": ["A"]})
        self.assertAlmostEqual(sum(ranks.values()), 1.0, places=5)
        self.assertAlmostEqual(ranks["A"], 1.0 / 3.0, places=3)


if __name__ == "__main__":
    unittest.main()
