---
name: of-shader-glsl
description: Source-backed openFrameworks GLSL shader guidance for writing, porting, and debugging oF shaders, especially texture coordinate/ARB rectangle texture issues, ofShader loading and uniforms, ofTexture/ofFbo shader inputs, GLSL header/version choices, multi-texture shaders, and screenshot/image debugging. Use when working on .vert/.frag/.glsl shader files or C++ code that binds textures, FBOs, or uniforms to ofShader.
---

# oF Shader GLSL

Use this skill when implementing or debugging openFrameworks shader code or the C++ that drives it. The common failure mode this skill prevents is mixing oF's default ARB rectangle textures (pixel coordinates) with `GL_TEXTURE_2D` shader code (normalized 0-1 UVs).

## Workflow

1. **Identify the texture target before changing shader sampling.** Check whether the app calls `ofDisableArbTex()`/`ofEnableArbTex()`, whether a texture/FBO is explicitly allocated with a target/settings, and whether the shader declares `sampler2DRect` or `sampler2D`. See `references/texture-coordinates.md`.
2. **Match GLSL syntax to renderer and shader header.** In oF examples, programmable-renderer shaders use `OF_GLSL_SHADER_HEADER`, default attributes (`position`, `color`, `normal`, `texcoord`), `in`/`out`, `texture(...)`, and default matrix uniforms such as `modelViewProjectionMatrix`; older GLSL examples use `#version 120`, `varying`, `gl_FragColor`, and `texture2DRect(...)`/`texture2D(...)` as appropriate. See `references/shader-api.md`.
3. **Use oF default shader plumbing deliberately.** Let `ofShader::load()` bind default attribute names before linking unless you intentionally use a custom binding path; in vertex shaders, use `position` and `texcoord` unless target code has custom mesh attributes. Then bind textures through `ofShader` deliberately. Use `shader.begin()`/`shader.end()`, then `setUniformTexture(name, texture, textureLocation)` with distinct texture units. For image/video/FBO-backed inputs, pass `getTexture()` where needed and verify `isAllocated()` before sampling. See `references/shader-api.md` and `references/multitexture-fbo-debug.md`.
4. **For FBOs, treat `getTexture()` as the shader input.** Allocate the FBO, draw into it inside `fbo.begin()`/`fbo.end()`, then pass `fbo.getTexture()` to the shader. See `references/multitexture-fbo-debug.md`.
5. **Debug visually with source-backed capture APIs when helpful.** Use `ofSaveScreen()` for the current full screen, or read pixels from an FBO/texture workflow and save with `ofSaveImage()` when you need an artifact. See `references/multitexture-fbo-debug.md`.

## Quick decisions

- If the project uses `ofDisableArbTex()` before loading/allocating textures, expect `GL_TEXTURE_2D`, normalized texture coordinates in the shader, `sampler2D`, and modern GLSL `texture(...)` or legacy `texture2D(...)` depending on the shader version.
- If the project uses oF defaults or `ofEnableArbTex()` on desktop GL, expect `GL_TEXTURE_RECTANGLE`, pixel texture coordinates, and rectangle sampler forms (`sampler2DRect`; `texture(...)` in GLSL 150 examples, `texture2DRect(...)` in GLSL 120 examples).
- If coordinates look scaled, stretched, tiled incorrectly, upside-down, or black, first verify mesh/local coordinates + matrix uniforms + texture target + sampler type + coordinate range before changing math.
- If a shader compiles in one example but not another, compare `OF_GLSL_SHADER_HEADER`, `#version`, `in`/`out` vs `varying`, and `texture(...)` vs legacy sampling functions.

## Load references as needed

- `references/texture-coordinates.md` — ARB rectangle vs `GL_TEXTURE_2D`, `ofEnableArbTex()`/`ofDisableArbTex()`, coordinate ranges, sampler choices, and texture/FBO target implications.
- `references/shader-api.md` — `ofShader` loading/setup, default attributes/uniforms, `begin()`/`end()`, `setUniformTexture()`, GLSL header/version conventions, and coordinate-system evidence.
- `references/multitexture-fbo-debug.md` — multi-texture examples, FBO-as-texture workflow, coordinate/origin traps that are locally sourced, and `ofSaveScreen()`/`ofSaveImage()` debugging.

## Guardrails

- Do not assert shader behavior from memory. Cite the local oF source/example path that backs the claim.
- Do not change global ARB texture state casually in the middle of an app; inspect where textures are loaded/allocated because oF applies the current texture type during allocation/loading.
- Do not mix sampler types and coordinate spaces. `sampler2DRect`/rectangle textures use pixel coordinates in the local examples and docs; `sampler2D`/`GL_TEXTURE_2D` examples normalize coordinates.
- Do not claim an origin flip rule unless the target code or local source shows it. The local FBO API documents `OF_FBOMODE_MATRIXFLIP`, and the alpha-mask example explicitly flips one generated texcoord path before using an FBO texture.
- Do not rename built-in attributes/uniforms casually. With default binding, oF examples and renderer source expect names such as `position`, `texcoord`, `color`, `normal`, `modelViewProjectionMatrix`, and `textureMatrix`.
