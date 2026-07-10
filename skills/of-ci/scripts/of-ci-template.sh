#!/usr/bin/env bash
set -u

usage() {
  cat <<'USAGE'
Usage: of-ci-template.sh [options]

Emit a conservative GitHub Actions workflow template for openFrameworks CI.
The emitted refs and inputs are grounded in upstream workflow definitions.

Options:
  --mode MODE          addon (default), of-checkout, of-actions-addon,
                       or of-actions-app.
  --test-app DIR       Addon test app directory. Default: testApp.
  --addon-name NAME    Addon directory name. Required by of-actions-addon.
  --app-name NAME      App directory name. Required by of-actions-app.
  --of-version VERSION openFrameworks release tag or nightly. Default: 0.12.1.
  --workflow-ref REF   of-actions tag or commit SHA. Default: v3.
  --configs JSON       Debug/Release JSON array. Default: ["Release"].
  --test-mode MODE     build-only, run, or test. Defaults to test for an
                       of-actions addon and build-only for an of-actions app.
  --help               Show this help.
USAGE
}

mode="addon"
test_app="testApp"
addon_name=""
app_name=""
of_version="0.12.1"
workflow_ref="v3"
configs='["Release"]'
test_mode=""

require_arg() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "$opt requires an argument" >&2
    usage >&2
    exit 64
  fi
}

validate_yaml_scalar() {
  local opt="$1"
  local value="$2"
  local regex="$3"
  if [[ ! "$value" =~ $regex ]]; then
    echo "$opt contains unsupported characters" >&2
    exit 64
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) require_arg "$1" "${2:-}"; mode="$2"; shift 2 ;;
    --test-app) require_arg "$1" "${2:-}"; test_app="$2"; shift 2 ;;
    --addon-name) require_arg "$1" "${2:-}"; addon_name="$2"; shift 2 ;;
    --app-name) require_arg "$1" "${2:-}"; app_name="$2"; shift 2 ;;
    --of-version) require_arg "$1" "${2:-}"; of_version="$2"; shift 2 ;;
    --workflow-ref) require_arg "$1" "${2:-}"; workflow_ref="$2"; shift 2 ;;
    --configs) require_arg "$1" "${2:-}"; configs="$2"; shift 2 ;;
    --test-mode) require_arg "$1" "${2:-}"; test_mode="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 64 ;;
  esac
done

if [[ "$mode" != "addon" && "$mode" != "of-checkout" && "$mode" != "of-actions-addon" && "$mode" != "of-actions-app" ]]; then
  echo "--mode must be addon, of-checkout, of-actions-addon, or of-actions-app" >&2
  exit 64
fi
validate_yaml_scalar "--test-app" "$test_app" '^[[:alnum:]_.\/-]+$'
if [[ -n "$addon_name" ]]; then
  validate_yaml_scalar "--addon-name" "$addon_name" '^[[:alnum:]_.-]+$'
fi
if [[ -n "$app_name" ]]; then
  validate_yaml_scalar "--app-name" "$app_name" '^[[:alnum:]_.-]+$'
fi
validate_yaml_scalar "--of-version" "$of_version" '^[[:alnum:]_.-]+$'
validate_yaml_scalar "--workflow-ref" "$workflow_ref" '^[[:alnum:]_.\/-]+$'
if [[ ! "$configs" =~ ^\[[[:space:]]*\"(Debug|Release)\"([[:space:]]*,[[:space:]]*\"(Debug|Release)\")?[[:space:]]*\]$ ]]; then
  echo '--configs must be a JSON array containing Debug and/or Release' >&2
  exit 64
fi
if [[ -n "$test_mode" && "$test_mode" != "build-only" && "$test_mode" != "run" && "$test_mode" != "test" ]]; then
  echo "--test-mode must be build-only, run, or test" >&2
  exit 64
fi

if [[ "$mode" == "of-actions-addon" ]]; then
  if [[ -z "$addon_name" ]]; then echo "--addon-name is required for of-actions-addon" >&2; exit 64; fi
  if [[ -z "$test_mode" ]]; then test_mode="test"; fi
  cat <<YAML
name: openFrameworks addon CI

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    uses: 2bbb/of-actions/.github/workflows/build-addon.yml@$workflow_ref
    with:
      of_version: "$of_version"
      addon_name: "$addon_name"
      test_app: "$test_app"
      configs: '$configs'
      test_mode: "$test_mode"
YAML
elif [[ "$mode" == "of-actions-app" ]]; then
  if [[ -z "$app_name" ]]; then echo "--app-name is required for of-actions-app" >&2; exit 64; fi
  if [[ -z "$test_mode" ]]; then test_mode="build-only"; fi
  cat <<YAML
name: openFrameworks app CI

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    uses: 2bbb/of-actions/.github/workflows/build-app.yml@$workflow_ref
    with:
      of_version: "$of_version"
      app_name: "$app_name"
      configs: '$configs'
      test_mode: "$test_mode"
YAML
elif [[ "$mode" == "of-checkout" ]]; then
  cat <<'YAML'
name: oF CI
on:
  push:
  pull_request:

jobs:
  linux64:
    runs-on: ubuntu-24.04
    env:
      TARGET: linux64
      RELEASE: latest
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: linux64-64gcc6
      - name: Download libraries
        run: ./scripts/linux/download_libs.sh -t "$RELEASE" -a 64gcc6
      - name: Install dependencies
        run: ./scripts/ci/"$TARGET"/install.sh
      - name: Build and test
        run: |
          scripts/ci/linux64/build.sh
          scripts/ci/linux64/run_tests.sh

  macos:
    runs-on: macos-15
    env:
      RELEASE: latest
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-makefiles
      - name: Download libraries
        run: ./scripts/osx/download_libs.sh -t "$RELEASE"
      - name: Build and test
        run: scripts/ci/osx/run_tests.sh
YAML
else
  cat <<YAML
name: Addon CI
on:
  push:
  pull_request:

# ${addon_name:+Addon: $addon_name}
# This template assumes a prior policy-approved step provides openFrameworks at OF_ROOT.
jobs:
  test-linux:
    runs-on: ubuntu-24.04
    env:
      OF_ROOT: \${{ github.workspace }}/openFrameworks
      TEST_APP: $test_app
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: linux64-addon
      - name: Build test app
        run: make -C "\$TEST_APP" -j2 Debug OF_ROOT="\$OF_ROOT"
      - name: Run test app
        run: |
          app_name="\$(basename "\$TEST_APP")"
          exe="\$TEST_APP/bin/\${app_name}_debug"
          if command -v xvfb-run >/dev/null 2>&1 && [ -z "\${DISPLAY:-}" ]; then
            xvfb-run "\$exe"
          else
            "\$exe"
          fi

  test-macos:
    runs-on: macos-15
    env:
      OF_ROOT: \${{ github.workspace }}/openFrameworks
      TEST_APP: $test_app
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-addon
      - name: Build test app
        run: make -C "\$TEST_APP" -j Debug OF_ROOT="\$OF_ROOT"
      - name: Run test app
        run: make -C "\$TEST_APP" RunDebug OF_ROOT="\$OF_ROOT"
YAML
fi
