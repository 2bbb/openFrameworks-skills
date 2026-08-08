# Multi-texture, FBO, coordinate/origin, and visual debugging notes

## Multi-texture source-backed workflow

The local `multiTextureShaderExample` shows a full C++/shader pattern:

1. Call `ofDisableArbTex()` during setup so the loaded/allocated inputs use `GL_TEXTURE_2D` semantics. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
2. Allocate an output FBO and a mask FBO with `fbo.allocate(camWidth, camHeight)` and `maskFbo.allocate(camWidth, camHeight)`. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
3. Check input textures are allocated before sampling: the draw path gates on `vidGrabber.getTexture().isAllocated()` and `fingerMovie.getTexture().isAllocated()`. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
4. Draw into the FBO between `fbo.begin()` and `fbo.end()`, bind the shader between `shader.begin()` and `shader.end()`, and pass textures with `setUniformTexture()`. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
5. Use distinct texture units: `tex0` at 1, `tex1` at 2, `tex2` at 3, and `maskTex` at 4 in the example. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
6. Normalize fragment coordinates for `sampler2D` by dividing by width/height uniforms. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.

## FBO as shader input

- `ofFbo` exposes `allocate()`, `isAllocated()`, `draw()`, `getTexture()`, `begin()`, and `end()`. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.
- `ofFboSettings` contains width, height, color-buffer count, internal format, texture target, wrapping, filtering, and multisampling fields. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.
- The alpha-mask example allocates a mask FBO, draws into it with `maskFbo.begin()`/`maskFbo.end()`, then passes it to the shader with `shader.setUniformTexture("maskTex", maskFbo.getTexture(), 0)`. Source: `openFrameworks/examples/shader/07_fboAlphaMaskExample/src/ofApp.cpp`.
- The same example passes `uMaskSize` from `maskFbo.getWidth()`/`maskFbo.getHeight()` and separately passes sample texture size, then remaps coordinates in the fragment shader before sampling multiple textures. Sources: `openFrameworks/examples/shader/07_fboAlphaMaskExample/src/ofApp.cpp`, `openFrameworks/examples/shader/07_fboAlphaMaskExample/bin/data/shadersGL3/shader.frag`.

## Composable postprocess and copy passes

When a shader/FBO pass becomes one layer in a larger engine, make these contracts explicit:

- **Input lifetime:** every sampled texture must remain alive and allocated through the draw. Required inputs should fail visibly when missing. For a sampler explicitly defined as optional, gate the source with `isAllocated()`, log/test both present and missing paths, and keep a real, long-lived allocated fallback texture when the shader contract still requires a binding.
- **Texture units:** assign units centrally for the whole pass/engine. `setUniformTexture()` binds the requested unit; two helpers choosing the same unit can overwrite each other's assumptions. Sources: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`, `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
- **Render target ownership:** pair every `fbo.begin()`/`end()` and do not reuse a shared scratch FBO from nested save/render paths unless reentrancy is designed and tested.
- **Raw blits:** prefer oF renderer/FBO helpers. If calling `glBlitFramebuffer` directly, bind the intended read and draw framebuffers explicitly and restore the surrounding framebuffer state. oF's multisample resolve path calls renderer `bindForBlitting()` before the blit and `unbind()` afterward. Sources: `openFrameworks/libs/openFrameworks/gl/ofFbo.cpp`, `https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBlitFramebuffer.xhtml`.
- **Alpha and draw state:** choose the clear alpha and blend/depth behavior for each pass, then restore state before returning. An opaque clear is a semantic decision, not a neutral reset for a transparent pipeline.
- **Allocation cost:** allocate feedback/intermediate FBOs lazily or on size/format changes, not unconditionally each frame; release them with the owning layer.

For a new renderer/layer kind, audit all integration surfaces together: creation, update/draw, input routing, duplication, parameter animation, save/restore, RPC/control handlers, and output capture. A successful standalone shader does not prove those engine-level paths.

## Coordinate and origin traps with local evidence

Only use these as diagnostics when the target code resembles the cited source.

- **Texture coordinate scale trap:** The alpha-mask shader notes that `texCoordVarying.x` maps from 0 to mask texture width and `texCoordVarying.y` maps from 0 to mask texture height, then remaps to the sampled texture size before sampling. Source: `openFrameworks/examples/shader/07_fboAlphaMaskExample/bin/data/shadersGL3/shader.frag`.
- **FBO matrix flip context:** `ofFbo::begin()` defaults to `OF_FBOMODE_PERSPECTIVE | OF_FBOMODE_MATRIXFLIP`; `OF_FBOMODE_MATRIXFLIP` is documented as flipping vertically. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.
- **Explicit FBO texcoord flip in example code:** The alpha-mask setup builds mesh texcoords and, when a generated texcoord path is used, calls `maskFbo.getTexture().getCoordFromPercent(tc.x, (1.0-tc.y))`. Source: `openFrameworks/examples/shader/07_fboAlphaMaskExample/src/ofApp.cpp`.
- **Plane texture coordinate range:** The simple texturing example maps plane texture coordinates from `(0,0)` to `(img.getWidth(), img.getHeight())`, then the shader divides by resolution for `sampler2D`. Sources: `openFrameworks/examples/shader/04_simpleTexturingExample/src/ofApp.cpp`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`.

## Visual debugging and capture

- `ofSaveScreen(fileName)` is documented to save the current screen image to disk and deduce output type from the filename. Source: `openFrameworks/libs/openFrameworks/utils/ofUtils.h`.
- The implementation of `ofSaveScreen()` asks the GL renderer to save the full viewport into `ofPixels`, then calls `ofSaveImage(pixels, fileName)`. Source: `openFrameworks/libs/openFrameworks/utils/ofUtils.cpp`.
- `ofSaveImage()` overloads save `ofPixels`, `ofFloatPixels`, or `ofShortPixels` to a path or buffer. Source: `openFrameworks/libs/openFrameworks/graphics/ofImage.h`.
- The `fboHighResOutputExample` reads an FBO into pixels with `fboOutput.readToPixels(pixels)` and saves those pixels with `ofSaveImage(...)`. Source: `openFrameworks/examples/gl/fboHighResOutputExample/src/ofApp.cpp`.

### Debugging checklist

- Save the current rendered frame with `ofSaveScreen("shader-debug.png")` if the on-screen output itself is wrong. Sources: `openFrameworks/libs/openFrameworks/utils/ofUtils.h`, `openFrameworks/libs/openFrameworks/utils/ofUtils.cpp`.
- For offscreen results, read the relevant FBO/texture path into pixels and use `ofSaveImage()` as shown by the high-res FBO example. Source: `openFrameworks/examples/gl/fboHighResOutputExample/src/ofApp.cpp`.
- When a texture appears black, verify `isAllocated()` checks in C++ before sampling, then verify the sampler type and coordinate scale. Sources: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`, `openFrameworks/examples/shader/07_fboAlphaMaskExample/bin/data/shadersGL3/shader.frag`.
