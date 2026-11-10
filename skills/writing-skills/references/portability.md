# Client paths and vendor extensions

Checked 2026-11-10 against vendor docs; Cursor is UNVERIFIED. These change
often; re-check before relying on them.

| Client | Project path | Personal path |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| OpenAI Codex | `.agents/skills/` (cwd up to repo root) | `~/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` |
| GitHub Copilot | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| Cursor (UNVERIFIED) | `.agents/skills/`, `.cursor/skills/` | unconfirmed |

`.agents/skills/` is the most widely shared project path.

Vendor extensions (other clients ignore or reject them):
- Claude Code frontmatter: `when_to_use`, `disable-model-invocation`
  (manual-only), `user-invocable`, `context: fork`, `agent`, `paths`, `model`,
  `effort`, `hooks`, `argument-hint`, `arguments`, `disallowed-tools`. Unknown
  keys are ignored silently, so a typo disables a feature without warning.
  Uploads to claude.ai accept only spec fields. Description plus
  `when_to_use` is truncated at 1,536 chars in the listing.
- Codex: optional side file `agents/openai.yaml` for UI metadata,
  `policy.allow_implicit_invocation` (manual-only), and tool dependencies.
  The skill list gets ~2% of context; descriptions are shortened first.
- Gemini CLI: activation via `activate_skill` with a user consent prompt.
- Body syntax such as `$ARGUMENTS` or `${CLAUDE_SKILL_DIR}` is Claude
  Code-only; use relative paths in shared skills.

Sources: https://code.claude.com/docs/en/skills,
https://developers.openai.com/codex/skills,
https://geminicli.com/docs/cli/skills/,
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
