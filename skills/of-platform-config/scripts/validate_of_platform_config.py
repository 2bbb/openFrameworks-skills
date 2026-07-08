#!/usr/bin/env python3
"""Validate common openFrameworks platform config files.

Checks are intentionally source-backed and conservative:
- addon_config.mk section names from projectGenerator's ofAddon.h parseStates.
- ADDON_* keys from projectGenerator's ofAddon.h / parseVariableValue.
- simple addons.make local-path existence relative to the project directory.

Usage:
  validate_of_platform_config.py path/to/addon_config.mk [path/to/addons.make ...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTIONS = {
    "meta", "common", "linux", "linux64", "linux/64", "msys2", "vs",
    "linuxarmv6l", "linuxarmv7l", "linuxaarch64", "linux/armv6l",
    "linux/armv7l", "linux/aarch64", "linux/arm64", "android/armeabi",
    "android/armeabi-v7a", "android/arm64-v8a", "android/x86", "android/x86_64",
    "emscripten", "emscripten/32", "emscripten/64", "android", "ios", "osx",
    "tvos", "macos", "watchos", "visionos", "catos",
}

META_KEYS = {"ADDON_NAME", "ADDON_DESCRIPTION", "ADDON_AUTHOR", "ADDON_TAGS", "ADDON_URL"}
PROJECT_KEYS = {
    "ADDON_DEPENDENCIES", "ADDON_INCLUDES", "ADDON_CFLAGS", "ADDON_CPPFLAGS",
    "ADDON_LDFLAGS", "ADDON_LIBS", "ADDON_DEFINES", "ADDON_ADDITIONAL_LIBS",
    "ADDON_SOURCES", "ADDON_HEADER_SOURCES", "ADDON_C_SOURCES", "ADDON_CPP_SOURCES",
    "ADDON_OBJC_SOURCES", "ADDON_LIBS_EXCLUDE", "ADDON_LIBS_DIR",
    "ADDON_SOURCES_EXCLUDE", "ADDON_INCLUDES_EXCLUDE", "ADDON_FRAMEWORKS_EXCLUDE",
    "ADDON_DATA", "ADDON_PKG_CONFIG_LIBRARIES", "ADDON_FRAMEWORKS",
    "ADDON_XCFRAMEWORKS", "ADDON_DLLS_TO_COPY",
}
ALL_KEYS = META_KEYS | PROJECT_KEYS
ASSIGN_RE = re.compile(r"^([A-Za-z0-9_]+)\s*(\+?=)\s*(.*)$")
SECTION_RE = re.compile(r"^([A-Za-z0-9_/]+):$")


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()


def validate_addon_config(path: Path) -> list[str]:
    errors: list[str] = []
    current = "common"
    for lineno, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = strip_comment(raw)
        if not line:
            continue
        section = SECTION_RE.match(line)
        if section:
            current = section.group(1)
            if current not in SECTIONS:
                errors.append(f"{path}:{lineno}: unknown addon_config.mk section '{current}'")
            continue
        assign = ASSIGN_RE.match(line)
        if not assign:
            continue
        key = assign.group(1)
        if key not in ALL_KEYS:
            errors.append(f"{path}:{lineno}: unknown ADDON_* key '{key}'")
            continue
        if current == "meta" and key not in META_KEYS:
            errors.append(f"{path}:{lineno}: key '{key}' is not a verified meta key")
        if current != "meta" and key in META_KEYS and key != "ADDON_NAME":
            errors.append(f"{path}:{lineno}: metadata key '{key}' outside meta section")
    return errors


def validate_addons_make(path: Path) -> list[str]:
    errors: list[str] = []
    project_dir = path.parent
    for lineno, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        entry = strip_comment(raw)
        if not entry:
            continue
        if any(sep in entry for sep in ("/", "\\")):
            candidate = (project_dir / entry).resolve()
            if not candidate.exists():
                errors.append(f"{path}:{lineno}: local addon path does not exist relative to project: {entry}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    checked = 0
    for path in args.paths:
        if not path.exists():
            errors.append(f"{path}: file does not exist")
            continue
        if path.name == "addon_config.mk":
            errors.extend(validate_addon_config(path))
            checked += 1
        elif path.name == "addons.make":
            errors.extend(validate_addons_make(path))
            checked += 1
        else:
            errors.append(f"{path}: unsupported file name (expected addon_config.mk or addons.make)")

    if errors:
        print("of-platform-config validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"of-platform-config validation passed ({checked} file(s) checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
