#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PRIMARY_PYTHON="${PYTHON_BIN:-python3}"
MATRIX_SPEC="${TAPESTRY_PYTHON_MATRIX:-python3.10 python3.11 python3.12}"
ALLOW_PARTIAL_MATRIX="${TAPESTRY_ALLOW_PARTIAL_MATRIX:-1}"

if ! command -v "$PRIMARY_PYTHON" >/dev/null 2>&1; then
  echo "[local-ci] Python interpreter not found: $PRIMARY_PYTHON" >&2
  exit 127
fi

read -r -a requested_matrix <<<"$MATRIX_SPEC"
available_matrix=()
missing_matrix=()
for python_bin in "${requested_matrix[@]}"; do
  if command -v "$python_bin" >/dev/null 2>&1; then
    available_matrix+=("$python_bin")
  else
    missing_matrix+=("$python_bin")
  fi
done

if [[ ${#available_matrix[@]} -eq 0 ]]; then
  available_matrix=("$PRIMARY_PYTHON")
fi

if [[ ${#missing_matrix[@]} -gt 0 ]]; then
  echo "[local-ci] Missing workflow matrix interpreters: ${missing_matrix[*]}" >&2
  if [[ "$ALLOW_PARTIAL_MATRIX" != "1" ]]; then
    echo "[local-ci] Refusing partial workflow run because TAPESTRY_ALLOW_PARTIAL_MATRIX=$ALLOW_PARTIAL_MATRIX" >&2
    exit 1
  fi
  echo "[local-ci] Continuing with available interpreters: ${available_matrix[*]}" >&2
fi

RELEASE_TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tapestry-local-ci.XXXXXX")"
cleanup() {
  rm -rf "$RELEASE_TMP_DIR"
}
trap cleanup EXIT

PYTEST_ARGS=("$@")

run_step() {
  local label="$1"
  shift
  echo "[local-ci] ${label}"
  "$@"
}

echo "[local-ci] Running local workflow parity checks from $ROOT_DIR"
echo "[local-ci] Primary interpreter: $($PRIMARY_PYTHON --version 2>&1)"
echo "[local-ci] Test matrix requested: ${requested_matrix[*]}"
echo "[local-ci] Test matrix available: ${available_matrix[*]}"

echo "[local-ci] Mirroring lint.yml"
run_step "Black format check" "$PRIMARY_PYTHON" -m black --check skills/tapestry/_src/ tests/
run_step "Ruff lint check" "$PRIMARY_PYTHON" -m ruff check skills/tapestry/_src/ tests/
if ! "$PRIMARY_PYTHON" -m mypy skills/tapestry/_src/ --ignore-missing-imports; then
  echo "[local-ci] mypy reported issues, but lint.yml keeps this step non-blocking (continue-on-error)." >&2
fi

echo "[local-ci] Mirroring deploy-portal-pages.yml validation step"
run_step "Portal SEO validation" "$PRIMARY_PYTHON" tools/check_portal_seo.py

echo "[local-ci] Mirroring release-skill-bundle.yml build step"
run_step "Release bundle build verification" "$PRIMARY_PYTHON" .github/build_release_bundle.py --output-dir "$RELEASE_TMP_DIR/releases"

echo "[local-ci] Mirroring tests.yml"
for python_bin in "${available_matrix[@]}"; do
  echo "[local-ci] Running tests with $($python_bin --version 2>&1)"
  "$python_bin" -m pytest tests/ -v --cov=skills/tapestry/_src --cov-report=xml --cov-report=term "${PYTEST_ARGS[@]}"
done

echo "[local-ci] Local workflow parity checks completed successfully"
