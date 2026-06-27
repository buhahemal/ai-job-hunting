#!/usr/bin/env bash
# Sync docs/wiki/*.md to the GitHub Wiki repository.
#
# Usage:
#   bash scripts/sync_docs_to_wiki.sh
#   GITHUB_REPO=owner/repo bash scripts/sync_docs_to_wiki.sh
#   GH_TOKEN=... GITHUB_REPO=owner/repo bash scripts/sync_docs_to_wiki.sh  # CI
#
# Requires: git, push access to REPO.wiki.git (enable Wiki in repo Settings first).

set -euo pipefail

REPO="${GITHUB_REPO:-buhahemal/ai-job-hunting}"
SOURCE_DIR="$(cd "$(dirname "$0")/../docs/wiki" && pwd)"
WORK_DIR="$(mktemp -d)"

if [ -n "${GH_TOKEN:-}" ]; then
  WIKI_URL="https://x-access-token:${GH_TOKEN}@github.com/${REPO}.wiki.git"
else
  WIKI_URL="https://github.com/${REPO}.wiki.git"
fi

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Missing wiki source directory: $SOURCE_DIR" >&2
  exit 1
fi

echo "Cloning wiki from https://github.com/${REPO}.wiki.git ..."
if ! git clone "$WIKI_URL" "$WORK_DIR"; then
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

git -c user.name="${GIT_AUTHOR_NAME:-github-actions[bot]}" \
  -c user.email="${GIT_AUTHOR_EMAIL:-github-actions[bot]@users.noreply.github.com}" \
  commit -m "${WIKI_COMMIT_MESSAGE:-docs: sync project tracker and phase pages from repo}"

# Wiki repos use master by default; push current HEAD to matching remote branch.
WIKI_BRANCH="$(git symbolic-ref --short HEAD)"
echo "Pushing wiki branch: ${WIKI_BRANCH}"
git push origin "HEAD:refs/heads/${WIKI_BRANCH}"

echo "Wiki synced: https://github.com/${REPO}/wiki"
