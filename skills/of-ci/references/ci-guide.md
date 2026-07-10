# openFrameworks CI guide

## Contents

- Evidence map
- Choose the CI shape
- `2bbb/of-actions` quick start
- CI design rules
- ofxUnitTests app contract
- Workflow template: oF checkout
- Workflow template: addon/app repo
- Project generator in CI

## Evidence map

This guide separates upstream repository evidence from openFrameworks source evidence. It was last checked against `2bbb/of-actions` on 2026-07-10.

- `https://github.com/2bbb/of-actions/blob/1bf82ebc85262ff0e1a7d809a0406aecfbf80e37/.github/workflows/build-addon.yml`: immutable v3 addon workflow inputs, three runner jobs, build/run logic, exit-code checks, and checkout layout.
- `https://github.com/2bbb/of-actions/blob/1bf82ebc85262ff0e1a7d809a0406aecfbf80e37/.github/workflows/build-app.yml`: immutable v3 app workflow inputs, three runner jobs, checkout layout, and `continue-on-error` behavior.
- `https://github.com/2bbb/of-actions/blob/1675fca03a831c2c70b114f351c35b17f339fe9f/.github/workflows/build-addon.yml`: newer inspected addon workflow with an extra macOS Xcode job, sequential config loops, and pre-build/cache inputs.
- `https://github.com/2bbb/of-actions`: maintainer usage and requirements. Treat the workflow files as authoritative when README prose and implementation differ.
- `https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows`: reusable workflows are called at the job level; a SHA is the safest stable/security ref; the called workflow receives the caller's `GITHUB_TOKEN`.

- `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h` and `openFrameworks/tests/*/*/src/main.cpp`: ofxUnitTests setup and no-window test app patterns.
- `openFrameworks/scripts/templates/*/Makefile`, `openFrameworks/docs/projectgenerator.md`, and `openFrameworks/scripts/ci/*`: project-local build/test conventions and CI execution patterns.
- `openFrameworks/.github/workflows/of.yml`: Linux job uses `ubuntu-24.04`, `actions/checkout@v6`, `hendrikmuhs/ccache-action@v1.2.23`, `awalsh128/cache-apt-pkgs-action@v1.6.0`, then downloads libs, installs dependencies, builds, and runs tests; macOS job uses `macos-15`, `actions/checkout@v6`, `hendrikmuhs/ccache-action@v1.2.23`, downloads libs, then runs `scripts/ci/osx/build.sh` or `scripts/ci/osx/run_tests.sh`.
- `openFrameworks/.github/workflows/nightly.yml`: uses `ubuntu-24.04`, `actions/checkout@v4`, `hendrikmuhs/ccache-action@v1.2.14`, `awalsh128/cache-apt-pkgs-action@latest`, and release packaging commands. Prefer the newer exact versions from `of.yml` for new CI.
- `openFrameworks/scripts/ci/linux64/install.sh`: installs Linux dependencies through `scripts/linux/ubuntu/install_dependencies.sh -y`.
- `openFrameworks/scripts/ci/linux64/build.sh`: builds OF core, `emptyExample`, and `allAddonsExample` with makefiles; uses `make -j2`.
- `openFrameworks/scripts/ci/linux64/run_tests.sh`: iterates `tests/*/*`, copies Linux template Makefile/config, builds `make -j2 Debug`, runs the debug binary from `bin`, and fails on nonzero status.
- `openFrameworks/scripts/ci/macos/build.sh`: builds macOS template project with `xcodebuild -configuration Release -target emptyExample`.
- `openFrameworks/scripts/ci/macos/run_tests.sh`: copies macOS template Makefile/config, builds `make -j Debug`, runs `make RunDebug`, and exits on nonzero status.
- `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`: ofxUnitTests logs pass/fail and exits with the number of failed tests; macros are `ofxTest`, `ofxTestEq`, `ofxTestGt`, `ofxTestLt`.
- `openFrameworks/tests/utils/strings/src/main.cpp`: concrete no-window unit-test app pattern.
- `projectGenerator/commandLine/README.md` and `projectGenerator/commandLine/src/main.cpp`: project generator supports `--ofPath`, `--platforms`, `--addons`, `--dryrun`, and `PG_OF_PATH`.

## Choose the CI shape

Use `2bbb/of-actions` when all of these are true:

- The repository root is one addon or one app.
- An addon test app is inside the addon repository, for example `testApp/`.
- The fixed macOS/Linux/Windows jobs are appropriate.
- The oF release is a published version or `nightly` that the workflow can resolve from `openframeworks/openFrameworks` releases.
- The called workflow's fixed provisioning and execution policy is acceptable.

Use custom CI when you need a different runner, platform, oF checkout, package manager, system dependency set, secrets, artifacts, multiple independent apps/addons, or caller-defined steps around the build. A job that calls a reusable workflow cannot also contain arbitrary `steps`.

