---
name: of-ci
description: Design and implement openFrameworks GitHub Actions CI and ofxUnitTests workflows, including 2bbb/of-actions reusable workflows. Use when Codex needs to add or review cross-platform oF addon/app CI, choose verified workflow refs and inputs, run build/test jobs, integrate ofxUnitTests, or diagnose CI behavior.
license: MIT
---

# openFrameworks CI

Use this skill to create source-grounded GitHub Actions CI for oF projects/addons without inventing workflow inputs, refs, runner behavior, or test semantics.

## Workflow

1. Read `references/ci-guide.md` before writing workflow YAML or test app code.
2. Decide whether the repo is:
   - an oF checkout using `scripts/ci/...`,
   - an addon/app suited to `2bbb/of-actions`, or
   - a custom addon/app workflow that must provision `OF_ROOT` itself.
3. Prefer `2bbb/of-actions` for ordinary public addon/app repositories when its fixed three-platform matrix and repository layout match the project. Use custom CI when the project needs unsupported runners, steps, secrets, artifacts, or setup.
4. Prefer ofxUnitTests for pass/fail test apps. Use `ofAppNoWindow` to avoid creating a real window, but ensure one-shot apps call `ofExit()`; `ofAppNoWindow` does not itself terminate the main loop.
5. Verify the called workflow file and ref before writing YAML. Use a full commit SHA when immutable third-party workflow pinning is required; otherwise use a reviewed release tag.
6. Validate YAML syntax and run the bundled template script's `--help` and output smoke checks.

## Practical patterns

- `2bbb/of-actions/.github/workflows/build-addon.yml@v3` and `build-app.yml@v3` are reusable workflows called at `jobs.<id>.uses`, not actions placed under `steps`.
- The caller supplies only `uses`, `with`, optional `permissions`, and other keywords GitHub permits on reusable-workflow jobs. The called workflow checks out the caller repository into the downloaded oF tree.
- `of-actions@v3` builds on macOS 14, Ubuntu 22.04, and Windows 2022. It downloads an oF release/nightly asset and builds Release by default.
- `test_mode: test` fails on any nonzero test exit. In `build-addon.yml@v3`, `run` tolerates ordinary nonzero exits but explicitly rejects crash-like exit codes. In `build-app.yml@v3`, `run` uses `continue-on-error` and does not separately distinguish crashes; use `test` when process status must gate CI.
- Linux oF source CI evidence uses `ubuntu-24.04`, `actions/checkout@v6`, `hendrikmuhs/ccache-action@v1.2.23`, and `awalsh128/cache-apt-pkgs-action@v1.6.0`.
- macOS oF source CI evidence uses `macos-15`, `actions/checkout@v6`, and `hendrikmuhs/ccache-action@v1.2.23`.
- oF source CI runs local scripts such as `scripts/ci/linux64/install.sh`, `scripts/ci/linux64/build.sh`, `scripts/ci/linux64/run_tests.sh`, and `scripts/ci/osx/run_tests.sh`.
- Custom addon/app CI can call the `of-build-test` script when that skill is also installed/copied into the repo, or inline equivalent build/run commands after it provisions oF.

## Bundled resources

- `references/ci-guide.md` — verified `of-actions`, custom CI, security, and ofxUnitTests reference.
- `scripts/of-ci-template.sh` — emits `of-actions` caller workflows or conservative source/custom workflow templates.
