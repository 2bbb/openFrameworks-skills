#!/usr/bin/env python3
"""Regression tests for safe Project Generator executable selection."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import locate_project_generator as locator


def make_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


class LocatorTests(unittest.TestCase):
    def test_prefers_cli_embedded_in_electron_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle = root / "projectGenerator-ai.app"
            gui = bundle / "Contents" / "MacOS" / "projectGenerator"
            cli = bundle / "Contents" / "Resources" / "app" / "app" / "projectGenerator"
            make_executable(gui)
            make_executable(cli)

            with patch("platform.system", return_value="Darwin"), patch.dict(os.environ, {"PATH": ""}, clear=False):
                candidates = locator.candidate_paths(None, [root])

            preferred = locator.preferred_candidate(candidates)
            self.assertIsNotNone(preferred)
            self.assertEqual(Path(preferred.path), cli.resolve())
            gui_candidate = next(candidate for candidate in candidates if Path(candidate.path) == gui.resolve())
            self.assertEqual(gui_candidate.kind, "electron-gui")
            self.assertFalse(gui_candidate.automation_safe)

    def test_does_not_select_outer_electron_gui_when_cli_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            gui = root / "projectGenerator" / "projectGenerator.app" / "Contents" / "MacOS" / "projectGenerator"
            make_executable(gui)

            with patch("platform.system", return_value="Darwin"), patch.dict(os.environ, {"PATH": ""}, clear=False):
                candidates = locator.candidate_paths(None, [root])

            self.assertIsNone(locator.preferred_candidate(candidates))
            gui_candidate = next(candidate for candidate in candidates if Path(candidate.path) == gui.resolve())
            self.assertTrue(gui_candidate.executable)
            self.assertFalse(gui_candidate.automation_safe)

    def test_path_entry_inside_project_generator_app_is_not_automation_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            gui = Path(temp_dir) / "projectGenerator.app" / "Contents" / "MacOS" / "projectGenerator"
            make_executable(gui)

            with patch("platform.system", return_value="Darwin"), patch.dict(os.environ, {"PATH": str(gui.parent)}, clear=False):
                candidates = locator.candidate_paths(None, [])

            self.assertIsNone(locator.preferred_candidate(candidates))
            self.assertTrue(any(candidate.executable and not candidate.automation_safe for candidate in candidates))


if __name__ == "__main__":
    unittest.main()
