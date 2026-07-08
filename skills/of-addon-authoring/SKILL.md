---
name: of-addon-authoring
description: Author, repair, review, or package openFrameworks addons. Use when Codex is working on ofx addon layout, addon_config.mk, project/example addons.make files, bundled libs, platform-specific source exclusions, Objective-C++ .mm boundaries, local addons, or testApp/example build setup.
---

# openFrameworks Addon Authoring

Use this skill to create or fix an openFrameworks addon that projectGenerator and the oF makefile templates can consume.

## Workflow

1. Identify the addon root and the oF project roots that use it (`testApp/`, `example-*`, or app folders).
2. Read [references/addon-layout.md](references/addon-layout.md) before changing structure, example projects, local addon paths, or bundled libraries.
3. Read [references/addon-config.md](references/addon-config.md) before editing `addon_config.mk` or platform-specific build behavior.
4. Read [references/platform-code.md](references/platform-code.md) before adding platform folders, source exclusions, `.mm` files, ObjC++ APIs, or PIMPL boundaries.
5. Run `python3 <skill>/scripts/validate_of_addon.py <addon-root>` after edits when an addon directory is available; then run the projectGenerator/build/test command appropriate to the repo.

## Rules

- Keep `addons.make` and `addon_config.mk` separate: project directories declare which addons to use; addon roots declare how the addon builds.
- Prefer conventional addon layout: public C++ API in `src/`, third-party code under `libs/`, and a buildable `testApp/` plus focused examples.
- Treat `addon_config.mk` as projectGenerator data, not normal Make syntax. Use only source-verified section names and `ADDON_*` keys.
- Use `%`, not `*`, for `ADDON_SOURCES_EXCLUDE`, `ADDON_INCLUDES_EXCLUDE`, `ADDON_LIBS_EXCLUDE`, and framework exclusion globs.
- Exclude every platform-incompatible source tree on every other platform; oF discovers source files recursively from `src/` and `libs/`.
- Keep headers pure C++. Put Objective-C++ in `.mm` and hide ObjC/Apple framework types behind PIMPL or private `.mm` implementation classes.
- Put `addons.make` in every buildable app directory and include the addon under test there.

## Validation

Use the bundled checker for fast static feedback:

```bash
python3 skills/of-addon-authoring/scripts/validate_of_addon.py path/to/ofxAddon
```

It does not replace projectGenerator or compiler validation; it catches common addon-authoring mistakes before those slower checks.
