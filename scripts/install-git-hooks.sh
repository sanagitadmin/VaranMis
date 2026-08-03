#!/usr/bin/env bash
set -euo pipefail

repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$repo" ]; then
  echo "Not inside a Git repository." >&2
  exit 1
fi
cd "$repo"
git config core.hooksPath .githooks
echo "Git hooks installed: core.hooksPath=.githooks"
