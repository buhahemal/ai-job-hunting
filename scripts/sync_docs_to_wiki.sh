#!/usr/bin/env bash
# Sync docs/wiki/*.md to the GitHub Wiki repository.
#
# Usage:
#   bash scripts/sync_docs_to_wiki.sh
#   GITHUB_REPO=owner/repo bash scripts/sync_docs_to_wiki.sh
#   GH_TOKEN=... GITHUB_REPO=owner/repo bash scripts/sync_docs_to_wiki.sh  # CI
#
# The main repo and wiki both use the `main` branch (override with WIKI_BRANCH).
# Requires: git, push access to REPO.wiki.git (enable Wiki in repo Settings first).

set -euo pipefail

REPO="${GITHUB_REPO:-buhahemal/ai-job-hunting}"
WIKI_BRANCH="${WIKI_BRANCH:-main}"
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

cd "$WORK_DIR"

# GitHub wikis may clone as legacy `master`; normalize to `main` for this project.
git checkout -B "$WIKI_BRANCH"

cp "$SOURCE_DIR"/*.md "$WORK_DIR/"
git add -A

if git diff --staged --quiet; then
  echo "Wiki already up to date on ${WIKI_BRANCH}."
  exit 0
fi

git -c user.name="${GIT_AUTHOR_NAME:-github-actions[bot]}" \
  -c user.email="${GIT_AUTHOR_EMAIL:-github-actions[bot]@users.noreply.github.com}" \
  commit -m "${WIKI_COMMIT_MESSAGE:-docs: sync project tracker and phase pages from repo}"

echo "Pushing wiki branch: ${WIKI_BRANCH}"
git push origin "$WIKI_BRANCH"

echo "Wiki synced: https://github.com/${REPO}/wiki"