## `2bbb/of-actions` quick start

Reusable workflows belong directly under `jobs.<job-id>.uses`. Do not put them under `steps`, and do not add `runs-on`; the called workflow owns its runners.

### Addon with ofxUnitTests

```yaml
name: openFrameworks addon CI

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    uses: 2bbb/of-actions/.github/workflows/build-addon.yml@v3
    with:
      of_version: "0.12.1"
      addon_name: "ofxYourAddon"
      test_app: "testApp"
      configs: '["Debug", "Release"]'
      test_mode: "test"
```

The called workflow downloads oF, then checks out the caller repository at `of_root/addons/<addon_name>`. `test_app` is relative to that checkout. The test app therefore needs its own `Makefile`, `addons.make`, and sources; the addon root needs `addon_config.mk`.

### App build

Ordinary graphical apps usually do not terminate on their own, so start with `build-only`. Use `run` or `test` only when the app has a deterministic self-exit path.

```yaml
name: openFrameworks app CI

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    uses: 2bbb/of-actions/.github/workflows/build-app.yml@v3
    with:
      of_version: "0.12.1"
      app_name: "yourGreatApp"
      configs: '["Release"]'
      test_mode: "build-only"
```

The app repository is checked out at `of_root/apps/myApps/<app_name>`. Its `Makefile` should therefore use the usual `OF_ROOT=../../..` relationship and include the oF makefile template; keep `addons.make` at the app root.

### Inputs in tag `v3`

Both tagged workflows accept:

| Input | Type | Required/default | Meaning |
|---|---|---|---|
| `of_version` | string | required | Release tag such as `0.12.1`, or `nightly` |
| `submodules` | boolean | `true` | Recursive checkout when true |
| `preprocessor_defines` | string | empty | Windows defines separated by semicolons |
| `cache_key_suffix` | string | `v1` | Manual cache-busting suffix |
| `test_mode` | string | `run` | `build-only`, `run`, or `test` |
| `configs` | string | `'["Release"]'` | JSON array containing `Debug` and/or `Release` |

Addon-only required inputs are `addon_name` and `test_app`. App-only required input is `app_name`. Preserve JSON quoting for `configs`; it is parsed with `fromJson` or `jq` inside the workflow.

Neither workflow declares reusable-workflow outputs. Do not write caller jobs that expect `needs.<job>.outputs.*` from these workflows.

### Test-mode semantics and caveats

- `build-only`: compile and do not execute. Prefer this for ordinary event-loop apps.
- `test`: execute and fail on every nonzero status. Use this with `ofxUnitTestsApp` or another app whose process status is a test result.
- Addon `run` in `build-addon.yml@v3`: execute, tolerate ordinary nonzero status, but fail on Unix signal-like status (`>=128`) and Windows crash-like status. This is useful only when nonzero is intentionally non-fatal.
- App `run` in `build-app.yml@v3`: the Run step uses `continue-on-error` and does not perform the addon's separate crash classification. Do not claim crash detection for this mode; use `test` if any abnormal exit must fail.
- App Windows execution in `build-app.yml@v3` looks for `<app_name>.exe` only. The tagged addon workflow has a Debug `_debug.exe` fallback, but the app workflow does not. Verify Windows Debug execution before depending on `configs: '["Debug"]'` with app `run`/`test`; Release build-only is the conservative app baseline.
- Both Linux workflows invoke `xvfb-run` for execution. A no-window test still needs to terminate; it only avoids a real rendering window.

### `ofAppNoWindow` is not an auto-exit mechanism

`ofAppNoWindow::doesLoop()` returning false means the window backend does not supply its own platform loop. `ofMainLoop::loop()` still repeatedly calls `loopOnce()` until `ofExit()`/close state stops it. The one-shot behavior of the standard test pattern comes from `ofxUnitTestsApp::setup()`, which calls `run()` and then `ofExit(numTestsFailed)`.

For a custom no-window smoke app, call `ofExit(status)` after the check. Otherwise a CI `run`/`test` job can wait forever.

### Ref selection and untagged features

- Convenient reviewed baseline: `@v3`.
- Immutable v3 pin verified on 2026-07-10: `@1bf82ebc85262ff0e1a7d809a0406aecfbf80e37`.
- Re-check the current tag/SHA before generating a long-lived workflow. A major tag is convenient but movable; a full commit SHA is immutable.
- The repository README examples still use `@v2`; treat those as usage shape, not evidence that v2 is the newest tag.
- As checked on 2026-07-10, `main` is ahead of `v3`. Its addon workflow adds an Xcode job and `pre_build_script`, `pre_build_script_windows`, `pre_build_cache_path`, and `pre_build_cache_key`. These inputs are not in tag `v3`, and the app workflow does not define them.
- If those addon features are required before another release tag exists, review and pin the exact main commit. The verified commit was `1675fca03a831c2c70b114f351c35b17f339fe9f`; do not use mutable `@main` silently.

