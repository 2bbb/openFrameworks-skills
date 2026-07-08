---
name: of-openframeworks
description: openFrameworks C++ creative-coding development guidance. Use when Codex needs to write, review, debug, build, test, or refactor openFrameworks apps or addons; work with ofApp, addons.make, addon_config.mk, oF examples, OpenGL/GLSL, platform-specific oF code, CI, or Project Generator output.
---

# openFrameworks

Use this skill for openFrameworks (oF) app/addon implementation and debugging. Ground factual guidance in the target openFrameworks checkout source/docs before editing; when a claim is not source-backed, omit it or verify it in the target project first.

## Workflow

1. Locate the oF root before editing or building. In Project Generator source, `isGoodOFPath()` requires `libs/`, `addons/`, and `scripts/`. Source: `projectGenerator/commandLine/src/main.cpp`.
2. Identify whether the target is an app/project or an addon. oF docs describe project placement under `OF_ROOT/apps/myApps`; bundled addons live under `addons/ofx*`. Sources: `openFrameworks/docs/projectgenerator.md`, `openFrameworks/addons/`.
3. Inspect existing `addons.make`, `config.make`, `Makefile`, generated IDE files, and addon `addon_config.mk` before changing build configuration. Sources: `openFrameworks/docs/msys2.md`, `openFrameworks/scripts/templates/*/Makefile`, `openFrameworks/addons/ofx*/addon_config.mk`.
4. Prefer local examples and headers for API shape and lifecycle names such as `setup()`, `update()`, `draw()`, and input callbacks. Sources: `openFrameworks/examples/templates/emptyExample/src/ofApp.*`, `openFrameworks/libs/openFrameworks/ofMain.h`.
5. Verify with the smallest relevant project build/test path available in the target repo. For command-line test apps, oF tests show `ofAppNoWindow` plus `ofxUnitTestsApp`. Sources: `openFrameworks/tests/*/*/src/main.cpp`, `openFrameworks/addons/ofxUnitTests/src/ofxUnitTests.h`.

## Load references as needed

- `references/of-conventions.md` — source-backed API/lifecycle, assets, logging, OpenGL/GLSL checks, and file-splitting caveats.
- `references/build-and-addons.md` — source-backed `addons.make`, `addon_config.mk`, platform sections, Project Generator interactions, build/test basics.
- `references/source-map.md` — where to inspect local oF docs/source/examples/bundled addons before making claims.

## Guardrails

- Do not confuse `addons.make` with `addon_config.mk`. Source: `openFrameworks/docs/msys2.md`, `openFrameworks/addons/ofx*/addon_config.mk`.
- Do not treat oF project `Makefile`s as standalone build systems; template Makefiles include `libs/openFrameworksCompiled/project/makefileCommon/compile.project.mk`. Source: `openFrameworks/scripts/templates/*/Makefile`.
- For `addon_config.mk` exclusion globs, use `%` wildcard as documented in bundled addon configs. Source: `openFrameworks/addons/ofxAssimp/addon_config.mk`.
- Use platform section names only after checking current local templates/source. Source: `openFrameworks/scripts/templates/`, `projectGenerator/commandLine/src/utils/Utils.h`.
- Regenerate generated project files with Project Generator when changing addon lists, platforms, templates, external source folders, or generated project membership. Sources: `openFrameworks/docs/projectgenerator.md`, `projectGenerator/commandLine/readme.md`.

## Maintenance lint

Before distributing updated oF skills, run `python3 skills/of-openframeworks/scripts/check_source_citations.py` from the skill repo root. It fails on non-portable repo-local mirrored-checkout citations and placeholder markers so source hints stay usable after install.

