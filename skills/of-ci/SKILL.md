---
name: of-ci
description: Design and implement openFrameworks GitHub Actions CI and ofxUnitTests test workflows. Use when Codex needs to add or review oF addon/app CI, choose locally grounded Actions versions, run Linux/macOS build/test jobs, integrate ofxUnitTests, or create CI scripts for openFrameworks projects.
license: MIT
---

# openFrameworks CI

Use this skill to create grounded GitHub Actions CI for oF projects/addons without inventing unsupported action versions or build behavior.

## Workflow

1. Read `references/ci-guide.md` before writing workflow YAML or test app code.
2. Decide whether the repo is:
   - an oF checkout using `scripts/ci/...`, or
   - an addon/app repo that must locate `OF_ROOT` and build one or more project directories.
3. Prefer ofxUnitTests for pass/fail test apps; use no-window tests where possible.
4. For workflow YAML, use only Actions versions found in local oF workflows unless the user explicitly provides another version.
5. Validate YAML syntax and run the safest local script `--help`/dry run checks available.

## Practical patterns

- Linux oF CI evidence uses `ubuntu-24.04`, `actions/checkout@v6`, `hendrikmuhs/ccache-action@v1.2.23`, and `awalsh128/cache-apt-pkgs-action@v1.6.0`.
- macOS oF CI evidence uses `macos-15`, `actions/checkout@v6`, and `hendrikmuhs/ccache-action@v1.2.23`.
- oF source CI runs local scripts such as `scripts/ci/linux64/install.sh`, `scripts/ci/linux64/build.sh`, `scripts/ci/linux64/run_tests.sh`, and `scripts/ci/osx/run_tests.sh`.
- Addon/app CI can call the `of-build-test` script when that skill is also installed/copied into the repo, or inline equivalent `make Debug` + direct run commands.

## Bundled resources

- `references/ci-guide.md` — grounded CI and ofxUnitTests reference with source-path evidence.
- `scripts/of-ci-template.sh` — emits a conservative GitHub Actions workflow template using only locally evidenced action versions.
