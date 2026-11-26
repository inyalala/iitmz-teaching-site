"""Automated HTML, link, and prose integrity checks for the teaching portal."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_OPEN_RE = re.compile(r"<h1\b", re.IGNORECASE)
DETAILS_OPEN_RE = re.compile(r"<details\b", re.IGNORECASE)
DETAILS_CLOSE_RE = re.compile(r"</details>", re.IGNORECASE)
SCRIPT_OPEN_RE = re.compile(r"<script\b", re.IGNORECASE)
SCRIPT_CLOSE_RE = re.compile(r"</script>", re.IGNORECASE)
ATTR_RE = re.compile(r"""(?:href|src)=["']([^"']+)["']""", re.IGNORECASE)


class TestPortalHtmlIntegrity(unittest.TestCase):
    """Verify structural HTML invariants, local links, and zero em-dashes."""

    def test_all_html_pages_structure_links_and_prose(self) -> None:
        html_files = sorted(REPO_ROOT.rglob("*.html"))
        self.assertGreaterEqual(len(html_files), 34)

        checked_links = 0
        for html_path in html_files:
            rel_path = html_path.relative_to(REPO_ROOT).as_posix()
            text = html_path.read_text(encoding="utf-8")

            titles = TITLE_RE.findall(text)
            self.assertEqual(
                len(titles), 1, f"{rel_path}: expected 1 <title>, found {len(titles)}"
            )
            self.assertTrue(
                titles[0].strip(), f"{rel_path}: <title> text must not be empty"
            )

            h1_count = len(H1_OPEN_RE.findall(text))
            self.assertEqual(
                h1_count, 1, f"{rel_path}: expected 1 <h1>, found {h1_count}"
            )

            details_open = len(DETAILS_OPEN_RE.findall(text))
            details_close = len(DETAILS_CLOSE_RE.findall(text))
            self.assertEqual(
                details_open,
                details_close,
                f"{rel_path}: unbalanced <details> ({details_open} vs {details_close})",
            )

            script_open = len(SCRIPT_OPEN_RE.findall(text))
            script_close = len(SCRIPT_CLOSE_RE.findall(text))
            self.assertEqual(
                script_open,
                script_close,
                f"{rel_path}: unbalanced <script> ({script_open} vs {script_close})",
            )

            self.assertNotIn("\u2014", text, f"{rel_path}: Unicode em-dash found")
            self.assertNotIn("&mdash;", text, f"{rel_path}: &mdash; entity found")
            self.assertNotIn("&#8212;", text, f"{rel_path}: &#8212; entity found")

            for raw_ref in ATTR_RE.findall(text):
                if raw_ref.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")):
                    continue
                clean_ref = unquote(raw_ref.split("#", 1)[0].split("?", 1)[0])
                if not clean_ref:
                    continue
                target = (html_path.parent / clean_ref).resolve()
                self.assertTrue(
                    target.exists(),
                    f"{rel_path}: broken local reference '{raw_ref}' -> {target}",
                )
                checked_links += 1

        self.assertGreater(checked_links, 500)


if __name__ == "__main__":
    unittest.main()
