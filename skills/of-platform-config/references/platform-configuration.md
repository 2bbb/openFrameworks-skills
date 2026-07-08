# openFrameworks platform configuration reference

Use this reference for concrete platform configuration facts. Citations point to local primary/reference files under this repository.

## Contents

- Platform setup notes
- Project Generator behavior and platform keys
- `addons.make` vs `addon_config.mk`
- Verified `addon_config.mk` sections and `ADDON_*` keys
- Platform-specific libraries, flags, and exclusions
- Bundled libraries and local addons
- Source citations

## Platform setup notes

These are concise setup facts verified from local openFrameworks docs/scripts. Do not expand them with external assumptions.

### macOS / OS X

- The docs say OS X use requires Xcode; examples can be opened with `.xcodeproj` and built/run from Xcode. Source: `openFrameworks/docs/osx.md`.
- New projects should be created with Project Generator, or by copying/renaming an existing similar example/project. Source: `openFrameworks/docs/osx.md`.
- The source tree contains both `scripts/templates/osx` and `scripts/templates/macos`, and Project Generator source maps host/target strings including `osx` and `macos`. Sources: `openFrameworks/scripts/templates/osx/config.make`, `openFrameworks/scripts/templates/macos/config.make`, `projectGenerator/commandLine/src/utils/Utils.h`.

### Linux

- Linux setup requires running a distro-specific `scripts/linux/<distro>/install_dependencies.sh`; optional codecs are installed with `install_codecs.sh`. Source: `openFrameworks/docs/linux.md`.
- The docs compile OF with `scripts/linux/compileOF.sh -jN`, then examples with `make` and `make run`. Source: `openFrameworks/docs/linux.md`.
- Linux Project Generator command-line install is described as `scripts/linux/compilePG.sh` in the docs. Source: `openFrameworks/docs/linux.md`.

### Windows Visual Studio

- Visual Studio docs require Git for Windows, Visual Studio 2022 or 2026 Community, and the Desktop development with C++ workload. Source: `openFrameworks/docs/visualstudio.md`.
- The docs tell git users to run a library download script and then use Project Generator for Visual Studio project files. Source: `openFrameworks/docs/visualstudio.md`.
- Project Generator's Visual Studio platform key is `vs`. Source: `projectGenerator/commandLine/src/utils/Utils.h`.

### Windows MSYS2

- MSYS2 docs require an MSYS2 install, package update with `pacman -Syu --noconfirm --needed`, running `scripts/msys2/install_dependencies.sh`, and compiling OF in `libs/openFrameworksCompiled/project` with `make`. Source: `openFrameworks/docs/msys2.md`.
- The docs distinguish MSYS/MINGW32/MINGW64 shells and warn to use the shell matching the chosen flavor. Source: `openFrameworks/docs/msys2.md`.
- MSYS2 project files use `config.make` and `addons.make`; `addons.make` lists one addon per line from the addons folder. Source: `openFrameworks/docs/msys2.md`.
- MSYS2 can copy runtime DLLs with `make copy_dlls`. Source: `openFrameworks/docs/msys2.md`.

### iOS

- iOS is a Project Generator platform key (`ios`) and an `addon_config.mk` parse section (`ios`). Sources: `projectGenerator/commandLine/src/utils/Utils.h`, `projectGenerator/commandLine/src/addons/ofAddon.h`.
- iOS examples under `examples/ios` use `ofxiOS` and Xcode project workflows. Sources: `openFrameworks/examples/ios/emptyExample/README.md`, `openFrameworks/addons/ofxiOS/src/ofxiOS.h`.
- The iOS library download script delegates to the macOS library download path with `-p macos`. Source: `openFrameworks/scripts/ios/download_libs.sh`.

### Android

- Android Studio docs list Android Studio, SDK/Build Tools/NDK/CMake/Command Line Tools, opening Android Studio projects from `examples/android`, and building directly with `./gradlew assembleDebug`. Source: `openFrameworks/docs/android_studio.md`.
- Git users are told to run `scripts/android/download_libs.sh` and use Project Generator for Android Studio project files. Source: `openFrameworks/docs/android_studio.md`.
- Project Generator's platform key is `android`; `addon_config.mk` supports general `android` plus ABI sections such as `android/armeabi-v7a`, `android/arm64-v8a`, `android/x86`, and `android/x86_64`. Sources: `projectGenerator/commandLine/src/utils/Utils.h`, `projectGenerator/commandLine/src/addons/ofAddon.h`.

### Emscripten

