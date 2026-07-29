# openFrameworks app architecture and runtime know-how

Use this as the first oF mental model before editing project code. Verify exact APIs in the target oF checkout because templates and examples can differ by release.

## `ofApp` and the processing-style lifecycle

The default template is organized around a small `main.cpp` and an `ofApp` class:

- `main.cpp` includes `ofMain.h` and `ofApp.h`, configures `ofGLWindowSettings`, calls `ofCreateWindow(settings)`, runs `std::make_shared<ofApp>()`, and enters `ofRunMainLoop()`. Source: `openFrameworks/examples/templates/emptyExample/src/main.cpp`.
- `ofApp` derives from `ofBaseApp`. Source: `openFrameworks/examples/templates/emptyExample/src/ofApp.h`.
- The template declares `setup()`, `update()`, `draw()`, and input/window/message callbacks. Source: `openFrameworks/examples/templates/emptyExample/src/ofApp.h`.
- `ofBaseApp` declares virtual `setup`, `update`, `draw`, `exit`, key, mouse, touch, window, drag, and message hooks. Source: `openFrameworks/libs/openFrameworks/app/ofBaseApp.h`.

Practical guidance:

- Treat `setup()` as one-time initialization, `update()` as state/time/input progression, and `draw()` as rendering. This is a useful processing-style model derived from the template shape; still inspect target project conventions before moving side effects.
- Keep rendering-only code in `draw()` when possible. Avoid heavy blocking I/O, sleeps, or long asset loads in `draw()` because the main loop calls it repeatedly. Verify actual threading/event constraints in the target platform before changing behavior.
- Preserve callback names and signatures exactly; generated project files and examples assume oF callback spellings.
- When `ofApp` grows, split by ownership and lifecycle rather than merely by screen region: keep app/window callbacks as orchestration, let input/media/services own their resources and shutdown, and let render helpers own only the draw state they can restore. Load `runtime-and-resources.md` before moving work to threads or sharing GPU objects.

## `std` and namespace practice

Current oF source contains legacy compatibility around std names, but do not rely on it when writing new project/addon code:

- `ofMain.h` has an `OF_LEGACY_INCLUDE_STD` path that uses `using namespace std;`, and otherwise imports a minimal list such as `std::string`, `std::vector`, and `std::shared_ptr`. Source: `openFrameworks/libs/openFrameworks/ofMain.h`.
- The changelog records repeated work to remove or reduce broad `using namespace std` usage. Source: `openFrameworks/CHANGELOG.md`.
- Many core `.cpp` files use narrow declarations such as `using std::string;` or direct `std::shared_ptr`. Source: `openFrameworks/libs/openFrameworks/`.

Good practice for generated skills and agent edits:

- Prefer explicit `std::vector`, `std::string`, `std::shared_ptr`, etc.
- If a local file already uses narrow `using std::name;`, match that style inside implementation files only.
- Avoid adding `using namespace std;` to headers, `ofApp.h`, addon public headers, or shared utility headers.

## Multi-window patterns

Use the local `examples/windowing/` examples as the source of truth. Two distinct patterns are visible:

### Multiple app instances

`multiWindowExample` creates two `ofGLFWWindowSettings` windows, creates separate `shared_ptr` app instances (`ofApp` and `GuiApp`), wires explicit shared state (`mainApp->gui = guiApp`), runs both apps with their windows, then calls `ofRunMainLoop()`. Source: `openFrameworks/examples/windowing/multiWindowExample/src/main.cpp`.

Use this when each window has its own app lifecycle and ownership. Keep cross-window state explicit and small; avoid hidden globals unless the target project already owns such a singleton.

### One app controlling additional window events

`multiWindowOneAppExample` creates main and GUI windows, can share OpenGL resources with `settings.shareContextWith`, disables v-sync on the GUI window, creates one `ofApp`, calls `setupGui()`, and attaches a GUI-window draw listener with `ofAddListener(guiWindow->events().draw, mainApp.get(), &ofApp::drawGui)`. Source: `openFrameworks/examples/windowing/multiWindowOneAppExample/src/main.cpp`.

