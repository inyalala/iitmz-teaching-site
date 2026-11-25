"""CLI utility to add or update a course slide deck, notebook, or lab handout."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COURSE_MAP = {
    "z2005": ROOT / "courses" / "z2005",
    "z5007": ROOT / "courses" / "z5007",
    "z3003": ROOT / "courses" / "dm-scale",
    "z2004": ROOT / "courses" / "z2004",
    "z5008": ROOT / "courses" / "z5008",
}

LARGE_FILE_WARN_MB = 40.0
LARGE_FILE_BLOCK_MB = 95.0


def sanitize_filename(name: str, expected_suffix: str) -> str:
    p = Path(name)
    if p.name != Path(p.name).name or "/" in name or "\\" in name:
        raise ValueError("Target filename must not contain path separators.")
    stem = re.sub(r"[^a-z0-9._-]+", "_", p.stem.lower()).strip("._-")
    if not stem or stem in {".", ".."}:
        raise ValueError(f"Unsafe or empty sanitized filename from {name!r}.")
    suffix = p.suffix.lower() or expected_suffix.lower()
    if suffix != expected_suffix.lower():
        raise ValueError(
            f"Filename extension {suffix!r} does not match source extension {expected_suffix!r}. "
            "Pass --allow-ext-change to override."
        )
    return f"{stem}{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a lecture slide PDF, HTML deck, PPTX, or Jupyter notebook into iitmz-teaching-site."
    )
    parser.add_argument(
        "--course",
        required=True,
        choices=sorted(COURSE_MAP.keys()),
        help="Target course code (z2005, z5007, z3003, z2004, or z5008).",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the source file (.pdf, .html, .pptx, .ipynb, etc.).",
    )
    parser.add_argument(
        "--subdir",
        default="slides",
        help="Relative folder inside the course directory (e.g. 'slides', 'lectures', '07-sorting', 'tutorials').",
    )
    parser.add_argument(
        "--name",
        default="",
        help="Optional target filename (defaults to sanitized lowercase source filename).",
    )
    parser.add_argument(
        "--allow-ext-change",
        action="store_true",
        help="Allow --name to change the file extension from the source file.",
    )
    parser.add_argument(
        "--allow-large",
        action="store_true",
        help="Override the 95 MB GitHub binary block guard (not recommended; prefer GitHub Releases).",
    )
    args = parser.parse_args()

    src = Path(args.file).expanduser().resolve()
    if not src.exists() or not src.is_file():
        print(f"Error: source file not found: {src}", file=sys.stderr)
        return 1

    size_mb = src.stat().st_size / (1024 * 1024)
    if size_mb >= LARGE_FILE_BLOCK_MB and not args.allow_large:
        print(
            f"Error: {src.name} is {size_mb:.1f} MB (GitHub rejects files >= 100 MB).\n"
            "Upload large datasets, videos, or archives to GitHub Releases on inyalala/iitmz-teaching-site "
            "and link the Release asset URL instead.",
            file=sys.stderr,
        )
        return 1
    if size_mb > LARGE_FILE_WARN_MB:
        print(
            f"Warning: {src.name} is {size_mb:.1f} MB (GitHub warns above 50 MB). Consider GitHub Releases.",
            file=sys.stderr,
        )

    course_dir = COURSE_MAP[args.course].resolve()
    target_dir = (course_dir / args.subdir).resolve()
    try:
        target_dir.relative_to(course_dir)
    except ValueError:
        print("Error: --subdir escapes the selected course directory.", file=sys.stderr)
        return 1

    raw_name = args.name or src.name
    try:
        if args.allow_ext_change:
            p = Path(raw_name)
            if p.name != raw_name or "/" in raw_name or "\\" in raw_name:
                raise ValueError("Target filename must not contain path separators.")
            stem = re.sub(r"[^a-z0-9._-]+", "_", p.stem.lower()).strip("._-")
            if not stem or stem in {".", ".."}:
                raise ValueError(f"Unsafe filename: {raw_name!r}")
            target_name = f"{stem}{p.suffix.lower()}"
        else:
            target_name = sanitize_filename(raw_name, src.suffix)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    dest = (target_dir / target_name).resolve()
    try:
        dest.relative_to(target_dir)
    except ValueError:
        print("Error: resolved destination escapes target folder.", file=sys.stderr)
        return 1

    existed = dest.exists()
    shutil.copy2(src, dest)

    rel_course = dest.relative_to(course_dir).as_posix()
    rel_repo = dest.relative_to(ROOT).as_posix()
    public_url = f"https://inyalala.github.io/iitmz-teaching-site/{rel_repo}"

    action = "Updated existing file" if existed else "Copied new file"
    print(f"{action}: {dest}")
    print(f"Course relative link: {rel_course}")
    print(f"Live student URL (after push): {public_url}")

    index_html = course_dir / "index.html"
    if index_html.exists():
        content = index_html.read_text(encoding="utf-8", errors="ignore")
        if rel_course in content:
            print(f"Index check: {rel_course} is already linked in {index_html.name}.")
        else:
            print(f'Index check: add `<a href="{rel_course}">` to {index_html} if this is a new session.')

    print("\nNext commands:")
    print(f'  git add "{rel_repo}"')
    print(f'  git commit -m "docs({args.course}): update {target_name}"')
    print("  git push origin main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
