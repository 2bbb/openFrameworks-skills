# oF shader texture coordinates and texture targets

This reference is limited to facts visible in the local openFrameworks checkout.

## Global ARB texture state

- `ofGetUsingArbTex()` reports whether oF is using `GL_TEXTURE_RECTANGLE` rather than `GL_TEXTURE_2D`. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- `ofEnableArbTex()` selects `GL_TEXTURE_RECTANGLE` textures. The local header says rectangle textures are enabled by default, allow pixel-based coordinates, are unavailable in OpenGL ES, and do not support mipmaps. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- `ofDisableArbTex()` selects `GL_TEXTURE_2D`. The local header says `GL_TEXTURE_2D` uses normalized coordinates between 0 and 1 along width and height and supports a wider range of core OpenGL features such as mipmaps. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- The implementation is a global boolean switch: `ofEnableArbTex()` sets it true; `ofDisableArbTex()` sets it false. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.cpp`.

## Allocation/loading implications

- `ofTexture::allocate(int w, int h, int glInternalFormat)` applies the currently set OF texture type and defaults to ARB rectangular textures if supported; OpenGL ES is the documented exception. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- `ofTexture` overloads can explicitly override the current default by passing a boolean `bUseARBExtension`, described as enabling rectangular textures for that texture. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- Mipmap generation is not supported by the default `GL_TEXTURE_RECTANGLE` target; the local header says to call `ofDisableArbTex()` before loading texture data for a texture that will generate mipmaps. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.
- `ofFboSettings::textureTarget` is documented as `GL_TEXTURE_2D` or `GL_TEXTURE_RECTANGLE_ARB`, so an FBO can carry either target depending on settings/defaults. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.

## Matching sampler and coordinate range

Use the sampler and coordinate math that match the actual texture target:

| Texture target/context | Shader sampler seen locally | Coordinate range shown locally | Local evidence |
| --- | --- | --- | --- |
| `GL_TEXTURE_2D` after `ofDisableArbTex()` | `sampler2D` | normalized before sampling | `openFrameworks/examples/shader/04_simpleTexturingExample/src/ofApp.cpp`; `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`; `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp` |
| rectangle texture / ARB default | `sampler2DRect` | pixel coordinates | `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders/posUpdate.frag`; `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders_gl3/posUpdate.frag`; `openFrameworks/libs/openFrameworks/gl/ofTexture.h` |

### GL_TEXTURE_2D example pattern

The simple texturing example calls `ofDisableArbTex()` in setup, loads `shadersGL3/shader` or `shadersGL2/shader`, maps plane texcoords to image width/height, and divides `texCoordVarying` by `resolution` before sampling `uniform sampler2D tex0`. Sources: `openFrameworks/examples/shader/04_simpleTexturingExample/src/ofApp.cpp`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL2/shader.frag`.

The multi-texture example calls `ofDisableArbTex()`, uses `sampler2D` uniforms, passes width/height uniforms, and divides `gl_FragCoord.xy` by those scales before sampling. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.

### Rectangle texture example pattern

The GPU particle shaders use rectangle samplers for FBO-like data textures. The GLSL 120 version enables `GL_ARB_texture_rectangle`, declares `sampler2DRect`, and samples with `texture2DRect(prevPosData, st)` where `st` comes from `gl_TexCoord[0].st`. The GLSL 150 version declares `sampler2DRect` and samples with `texture(prevPosData, vTexCoord)`. Sources: `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders/posUpdate.frag`, `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders_gl3/posUpdate.frag`.

## Practical fixes

- For normalized UV shader code, call `ofDisableArbTex()` before loading/allocating the textures that shader will sample, then use `sampler2D` and normalized coordinates. Source examples: `openFrameworks/examples/shader/04_simpleTexturingExample/src/ofApp.cpp`, `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
- For default oF rectangle textures, use `sampler2DRect` and pixel coordinates. Source examples: `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders/posUpdate.frag`, `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders_gl3/posUpdate.frag`.
- For FBOs, inspect `ofFboSettings::textureTarget` or the allocation path before choosing the sampler. Source: `openFrameworks/libs/openFrameworks/gl/ofFbo.h`.