Use this when one app owns model/state and an auxiliary window is only another view/control surface. When touching OpenGL objects across windows, inspect whether `shareContextWith` is required in the target oF/GLFW setup.

Window ownership, event-listener ownership, and OpenGL context sharing are separate decisions. A shared context can make selected GL resources visible across windows, but it does not manage C++ object or listener lifetime. Store auxiliary listeners on an owner that outlives their callbacks; load `runtime-and-resources.md` for token and legacy-listener patterns.

## Apple Objective-C++ boundaries

For macOS/iOS/tvOS/visionOS code, prefer a C++ public surface and private Objective-C++ implementation:

- `ofxiOS.h` says any `.cpp` file that includes it needs to be renamed to `.mm` for Objective-C++ support. Source: `openFrameworks/addons/ofxiOS/src/ofxiOS.h`.
- AVFoundation-related oF headers expose C++ classes but guard Objective-C members with `__OBJC__` or present them as `void *` to non-ObjC translation units. Sources: `openFrameworks/libs/openFrameworks/video/ofAVFoundationPlayer.h`, `openFrameworks/libs/openFrameworks/video/ofAVFoundationGrabber.h`.
- `ofAVEngineSoundPlayer.h` uses an Objective-C object alias only under `__OBJC__` and otherwise uses an opaque pointer-like type. Source: `openFrameworks/libs/openFrameworks/sound/ofAVEngineSoundPlayer.h`.

Agent rule: unless the target is intentionally Apple-only, do not make users include Apple framework headers or Objective-C syntax from ordinary `ofApp.h`, addon public headers, or C++ examples. Use C++ wrappers, PIMPL, opaque handles, and `.mm` implementation files so consumers can treat the addon/app as normal C++.

## Logging and diagnostics

Use oF logging helpers instead of ad-hoc `std::cout` for runtime diagnostics:

- `ofLog.h` declares `ofSetLogLevel`, module-specific log levels, `ofLogToFile`, `ofLogToConsole`, and typed log helpers such as `ofLogNotice`, `ofLogWarning`, and `ofLogError`. Source: `openFrameworks/libs/openFrameworks/utils/ofLog.h`.
- `ofLogExample` demonstrates global and module-specific log levels, stream-style logging, printf-style logging, file logging under `bin/data`, and returning to console logging. Source: `openFrameworks/examples/strings/ofLogExample/src/ofApp.cpp`.
- Core oF source uses module names for diagnostics such as `ofLogWarning("ofRectangle")`. Source: `openFrameworks/libs/openFrameworks/`.

Recommended agent behavior:

```cpp
ofLogNotice("MyModule") << "started";
ofLogWarning("MyModule") << "recoverable issue";
ofLogError("MyModule") << "operation failed";
```

For verbose investigation, prefer:

```cpp
ofSetLogLevel("MyModule", OF_LOG_VERBOSE);
ofLogVerbose("MyModule") << "details";
```

Do not leave noisy per-frame logs in `update()` or `draw()` unless guarded by log level, throttling, or a debug flag; repeated callbacks can flood console/file output.

## Agent good/bad know-how checklist

Good:

- Start from the nearest oF example and the target checkout headers.
- Keep `setup/update/draw` responsibilities clear.
- Prefer `std::`/narrow `using std::name` over broad namespace imports.
- Keep Apple Objective-C++ details out of public headers unless the API is intentionally Apple-only.
- Use `ofLog*` with module names for diagnostics.
- For multi-window, choose either separate app instances or one-app/listener pattern deliberately.
- Verify generated project membership after adding new `.cpp` files.

Bad:

- Inventing APIs from memory instead of checking `examples/` or `libs/openFrameworks/`.
- Adding global `using namespace std;` to headers.
- Leaking `#import`, `@interface`, `NSObject`, `id<...>`, or Apple framework handles into public C++ headers.
- Moving asset loads or blocking work into `draw()` without a measured reason.
- Sharing multi-window state through unmanaged globals when explicit ownership is available.
- Assuming all window contexts share GL resources; check the example and target settings.
- Using `std::cout` for all diagnostics when oF logging can set levels, modules, and output channels.
