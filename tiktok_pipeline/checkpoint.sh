#!/usr/bin/env bash
set -euo pipefail
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -- tiktok_history/
if ! git diff --cached --quiet; then
  git commit -m 'Registra estado TikTok [skip ci]'
  for attempt in 1 2 3; do
    git fetch origin "$GITHUB_REF_NAME"
    git rebase "origin/$GITHUB_REF_NAME"
    if git push origin "HEAD:$GITHUB_REF_NAME"; then exit 0; fi
  done
  exit 1
fi
