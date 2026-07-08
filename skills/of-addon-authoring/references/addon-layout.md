# Addon Layout and Project Files

Source basis:

- `projectGenerator/commandLine/src/main.cpp` parses `addons.make` when updating a project (around `updateProject`).
- `projectGenerator/commandLine/src/projects/baseProject.cpp` reads `projectDir/addons.make` in `parseAddons()` and sends each non-comment line to `addAddon()`.
- `projectGenerator/commandLine/src/addons/ofAddon.cpp` loads addon sources from `<addon>/src`, include folders from `<addon>/src` and `<addon>/libs`, and libraries/frameworks from `<addon>/libs`.
- `of-skill/addon-guide.md` documents the repo-local addon layout and testApp conventions.

## Recommended Tree

```text
ofxYourAddon/
  addon_config.mk
  src/
    ofxYourAddon.h
    ofxYourAddon.cpp
    platform/
      osx/
      vs/
      linux/
      ios/
  libs/
    vendor/
      include/
      src/
      lib/
  testApp/
    addons.make
    Makefile
    src/
      main.cpp
      ofApp.h
      ofApp.cpp
  example-basic/
    addons.make
    Makefile
    src/
```

Keep generated project files (`.xcodeproj`, `.vcxproj`, `.qbs`, `.cbp`) consistent with projectGenerator output. Addon source should usually live in the addon, not copied into each example.

## `addons.make` vs `addon_config.mk`

`addons.make`:

- Lives inside each project directory: `testApp/`, `example-*`, or an app under `apps/myApps/`.
- Is plain text, one addon name or local addon path per line.
- Tells projectGenerator and oF build logic which addons the project uses.
- Is not a Makefile despite the extension.

Example:

```text
ofxYourAddon
ofxGui
```

`addon_config.mk`:

- Lives at the addon root.
- Describes how the addon builds: metadata, include paths, libraries, flags, framework lists, data files, and platform exclusions.
- Uses oF/projectGenerator's sectioned key-value parser, not normal Makefile targets.

## Local Addons

Local addons are supported when an `addons.make` entry is a path with a parent component and that path exists relative to the project directory. `ofAddon::load()` sets `isLocalAddon = true` in that case and otherwise looks under `<OF_ROOT>/addons/<name>` (`projectGenerator/commandLine/src/addons/ofAddon.cpp`). The source comment says a local addon is any valid filesystem addon, not necessarily a folder named `local_addons`.

Example from a project directory:

```text
../../../addons/ofxYourAddon
../local_addons/ofxExperimentalThing
```

Preserve the user's exact `addons.make` entry where possible; projectGenerator stores `addonMakeName` before cleaning comments.

## Bundled Libs

ProjectGenerator scans `libs/` recursively for include folders and libraries (`ofAddon::load()` and `parseLibsPath()`). Real bundled-lib examples:

- `openFrameworks/addons/ofxOpenCv/addon_config.mk` lists Android static libraries under `libs/opencv/lib/android/...` and Emscripten libraries with `%`.
- `openFrameworks/addons/ofxAssimpModelLoader/addon_config.mk` excludes system-provided Linux Assimp libs with `ADDON_LIBS_EXCLUDE` and uses Android/macOS specific `ADDON_LIBS`.
- `openFrameworks/addons/ofxKinect/addon_config.mk` uses `ADDON_PKG_CONFIG_LIBRARIES = libusb-1.0` on Linux/MSYS2 and platform-specific include exclusions.

Guidance:

- Put vendored headers under `libs/<name>/include` when possible.
- Put vendored source under `libs/<name>/src` only when it should compile into the consuming app.
- Put prebuilt libraries under `libs/<name>/lib/<platform>/...` and specify `ADDON_LIBS` when automatic discovery is not enough.
- Use `ADDON_PKG_CONFIG_LIBRARIES` for system libraries on Linux/MSYS2 when the openFrameworks examples do that for the same kind of dependency.

## Examples and `testApp`

Every buildable example needs its own `addons.make`. Forgetting it leaves addon types unresolved even when the addon itself is valid.

For addon validation, prefer:

- `testApp/` for a minimal build/test target.
- `example-basic/` for user-facing demonstration.
- Additional `example-*` folders only when they prove different APIs or platform integrations.

The standard `Makefile` under an addon example normally points `OF_ROOT` three levels up when the project is `addons/ofxName/testApp`:

```makefile
ifndef OF_ROOT
	OF_ROOT=../../..
endif
include $(OF_ROOT)/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk
```
