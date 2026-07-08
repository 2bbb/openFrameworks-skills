#!/usr/bin/env python3
"""Static checks for common openFrameworks addon authoring mistakes."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VALID_SECTIONS = {
    "meta",
    "common",
    "linux",
    "linux64",
    "linux/64",
    "msys2",
    "vs",
    "linuxarmv6l",
    "linuxarmv7l",
    "linuxaarch64",
    "linux/armv6l",
    "linux/armv7l",
    "linux/aarch64",
    "linux/arm64",
    "android/armeabi",
    "android/armeabi-v7a",
    "android/arm64-v8a",
    "android/x86",
    "android/x86_64",
    "emscripten",
    "emscripten/32",
    "emscripten/64",
    "android",
    "ios",
    "osx",
    "tvos",
    "macos",
    "watchos",
    "visionos",
    "catos",
}

META_KEYS = {
    "ADDON_NAME",
    "ADDON_DESCRIPTION",
    "ADDON_AUTHOR",
    "ADDON_TAGS",
    "ADDON_URL",
}

PROJECT_KEYS = {
    "ADDON_DEPENDENCIES",
    "ADDON_INCLUDES",
    "ADDON_CFLAGS",
    "ADDON_CPPFLAGS",
    "ADDON_LDFLAGS",
    "ADDON_LIBS",
    "ADDON_DEFINES",
    "ADDON_SOURCES",
    "ADDON_HEADER_SOURCES",
    "ADDON_C_SOURCES",
    "ADDON_CPP_SOURCES",
    "ADDON_OBJC_SOURCES",
    "ADDON_LIBS_EXCLUDE",
    "ADDON_LIBS_DIR",
    "ADDON_SOURCES_EXCLUDE",
    "ADDON_INCLUDES_EXCLUDE",
    "ADDON_FRAMEWORKS_EXCLUDE",
    "ADDON_DATA",
    "ADDON_PKG_CONFIG_LIBRARIES",
    "ADDON_FRAMEWORKS",
    "ADDON_DLLS_TO_COPY",
    "ADDON_ADDITIONAL_LIBS",
}

EXCLUDE_KEYS = {
    "ADDON_LIBS_EXCLUDE",
    "ADDON_SOURCES_EXCLUDE",
    "ADDON_INCLUDES_EXCLUDE",
    "ADDON_FRAMEWORKS_EXCLUDE",
}

OBJC_PATTERNS = [
    re.compile(r"^\s*#\s*import\b", re.MULTILINE),
    re.compile(r"@\s*(interface|protocol|class)\b"),
    re.compile(r"\bid\s*<"),
    re.compile(r"\b(NSObject|NSString|NSArray|NSDictionary)\b"),
]


def add_issue(issues: list[str], path: Path, line: int | None, message: str) -> None:
    loc = str(path) if line is None else f"{path}:{line}"
    issues.append(f"{loc}: {message}")


def add_warning(warnings: list[str], path: Path, line: int | None, message: str) -> None:
    loc = str(path) if line is None else f"{path}:{line}"
    warnings.append(f"{loc}: {message}")


def parse_addon_config(path: Path, issues: list[str]) -> set[str]:
    current = ""
    seen_sections: set[str] = set()
    if not path.exists():
        add_issue(issues, path, None, "missing addon_config.mk")
        return seen_sections

    for line_no, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and "=" not in line:
            current = line[:-1].strip()
            seen_sections.add(current)
            if current not in VALID_SECTIONS:
                add_issue(issues, path, line_no, f"unknown addon_config.mk section '{current}'")
            continue
        if "=" not in line:
            continue
        op = "+=" if "+=" in line else "="
        key, value = [part.strip() for part in line.split(op, 1)]
        if current == "meta":
            valid = key in META_KEYS
        elif current:
            valid = key in PROJECT_KEYS
        else:
            valid = False
        if not valid:
            add_issue(issues, path, line_no, f"unknown or misplaced key '{key}' in section '{current or '<none>'}'")
        if key in EXCLUDE_KEYS and "*" in value:
            add_issue(issues, path, line_no, f"{key} uses '*'; use '%' for oF addon exclusion globs")
        if key == "ADDON_XCFRAMEWORKS" and current == "osx":
            add_issue(
                issues,
                path,
                line_no,
                "ADDON_XCFRAMEWORKS is parsed but omitted from projectGenerator's osx key whitelist; test this PG version or prefer libs discovery/ADDON_LIBS",
            )
    return seen_sections


def check_project(project_dir: Path, addon_name: str, issues: list[str]) -> None:
    addons_make = project_dir / "addons.make"
    if not addons_make.exists():
        add_issue(issues, addons_make, None, "missing addons.make in buildable project")
        return
    entries = []
    for raw in addons_make.read_text(errors="replace").splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(stripped.split("#", 1)[0].strip())
    if addon_name not in entries and not any(Path(entry).name == addon_name for entry in entries):
        add_issue(issues, addons_make, None, f"does not list '{addon_name}' or a local path ending in that name")


def check_objc_headers(addon_root: Path, issues: list[str]) -> None:
    for header in list((addon_root / "src").rglob("*.h")) + list((addon_root / "src").rglob("*.hpp")):
        text = header.read_text(errors="replace")
        for pattern in OBJC_PATTERNS:
            match = pattern.search(text)
            if match:
                line_no = text[: match.start()].count("\n") + 1
                add_issue(issues, header, line_no, "Objective-C/ObjC++ syntax in public header; hide it behind PIMPL and .mm")
                break


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate common openFrameworks addon structure and addon_config.mk mistakes.")
    parser.add_argument("addon_root", type=Path, help="Path to an ofx addon root")
    args = parser.parse_args()

    addon_root = args.addon_root.resolve()
    issues: list[str] = []
    warnings: list[str] = []

    if not addon_root.exists() or not addon_root.is_dir():
        print(f"{addon_root}: addon root does not exist or is not a directory", file=sys.stderr)
        return 2

    addon_name = addon_root.name
    parse_addon_config(addon_root / "addon_config.mk", issues)

    if not (addon_root / "src").exists():
        add_issue(issues, addon_root / "src", None, "missing src/ directory")
    else:
        check_objc_headers(addon_root, issues)

    for candidate in sorted(addon_root.iterdir()):
        if not candidate.is_dir():
            continue
        if candidate.name == "testApp" or candidate.name.startswith("example"):
            check_project(candidate, addon_name, issues)

    if not (addon_root / "testApp").exists():
        add_warning(warnings, addon_root / "testApp", None, "missing testApp/ smoke-test project")

    if issues:
        print("openFrameworks addon validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    for warning in warnings:
        print(f"warning: {warning}")
    print(f"openFrameworks addon validation passed: {addon_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