Do not add `secrets: inherit` just to make release resolution work. GitHub grants a called workflow access to the caller's `github.token`/`secrets.GITHUB_TOKEN`, and these workflows request `contents: read`. Pass other secrets only when a reviewed called workflow explicitly defines and requires them.

## CI design rules

- Verify third-party reusable-workflow refs and inputs from the called workflow file. Prefer a full SHA where immutable pinning is required.
- Keep oF-source CI and addon/app CI separate. oF-source CI can call `scripts/ci/...`; external addon/app CI can use `2bbb/of-actions` or explicitly provision an oF checkout and set `OF_ROOT`.
- Test apps need their own `addons.make`; include both the addon under test and `ofxUnitTests` for assertion-based tests.
- Prefer `Debug` for unit tests because local oF CI runs tests as Debug.
- On Linux headless runners, use no-window tests when possible; otherwise wrap direct app execution in `xvfb-run` if available/installed. No-window apps still require an explicit exit path.
- Preserve stdout/stderr logs as artifacts or inline log output when failures are hard to diagnose.

## ofxUnitTests app contract

`ofxUnitTestsApp::setup()` calls `run()`, logs pass/fail counts, then exits with the failed-test count. Therefore CI can simply run the test binary and trust the process status.

Minimal no-window `src/main.cpp`:

```cpp
#include "ofMain.h"
#include "ofAppNoWindow.h"
#include "ofxUnitTests.h"

class ofApp: public ofxUnitTestsApp{
    void run() override{
        ofxTest(true, "condition holds");
        ofxTestEq(2 + 2, 4, "arithmetic");
    }
};

int main(){
    ofInit();
    auto window = std::make_shared<ofAppNoWindow>();
    auto app = std::make_shared<ofApp>();
    ofRunApp(window, app);
    return ofRunMainLoop();
}
```

## Workflow template: oF checkout

Use this shape only inside an openFrameworks checkout with its `scripts/ci` tree available:

```yaml
name: oF CI
on:
  push:
  pull_request:

jobs:
  linux64:
    runs-on: ubuntu-24.04
    env:
      TARGET: linux64
      RELEASE: latest
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: linux64-64gcc6
      - name: Download libraries
        run: ./scripts/linux/download_libs.sh -t "$RELEASE" -a 64gcc6
      - name: Install dependencies
        run: ./scripts/ci/"$TARGET"/install.sh
      - name: Build and test
        run: |
          scripts/ci/linux64/build.sh
          scripts/ci/linux64/run_tests.sh

  macos:
    runs-on: macos-15
    env:
      RELEASE: latest
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-makefiles
      - name: Download libraries
        run: ./scripts/osx/download_libs.sh -t "$RELEASE"
      - name: Build and test
        run: scripts/ci/osx/run_tests.sh
```

This template assumes an oF source checkout with the upstream download and CI scripts present. Pin `RELEASE` to the release policy being tested rather than leaving it ambiguous.

## Workflow template: addon/app repo

Use this shape when CI already has an `OF_ROOT` checkout available or a previous step creates it:

```yaml
name: Addon CI
on:
  push:
  pull_request:

jobs:
  test-linux:
    runs-on: ubuntu-24.04
    env:
      OF_ROOT: ${{ github.workspace }}/openFrameworks
      TEST_APP: testApp
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: linux64-addon
      - name: Build test app
        run: make -C "$TEST_APP" -j2 Debug OF_ROOT="$OF_ROOT"
      - name: Run test app
        run: |
          app_name="$(basename "$TEST_APP")"
          exe="$TEST_APP/bin/${app_name}_debug"
          if command -v xvfb-run >/dev/null 2>&1 && [ -z "${DISPLAY:-}" ]; then
            xvfb-run "$exe"
          else
            "$exe"
          fi

  test-macos:
    runs-on: macos-15
    env:
      OF_ROOT: ${{ github.workspace }}/openFrameworks
      TEST_APP: testApp
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-addon
      - name: Build test app
        run: make -C "$TEST_APP" -j Debug OF_ROOT="$OF_ROOT"
      - name: Run test app
        run: make -C "$TEST_APP" RunDebug OF_ROOT="$OF_ROOT"
```

Add explicit oF checkout/download/install steps based on repository policy; do not invent release URLs without checking the target openFrameworks release assets or an approved project-local download helper.

## Project generator in CI

When CI must refresh project files, use explicit paths and dry runs for diagnosis:

```bash
projectGenerator -o"$OF_ROOT" -a"ofxYourAddon,ofxUnitTests" "$TEST_APP"
projectGenerator -o"$OF_ROOT" -d "$TEST_APP"
```

`PG_OF_PATH` can replace `-o` when configured in the job environment.
