# ofShader API and GLSL version/header notes

## Loading and setup

- `ofShader::load(shaderName)` expands a base path to `shaderName.vert` and `shaderName.frag`, then calls the two-file overload. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.
- `ofShader::load(vertName, fragName, geomName)` calls `setupShaderFromFile()` for non-empty vertex/fragment paths, optionally geometry on non-ES targets, calls `bindDefaults()` when using the programmable renderer, then links the program. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.cpp`.
- `ofShader` also exposes `setupShaderFromFile()`, `setupShaderFromSource()`, `bindDefaults()`, `unload()`, and `isLoaded()`. Source: `openFrameworks/libs/openFrameworks/gl/ofShader.h`.
- The multi-texture example documents three local loading styles: base name lookup for `.frag`/`.vert`, explicit vertex/fragment filenames, and shader source passed as a string. Source: `openFrameworks/examples/gl/multiTextureShaderExample/src/ofApp.cpp`.

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

## modelViewProjectionMatrix

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
