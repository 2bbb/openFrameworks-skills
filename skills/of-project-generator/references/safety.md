# Project Generator safety guide

## Path safety

- Prefer projects inside the same oF distribution, commonly under `OF_ROOT/apps/myApps`, because oF docs warn that non-standard/outside paths make relative paths more fragile. Source: `openFrameworks/docs/projectgenerator.md`.
- Validate an oF root by checking for `libs/`, `addons/`, and `scripts/`, matching local PG `isGoodOFPath()`. Source: `projectGenerator/commandLine/src/main.cpp`.
- Quote paths in commands; local docs show quoted option values for paths/addon lists. Source: `projectGenerator/commandLine/readme.md`.

## Before running PG

1. Locate the executable with `scripts/locate_project_generator.py`; the script reports candidates and does not execute them. Source: `skills/of-project-generator/scripts/locate_project_generator.py`.
2. Run `--help`, `--version`, `--getplatform`, or `--getofpath` when executable compatibility/path resolution matters. Source: `projectGenerator/commandLine/src/main.cpp`.
3. For an existing project, inspect `addons.make`, `config.make`, `Makefile`, and current generated IDE files. Sources: `openFrameworks/docs/msys2.md`, `openFrameworks/scripts/templates/`.
4. Run `--dryrun` for recursive updates or unfamiliar generated-file changes; PG docs warn about recursive updates and suggest dry-run. Source: `projectGenerator/commandLine/readme.md`.
5. Consider `--backup` when replacing generated project files; current source supports the flag. Source: `projectGenerator/commandLine/src/main.cpp`.

## After running PG

Review changed generated files before editing code that depends on them:

- `addons.make`, `config.make`, `Makefile`; sources: `openFrameworks/docs/msys2.md`, `openFrameworks/scripts/templates/*/Makefile`.
- IDE/project files such as Xcode, Visual Studio, Code::Blocks, Qbs, or platform templates present in the local checkout; source: `openFrameworks/scripts/templates/`, `projectGenerator/commandLine/src/projects/`.
- Addon parsing results for includes, libs, sources, frameworks, and exclusions; source: `openFrameworks/addons/ofx*/addon_config.mk`, `projectGenerator/commandLine/src/addons/ofAddon.cpp`.

## Locator behavior

`locate_project_generator.py` is intentionally generic. Its behavior is script-defined:

- It accepts `--of-root`, repeated `--search-root`, `--json`, and `--first`.
- It rejects `--of-root` unless it contains `libs/`, `addons/`, and `scripts/`.
- It searches candidate names by host platform (`projectGenerator`, `commandLine`, and `.exe` variants as applicable), `PG_OF_PATH`, extra roots, and existing executables on `PATH`.
- It prints a preferred executable candidate if one exists; otherwise it returns non-zero for `--first`/`--json` and normal output.

Source: `skills/of-project-generator/scripts/locate_project_generator.py`.

Path variants in the script are supported by local evidence that PG can live in source `apps/projectGenerator/commandLine/bin`, packaged `projectGenerator/` folders, Electron app resources, and installed `PATH` locations. Sources: `projectGenerator/README.md`, `projectGenerator/frontend/readme.md`, `openFrameworks/scripts/of.sh`, `openFrameworks/scripts/linux/compilePG.sh`, `openFrameworks/scripts/dev/download_pg.sh`.

## Avoid

- Do not recursively update an entire oF checkout unless explicitly requested. Source: `projectGenerator/commandLine/readme.md`.
- Do not hand-edit generated IDE files before checking whether the real issue is addon/source/template input that PG should regenerate. Source: `openFrameworks/docs/projectgenerator.md`, `projectGenerator/commandLine/readme.md`.
