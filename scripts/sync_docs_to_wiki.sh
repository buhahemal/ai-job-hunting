#!/usr/bin/env bash
# Sync docs/wiki/*.md to the GitHub Wiki repository.
#
# Usage:
#   bash scripts/sync_docs_to_wiki.sh
#   GITHUB_REPO=owner/repo bash scripts/sync_docs_to_wiki.sh
#
# Requires: git, push access to REPO.wiki.git (enable Wiki in repo Settings first).

set -euo pipefail

REPO="${GITHUB_REPO:-buhahemal/ai-job-hunting}"
WIKI_URL="https://github.com/${REPO}.wiki.git"
SOURCE_DIR="$(cd "$(dirname "$0")/../docs/wiki" && pwd)"
WORK_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Missing wiki source directory: $SOURCE_DIR" >&2
  exit 1
fi

echo "Cloning wiki from $WIKI_URL ..."
if ! git clone "$WIKI_URL" "$WORK_DIR" 2>/dev/null; then
  echo ""
  echo "Could not clone wiki. Enable GitHub Wiki in repository Settings, then retry." >&2
  echo "  Settings → General → Features → Wikis" >&2
  exit 1
fi

cp "$SOURCE_DIR"/*.md "$WORK_DIR/"

cd "$WORK_DIR"
git add -A

if git diff --staged --quiet; then
  echo "Wiki already up to date."
  exit 0
fi

git -c user.name="github-actions[bot]" -c user.email="github-actions[bot]@users.noreply.github.com" \
  commit -m "docs: sync project tracker and phase pages from repo"

git push origin master 2>/dev/null || git push origin main

echo "Wiki synced: https://github.com/${REPO}/wiki"
