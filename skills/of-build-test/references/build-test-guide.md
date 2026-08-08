# openFrameworks build/test guide

## Contents

- [Evidence map](#evidence-map)
- [Build commands](#build-commands)
- [Capturing stdout/stderr](#capturing-stdoutstderr)
- [Running built apps](#running-built-apps)
- [ofxUnitTests pattern](#ofxunittests-pattern)
- [Layered addon verification](#layered-addon-verification)
- [Deterministic visual smoke mode](#deterministic-visual-smoke-mode)
- [Visual capture](#visual-capture)
- [Performance evidence](#performance-evidence)
- [Project generator refresh](#project-generator-refresh)

## Evidence map

This guide is grounded only in the following local evidence:

- `openFrameworks/scripts/templates/*/Makefile`, `openFrameworks/scripts/ci/linux64/run_tests.sh`, and `openFrameworks/scripts/ci/macos/run_tests.sh`: source-backed make/test execution patterns.
- `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`, `openFrameworks/tests/*/*/src/main.cpp`, and bundled addon/project templates: source-backed test app and addon project patterns.
- `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`: default goal is `Release`; supported targets include `Release`, `Debug`, `run`, `RunRelease`, `RunDebug`, `ReleaseNoOF`, `DebugNoOF`; `run` dispatches platform run command.
- `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/config.project.mk`: default `OF_ROOT=../../..`; `addons.make` is read from project root; project sources are found under `src`; Debug adds `-DDEBUG`, Release adds `-DNDEBUG`.
- `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/config.shared.mk`: platform detection maps Darwin to `osx` and Linux x86_64 to `linux64`.
- `openFrameworks/scripts/templates/vscode/.vscode/tasks.json`: VS Code tasks use `make -j -s`, `make Debug -j -s`, `make RunRelease`, and clean targets.
- `openFrameworks/scripts/ci/linux64/run_tests.sh`: tests are built with `make -j2 Debug`; debug binary is run from `bin/`, sometimes through `gdb`; nonzero exit exits CI.
- `openFrameworks/scripts/ci/macos/run_tests.sh`: macOS tests copy template Makefile/config, build with `make -j Debug`, then run with `make RunDebug`.
- `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`: `ofxUnitTestsApp::setup()` runs `run()`, logs pass/fail counts, and calls `ofExit(numTestsFailed)`; macros are `ofxTest`, `ofxTestEq`, `ofxTestGt`, `ofxTestLt`.
- `openFrameworks/tests/utils/strings/src/main.cpp`: concrete no-window ofxUnitTests app using `ofInit()`, `ofAppNoWindow`, `ofRunApp(window, app)`, and `ofRunMainLoop()`.
- `openFrameworks/libs/openFrameworks/utils/ofUtils.h` and `ofUtils.cpp`: `ofSaveScreen(path)`, `ofSaveViewport(path)`, and `ofSaveFrame()` save current GL output through pixels and `ofSaveImage`.
- `openFrameworks/libs/openFrameworks/graphics/ofImage.h`: `ofSaveImage` overloads for `ofPixels`, `ofFloatPixels`, and `ofShortPixels`; `ofImage::save(...)` exists.
- `openFrameworks/examples/gl/fboHighResOutputExample/src/ofApp.cpp`: `fboOutput.readToPixels(pixels); ofSaveImage(pixels, ofGetTimestampString()+".jpg", OF_IMAGE_QUALITY_BEST);`.
- `projectGenerator/commandLine/README.md`: `projectGenerator -o"pathToOF" pathOfNewProject`; update existing projects similarly; `PG_OF_PATH` can supply oF root.
- `projectGenerator/commandLine/src/projects/baseProject.cpp`: Linux targets use the `vscode` template; project generator saves `addons.make`; source files under `src` are gathered.
- `projectGenerator/commandLine/src/main.cpp`: command-line options include `--ofPath`, `--platforms`, `--addons`, `--template`, `--dryrun`, and `PG_OF_PATH` fallback.

## Build commands

Run commands from the project/test-app directory unless using `make -C`:

```bash
make -j Release        # release app and oF library
make -j Debug          # debug app and oF library
make RunRelease        # run release using platform run command
make RunDebug          # run debug using platform run command
make CleanRelease
make CleanDebug
make clean
```

Notes:

- `compile.project.mk` defaults to `Release` when no target is specified.
- `OF_ROOT` defaults to `../../..`; override it when the project is not three directories below the oF root.
- `addons.make` belongs in each buildable project directory and lists addon names, one per line.
- `Debug` and `Release` produce different optimization defines; do not treat them as interchangeable when debugging failures.

## Capturing stdout/stderr

Use separate files first; merge only for human-friendly summaries:

```bash
mkdir -p build-logs
make -j Debug >build-logs/build.stdout.log 2>build-logs/build.stderr.log
status=$?
cat build-logs/build.stderr.log
exit $status
```

For repeated runs, use:

```bash
skills/of-build-test/scripts/of-build-run.sh --project path/to/app --target Debug --run --log-dir build-logs
```

The script writes build and run stdout/stderr files and exits with the failing command's status.

## Running built apps

### macOS

The built executable is inside the app bundle:

```bash
./bin/MyApp.app/Contents/MacOS/MyApp
./bin/MyApp_debug.app/Contents/MacOS/MyApp_debug
```

`make RunDebug`/`make RunRelease` is still preferred when the project Makefile knows the platform run command.

### Linux

Common direct paths are:

```bash
./bin/MyApp
./bin/MyApp_debug
```

On headless Linux, run windowed apps with `xvfb-run`:

```bash
xvfb-run ./bin/MyApp_debug
```

No-window ofxUnitTests apps using `ofAppNoWindow` may not need a display server.

## ofxUnitTests pattern

`addons.make`:

```text
ofxYourAddon
ofxUnitTests
```

`src/main.cpp` minimal pattern:

```cpp
#include "ofMain.h"
#include "ofAppNoWindow.h"
#include "ofxUnitTests.h"

class ofApp: public ofxUnitTestsApp{
    void run() override{
        ofxTestEq(1 + 1, 2, "basic arithmetic");
        ofxTest(true, "condition holds");
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

Macros grounded in `ofxUnitTests.h`: `ofxTest`, `ofxTestEq`, `ofxTestGt`, `ofxTestLt`.

## Layered addon verification

Do not let one green build stand in for every contract. Select the smallest layers that prove the change:

1. **Repository/static checks** — `git diff --check`, configuration validators, source-citation or packaging checks.
2. **Pure C++ tests** — algorithms, parsers, math, queue policies, and serialization that do not need an oF window.
3. **Public-header compile** — compile a tiny translation unit that includes the public umbrella header with the documented C++ standard and warnings enabled. This catches incomplete types, leaked ObjC/platform headers, missing includes, and accidental reliance on include order.
4. **Sanitizer/static analysis** — run on the smallest target that exercises memory, bounds, lifetime, and undefined-behavior risks when the local compiler supports it. Treat availability as platform/toolchain-specific.
5. **oF Debug/Release build** — build the minimal test app and every example affected by the API change. Debug and Release are distinct configurations in the oF make layer.
6. **Runtime smoke** — require an explicit success/failure oracle, timeout, and captured logs.
7. **Visual evidence** — inspect a deterministic screenshot or FBO artifact when correctness includes rendering, alpha, fill/blend/depth state, or interaction-visible behavior.
8. **Performance evidence** — only when the claim is about throughput, latency, allocation, or frame time.

For an addon example portfolio, prefer focused examples that each prove one API area over one large demo that makes failures hard to localize. Keep one minimal example suitable for build smoke.

The oF repository supplies `ofAppNoWindow`/`ofxUnitTests`, separate Debug/Release make targets, and image capture APIs; sanitizer, analyzer, and public-header targets are addon-owned gates rather than universal oF targets. Sources: `openFrameworks/tests/`, `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`, `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`, `openFrameworks/libs/openFrameworks/utils/ofUtils.h`.

## Deterministic visual smoke mode

For a windowed app that must be tested repeatedly, add an opt-in mode owned by the app rather than relying on an agent to close it manually:

1. Parse an explicit argument in `main(int argc, char** argv)` such as `--smoke-test`; pass the resulting flag into `ofApp` through its constructor or setup state.
2. Wait for a deterministic readiness condition: required resources allocated, first valid input/frame available, or a bounded warm-up frame count reached.
3. Render the target state in `draw()`.
4. Save the screen/FBO to a stable, ignored artifact path.
5. Log a unique success/failure marker and call `ofExit(0)` or `ofExit(nonzero)`.
6. Run the exact executable under an external timeout and capture stdout/stderr separately.
7. Verify process status, marker uniqueness, artifact existence/nonzero size, and pixels when the visual contract requires it.

`ofSaveScreen()` reads the current GL viewport and saves pixels. `ofExit(status)` asks the main loop to close with that status, and `ofMainLoop::loop()` returns it after exit callbacks. Sources: `openFrameworks/libs/openFrameworks/utils/ofUtils.h`, `openFrameworks/libs/openFrameworks/utils/ofUtils.cpp`, `openFrameworks/libs/openFrameworks/app/ofAppRunner.cpp`, `openFrameworks/libs/openFrameworks/app/ofMainLoop.cpp`.

Guard the capture so it runs once. Do not use only a fixed sleep when readiness can be observed, and always keep an external timeout for failed initialization. Put generated captures/logs outside tracked source or add exact ignore rules; never ignore hand-authored fixture/reference images accidentally.

## Visual capture

Use the simplest capture that matches the app:

- Current full GL output: `ofSaveScreen("screen.png")`.
- Current viewport: `ofSaveViewport("viewport.png")`.
- Numbered PNG frame: `ofSaveFrame()`.
- FBO/high-res output: read the FBO to pixels and call `ofSaveImage(pixels, path, OF_IMAGE_QUALITY_BEST)`.

For automated verification, prefer `build-logs/`, a temporary test-artifact directory, or another generated-output path outside the runtime asset tree. If the app must write through oF's data path, use an explicitly ignored subdirectory such as `bin/data/test-artifacts/`, not the same folders that hold tracked runtime assets. Then inspect file existence, size, and pixels if needed.

## Performance evidence

Before claiming an optimization:

- define the metric and unit, and distinguish producer throughput, end-to-end latency, GPU time, CPU time, allocation count, and dropped work;
- preserve correctness checks alongside timing so a faster empty/incorrect path cannot pass;
- capture environment facts that affect interpretation: build configuration, platform/device, resolution/work size, VSync/target FPS, and relevant queue depth;
- use warm-up plus repeated samples and report the sample set or summary method, not only the best run;
- store a structured result artifact when practical, then compare baseline and candidate under the same harness;
- document backpressure, dropped frames, final drain, and synchronization points for asynchronous/ring-buffer paths;
- state whether a result improves throughput, latency, or both. A deferred/ring path can improve producer overlap without reducing final completion latency.

Keep absolute performance numbers project-local. Reusable skill guidance should describe the measurement contract, not promise results for other hardware.

## Project generator refresh

When platform project files are stale, use the command-line project generator with an explicit oF path or `PG_OF_PATH`:

```bash
projectGenerator -o"/path/to/openFrameworks" path/to/project
projectGenerator -o"/path/to/openFrameworks" -a"ofxGui,ofxUnitTests" path/to/project
projectGenerator -o"/path/to/openFrameworks" -p"osx" path/to/project
projectGenerator -o"/path/to/openFrameworks" -d path/to/project   # dry run
```

On Windows, the local docs state long options use `/` form rather than `-` form.
