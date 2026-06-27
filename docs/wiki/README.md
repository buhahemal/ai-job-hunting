# GitHub Wiki source

Markdown files here sync to the repository wiki:

**https://github.com/buhahemal/ai-job-hunting/wiki**

## Pages

| File                    | Wiki page          |
| ----------------------- | ------------------ |
| `Home.md`               | Home               |
| `Phases.md`             | Phases             |
| `Built-vs-Pending.md`   | Built vs Pending   |
| `Profile-and-Resume.md` | Profile and Resume |
| `_Sidebar.md`           | Sidebar navigation |

## Sync

**Automatic:** push to `main` when these files change — workflow [sync-wiki.yml](../../.github/workflows/sync-wiki.yml).

**Manual:**

```bash
bash scripts/sync_docs_to_wiki.sh
```

**Prerequisite:** Enable Wikis under **Settings → General → Features → Wikis**.

The wiki git repo is synced on branch **`main`** (same as this repository). Legacy wiki
checkouts on `master` are normalized to `main` before push.

Also update [PROJECT-TRACKER.md](../PROJECT-TRACKER.md) in the repo when marking deliverables complete.
