---
name: of-platform-config
description: Configure openFrameworks projects and addons for target platforms. Use when Codex needs to edit or review openFrameworks platform setup, Project Generator platform selections/templates, addons.make, addon_config.mk, platform-specific ADDON_* flags, source/library exclusions, bundled libs, DLL/framework/XCFramework handling, local addons, or macOS/Linux/Windows Visual Studio/MSYS2/iOS/Android/Emscripten build configuration.
---

# openFrameworks Platform Config

Use this skill to make verified, platform-aware changes to openFrameworks project and addon configuration. Keep guidance source-backed: if a platform detail is not present in the local openFrameworks/projectGenerator/of-skill references, leave it out or mark it as a project-local assumption.

## Workflow

1. Identify the target surface:
   - Project setup or generation: inspect Project Generator/platform docs and generated project files.
   - Project addon selection: edit `addons.make` only.
   - Addon build metadata: edit the addon's `addon_config.mk`.
   - Bundled binaries/local addons: inspect `libs/`, relative paths, and platform folders before editing.
2. Load details from `references/platform-configuration.md` when changing platform keys, `addon_config.mk`, bundled libs, exclusions, or Project Generator behavior.
3. Prefer the smallest platform-scoped change. Use existing section names and `ADDON_*` keys exactly as verified from projectGenerator source.
4. Validate:
   - Run this skill's `scripts/validate_of_platform_config.py` against changed `addon_config.mk`/`addons.make` files when present.
   - Run the platform's normal generation/build command if available in the repo or user task.

## Core rules

- Use Project Generator platform keys verified from source for generation (`android`, `ios`, `linux`, `linux64`, `linuxarmv6l`, `linuxarmv7l`, `linuxaarch64`, `msys2`, `osx`, `vs`, `tvos`).
- In `addon_config.mk`, use verified parse sections such as `common`, `linux*`, `msys2`, `vs`, Android ABI sections, `emscripten`, `ios`, `osx`, and Apple variants listed in the reference.
- Put addon names or local addon paths in `addons.make`; put include paths, libraries, compiler/linker flags, source overrides, data, and exclusions in `addon_config.mk`.
- Treat `%` in exclusions as the openFrameworks wildcard used by projectGenerator's addon parser.
- For platform-specific libraries, prefer platform/architecture subfolders under `libs/` when the existing addon layout supports it; otherwise use scoped `ADDON_LIBS`, `ADDON_FRAMEWORKS`, `ADDON_XCFRAMEWORKS`, `ADDON_DLLS_TO_COPY`, `ADDON_PKG_CONFIG_LIBRARIES`, and exclusions.
- Local addons are valid when the path in `addons.make` resolves from the project directory; projectGenerator maps their files under `local_addons` in generated projects.

## Reference map

- `references/platform-configuration.md` — verified platform keys, Project Generator behavior, platform setup notes, `addons.make` vs `addon_config.mk`, `ADDON_*` keys, exclusions, bundled libraries, and source citations.
- `scripts/validate_of_platform_config.py` — static checker for known `addon_config.mk` section names/keys and simple `addons.make` path issues.
