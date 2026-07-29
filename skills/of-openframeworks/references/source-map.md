# Source map for authoritative oF lookup

When local source is available, prefer it over memory. Add source-path citations to deliverables when stating facts.

## openFrameworks tree

- `openFrameworks/docs/` — platform/setup docs, including `projectgenerator.md`, `linux.md`, `osx.md`, `visualstudio.md`, `msys2.md`, and `PLATFORMS.md`.
- `openFrameworks/examples/` — source-backed usage patterns by topic. Start near the target feature.
- `openFrameworks/addons/` — bundled addon implementations and `addon_config.mk` examples.
- `openFrameworks/libs/openFrameworks/` — core oF headers and source.
- `openFrameworks/libs/openFrameworksCompiled/project/` — compiled-library/project support where present.
- `openFrameworks/scripts/templates/` — generated project templates and platform Makefile/config shapes.
- `openFrameworks/tests/` — local test app patterns, including `ofAppNoWindow` and `ofxUnitTests` usage.

## Runtime/resource lookup

- `openFrameworks/examples/threads/` and `openFrameworks/libs/openFrameworks/utils/ofThread*.h` — worker lifecycle, channels, and CPU/main-thread graphics handoff.
- `openFrameworks/libs/openFrameworks/events/` — event order, listener tokens, legacy add/remove helpers, and frame timing counters.
- `openFrameworks/libs/openFrameworks/utils/ofFileUtils.*` — data-root and path resolution behavior.
- `openFrameworks/libs/openFrameworks/graphics/`, `openFrameworks/libs/openFrameworks/gl/`, and `openFrameworks/libs/openFrameworks/video/` — CPU/GPU resources, render state, FBO behavior, and media update lifecycle.

## Lookup strategy

1. Search examples/tests for the exact class, callback, or project shape.
2. Search bundled addons for `addon_config.mk` and dependency patterns.
3. Search core headers/source for API signatures and lifecycle requirements.
4. Search Project Generator docs/source before claiming generated-file behavior.
5. If the claim is still unsupported, omit it from final skill text or phrase it as an instruction to inspect local project evidence.
