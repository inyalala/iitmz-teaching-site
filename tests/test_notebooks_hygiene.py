"""Repository-wide Jupyter notebook structural and execution hygiene unittest."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COURSES_DIR = REPO_ROOT / "courses"


def _is_starter_notebook(nb_path: Path) -> bool:
    name = nb_path.name
    return (
        "STUDENT" in name
        or name.startswith(("W02_Thu_", "W03_Thu_", "W04_Thu_", "W05_Thu_", "W07_Thu_"))
    )


class TestNotebookHygiene(unittest.TestCase):
    """Verify valid nbformat v4 JSON, Python syntax, and executed reference cells across all notebooks."""

    def test_all_notebooks_valid_nbformat_v4_and_syntax(self) -> None:
        notebooks = sorted(COURSES_DIR.rglob("*.ipynb"))
        self.assertGreaterEqual(len(notebooks), 52)
        for nb_path in notebooks:
            rel = nb_path.relative_to(REPO_ROOT).as_posix()
            with self.subTest(notebook=rel):
                data = json.loads(nb_path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("nbformat"), 4, f"{rel}: expected nbformat == 4")
                cells = data.get("cells")
                self.assertIsInstance(cells, list)
                self.assertGreater(len(cells), 0, f"{rel}: no cells")

                code_cells = [c for c in cells if c.get("cell_type") == "code"]
                self.assertGreater(len(code_cells), 0, f"{rel}: no code cells")

                for idx, cell in enumerate(code_cells):
                    src_lines = cell.get("source", [])
                    src_text = "".join(src_lines) if isinstance(src_lines, list) else str(src_lines)
                    # Strip Colab shell/IPython magic lines before AST validation
                    py_lines = [
                        ln for ln in src_text.splitlines() if not ln.lstrip().startswith(("!", "%"))
                    ]
                    ast.parse("\n".join(py_lines), filename=f"{rel}#cell{idx}")

                if not _is_starter_notebook(nb_path):
                    for idx, cell in enumerate(code_cells):
                        self.assertIsNotNone(
                            cell.get("execution_count"),
                            f"{rel} cell {idx}: reference notebook must be executed",
                        )
                        self.assertIsInstance(cell.get("outputs"), list)


if __name__ == "__main__":
    unittest.main()
