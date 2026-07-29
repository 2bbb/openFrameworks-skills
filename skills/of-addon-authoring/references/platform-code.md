# Platform-Specific Code and ObjC++ Boundaries

Source basis:

- `projectGenerator/commandLine/src/addons/ofAddon.cpp` recursively discovers source from `src/` and `libs/`, then applies `ADDON_SOURCES_EXCLUDE` to `srcFiles`, C/C++/ObjC source lists, and headers.
- `openFrameworks/addons/ofxiOS/src/ofxiOS.h` says files including it need `.mm` to support Objective-C++.
- `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.h` and `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.mm` and other `ofxiOS` `.mm` files show ObjC++ implementation living in `.mm`.
- `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.h` and `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.mm` show a public C++/Objective-C++ boundary in a bundled addon utility.
- `openFrameworks/libs/openFrameworks/video/ofAVFoundationPlayer.h`, `openFrameworks/libs/openFrameworks/video/ofAVFoundationGrabber.h`, and `openFrameworks/libs/openFrameworks/sound/ofAVEngineSoundPlayer.h` expose C++ classes while Objective-C objects are guarded by `__OBJC__` or represented as `void *`/opaque aliases for non-ObjC translation units.
- `openFrameworks/addons/ofxiOS/src/ofxiOS.h` explicitly says `.cpp` files including it need to be renamed to `.mm`, so exposing ObjC++ headers expands that requirement to users.

## Source Discovery Means Exclude Aggressively

ProjectGenerator does not know which platform subfolders are mutually exclusive unless `addon_config.mk` says so. It scans:

- `<addon>/src`
- `<addon>/libs`
- extra folders from `ADDON_LIBS_DIR`
- extra folders from `ADDON_ADDITIONAL_LIBS`

Then it excludes matching paths. Therefore, if `src/platform/osx/MetalThing.mm` exists, exclude it from `vs`, `msys2`, Linux, Android, and Emscripten sections.

Example:

```makefile
osx:
	ADDON_FRAMEWORKS += Metal IOSurface Foundation
	ADDON_SOURCES_EXCLUDE += src/platform/vs/%
	ADDON_SOURCES_EXCLUDE += src/platform/linux/%
	ADDON_SOURCES_EXCLUDE += src/platform/android/%

vs:
	ADDON_LDFLAGS += d3d11.lib dxgi.lib
	ADDON_SOURCES_EXCLUDE += src/platform/osx/%
	ADDON_SOURCES_EXCLUDE += src/platform/linux/%
	ADDON_SOURCES_EXCLUDE += src/platform/android/%

linux64:
	ADDON_SOURCES_EXCLUDE += src/platform/osx/%
	ADDON_SOURCES_EXCLUDE += src/platform/vs/%
	ADDON_SOURCES_EXCLUDE += src/platform/android/%
```

Use the folder names your addon actually uses. Keep the section list aligned with the platforms the repo supports.

## Objective-C++ and `.mm`

Use `.mm` for any implementation file that imports Objective-C or Apple framework APIs. Keep `.cpp` files standard C++.

For Apple-specific implementation, the oF-friendly default is: public headers expose pure C++ as far as possible, and Objective-C/Objective-C++ details stay in implementation files or private Apple-only headers. Users generally want to include and use an addon as C++ from `ofApp.h/.cpp`; forcing them to compile their app as Objective-C++ is a cost and should be a deliberate exception, not the default.

Do not expose Objective-C types in public addon headers. Headers are included by user `.cpp` files and by non-Apple compilers. If a public API needs Apple-backed implementation, use PIMPL or an internal pure-C++ interface.

```cpp
// src/ofxYourAddon.h -- pure C++
#pragma once
#include <memory>

class ofxYourAddon {
public:
	~ofxYourAddon();
	void setup();
private:
	class Impl;
	std::unique_ptr<Impl> impl;
};
```

```objc
// src/platform/osx/ofxYourAddonApple.mm -- ObjC++
#include "ofxYourAddon.h"
#import <Metal/Metal.h>

class ofxYourAddon::Impl {
public:
	id<MTLDevice> device = MTLCreateSystemDefaultDevice();
};

ofxYourAddon::~ofxYourAddon() = default;
```

Also add Apple-only source exclusions for other platforms. The evidence from `ofxiOS.h` is direct: any `.cpp` files including it must be renamed to `.mm` for Objective-C++ support; therefore avoid making ordinary users include such headers unless the whole target intentionally uses ObjC++.

When renaming an implementation between `.cpp` and `.mm`, first confirm that:

- the old filename is absent from generated project files and addon declarations;
- the new `.mm` file is discovered for Apple targets;
- Apple sources are excluded from non-Apple targets;
- required Apple frameworks are present in the correct `addon_config.mk` section.

Then update/regenerate generated IDE membership and perform a clean rebuild to flush stale project, object, and dependency state. Project Generator classifies `.mm` as Objective-C++ source, while the make path generates `.d` dependency files beside object files and its `clean` target removes project/addon objects and the project object-output tree. Sources: `projectGenerator/commandLine/src/projects/xcodeProject.h`, `projectGenerator/commandLine/src/projects/baseProject.cpp`, `openFrameworks/libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`.


## Public C++ API, private Apple implementation

When adding macOS/iOS/tvOS/visionOS functionality to an addon, prefer this layering:

1. Public `src/ofxThing.h`: pure C++ API, standard-library/oF types, and at most a forward-declared C++ `Impl`.
2. Public `src/ofxThing.cpp` if possible: platform-neutral forwarding and lifetime management.
3. Private `src/platform/osx/ofxThingApple.mm` or equivalent: `#import` Apple frameworks, Objective-C classes, delegates, ARC-sensitive code, and native handles.
4. `addon_config.mk`: include Apple frameworks/sources only for Apple sections and exclude Apple implementation folders everywhere else.

This matches the consumer expectation that an oF addon can be used from normal C++ project files. Only expose Objective-C/ObjC++ in public headers when the addon is explicitly Apple-only and the required `.mm` compile boundary is documented in the app/example.

## Header Hygiene

Avoid these in public `.h/.hpp` unless guarded behind Apple-only private headers that are never included by cross-platform code:

- `#import`
- `@class`, `@interface`, `@protocol`
- `NSObject`, `id<...>`, `NSString`, `MTL*`, `CVPixelBufferRef`, or other Apple framework concrete types
- Objective-C property or message syntax

Prefer:

- C++ standard/library types in public APIs.
- Forward-declared C++ classes.
- Opaque handles wrapped by implementation files.
- Platform adapters in `src/platform/<section>/`.

## Bundled Platform Libraries

For multi-platform vendored libraries:

- Keep all platforms under one vendor folder when the upstream layout is stable.
- Use `ADDON_LIBS_EXCLUDE` and `ADDON_INCLUDES_EXCLUDE` to avoid incompatible prebuilt libraries and headers.
- Use exact `ADDON_LIBS =` lists for Android and Emscripten when link order or architecture matters, following `ofxOpenCv`.
- Use `ADDON_PKG_CONFIG_LIBRARIES` on Linux/MSYS2 when system packages are expected, following `ofxAssimp`, `ofxOpenCv`, and `ofxKinect`.