- `addon_config.mk` supports `emscripten`, `emscripten/32`, and `emscripten/64` parse sections. Source: `projectGenerator/commandLine/src/addons/ofAddon.h`.
- The local install script checks or installs Emscripten through Homebrew on macOS, apt on Linux, winget on Windows, or clones/activates `emsdk` when asked to install from source. Source: `openFrameworks/scripts/emscripten/install_emscripten.sh`.
- Emscripten templates use normal `config.make`/`OF_ROOT` inclusion into `libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`. Source: `openFrameworks/scripts/templates/emscripten/Makefile`.
- `emscripten` appears in addon parse sections and core addon configs, but not in `platformsOptions` for Project Generator command-line `--platforms` in the inspected source. Sources: `projectGenerator/commandLine/src/addons/ofAddon.h`, `projectGenerator/commandLine/src/utils/Utils.h`, `openFrameworks/addons/ofxAssimp/addon_config.mk`.

## Project Generator behavior and platform keys

- Command-line option help describes `--platforms, -p` as a platform list. Source: `projectGenerator/commandLine/src/main.cpp`.
- `allplatforms` expands to every entry in `platformsOptions`. Source: `projectGenerator/commandLine/src/main.cpp`.
- Verified `platformsOptions`: `android`, `ios`, `linux`, `linux64`, `linuxarmv6l`, `linuxarmv7l`, `linuxaarch64`, `msys2`, `osx`, `vs`, `tvos`. Source: `projectGenerator/commandLine/src/utils/Utils.h`.
- Host/target string map also includes `macos` for `OF_TARGET_MACOS`; use this only where the source path or config already uses `macos`. Source: `projectGenerator/commandLine/src/utils/Utils.h`.
- Template configs use `PLATFORMS`, `DESCRIPTION`, and `RENAME`. A template is supported when its `PLATFORMS` contains the current target. Source: `projectGenerator/commandLine/src/projects/baseProject.cpp`.
- Project Generator docs say it can generate platform project files, add addons, update existing projects, and recursively update projects in advanced mode. Source: `openFrameworks/docs/projectgenerator.md`.
- Project Generator docs recommend keeping projects inside the OF tree because relative paths are less fragile. Source: `openFrameworks/docs/projectgenerator.md`.

## `addons.make` vs `addon_config.mk`

Use `addons.make` for the project-level addon list. Use `addon_config.mk` inside an addon for build metadata.

- `addons.make`: one addon name/path per line for the project. MSYS2 docs explicitly describe adding addon names here. Source: `openFrameworks/docs/msys2.md`.
- Project Generator cleans addon lines by stripping comments after `#`, preserves the original `addons.make` spelling in `addonMakeName`, and loads each addon for the active target platform. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- Local addons are detected when the `addons.make` entry has a parent path and exists relative to the project directory; generated file grouping uses `local_addons`. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- `addon_config.mk`: parsed after source/include/lib discovery and before exclusions are applied. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

## Verified `addon_config.mk` sections

Source: `projectGenerator/commandLine/src/addons/ofAddon.h`.

Use these section headers exactly with a trailing colon:

```make
meta:
common:
linux:
linux64:
linux/64:
linuxarmv6l:
linuxarmv7l:
linuxaarch64:
linux/armv6l:
linux/armv7l:
linux/aarch64:
linux/arm64:
msys2:
vs:
android:
android/armeabi:
android/armeabi-v7a:
android/arm64-v8a:
android/x86:
android/x86_64:
emscripten:
emscripten/32:
emscripten/64:
ios:
osx:
tvos:
macos:
watchos:
visionos:
catos:
```

Parsing rule: `meta` and `common` always apply. Any other section applies only when it equals the target platform string passed to addon parsing. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

## Verified `ADDON_*` keys

