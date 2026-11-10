---
name: github
description: "GitHub via gh CLI: PRs with Hermes session identity, issues, reviews, repos, auth."
author: Ben Barclay (benbarclay), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  version: "2.0.1"
  hermes:
    tags: [github, gh, git, pull-requests, issues, code-review, repos, auth, ci]
    category: software-development
    related_skills: [codebase-inspection, requesting-code-review]
---

# GitHub

Work GitHub end to end with the `gh` CLI (REST fallback where noted): auth,
issues, the PR lifecycle, issue-to-PR delivery, code review, and repo
management. This skill consolidates six former skills; each workflow lives
complete in its reference file — ALWAYS read the matching reference before
starting that workflow. The body below routes and defines shared requirements.

## Routing

| Task | Read first |
|---|---|
| Auth broken / new machine / token or SSH setup / gh login | `references/auth.md` |
| Create, triage, label, assign, close issues | `references/issues.md` |
| Branch, commit, open PR, watch CI, merge | `references/pr-workflow.md` |
| Carry an ISSUE to a verified PR (full delivery loop) | `references/issue-to-pr.md` |
| Review someone's PR: diffs, inline comments, verdict | `references/code-review.md` |
| Clone/create/fork repos, remotes, releases | `references/repo-management.md` |

Supporting assets: `scripts/gh-env.sh` + `scripts/git-credential-token.py`
(auth helpers), `templates/` (PR bodies, bug report, feature request),
`references/ci-troubleshooting.md`, `references/conventional-commits.md`,
`references/github-api-cheatsheet.md`, `references/review-output-template.md`.

## Core discipline (applies to every workflow)

- Preflight once per session: `gh auth status` — if it fails, go to
  `references/auth.md` before anything else.
- Prefer `gh` over raw REST; drop to `gh api` only for endpoints the
  porcelain lacks (the cheatsheet lists them).
- Never report CI green without checking `gh pr checks` yourself; never
  claim merged without verifying `state,mergedAt`.
- Read full context before writing: `gh issue view --comments` /
  `gh pr view --comments` — decisions live in threads, not titles.
- Sweep for duplicates before creating anything:
  `gh pr list --search` / `gh issue list --search`.

## PR submitter identity

Whenever you create a PR from Hermes, include your current profile and durable
session ID in its body so review feedback can return to the originating session.
This applies to both `gh` and REST creation, including issue-to-PR workflows.

1. Immediately before preparing the PR body, use `terminal` to run
   `printenv HERMES_SESSION_PROFILE HERMES_SESSION_ID`. The two output lines
   are the current profile and session ID, in that order. Read only these fields.
2. Append the following two lines to the body, replacing the placeholders with
   those actual values yourself:

   ```text
   Hermes profile: <current profile>
   Hermes session_id: <current durable session ID>
   ```

3. Resolve missing or conflicting values before creating the PR. Never invent
   an ID, use the latest session, substitute a UI session ID, or infer the author
   from the profile holding GitHub credentials. Include the identity only once.
4. After creating the PR, read back its body and verify that both values match
   this session before reporting completion. When editing an existing PR, retain
   its original submitter identity unless the operator explicitly transfers it.

## Verification

- The workflow's own reference file defines done for that task.
- Cross-cutting: every claim about remote state (CI, merge, release,
  issue state) is backed by a fresh `gh` read, never memory.
