# Platform-Specific Code and ObjC++ Boundaries

Source basis:

- `projectGenerator/commandLine/src/addons/ofAddon.cpp` recursively discovers source from `src/` and `libs/`, then applies `ADDON_SOURCES_EXCLUDE` to `srcFiles`, C/C++/ObjC source lists, and headers.
- `openFrameworks/addons/ofxiOS/src/ofxiOS.h` says files including it need `.mm` to support Objective-C++.
- `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.h` and `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.mm` and other `ofxiOS` `.mm` files show ObjC++ implementation living in `.mm`.
- `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.h` and `openFrameworks/addons/ofxiOS/src/utils/ofxiOSExtras.mm` show a public C++/Objective-C++ boundary in a bundled addon utility.

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

Do not expose Objective-C types in public addon headers. Headers are included by user `.cpp` files and by non-Apple compilers. If a public API needs Apple-backed implementation, use PIMPL or an internal pure-C++ interface.

```cpp
// src/ofxYourAddon.h -- pure C++
#pragma once
#include <memory>

class ofxYourAddon {
public:
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
```

Also add Apple-only source exclusions for other platforms. The evidence from `ofxiOS.h` is direct: any `.cpp` files including it must be renamed to `.mm` for Objective-C++ support.

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
