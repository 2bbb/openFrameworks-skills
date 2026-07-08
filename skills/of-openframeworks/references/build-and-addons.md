# openFrameworks build, addons, and CI

Use this page as a source-backed checklist, not as a substitute for inspecting the target project.

## Project files

- `addons.make` is documented as the file used to select addons for a project; it is separate from `config.make`. Source: `openFrameworks/docs/msys2.md`.
- Template Makefiles load `config.make` if present, set `OF_ROOT` when missing, then include `$(OF_ROOT)/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`. Source: `openFrameworks/scripts/templates/*/Makefile`.
- `OF_ROOT` defaults commonly assume project depth under the oF tree; oF docs recommend keeping projects inside the same oF release because outside/non-standard paths make relative paths more fragile. Sources: `openFrameworks/scripts/templates/*/Makefile`, `openFrameworks/docs/projectgenerator.md`.

Typical template shape:

```makefile
ifneq ($(wildcard config.make),)
    include config.make
endif

ifndef OF_ROOT
    OF_ROOT=../../..
endif

include $(OF_ROOT)/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk
```

## `addon_config.mk`

Bundled addon configs document that all variables are optional; when absent, PG and makefiles try to parse values from the filesystem. They also document `=` as replacing parsed/current values and `+=` as appending. Source: `openFrameworks/addons/ofxAssimp/addon_config.mk`.

Common sections and variables visible in bundled addons:

```makefile
meta:
    ADDON_NAME = ofxMyAddon
    ADDON_DESCRIPTION = Short description
    ADDON_AUTHOR = Author

common:
    ADDON_INCLUDES = src libs/somelib/include
    ADDON_DEPENDENCIES = ofxGui ofxOsc
    ADDON_SOURCES_EXCLUDE = libs/somelib/examples/%

osx:
    ADDON_FRAMEWORKS = Foundation OpenGL
    ADDON_SOURCES_EXCLUDE += src/platform/win/%

vs:
    ADDON_LDFLAGS = opengl32.lib
    ADDON_SOURCES_EXCLUDE += src/platform/posix/%

linux64:
    ADDON_PKG_CONFIG_LIBRARIES = opencv4
    ADDON_LDFLAGS = -lGL
```

Sources: `openFrameworks/addons/ofxAssimp/addon_config.mk`, `openFrameworks/addons/ofxOpenCv/addon_config.mk`, `openFrameworks/addons/ofxOsc/addon_config.mk`, `openFrameworks/addons/ofxPoco/addon_config.mk`.

## Excludes and platform sections

- Exclusion variables in bundled configs use `%` as the wildcard for path matching. Source: `openFrameworks/addons/ofxAssimp/addon_config.mk`.
- Platform section names used by bundled configs include examples such as `osx`, `macos`, `vs`, `msys2`, `linux`, `linux64`, `linuxarmv6l`, `linuxarmv7l`, `linuxaarch64`, `ios`, `android/...`, and `emscripten`. Sources: `openFrameworks/addons/ofxOsc/addon_config.mk`, `openFrameworks/addons/ofxOpenCv/addon_config.mk`.
- PG platform options are a narrower list in `platformsOptions`; check it when generating projects. Source: `projectGenerator/commandLine/src/utils/Utils.h`.

## Project Generator interactions

Use Project Generator after changes that should affect generated project files: addon selection, target platforms, templates, external source folders, frameworks, or IDE membership. PG docs state it can create and update projects, add addons, and recursively update projects. Sources: `openFrameworks/docs/projectgenerator.md`, `projectGenerator/commandLine/readme.md`.

For CLI details, load the `of-project-generator` skill.

## Test apps

openFrameworks local tests provide the source-backed pattern for headless command-line tests:

- Include `ofAppNoWindow.h` in `main.cpp`.
- Use `ofxUnitTestsApp` as the test app base and assertion macros such as `ofxTest`, `ofxTestEq`, `ofxTestGt`, and `ofxTestLt`.

Sources: `openFrameworks/tests/addons/ofxOsc/src/main.cpp`, `openFrameworks/tests/types/parameters/src/main.cpp`, `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`.

## Runtime/build checks

- Make-based template targets are defined by the oF make system included from `compile.project.mk`; inspect the target project and local oF makefiles before assuming target names. Source: `openFrameworks/scripts/templates/*/Makefile`.
- macOS generated app bundles and Linux `bin/` outputs are project/template dependent; inspect the generated project before writing a smoke command. Source: `openFrameworks/scripts/templates/`, `openFrameworks/examples/`.
