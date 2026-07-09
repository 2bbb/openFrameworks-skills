# ofShader API and GLSL version/header notes

## Loading and setup

- `ofShader::load(shaderName)` expands a base path to `shaderName.vert` and `shaderName.frag`, then calls the two-file overload. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.
- `ofShader::load(vertName, fragName, geomName)` calls `setupShaderFromFile()` for non-empty vertex/fragment paths, optionally geometry on non-ES targets, calls `bindDefaults()` when using the programmable renderer, then links the program. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.
- `ofShader` also exposes `setupShaderFromFile()`, `setupShaderFromSource()`, `bindDefaults()`, `unload()`, and `isLoaded()`. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.h`.
- The multi-texture example documents three local loading styles: base name lookup for `.frag`/`.vert`, explicit vertex/fragment filenames, and shader source passed as a string. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.


## Default attributes and renderer-provided uniforms

When a shader is loaded through the normal oF programmable-renderer path, oF provides a small fixed contract between `ofMesh`/renderer state and GLSL names. Keep this contract unless the target project intentionally does its own bindings.

### Default attribute names and locations

`ofShader::bindDefaults()` binds these GLSL attribute names before linking:

| GLSL name | `ofShader` enum/location | Typical data | Source |
| --- | --- | --- | --- |
| `position` | `POSITION_ATTRIBUTE = 0` | mesh/polyline vertices, 3 floats | `openFrameworks/libs/openFrameworks/gl/ofShader.h`, `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`, `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp` |
| `color` | `COLOR_ATTRIBUTE = 1` | per-vertex color, 4 floats | same as above |
| `normal` | `NORMAL_ATTRIBUTE = 2` | normal, 3 floats | same as above |
| `texcoord` | `TEXCOORD_ATTRIBUTE = 3` | texture coordinate, 2 floats | same as above |

Renderer source enables/disables these arrays based on available mesh data and uploads vertex/color/normal/texcoord pointers to those locations. Source: `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`.

Practical rule: for normal oF mesh drawing, write vertex shaders with `in vec4 position;`, `in vec2 texcoord;`, `in vec4 color;`, and/or `in vec3 normal;` rather than inventing names like `aPosition` unless you also bind or feed those attributes yourself.

### Matrix and renderer uniforms

The programmable renderer defines and uploads these matrix uniforms when a shader is current:

- `modelMatrix`
- `viewMatrix`
- `modelViewMatrix`
- `projectionMatrix`
- `modelViewProjectionMatrix`
- `textureMatrix`

Sources: uniform-name constants and upload calls in `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`.

The renderer's built-in vertex shader and local examples use:

```glsl
uniform mat4 modelViewProjectionMatrix;
in vec4 position;

void main() {
    gl_Position = modelViewProjectionMatrix * position;
}
```

For texture coordinates, the built-in shader applies the texture matrix before passing varyings:

```glsl
uniform mat4 textureMatrix;
in vec2 texcoord;
out vec2 texCoordVarying;

