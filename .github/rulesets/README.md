# GitHub Rulesets

Reference ruleset for protecting `main` on **AI Job Hunter**.

## What it enforces

| Rule                   | Purpose                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| Pull request required  | No direct pushes to `main` (0 approvals — solo-friendly; set to `1` for teams)                    |
| Required status checks | All jobs from [`.github/workflows/ci.yml`](../workflows/ci.yml) plus CodeQL and Dependency Review |
| No force-push          | `non_fast_forward`                                                                                |
| No branch delete       | `deletion` on `main`                                                                              |
| Conventional commits   | Matches [commitlint](../commitlint.config.cjs) (`feat(scope): message`)                           |

Add `bypass_actors` in GitHub UI if admins need emergency bypass (not included by default).

## Apply via GitHub CLI

Replace `OWNER/REPO` with your repository (e.g. `buhahemal/ai-job-hunting`):

```bash
gh api repos/OWNER/REPO/rulesets \
  --method POST \
  --input .github/rulesets/main-branch-protection.json
```

## Apply via UI

1. **Settings → Rules → Rulesets → New ruleset**
2. Target: **Branch**, include `main`
3. Copy rules from `main-branch-protection.json` (status check names must match your Actions tab exactly)

## Verify check names

After one CI run on a PR, open the PR checks dropdown and confirm contexts match `CI / lint`, `CodeQL / Analyze (python)`, etc. Rename entries in the JSON if GitHub displays different labels.

## Optional tightening

- Set `required_approving_review_count` to `1` for team review
- Add `required_signatures` if you use GPG signing
- Remove `Dependency Review` from required checks if you only want it on PRs from forks (it already runs only on `pull_request`)
