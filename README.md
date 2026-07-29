# openFrameworks Skills for Codex

Codex skills for building, debugging, reviewing, and maintaining openFrameworks apps/addons. The skills are split by task so an agent can load only the relevant guidance.

## Skills

- `of-openframeworks` — core oF app architecture, `ofApp` lifecycle, source lookup, data paths, threading/live-frame handoff, events, CPU/GPU resources, timing, video, logging, namespaces, multi-window patterns, and general oF good/bad know-how.
- `of-project-generator` — Project Generator CLI discovery, project creation/update, addons, templates, and generated files.
- `of-build-test` — local build/smoke/unit-test workflows for oF projects.
- `of-addon-authoring` — addon layout, `addon_config.mk`, examples, tests, dependencies, and packaging.
- `of-platform-config` — platform sections, generated config files, and platform-specific build settings.
- `of-shader-glsl` — oF OpenGL/GLSL shader, texture, renderer, and asset checks.
- `of-ci` — `2bbb/of-actions`, custom CI, ofxUnitTests, and validation flow for oF addons/apps and oF itself.

## Install

Copy the desired skill directories into your Codex skills directory, or install this repository as a skill source if your Codex setup supports repo-based skill installation.

The mirrored source trees used to build these skills are intentionally not distributed. Skill text cites portable upstream path hints such as `openFrameworks/examples/...`; after installation, verify those against the target local openFrameworks checkout.

## Example prompts

See `examples/prompts/` for prompt snippets covering app architecture, build/test, Project Generator, addon authoring, shaders, and CI.

## Validate

```bash
python3 scripts/validate_repo.py
```

The validation checks skill metadata, local-only path leakage, script syntax/help behavior, and the source-citation guard. CI runs the same command.

## License

MIT. See `LICENSE`.
