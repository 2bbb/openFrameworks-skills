#!/usr/bin/env bash
set -u

usage() {
  cat <<'USAGE'
Usage: of-build-run.sh --project DIR [--target Debug|Release] [--run] [--xvfb auto|always|never] [--log-dir DIR] [--app-name NAME] [-- OF_ROOT=/path]

Build and optionally run an openFrameworks makefile project while capturing stdout/stderr.

Options:
  --project DIR       Project/test app directory containing Makefile. Required.
  --target TARGET     Make target to build: Debug or Release. Default: Release.
  --run               Run after successful build.
  --xvfb MODE         Linux run wrapper: auto, always, never. Default: auto.
  --log-dir DIR       Log directory. Default: DIR/build-logs.
  --app-name NAME     Override executable/app basename. Default: project directory basename plus _debug for Debug.
  --help              Show this help.

Extra arguments after -- are passed to make, e.g. OF_ROOT=/path/to/openFrameworks.
USAGE
}

project=""
target="Release"
run_after=0
xvfb_mode="auto"
log_dir=""
app_name=""
make_args=()

require_arg() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "$opt requires an argument" >&2
    usage >&2
    exit 64
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) require_arg "$1" "${2:-}"; project="$2"; shift 2 ;;
    --target) require_arg "$1" "${2:-}"; target="$2"; shift 2 ;;
    --run) run_after=1; shift ;;
    --xvfb) require_arg "$1" "${2:-}"; xvfb_mode="$2"; shift 2 ;;
    --log-dir) require_arg "$1" "${2:-}"; log_dir="$2"; shift 2 ;;
    --app-name) require_arg "$1" "${2:-}"; app_name="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    --) shift; make_args=("$@"); break ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 64 ;;
  esac
done

if [[ -z "$project" ]]; then echo "--project is required" >&2; exit 64; fi
if [[ "$target" != "Debug" && "$target" != "Release" ]]; then echo "--target must be Debug or Release" >&2; exit 64; fi
if [[ "$xvfb_mode" != "auto" && "$xvfb_mode" != "always" && "$xvfb_mode" != "never" ]]; then echo "--xvfb must be auto, always, or never" >&2; exit 64; fi
if [[ ! -d "$project" ]]; then echo "Project directory not found: $project" >&2; exit 66; fi
if [[ ! -f "$project/Makefile" ]]; then echo "Makefile not found in: $project" >&2; exit 66; fi

project_abs="$(cd "$project" && pwd -P)"
base="$(basename "$project_abs")"
if [[ -z "$app_name" ]]; then
  if [[ "$target" == "Debug" ]]; then app_name="${base}_debug"; else app_name="$base"; fi
fi
if [[ -z "$log_dir" ]]; then log_dir="$project_abs/build-logs"; fi
mkdir -p "$log_dir"

build_out="$log_dir/build-${target}.stdout.log"
build_err="$log_dir/build-${target}.stderr.log"
run_out="$log_dir/run-${target}.stdout.log"
run_err="$log_dir/run-${target}.stderr.log"

echo "[of-build-run] project=$project_abs target=$target logs=$log_dir"
(
  cd "$project_abs" || exit 66
  if [[ ${#make_args[@]} -gt 0 ]]; then
    make -j "$target" "${make_args[@]}"
  else
    make -j "$target"
  fi
) >"$build_out" 2>"$build_err"
build_status=$?
echo "[of-build-run] build exit=$build_status stdout=$build_out stderr=$build_err"
if [[ $build_status -ne 0 ]]; then exit $build_status; fi

if [[ $run_after -eq 0 ]]; then exit 0; fi

run_cmd=()
uname_s="$(uname -s)"
if [[ "$uname_s" == "Darwin" ]]; then
  if [[ -x "$project_abs/bin/${app_name}.app/Contents/MacOS/${app_name}" ]]; then
    run_cmd=("$project_abs/bin/${app_name}.app/Contents/MacOS/${app_name}")
  else
    if [[ ${#make_args[@]} -gt 0 ]]; then run_cmd=(make "Run${target}" "${make_args[@]}"); else run_cmd=(make "Run${target}"); fi
  fi
elif [[ "$uname_s" == "Linux" ]]; then
  exe="$project_abs/bin/$app_name"
  if [[ ! -x "$exe" && "$target" == "Debug" && -x "$project_abs/bin/${base}_debug" ]]; then exe="$project_abs/bin/${base}_debug"; fi
  if [[ -x "$exe" ]]; then
    if [[ "$xvfb_mode" == "always" ]] || { [[ "$xvfb_mode" == "auto" && -z "${DISPLAY:-}" ]] && command -v xvfb-run >/dev/null 2>&1; }; then
      run_cmd=(xvfb-run "$exe")
    else
      run_cmd=("$exe")
    fi
  else
    if [[ ${#make_args[@]} -gt 0 ]]; then run_cmd=(make "Run${target}" "${make_args[@]}"); else run_cmd=(make "Run${target}"); fi
  fi
else
  if [[ ${#make_args[@]} -gt 0 ]]; then run_cmd=(make "Run${target}" "${make_args[@]}"); else run_cmd=(make "Run${target}"); fi
fi

echo "[of-build-run] run command: ${run_cmd[*]}"
(
  cd "$project_abs" || exit 66
  "${run_cmd[@]}"
) >"$run_out" 2>"$run_err"
run_status=$?
echo "[of-build-run] run exit=$run_status stdout=$run_out stderr=$run_err"
exit $run_status
