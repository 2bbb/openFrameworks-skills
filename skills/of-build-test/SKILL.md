---
name: of-build-test
description: Build, run, test, log, and visually verify openFrameworks apps/addons. Use when Codex needs practical oF make build commands, stdout/stderr capture, macOS .app execution, Linux xvfb/headless execution, ofSaveScreen/ofSaveImage capture, or ofxUnitTests run patterns for local verification.
license: MIT
---

# openFrameworks Build/Test

Use this skill to turn an oF project or addon test app into a verified build/run result with logs and optional image artifacts.

## Workflow

1. Identify the project directory containing `Makefile`, `src/`, and usually `addons.make`.
2. Read `references/build-test-guide.md` before changing build/test commands, headless behavior, screenshot capture, or ofxUnitTests structure.
3. Prefer the bundled script for repeatable command capture:
   ```bash
   skills/of-build-test/scripts/of-build-run.sh --project path/to/app --target Debug --run --log-dir build-logs
   ```
4. Inspect both exit code and generated logs before claiming success.
5. For visual verification, make the app save an artifact from `draw()` or an FBO readback, then run the app and inspect the output image.

## Command patterns

- Build Release: `make -j Release` or `make -j` when the project defaults are acceptable.
- Build Debug: `make -j Debug`.
- Run via make: `make RunRelease` or `make RunDebug`.
- Run direct macOS executable: `bin/AppName.app/Contents/MacOS/AppName`.
- Run direct Linux executable: `bin/AppName` or `bin/AppName_debug`; use `xvfb-run` on headless Linux if the app opens a window.
- Capture logs with shell redirection or the bundled script; keep stdout and stderr separate when diagnosing.

## ofxUnitTests quick pattern

Use `ofxUnitTests` when tests need assertions and process exit status:

- Add `ofxUnitTests` to the test app `addons.make`.
- Inherit from `ofxUnitTestsApp` and override `run()`.
- Use `ofAppNoWindow` in `main.cpp` for headless tests.
- Treat exit code `0` as pass; nonzero means failed assertions.

## Bundled resources

- `references/build-test-guide.md` — grounded command/reference details with source-path evidence.
- `scripts/of-build-run.sh` — build/run wrapper that captures stdout/stderr, handles macOS `.app` executables, and can use `xvfb-run` on Linux.
