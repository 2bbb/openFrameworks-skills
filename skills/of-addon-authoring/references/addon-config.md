# `addon_config.mk` Reference

## Contents

- [Source basis](#source-basis)
- [Source-Verified Sections](#source-verified-sections)
- [Source-Verified Keys](#source-verified-keys)
- [Assignment Semantics](#assignment-semantics)
- [Common Template](#common-template)
- [Exclusions](#exclusions)
- [Upstream source or prebuilt backend](#upstream-source-or-prebuilt-backend)
- [Platform Notes](#platform-notes)

## Source basis

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

## Upstream source or prebuilt backend

Choose the integration boundary deliberately instead of letting recursive discovery decide it accidentally.

Compile upstream source through the addon when:

- the source set is small and portable;
- required compile flags are expressible in `addon_config.mk`;
- the target project should rebuild that dependency with its own toolchain;
- samples, tests, tools, and unsupported backends can be excluded precisely.

Link a prebuilt/static backend when:

- upstream has its own substantial build system or generated configuration;
- recursive discovery would pull in mutually exclusive backends, tools, tests, or platform code;
- build time or IDE indexing becomes unreasonable;
- one audited library artifact gives a clearer boundary than hundreds of upstream translation units.

For a prebuilt boundary:

1. Keep the thin oF-facing wrapper in `src/`.
2. Put public upstream headers under `libs/<name>/include` or add their exact include directory.
3. Exclude upstream source trees with `ADDON_SOURCES_EXCLUDE += libs/<name>/src/%` when they remain in the distribution.
4. Add the actual library through `ADDON_LIBS` or the conventional platform library folders.
5. Add required system frameworks/libraries in platform sections.
6. Record the upstream version, license, architectures, deployment target, C++ runtime/ABI assumptions, and the reproducible command that built the artifact.
7. Verify both the make path and every generated IDE project promised by the addon.

PG recursively scans addon `src/` and `libs/`, then applies source/library exclusions; the oF make layer similarly discovers source under `libs/`, gathers platform libraries, and links `PROJECT_ADDONS_LIBS`. Sources: `projectGenerator/commandLine/src/addons/ofAddon.cpp`, `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/config.addons.mk`, `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`.

Do not ship a prebuilt artifact without its matching headers/license or assume a binary built for one architecture/configuration is portable to another. Prefer reproducible build scripts and checksums for generated artifacts.

## Platform Notes

- Windows Visual Studio section is `vs`; MSYS2 is `msys2`.
- Use `/DNAME` or `ADDON_DEFINES` for Windows-style defines; use `-DNAME` in Unix compiler flags.
- Linux libraries often belong in `ADDON_PKG_CONFIG_LIBRARIES` or `ADDON_LDFLAGS`.
- Apple system frameworks belong in `ADDON_FRAMEWORKS` when they are framework names, not paths.
- If a framework value includes `/` or `\`, `ofAddon.cpp` treats it as a path and prefixes it with the addon path.
