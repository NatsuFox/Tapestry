#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_DIR="$ROOT_DIR/.git/hooks"
PRE_COMMIT_SOURCE="$ROOT_DIR/tools/git-hooks/pre-commit"
PRE_PUSH_SOURCE="$ROOT_DIR/tools/git-hooks/pre-push"
PRE_COMMIT_TARGET="$HOOK_DIR/pre-commit"
PRE_PUSH_TARGET="$HOOK_DIR/pre-push"

if [[ ! -d "$HOOK_DIR" ]]; then
  echo "[install-hooks] .git/hooks not found under $ROOT_DIR" >&2
  exit 1
fi

install -m 0755 "$PRE_COMMIT_SOURCE" "$PRE_COMMIT_TARGET"
install -m 0755 "$PRE_PUSH_SOURCE" "$PRE_PUSH_TARGET"

echo "[install-hooks] Installed pre-commit hook to $PRE_COMMIT_TARGET"
echo "[install-hooks] Installed pre-push hook to $PRE_PUSH_TARGET"
echo "[install-hooks] Every commit and push will now run ./tools/run_local_ci.sh unless TAPESTRY_SKIP_LOCAL_CI=1 is set."
