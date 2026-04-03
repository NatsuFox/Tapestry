#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[local-ci] Python interpreter not found: $PYTHON_BIN" >&2
  exit 127
fi

echo "[local-ci] Running GitHub Actions test workflow locally from $ROOT_DIR"
echo "[local-ci] Using interpreter: $($PYTHON_BIN --version 2>&1)"

exec "$PYTHON_BIN" -m pytest tests/ -v --cov=skills/tapestry/_src --cov-report=xml --cov-report=term "$@"
