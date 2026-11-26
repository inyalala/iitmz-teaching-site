"""Automated sitemap.xml, canonical, OpenGraph/Twitter SEO, and JSON-LD parity checks."""

import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://inyalala.github.io/iitmz-teaching-site/"
CANONICAL_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*>', re.IGNORECASE)
OG_TITLE_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]*>', re.IGNORECASE)
TWITTER_CARD_RE = re.compile(r'<meta[^>]+name=["\']twitter:card["\'][^>]*>', re.IGNORECASE)
JSONLD_RE = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


class TestSitemapAndSeoParity(unittest.TestCase):
    """Verify sitemap parity, SEO meta tags, and JSON-LD across all HTML pages."""

    def test_sitemap_matches_all_html_pages(self) -> None:
        sitemap_path = REPO_ROOT / "sitemap.xml"
        self.assertTrue(sitemap_path.exists(), "sitemap.xml must exist")

        tree = ET.parse(sitemap_path)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = {
            el.text.strip()
            for el in tree.getroot().findall("sm:url/sm:loc", ns)
            if el.text
        }

        html_urls = set()
        for html_path in sorted(REPO_ROOT.rglob("*.html")):
            rel = html_path.relative_to(REPO_ROOT).as_posix()
            url = BASE_URL if rel == "index.html" else f"{BASE_URL}{rel}"
            html_urls.add(url)

        self.assertEqual(
            html_urls - sitemap_urls,
            set(),
            f"HTML pages missing from sitemap.xml: {sorted(html_urls - sitemap_urls)}",
        )
        self.assertEqual(
            sitemap_urls - html_urls,
            set(),
            f"Stale URLs in sitemap.xml: {sorted(sitemap_urls - html_urls)}",
        )

    def test_all_html_pages_seo_and_jsonld(self) -> None:
        for html_path in sorted(REPO_ROOT.rglob("*.html")):
            rel = html_path.relative_to(REPO_ROOT).as_posix()
            text = html_path.read_text(encoding="utf-8")

            self.assertTrue(
                CANONICAL_RE.search(text), f"{rel}: missing canonical link"
            )
            if 'http-equiv="refresh"' in text.lower():
                continue

            self.assertTrue(
                OG_TITLE_RE.search(text), f"{rel}: missing og:title meta"
            )
            self.assertTrue(
                TWITTER_CARD_RE.search(text), f"{rel}: missing twitter:card meta"
            )

            ld_blocks = JSONLD_RE.findall(text)
            self.assertGreaterEqual(
                len(ld_blocks), 1, f"{rel}: missing application/ld+json block"
            )
            for raw_json in ld_blocks:
                data = json.loads(raw_json)
                self.assertEqual(
                    data.get("@context"),
                    "https://schema.org",
                    f"{rel}: JSON-LD @context must be https://schema.org",
                )
                if "@graph" in data:
                    self.assertTrue(
                        isinstance(data["@graph"], list) and len(data["@graph"]) > 0,
                        f"{rel}: JSON-LD @graph must be non-empty list",
                    )
                    for item in data["@graph"]:
                        self.assertIn("@type", item, f"{rel}: @graph item missing @type")
                else:
                    self.assertIn("@type", data, f"{rel}: JSON-LD missing @type")


if __name__ == "__main__":
    unittest.main()
