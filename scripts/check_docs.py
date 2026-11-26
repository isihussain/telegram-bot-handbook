#!/usr/bin/env python3
"""Offline checks for this repository.

Runs without a bot token and without network access:

* every docs page has a title, TL;DR, Applies-to line and a Sources section
* every relative link points at a file that exists (or at a page listed in llms.txt)
* code fences are balanced
* every Python file in src/, examples/ and tests/ compiles

Usage:
    python scripts/check_docs.py            # allows links to pages listed in llms.txt
    python scripts/check_docs.py --strict   # every linked file must exist

The non-strict mode exists so a category can be merged before the pages it links to
from other categories. ``--strict`` is what you run before a release.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANIFEST = ROOT / "llms.txt"

REQUIRED_MARKERS = ("**TL;DR:**", "**Applies to:**")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
DOC_PATH_PATTERN = re.compile(r"docs/[A-Za-z0-9_./-]+\.md")
SKIP_SCHEMES = ("http://", "https://", "mailto:", "#", "tg://")
FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Remove fenced and inline code so examples are not mistaken for links."""
    return INLINE_CODE.sub("", FENCED_BLOCK.sub("", text))


def manifest_pages() -> set[str]:
    if not MANIFEST.exists():
        return set()
    return set(DOC_PATH_PATTERN.findall(MANIFEST.read_text(encoding="utf-8")))


def markdown_files() -> list[Path]:
    return sorted(DOCS.rglob("*.md"))


def check_page(path: Path, manifest: set[str], strict: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    relative = path.relative_to(ROOT)

    if not lines or not lines[0].startswith("# "):
        errors.append(f"{relative}: first line must be a level-1 heading")

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"{relative}: missing {marker}")

    if "\n## Sources\n" not in text:
        errors.append(f"{relative}: missing '## Sources' section")

    if text.count("\n```") % 2 != 0:
        errors.append(f"{relative}: unbalanced code fences")

    for target in LINK_PATTERN.findall(strip_code(text)):
        if target.startswith(SKIP_SCHEMES):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        if resolved.exists():
            continue
        planned = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else ""
        if not strict and planned in manifest:
            continue
        errors.append(f"{relative}: broken link -> {target}")

    return errors


def check_readme(manifest: set[str], strict: bool) -> list[str]:
    errors: list[str] = []
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(strip_code(text)):
        if target.startswith(SKIP_SCHEMES):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        resolved = (ROOT / clean).resolve()
        if resolved.exists():
            continue
        planned = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else ""
        if not strict and planned in manifest:
            continue
        errors.append(f"README.md: broken link -> {target}")
    return errors


def check_python() -> list[str]:
    errors: list[str] = []
    patterns = ("src/**/*.py", "examples/*.py", "tests/*.py", "scripts/*.py")
    for pattern in patterns:
        for path in sorted(ROOT.glob(pattern)):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def check_index_coverage() -> list[str]:
    """Every docs page must be reachable from README.md or llms.txt."""
    errors: list[str] = []
    indexes = ""
    for name in ("README.md", "llms.txt"):
        candidate = ROOT / name
        if candidate.exists():
            indexes += candidate.read_text(encoding="utf-8")
    for path in markdown_files():
        if path.name == "_TEMPLATE.md":
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative not in indexes:
            errors.append(f"{relative}: not listed in README.md or llms.txt")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="require every linked file to exist instead of allowing llms.txt entries",
    )
    args = parser.parse_args()

    manifest = manifest_pages()
    errors: list[str] = []
    pages = markdown_files()
    if not pages:
        errors.append("docs/: no markdown pages found")

    for page in pages:
        errors.extend(check_page(page, manifest, args.strict))
    errors.extend(check_readme(manifest, args.strict))
    errors.extend(check_python())
    errors.extend(check_index_coverage())

    if errors:
        print(f"{len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    mode = "strict" if args.strict else "manifest-aware"
    print(f"OK: {len(pages)} docs pages, links ({mode}), fences and Python files are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
