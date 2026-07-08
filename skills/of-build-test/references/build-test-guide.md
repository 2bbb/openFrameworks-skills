# openFrameworks build/test guide

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

## Visual capture

Use the simplest capture that matches the app:

- Current full GL output: `ofSaveScreen("screen.png")`.
- Current viewport: `ofSaveViewport("viewport.png")`.
- Numbered PNG frame: `ofSaveFrame()`.
- FBO/high-res output: read the FBO to pixels and call `ofSaveImage(pixels, path, OF_IMAGE_QUALITY_BEST)`.

For automated verification, save to a stable path under `bin/data` or another known output directory, run the app long enough to emit the file, then inspect file existence, size, and pixels if needed.

## Project generator refresh

When platform project files are stale, use the command-line project generator with an explicit oF path or `PG_OF_PATH`:

```bash
projectGenerator -o"/path/to/openFrameworks" path/to/project
projectGenerator -o"/path/to/openFrameworks" -a"ofxGui,ofxUnitTests" path/to/project
projectGenerator -o"/path/to/openFrameworks" -p"osx" path/to/project
projectGenerator -o"/path/to/openFrameworks" -d path/to/project   # dry run
```

On Windows, the local docs state long options use `/` form rather than `-` form.
