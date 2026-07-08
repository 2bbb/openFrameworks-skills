#!/usr/bin/env python3
"""Repository validation for the openFrameworks Codex skills."""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FORBIDDEN = [
    "reference/",
    "working-docs/",
    "of-skill/",
    "TODO",
    "FIXME",
    "TBD",
    "XXX",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail(f"{path}: unterminated YAML frontmatter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"{path}: invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_skills() -> None:
    if not SKILLS.is_dir():
        fail("missing skills/ directory")
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        fail("no skill directories found")
    for skill in skill_dirs:
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            fail(f"{skill}: missing SKILL.md")
        meta = parse_frontmatter(skill_md)
        if meta.get("name") != skill.name:
            fail(f"{skill_md}: name {meta.get('name')!r} does not match directory {skill.name!r}")
        if len(meta.get("description", "")) < 50:
            fail(f"{skill_md}: description is too short for routing")


def validate_no_forbidden_text() -> None:
    scan_roots = [ROOT / "README.md", ROOT / "examples", ROOT / "scripts", SKILLS, ROOT / ".github"]
    for base in scan_roots:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for path in paths:
            if path.name == "validate_repo.py":
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in FORBIDDEN:
                if marker in text:
                    fail(f"{path}: forbidden marker {marker!r}")


def validate_python() -> None:
    for path in sorted((ROOT / "scripts").glob("*.py")) + sorted(SKILLS.glob("*/scripts/*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def validate_shell() -> None:
    for path in sorted(SKILLS.glob("*/scripts/*.sh")):
        run(["bash", "-n", str(path)])


def validate_help() -> None:
    help_scripts = [
        SKILLS / "of-build-test/scripts/of-build-run.sh",
        SKILLS / "of-project-generator/scripts/locate_project_generator.py",
        SKILLS / "of-ci/scripts/of-ci-template.sh",
        SKILLS / "of-ci/scripts/validate_workflow.py",
        SKILLS / "of-shader-glsl/scripts/check_shader_assets.py",
        SKILLS / "of-openframeworks/scripts/check_source_citations.py",
    ]
    for path in help_scripts:
        if path.exists():
            run([str(path), "--help"])


def validate_agents() -> None:
    agent = ROOT / "agents/openai.yaml"
    if not agent.is_file():
        fail("missing agents/openai.yaml")
    text = agent.read_text(encoding="utf-8")
    for skill in sorted(p.name for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if f"${skill}" not in text:
            fail(f"agents/openai.yaml does not mention ${skill}")


def main() -> int:
    validate_skills()
    validate_no_forbidden_text()
    validate_python()
    validate_shell()
    validate_help()
    validate_agents()
    run(["python3", "skills/of-openframeworks/scripts/check_source_citations.py"])
    print("OK: repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
