#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_SOURCE="$ROOT_DIR/tools/git-hooks/pre-commit"
HOOK_TARGET="$ROOT_DIR/.git/hooks/pre-commit"

if [[ ! -d "$ROOT_DIR/.git/hooks" ]]; then
  echo "[install-hooks] .git/hooks not found under $ROOT_DIR" >&2
  exit 1
fi

install -m 0755 "$HOOK_SOURCE" "$HOOK_TARGET"
echo "[install-hooks] Installed pre-commit hook to $HOOK_TARGET"
echo "[install-hooks] Every commit will now run ./tools/run_local_ci.sh unless TAPESTRY_SKIP_LOCAL_CI=1 is set."
