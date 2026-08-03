#!/usr/bin/env bash
set -euo pipefail

run_tests=0
if [ "${1:-}" = "--run-tests" ]; then
  run_tests=1
fi

repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$repo" ]; then
  echo "Not inside a Git repository." >&2
  exit 1
fi
cd "$repo"

branch="$(git branch --show-current)"
echo "Repository: $repo"
echo "Branch: $branch"
echo "Remotes:"
git remote -v

git fetch --prune

if [ -n "$(git status --porcelain)" ]; then
  git status --short --branch
  echo "Working tree has local changes. Nothing was pulled." >&2
  exit 1
fi

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
if [ -z "$upstream" ]; then
  echo "Current branch has no upstream. Configure upstream before syncing." >&2
  exit 1
fi

read -r ahead behind < <(git rev-list --left-right --count "HEAD...$upstream")
if [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
  echo "Branch diverged from $upstream. Resolve manually." >&2
  exit 1
fi
if [ "$ahead" -gt 0 ]; then
  echo "Branch has $ahead unpushed commit(s). Push or inspect before pulling." >&2
  exit 1
fi
if [ "$behind" -gt 0 ]; then
  git pull --ff-only
else
  echo "Already up to date."
fi

./scripts/validate-docs.sh

if [ "$run_tests" -eq 1 ]; then
  py="python"
  [ -x ".venv/Scripts/python.exe" ] && py=".venv/Scripts/python.exe"
  [ -x ".venv/bin/python" ] && py=".venv/bin/python"
  "$py" manage.py check
  "$py" manage.py test
fi

echo
echo "--- docs/CURRENT_STATUS.md ---"
sed -n '1,80p' docs/CURRENT_STATUS.md
echo
echo "--- docs/HANDOFF.md ---"
sed -n '1,120p' docs/HANDOFF.md
echo
echo "Sync completed safely."
