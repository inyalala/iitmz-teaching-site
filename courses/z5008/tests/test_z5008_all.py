"""Automated unittest self-test suite verifying all 7 Z5008 Big Data Lab Python modules."""

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


class TestZ5008BigDataLab(unittest.TestCase):
    """Run all BD01-BD07 Lakehouse, Spark, Airflow, Streaming, MLlib, MLflow, and Telemetry modules."""

    def test_all_bd_modules_pass(self) -> None:
        scripts = sorted((COURSE_ROOT / "code").glob("bd*.py"))
        self.assertEqual(len(scripts), 7, f"Expected 7 bd scripts, found {len(scripts)}")
        for script in scripts:
            with self.subTest(module=script.name):
                mod = _load_module(script)
                self.assertTrue(hasattr(mod, "run_tests"), f"{script.name} missing run_tests()")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    mod.run_tests()
                self.assertIn("passed", buf.getvalue().lower())

    def test_prometheus_quantiles_monotonic(self) -> None:
        bd05 = _load_module(COURSE_ROOT / "code/bd05_pipeline_telemetry_observability.py")
        vals = [10.0, 20.0, 35.0, 50.0, 120.0]
        self.assertLessEqual(bd05.percentile(vals, 50), bd05.percentile(vals, 95))
        self.assertLessEqual(bd05.percentile(vals, 95), bd05.percentile(vals, 99))


if __name__ == "__main__":
    unittest.main()