Source: `projectGenerator/commandLine/src/addons/ofAddon.h` and parser handling in `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

Metadata keys for `meta:`:

- `ADDON_NAME`
- `ADDON_DESCRIPTION`
- `ADDON_AUTHOR`
- `ADDON_TAGS`
- `ADDON_URL`

Build/project keys:

- `ADDON_DEPENDENCIES`
- `ADDON_INCLUDES`
- `ADDON_CFLAGS`
- `ADDON_CPPFLAGS`
- `ADDON_LDFLAGS`
- `ADDON_LIBS`
- `ADDON_DEFINES`
- `ADDON_SOURCES`
- `ADDON_HEADER_SOURCES`
- `ADDON_C_SOURCES`
- `ADDON_CPP_SOURCES`
- `ADDON_OBJC_SOURCES`
- `ADDON_LIBS_EXCLUDE`
- `ADDON_LIBS_DIR`
- `ADDON_SOURCES_EXCLUDE`
- `ADDON_INCLUDES_EXCLUDE`
- `ADDON_FRAMEWORKS_EXCLUDE`
- `ADDON_DATA`
- `ADDON_PKG_CONFIG_LIBRARIES`
- `ADDON_FRAMEWORKS`
- `ADDON_DLLS_TO_COPY`
- `ADDON_ADDITIONAL_LIBS`
- `ADDON_XCFRAMEWORKS` is implemented by `parseVariableValue`, but is absent from `AddonProjectVariables` in the inspected header; be cautious and verify with the target projectGenerator version before relying on it in non-`common` sections.

Assignment behavior:

- `=` replaces the variable's accumulated value; `+=` appends. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- Values split on spaces unless quoted; `$(OF_ROOT)` and environment variables can be substituted. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- Relative paths for include/source/lib-style keys are resolved from the addon path into project-relative paths. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

## Platform-specific libraries, flags, and exclusions

- `ADDON_PKG_CONFIG_LIBRARIES`: used by core addons on Linux-like targets to use system packages instead of bundled libs; examples include `ofxOpenCv` and `ofxAssimpModelLoader`. Sources: `openFrameworks/addons/ofxOpenCv/addon_config.mk`, `openFrameworks/addons/ofxAssimpModelLoader/addon_config.mk`.
- `ADDON_LIBS_EXCLUDE` and `ADDON_INCLUDES_EXCLUDE`: core addons use these to suppress bundled library trees when platform system packages are used. Sources: `openFrameworks/addons/ofxOpenCv/addon_config.mk`, `openFrameworks/addons/ofxAssimpModelLoader/addon_config.mk`.
- `ADDON_SOURCES_EXCLUDE`: used when unwanted sources remain after include-path exclusions; parser comments say source exclusions should use this field. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- `%` wildcard: exclusions replace `.` with escaped dots, `%` with `.*`, prefix the pattern with `.*`, normalize backslashes to forward slashes, and apply regex search. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- `ADDON_FRAMEWORKS`: system frameworks can be bare names; paths with slashes are treated as addon-relative paths. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- `ADDON_DLLS_TO_COPY`: parsed into DLL copy paths; projectGenerator also recursively finds DLLs for `vs`, `msys2`, `vscode`, and Linux target strings. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- `ADDON_DEFINES`, `ADDON_CFLAGS`, `ADDON_CPPFLAGS`, and `ADDON_LDFLAGS` are valid project keys for platform-specific compile/link behavior. Source: `projectGenerator/commandLine/src/addons/ofAddon.h`.

## Bundled libraries and local addons

- Addon source files are discovered recursively under `src`; include paths are discovered from `src` and `libs` folders, with platform-aware folder filtering. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- For Apple targets `osx`, `macos`, `ios`, and `tvos`, library scanning looks under both `macos` and `osx` folders and scans frameworks for both names. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- For other targets, library scanning uses the active platform string. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- Folder filtering treats known platform folder names as platform-specific and skips folders that do not match the active platform, with special cases for `win32`/Windows and `posix`/non-Windows. Source: `projectGenerator/commandLine/src/utils/Utils.cpp`.
- `ADDON_ADDITIONAL_LIBS` and `ADDON_LIBS_DIR` allow scanning additional addon-relative library directories. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.
- Local addon paths in `addons.make` are not restricted to a folder named `local_addons`; they only need to resolve from the project directory. Source: `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

## Source citations

Primary/local sources used:

- Project Generator platform keys and platform map: `projectGenerator/commandLine/src/utils/Utils.h`
- Project Generator platform/folder filtering: `projectGenerator/commandLine/src/utils/Utils.cpp`
- Project Generator CLI platform option: `projectGenerator/commandLine/src/main.cpp`
- Template parsing and `PLATFORMS`: `projectGenerator/commandLine/src/projects/baseProject.cpp`
- Addon parser sections/keys/load behavior: `projectGenerator/commandLine/src/addons/ofAddon.h`, `projectGenerator/commandLine/src/addons/ofAddon.cpp`
- Platform docs: `openFrameworks/docs/osx.md`, `openFrameworks/docs/linux.md`, `openFrameworks/docs/visualstudio.md`, `openFrameworks/docs/msys2.md`, `openFrameworks/docs/android_studio.md`, `openFrameworks/docs/projectgenerator.md`
- Emscripten install/template sources: `openFrameworks/scripts/emscripten/install_emscripten.sh`, `openFrameworks/scripts/templates/emscripten/Makefile`
- Core addon examples: `openFrameworks/addons/ofxKinect/addon_config.mk`, `openFrameworks/addons/ofxOpenCv/addon_config.mk`, `openFrameworks/addons/ofxAssimpModelLoader/addon_config.mk`, `openFrameworks/addons/ofxOsc/addon_config.mk`
