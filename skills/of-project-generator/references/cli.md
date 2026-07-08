# Project Generator CLI reference

This page summarizes the local command-line PG docs/source. Verify against the executable's `--help` when available.

## Option forms

Unix-like builds accept short or long hyphen flags. Argument options can use attached values; the command-line readme says lists should be comma-separated and that `:` or `=` may be used for parameter options. Source: `projectGenerator/commandLine/readme.md`.

```bash
projectGenerator [options] pathName
projectGenerator -o"/path/to/of" -a"ofxGui,ofxOsc" pathName
projectGenerator --ofPath="/path/to/of" --addons="ofxGui,ofxOsc" pathName
```

Windows command-line PG uses slash-style long flags and no abbreviations. Source: `projectGenerator/commandLine/readme.md`.

```powershell
projectGenerator.exe /ofPath="C:\openFrameworks" /addons="ofxGui,ofxOsc" pathName
```

## Core options

| Unix | Windows | Purpose | Source |
|---|---|---|---|
| `-h`, `--help` | `/help` | Print help. | `projectGenerator/commandLine/readme.md`, `projectGenerator/commandLine/src/main.cpp` |
| `-o`, `--ofPath` | `/ofPath` | Set openFrameworks root; `PG_OF_PATH` is also supported. | same |
| `-a`, `--addons` | `/addons` | Comma-separated addon list. | same |
| `-p`, `--platforms` | `/platforms` | Comma-separated target platforms. | same |
| `-t`, `--template` | `/template` | Project template name. | same |
| `-l`, `--listtemplates` | `/listtemplates` | List templates for selected/current platform(s). | same |
| `-d`, `--dryrun` | `/dryrun` | Do not change files. | same |
| `-r`, `--recursive` | `/recursive` | Recursively update; applies only to update. | same |
| `-v`, `--verbose` | `/verbose` | Verbose diagnostics. | same |
| `-s`, `--source` | `/source` | External source/include folders. | `projectGenerator/commandLine/src/main.cpp` |
| `-w`, `--version` | `/version` | Print PG version. | same |
| `-g`, `--getofpath` | `/getofpath` | Print resolved oF path. | same |
| `-i`, `--getplatform` | `/getplatform` | Print host platform. | same |
| `-b`, `--backup` | `/backup` | Back up project files when replacing templates. | same |
| `-f`, `--frameworks` | `/frameworks` | Comma-separated frameworks list. | same |

## Platform names

Current PG source lists these platform options: `android`, `ios`, `linux`, `linux64`, `linuxarmv6l`, `linuxarmv7l`, `linuxaarch64`, `msys2`, `osx`, `vs`, `tvos`. Source: `projectGenerator/commandLine/src/utils/Utils.h`.

Templates determine what can actually be generated for a local checkout. Source: `projectGenerator/commandLine/src/projects/baseProject.cpp`.

## Common recipes

Create or update a normal app:

```bash
pg --ofPath="$OF_ROOT" "$OF_ROOT/apps/myApps/MyApp"
```

Create/update with addons:

```bash
pg --ofPath="$OF_ROOT" --addons="ofxGui,ofxOsc" "$OF_ROOT/apps/myApps/MyApp"
```

List templates for macOS:

```bash
pg --ofPath="$OF_ROOT" --platforms="osx" --listtemplates "$OF_ROOT/apps/myApps/TemplateProbe" --dryrun
```

Dry-run recursive update:

```bash
pg --ofPath="$OF_ROOT" --recursive --dryrun "$OF_ROOT/apps/myApps"
```

Sources: `projectGenerator/commandLine/readme.md`, `projectGenerator/commandLine/src/main.cpp`.

## Behavior to remember

- If `pathName` exists, PG updates it; if it does not exist, PG creates it. Source: `projectGenerator/commandLine/readme.md`.
- `PG_OF_PATH` can replace `-o`/`--ofPath`; source also checks it while resolving oF path. Sources: `projectGenerator/commandLine/readme.md`, `projectGenerator/commandLine/src/main.cpp`.
- `--recursive` is update-only and the readme calls it aggressive; dry-run is suggested. Source: `projectGenerator/commandLine/readme.md`.
