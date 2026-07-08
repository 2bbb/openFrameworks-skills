#!/usr/bin/env bash
set -u

usage() {
  cat <<'USAGE'
Usage: of-ci-template.sh [--mode addon|of-checkout] [--test-app DIR] [--addon-name NAME]

Emit a conservative GitHub Actions workflow template for openFrameworks CI.
The emitted action versions are grounded in upstream openFrameworks workflows.

Options:
  --mode MODE        addon (default) or of-checkout.
  --test-app DIR     Test app directory for addon mode. Default: testApp.
  --addon-name NAME  Optional addon name comment for addon mode.
  --help             Show this help.
USAGE
}

mode="addon"
test_app="testApp"
addon_name=""

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
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 64 ;;
  esac
done

if [[ "$mode" != "addon" && "$mode" != "of-checkout" ]]; then echo "--mode must be addon or of-checkout" >&2; exit 64; fi
validate_yaml_scalar "--test-app" "$test_app" '^[[:alnum:]_.\/-]+$'
if [[ -n "$addon_name" ]]; then
  validate_yaml_scalar "--addon-name" "$addon_name" '^[[:alnum:]_.-]+$'
fi

if [[ "$mode" == "of-checkout" ]]; then
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
      - name: Install dependencies
        run: ./scripts/ci/$TARGET/install.sh
      - name: Build and test
        run: |
          scripts/ci/linux64/build.sh
          scripts/ci/linux64/run_tests.sh

  macos:
    runs-on: macos-15
    env:
      DEVELOPER_DIR: /Applications/Xcode.app/Contents/Developer
      SDKROOT: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
    steps:
      - uses: actions/checkout@v6
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1.2.23
        with:
          key: osx-makefiles
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
