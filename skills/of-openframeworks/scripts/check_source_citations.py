#!/usr/bin/env python3
"""Lint distributed oF skill files for non-portable source citations.

The skills are distributed without the repo-local mirrored source checkout, so source
hints must point to upstream/source-relative paths such as openFrameworks/libs/...
or projectGenerator/commandLine/... instead of repo-local mirrored checkout paths.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("repo-local reference-directory path", re.compile(re.escape("reference" + "/"))),
    ("repo-local openFrameworks citation", re.compile(re.escape("reference" + "/" + "openFrameworks" + "/"))),
    ("repo-local projectGenerator citation", re.compile(re.escape("reference" + "/" + "projectGenerator" + "/"))),
    ("repo-local of-skill citation", re.compile(re.escape("reference" + "/" + "of-skill" + "/"))),
    ("placeholder marker", re.compile(r"\b(?:" + "TO" + "DO|FIX" + "ME|T" + "BD|X" + "XX)\b", re.IGNORECASE)),
)

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".sh",
    ".py",
}


def default_skills_root() -> Path:
    # .../skills/of-openframeworks/scripts/check_source_citations.py -> .../skills
    return Path(__file__).resolve().parents[2]


def iter_distributed_files(skills_root: Path):
    for skill_dir in sorted(skills_root.glob("of-*")):
        if not skill_dir.is_dir():
            continue
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            if any(part in {".git", "__pycache__"} for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_SUFFIXES or path.name == "SKILL.md":
                yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=default_skills_root(),
        help="Path containing distributed of-* skill directories (default: repo skills/).",
    )
    args = parser.parse_args(argv)

    skills_root = args.skills_root.resolve()
    failures: list[str] = []
    for path in iter_distributed_files(skills_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    rel = path.relative_to(skills_root.parent) if skills_root.parent in path.parents else path
                    failures.append(f"{rel}:{lineno}: {label}: {line.strip()}")

    if failures:
        print("Source citation lint failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Source citation lint passed for {skills_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
