# openFrameworks conventions and gotchas

Use local source as the authority for signatures, names, and ownership. These notes summarize patterns visible in the checked-out references.

## API and app shape

- For `ofApp`, `setup/update/draw`, namespace, multi-window, and logging guidance, load `app-architecture.md` first.
- Template app files use an `ofApp` class with `setup()`, `update()`, `draw()`, and event callbacks such as `keyPressed`, `mouseDragged`, and `windowResized`. Source: `openFrameworks/examples/templates/emptyExample/src/ofApp.h`.
- Core and addon classes commonly use `of`/`ofx` prefixes (`ofTexture`, `ofFbo`, `ofxOsc`, etc.). Sources: `openFrameworks/libs/openFrameworks/`, `openFrameworks/addons/`.
- Prefer examples near the target feature before inventing a new pattern; examples are organized by topic and intended as small demonstrations. Source: `openFrameworks/examples/README.md`.

## Resources and assets

- Many examples load assets from `bin/data` or save output through oF file/image APIs. Use `ofToDataPathFS(path, true)` when a non-oF API needs an absolute path; do not hardcode a launch-directory assumption. Source: `openFrameworks/libs/openFrameworks/utils/ofFileUtils.h`.
- For GPU/media objects, check the local class header/source for required `allocate()`, `load()`, `update()`, `isFrameNew()`, `isAllocated()`, `close()`, or `clear()` calls before changing ownership. Source: `openFrameworks/libs/openFrameworks/`.
- Load `runtime-and-resources.md` for detailed data-path, thread handoff, event lifetime, timing, video, and render-state guidance.

## Logging and diagnostics

- The oF source and `ofLogExample` use `ofLogNotice`, `ofLogWarning`, `ofLogError`, `ofSetLogLevel`, `ofLogToFile`, and `ofLogToConsole`. Sources: `openFrameworks/libs/openFrameworks/`, `openFrameworks/examples/strings/ofLogExample/src/ofApp.cpp`, `openFrameworks/libs/openFrameworks/utils/ofLog.h`.

Example style:

```cpp
ofLogNotice("Component") << "message";
ofLogWarning("Component") << "warning";
ofLogError("Component") << "error";
```

For automated tests, follow local `ofxUnitTests` examples rather than relying on visual inspection. Sources: `openFrameworks/tests/`, `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`.

## OpenGL and GLSL checks

- oF examples include cases that explicitly call `ofDisableArbTex()` when model texture coordinates need `GL_TEXTURE_2D`. Source: `openFrameworks/examples/ios/assimpExample/src/ofApp.mm`.
- Shader and texture behavior depends on renderer/platform/example context; inspect nearby `examples/gl`, `examples/shader`, and the target code before changing shader versions, texture targets, matrices, or UV assumptions. Sources: `openFrameworks/examples/gl/`, `openFrameworks/examples/shader/`, `openFrameworks/libs/openFrameworks/gl/`.

## File splitting and generated projects

- Make templates include the oF make layer, but generated IDE projects explicitly list files. Inspect current generated files and PG workflow before splitting `ofApp.cpp` into new translation units. Sources: `openFrameworks/scripts/templates/*/Makefile`, `openFrameworks/scripts/templates/*/*.vcxproj`, `openFrameworks/scripts/templates/*/*.xcodeproj`, `openFrameworks/docs/projectgenerator.md`.
