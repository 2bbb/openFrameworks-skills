#!/usr/bin/env python3
"""Locate openFrameworks Project Generator executables without running them."""

from __future__ import annotations

import argparse
import json
import os
import platform
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


EXECUTABLE_NAMES = {
    "Windows": ("projectGenerator.exe", "commandLine.exe"),
    "Darwin": ("projectGenerator", "commandLine"),
    "Linux": ("projectGenerator", "commandLine"),
}


@dataclass(frozen=True)
class Candidate:
    path: str
    exists: bool
    executable: bool
    automation_safe: bool
    kind: str
    reason: str


def is_of_root(path: Path) -> bool:
    return path.is_dir() and (path / "libs").is_dir() and (path / "addons").is_dir() and (path / "scripts").is_dir()


def executable_names() -> tuple[str, ...]:
    return EXECUTABLE_NAMES.get(platform.system(), ("projectGenerator", "projectGenerator.exe", "commandLine"))


def executable_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    if platform.system() == "Windows" or path.suffix.lower() == ".exe":
        return True
    return os.access(path, os.X_OK)


def is_electron_gui_shell(path: Path) -> bool:
    """Return true for the outer macOS Electron PG app executable.

    Packaged Project Generator releases contain two binaries with similar names:
    the Electron GUI at ``*.app/Contents/MacOS/projectGenerator`` and the actual
    command-line generator under ``Contents/Resources/app/app/projectGenerator``.
    The GUI shell must not be selected for CLI automation.
    """
    parts = path.parts
    for index, part in enumerate(parts):
        if not part.lower().endswith(".app"):
            continue
        if tuple(parts[index + 1 : index + 3]) != ("Contents", "MacOS"):
            continue
        bundle_name = part[:-4].lower()
        return bundle_name.startswith("projectgenerator") and path.name.lower() == "projectgenerator"
    return False


def add_candidate(candidates: list[Candidate], path: Path, reason: str, kind: str | None = None) -> None:
    resolved = path.expanduser()
    try:
        display = str(resolved.resolve(strict=False))
    except OSError:
        display = str(resolved)
    if any(c.path == display for c in candidates):
        return
    gui_shell = is_electron_gui_shell(resolved)
    resolved_kind = kind or ("electron-gui" if gui_shell else "cli")
    candidates.append(
        Candidate(
            path=display,
            exists=resolved.is_file(),
            executable=executable_ok(resolved),
            automation_safe=resolved_kind != "electron-gui",
            kind=resolved_kind,
            reason=reason,
        )
    )


def project_generator_app_bundles(root: Path) -> list[Path]:
    """Find nearby packaged macOS PG app bundles without recursive traversal."""
    bundles: list[Path] = []
    if root.suffix.lower() == ".app":
        bundles.append(root)
    for parent in (root, root / "projectGenerator"):
        if parent.is_dir():
            bundles.extend(sorted(parent.glob("projectGenerator*.app")))
    unique: list[Path] = []
    for bundle in bundles:
        if bundle not in unique:
            unique.append(bundle)
    return unique


def preferred_candidate(candidates: Iterable[Candidate]) -> Candidate | None:
    return next((candidate for candidate in candidates if candidate.executable and candidate.automation_safe), None)


def candidate_paths(of_root: Path | None, extra_roots: Iterable[Path]) -> list[Candidate]:
    candidates: list[Candidate] = []
    roots: list[Path] = []
    if of_root is not None:
        roots.append(of_root)
    env_root = os.environ.get("PG_OF_PATH")
    if env_root:
        roots.append(Path(env_root))
    roots.extend(extra_roots)

    names = executable_names()
    for root in roots:
        root = root.expanduser()
        for name in names:
            add_candidate(candidates, root / "projectGenerator" / "commandLine" / "bin" / name, "source commandLine bin")
            add_candidate(candidates, root / "apps" / "projectGenerator" / "commandLine" / "bin" / name, "openFrameworks apps/projectGenerator bin")
            add_candidate(candidates, root / "projectGenerator" / "resources" / "app" / "app" / name, "packaged Electron resources app")
            add_candidate(candidates, root / "projectGenerator" / name, "projectGenerator folder")
            add_candidate(candidates, root / "projectGenerator" / "commandLine" / name, "commandLine folder")
            add_candidate(candidates, root / "projectGenerator" / "projectGenerator.app" / "Contents" / "MacOS" / name, "macOS app bundle")
            add_candidate(candidates, root / "projectGenerator" / "commandLine.app" / "Contents" / "MacOS" / name, "macOS commandLine app bundle")
            add_candidate(candidates, root / "scripts" / "projectGenerator" / name, "scripts projectGenerator")
        if platform.system() == "Darwin":
            for app_bundle in project_generator_app_bundles(root):
                for name in names:
                    add_candidate(
                        candidates,
                        app_bundle / "Contents" / "Resources" / "app" / "app" / name,
                        "CLI embedded in packaged Electron app",
                    )
                    add_candidate(
                        candidates,
                        app_bundle / "Contents" / "MacOS" / name,
                        "outer Electron GUI executable; do not use for CLI automation",
                        kind="electron-gui",
                    )

    for name in names:
        for directory in os.environ.get("PATH", "").split(os.pathsep):
            if directory:
                path = Path(directory) / name
                if path.is_file():
                    add_candidate(candidates, path, "PATH")
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Locate openFrameworks Project Generator executable candidates without executing them.")
    parser.add_argument("--of-root", type=Path, help="Path to an openFrameworks root directory.")
    parser.add_argument("--search-root", type=Path, action="append", default=[], help="Additional root to search. May be repeated.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--first", action="store_true", help="Print only the first executable candidate path.")
    args = parser.parse_args()

    if args.of_root and not is_of_root(args.of_root.expanduser()):
        parser.error(f"--of-root does not look like an openFrameworks root: {args.of_root}")

    candidates = candidate_paths(args.of_root, args.search_root)
    preferred = preferred_candidate(candidates)

    if args.first:
        if preferred:
            print(preferred.path)
            return 0
        return 1

    if args.json:
        print(json.dumps({"preferred": asdict(preferred) if preferred else None, "candidates": [asdict(c) for c in candidates]}, indent=2))
        return 0 if preferred else 1

    if preferred:
        print(f"preferred: {preferred.path}")
    else:
        print("preferred: <none found>")
    for c in candidates:
        status = "unsafe-gui" if c.executable and not c.automation_safe else "executable" if c.executable else "exists" if c.exists else "missing"
        print(f"{status}\t{c.path}\t# {c.reason}")
    return 0 if preferred else 1


if __name__ == "__main__":
    raise SystemExit(main())
