---
name: of-project-generator
description: openFrameworks Project Generator CLI guidance and safe automation. Use when Codex needs to create, update, or regenerate openFrameworks app/addon project files; choose PG platform flags or templates; add addons/frameworks/external source folders; locate the Project Generator executable; or avoid destructive recursive updates.
---

# openFrameworks Project Generator

Use this skill to safely run or advise on the openFrameworks Project Generator (PG). Ground commands and claims in local PG/openFrameworks docs/source before running or documenting them.

## Workflow

1. Locate the oF root. Local PG source accepts an oF root with `libs/`, `addons/`, and `scripts/`. Source: `projectGenerator/commandLine/src/main.cpp`.
2. Locate a PG executable with `scripts/locate_project_generator.py` before guessing paths. The locator only reports candidates; it does not execute PG. Source: `skills/of-project-generator/scripts/locate_project_generator.py`.
3. Use explicit `--ofPath`/`/ofPath` or `PG_OF_PATH`; PG docs/source support both and also try local path resolution. Sources: `projectGenerator/commandLine/readme.md`, `projectGenerator/commandLine/src/main.cpp`.
4. Dry-run first for recursive updates or unfamiliar/generated-file changes. PG command-line docs warn that recursive is aggressive and suggest dry-run. Source: `projectGenerator/commandLine/readme.md`.
5. Regenerate only the intended project directory unless the user explicitly requested recursive update. Source: `projectGenerator/commandLine/readme.md`.
6. Review generated diffs before making code changes that depend on them.

## Locate PG

```bash
python3 path/to/skills/of-project-generator/scripts/locate_project_generator.py --of-root /path/to/openFrameworks
```

The script prints candidate executables and marks the preferred existing executable. Use `--json` for machine-readable output. Candidate paths are script-defined and based on local source/release path evidence from `projectGenerator/README.md`, `projectGenerator/frontend/readme.md`, `openFrameworks/scripts/of.sh`, `openFrameworks/scripts/linux/compilePG.sh`, and `openFrameworks/scripts/dev/download_pg.sh`.

## CLI essentials

Unix-like flags:

```bash
projectGenerator --ofPath="/path/to/openFrameworks" "/path/to/openFrameworks/apps/myApps/MyApp"
projectGenerator --ofPath="/path/to/openFrameworks" --addons="ofxGui,ofxOsc" "/path/to/openFrameworks/apps/myApps/MyApp"
projectGenerator --ofPath="/path/to/openFrameworks" --platforms="osx" --template="emptyExample" "/path/to/project"
projectGenerator --ofPath="/path/to/openFrameworks" --dryrun "/path/to/existingProject"
projectGenerator --ofPath="/path/to/openFrameworks" --recursive --dryrun "/path/to/projectsFolder"
```

Windows PG uses slash-style long flags and no abbreviations:

```powershell
& $pg /ofPath="C:\openFrameworks" /addons="ofxGui,ofxOsc" "C:\openFrameworks\apps\myApps\MyApp"
& $pg /ofPath="C:\openFrameworks" /dryrun "C:\openFrameworks\apps\myApps\MyApp"
```

Sources: `projectGenerator/commandLine/readme.md`, `projectGenerator/commandLine/src/main.cpp`.

## Load references as needed

- `references/cli.md` — source-backed CLI options, platform names, examples, and create/update behavior.
- `references/safety.md` — source-backed path rules, dry-run policy, locator behavior, and generated-file review checklist.

## Practical rules

- Existing `pathName` means update; missing `pathName` means create. Source: `projectGenerator/commandLine/readme.md`.
- `--addons` is parsed as a comma-separated list. Source: `projectGenerator/commandLine/src/main.cpp`.
- `--platforms`, `--source`, and `--frameworks` are parsed as comma-separated lists in current PG source. Source: `projectGenerator/commandLine/src/main.cpp`.
- Use `--listtemplates` with `--platforms` to discover templates for the selected/current platform(s). Source: `projectGenerator/commandLine/readme.md`.
- Prefer projects inside the oF tree when possible; oF docs warn that outside/non-standard paths make relative paths more fragile. Source: `openFrameworks/docs/projectgenerator.md`.