void main() {
    texCoordVarying = (textureMatrix * vec4(texcoord.x, texcoord.y, 0.0, 1.0)).xy;
}
```

Sources: `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.vert`, `openFrameworks/examples/shader/07_fboAlphaMaskExample/bin/data/shadersGL3/shader.vert`.

Other renderer uniforms visible in source include `globalColor`, `usingTexture`, `usingColors`, and `bitmapText`. Treat these as renderer-internal unless the target shader is deliberately matching oF built-in shader behavior. Source: `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`.

## Coordinate systems: vertices, screen, texcoords, and sampling

Separate these coordinate spaces before debugging shader math:

1. **Vertex/local/world/screen coordinates**: `position` enters the shader in the mesh/object coordinate space produced by oF drawing calls. `modelViewProjectionMatrix * position` converts it to clip space for `gl_Position`. Sources: local shader examples and renderer built-in shader in `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.vert`, `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`.
2. **Fragment coordinates**: `gl_FragCoord.xy` is window/framebuffer pixel space. The multi-texture example divides `gl_FragCoord.xy` by width/height uniforms before sampling `sampler2D`. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
3. **Mesh texture coordinates**: `texcoord` comes from mesh texture coordinates. Examples often pass it to `texCoordVarying`; built-in renderer shaders may transform it by `textureMatrix`. Sources: `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.vert`.
4. **Sampler coordinates**: `sampler2D` expects normalized 0-1-ish coordinates for `GL_TEXTURE_2D`; `sampler2DRect` expects pixel coordinates for rectangle textures in local examples. Source: `references/texture-coordinates.md`.

`ofTexture::getCoordFromPercent(x, y)` converts normalized percentages into texture coordinates; for rectangle textures it returns width/height-scaled coordinates, while non-rectangle paths use texture `tex_t`/`tex_u`. Source: `openFrameworks/libs/openFrameworks/gl/ofTexture.cpp`, `openFrameworks/libs/openFrameworks/gl/ofTexture.h`.

Practical debugging order:

- If geometry is misplaced, inspect `position`, transforms, camera, and `modelViewProjectionMatrix` first.
- If the texture is misplaced on correct geometry, inspect `texcoord`, `textureMatrix`, ARB/rectangle state, and sampler type.
- If screen-space effects drift with window size, inspect `gl_FragCoord` normalization and viewport/FBO dimensions.
- If FBO output is vertically flipped, inspect `ofFbo::begin()` mode and any explicit texcoord flip in target code before adding another flip.

## begin/end and uniforms

- `ofShader` exposes `begin()` and `end()` for binding/unbinding the shader program around drawing. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.h`.
- The simple texturing example binds a texture, calls `shader.begin()`, sets uniforms, draws a plane, calls `shader.end()`, then unbinds the texture. Source: `openFrameworks/examples/shader/04_simpleTexturingExample/src/ofApp.cpp`.
- `ofShader::setUniformTexture()` overloads accept `ofBaseHasTexture`, `ofTexture`, raw texture target/id, or `ofTextureData`. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.h`.
- The implementation activates `GL_TEXTURE0 + textureLocation`, binds the texture target/id, sets the sampler uniform to `textureLocation`, then restores `GL_TEXTURE0`. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.
- Pass distinct texture locations for multiple texture uniforms. The multi-texture example uses locations 1, 2, 3, and 4 for video, image, movie, and mask FBO inputs. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.

## GLSL header/version patterns in local examples

- Local programmable-renderer examples use `OF_GLSL_SHADER_HEADER` in shader source strings or shader files. Comments in the multi-texture example say oF replaces it with the appropriate shader header. Sources: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`, `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`.
- GLSL 150 examples use `in`/`out` variables and `texture(...)`. Sources: `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`, `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders_gl3/posUpdate.frag`.
- GLSL 120 examples use legacy forms such as `varying`, `gl_FragColor`, and `texture2D(...)`/`texture2DRect(...)`. Sources: `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL2/shader.frag`, `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders/posUpdate.frag`.
- The rectangle GLSL 120 particle shader explicitly declares `#version 120` and `#extension GL_ARB_texture_rectangle : enable` before using `sampler2DRect`/`texture2DRect`. Source: `openFrameworks/examples/gl/gpuParticleSystemExample/bin/data/shaders/posUpdate.frag`.

## `modelViewProjectionMatrix` quick evidence

- Local shader examples declare `uniform mat4 modelViewProjectionMatrix` in vertex shaders and multiply it by the vertex `position` to produce `gl_Position`. Sources: `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.vert`, `openFrameworks/examples/shader/02_simpleVertexDisplacementExample/bin/data/shadersGL3/shader.vert`, `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.
- oF's programmable renderer source has a static uniform name `modelViewProjectionMatrix` and its built-in shader strings use that uniform. Source: `openFrameworks/libs/openFrameworks/gl/ofGLProgrammableRenderer.cpp`.
- `ofShader::load()` calls `bindDefaults()` for the programmable renderer before linking. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.

## Minimal source-backed patterns

### Programmable renderer texture shader with normalized `sampler2D`

```glsl
OF_GLSL_SHADER_HEADER
uniform sampler2D tex0;
uniform vec2 resolution;
in vec2 texCoordVarying;
out vec4 outputColor;

void main() {
    outputColor = texture(tex0, texCoordVarying / resolution);
}
```

Backed by: `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.frag`.

### Programmable renderer vertex transform

```glsl
OF_GLSL_SHADER_HEADER
uniform mat4 modelViewProjectionMatrix;
in vec4 position;

void main() {
    gl_Position = modelViewProjectionMatrix * position;
}
```

Backed by: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp` and `openFrameworks/examples/shader/04_simpleTexturingExample/bin/data/shadersGL3/shader.vert`.
