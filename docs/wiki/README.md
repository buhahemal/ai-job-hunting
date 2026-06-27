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

The wiki repo uses the `master` branch by default. The sync script pushes `HEAD` to the
checked-out branch (never assumes `main`).

Also update [PROJECT-TRACKER.md](../PROJECT-TRACKER.md) in the repo when marking deliverables complete.
