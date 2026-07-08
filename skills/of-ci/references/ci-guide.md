# openFrameworks CI guide

## Evidence map

This guide is grounded only in the following local evidence:

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

## CI design rules

- Use exact action versions from local workflows unless the user supplies/approves another source.
- Keep oF-source CI and addon/app CI separate. oF-source CI can call `scripts/ci/...`; external addon CI usually needs to install or cache an oF checkout and set `OF_ROOT`.
- Test apps need their own `addons.make`; include both the addon under test and `ofxUnitTests` for assertion-based tests.
- Prefer `Debug` for unit tests because local oF CI runs tests as Debug.
- On Linux headless runners, use no-window tests when possible; otherwise wrap direct app execution in `xvfb-run` if available/installed.
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
      - name: Install dependencies
        run: ./scripts/ci/$TARGET/install.sh
      - name: Build and test
        run: |
          scripts/ci/linux64/build.sh
          scripts/ci/linux64/run_tests.sh

  macos:
    runs-on: macos-15
    env:
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-makefiles
      - name: Build and test
        run: scripts/ci/osx/run_tests.sh
```

This omits some oF upstream release/lib download steps; add them only when the target repo has the same scripts and needs prebuilt libs.

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
