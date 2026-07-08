# `addon_config.mk` Reference

Source basis:

- `projectGenerator/commandLine/src/addons/ofAddon.h` defines parser states, metadata keys, and project variable constants.
- `projectGenerator/commandLine/src/addons/ofAddon.cpp` parses sections, supports `=` and `+=`, splits values on spaces or quoted groups, prefixes relative paths with the addon path, and applies exclusions.
- `openFrameworks/addons/ofxAssimp/addon_config.mk`, `ofxAssimpModelLoader/addon_config.mk`, `ofxOpenCv/addon_config.mk`, `ofxOsc/addon_config.mk`, and `ofxKinect/addon_config.mk` are real examples.

## Source-Verified Sections

`ofAddon.h` defines these parse states:

```text
meta
common
linux
linux64
linux/64
msys2
vs
linuxarmv6l
linuxarmv7l
linuxaarch64
linux/armv6l
linux/armv7l
linux/aarch64
linux/arm64
android/armeabi
android/armeabi-v7a
android/arm64-v8a
android/x86
android/x86_64
emscripten
emscripten/32
emscripten/64
android
ios
osx
tvos
macos
watchos
visionos
catos
```

Use the section names present in the target oF version and real addons. `osx`, `vs`, `msys2`, `linux64`, `linux`, `linuxarmv6l`, `linuxarmv7l`, `linuxaarch64`, `android/*`, `emscripten`, and `ios` are present in bundled addon configs. `ofxOsc` also contains a `macos:` block.

## Source-Verified Keys

Metadata keys accepted in `meta:` (`AddonMetaVariables` in `ofAddon.h`):

```text
ADDON_NAME
ADDON_DESCRIPTION
ADDON_AUTHOR
ADDON_TAGS
ADDON_URL
```

Project/build keys listed in `AddonProjectVariables`:

```text
ADDON_DEPENDENCIES
ADDON_INCLUDES
ADDON_CFLAGS
ADDON_CPPFLAGS
ADDON_LDFLAGS
ADDON_LIBS
ADDON_DEFINES
ADDON_SOURCES
ADDON_HEADER_SOURCES
ADDON_C_SOURCES
ADDON_CPP_SOURCES
ADDON_OBJC_SOURCES
ADDON_LIBS_EXCLUDE
ADDON_LIBS_DIR
ADDON_SOURCES_EXCLUDE
ADDON_INCLUDES_EXCLUDE
ADDON_FRAMEWORKS_EXCLUDE
ADDON_DATA
ADDON_PKG_CONFIG_LIBRARIES
ADDON_FRAMEWORKS
ADDON_DLLS_TO_COPY
ADDON_ADDITIONAL_LIBS
```

`ofAddon.h` also defines `ADDON_XCFRAMEWORKS`, and `ofAddon.cpp` has parse logic for it, but it is absent from `AddonProjectVariables`. Be conservative: do not rely on `ADDON_XCFRAMEWORKS` in `osx:` without testing the exact projectGenerator version. Prefer automatic `.xcframework` discovery under `libs/` for Apple package targets or explicit `ADDON_LIBS` where known-good examples use it.

## Assignment Semantics

`=` replaces the parsed/default value. `+=` appends. This is stated in every bundled `addon_config.mk` header and implemented in `ofAddon.cpp` with `addToValue`.

Use `+=` for platform exclusions and extra include paths unless intentionally replacing auto-discovered values:

```makefile
common:
	ADDON_INCLUDES += libs/vendor/include
	ADDON_DEPENDENCIES += ofxGui

vs:
	ADDON_DEFINES += MY_ADDON_USE_D3D11
	ADDON_LDFLAGS += d3d11.lib dxgi.lib
```

Use `=` when selecting an exact library list, as `ofxOpenCv` and `ofxAssimpModelLoader` do for Android and Emscripten `ADDON_LIBS`.

## Common Template

```makefile
meta:
	ADDON_NAME = ofxYourAddon
	ADDON_DESCRIPTION = Short, factual addon description
	ADDON_AUTHOR = Author Name
	ADDON_TAGS = "graphics" "hardware"
	ADDON_URL = https://example.invalid/ofxYourAddon

common:
	ADDON_INCLUDES += src
	ADDON_INCLUDES += libs/vendor/include
	ADDON_SOURCES_EXCLUDE += libs/vendor/examples/%
	ADDON_SOURCES_EXCLUDE += libs/vendor/tests/%

osx:
	ADDON_FRAMEWORKS += Foundation Metal IOSurface
	ADDON_SOURCES_EXCLUDE += src/platform/vs/%
	ADDON_SOURCES_EXCLUDE += src/platform/linux/%

vs:
	ADDON_DEFINES += NOMINMAX
	ADDON_LDFLAGS += d3d11.lib dxgi.lib
	ADDON_SOURCES_EXCLUDE += src/platform/osx/%
	ADDON_SOURCES_EXCLUDE += src/platform/linux/%

linux64:
	ADDON_PKG_CONFIG_LIBRARIES += libdrm
	ADDON_LDFLAGS += -lGL
	ADDON_SOURCES_EXCLUDE += src/platform/osx/%
	ADDON_SOURCES_EXCLUDE += src/platform/vs/%
```

## Exclusions

`ofAddon.cpp` converts exclusion patterns by replacing `%` with `.*` before applying a regex. Use `%` for addon_config exclusion globs. Real examples:

- `openFrameworks/addons/ofxOsc/addon_config.mk` excludes `libs/oscpack/src/ip/win32/%` on POSIX platforms and `libs/oscpack/src/ip/posix/%` on Windows.
- `openFrameworks/addons/ofxKinect/addon_config.mk` excludes `libs/libfreenect/platform/%` and `libs/libusb-1.0/%`.
- `openFrameworks/addons/ofxOpenCv/addon_config.mk` excludes `libs/opencv/%` for system package builds.

Do not use `*` in `ADDON_SOURCES_EXCLUDE`, `ADDON_INCLUDES_EXCLUDE`, `ADDON_LIBS_EXCLUDE`, or `ADDON_FRAMEWORKS_EXCLUDE`. Use `%`.

## Platform Notes

- Windows Visual Studio section is `vs`; MSYS2 is `msys2`.
- Use `/DNAME` or `ADDON_DEFINES` for Windows-style defines; use `-DNAME` in Unix compiler flags.
- Linux libraries often belong in `ADDON_PKG_CONFIG_LIBRARIES` or `ADDON_LDFLAGS`.
- Apple system frameworks belong in `ADDON_FRAMEWORKS` when they are framework names, not paths.
- If a framework value includes `/` or `\`, `ofAddon.cpp` treats it as a path and prefixes it with the addon path.
