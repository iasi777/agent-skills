# Hermes installation and execution

Integration guidance dated 2026-11-10. This package uses portable frontmatter and
Python 3, with no Hermes-specific metadata extensions.

Require an explicitly named Hermes profile. Resolve that profile's actual home
on the host/container running Hermes, then copy this entire skill directory to
`<profile-home>/skills/cf-temp-mail-agent-mail/`. Inspect same-name copies before
updating; preserve unrelated files. Check project skill directories for shadowing.
Do not assume the author's local `~/.hermes` is the runtime profile.

Configure credential files in the Hermes runtime, outside the skill directory,
with directory mode 0700 and file mode 0600. The client discovers
`$HERMES_HOME/cf-temp-mail/credentials.json` before the personal default;
`--credentials` overrides both. A local authoring-machine credential
path does not imply remote access. Use the intended deployment's API base.

Verify Python 3, run the client's `--help`, check skill discovery in the installed
Hermes version, and validate `/api/settings` or `/open_api/settings`. Report the
source, named profile, resolved destination, conflicts, and validation performed.
Claim a Hermes run only after an actual invocation succeeds.

For scheduled checks, use the installed Hermes scheduling interface only when
requested. Supply the skill name, selected credential file, filters, deadline,
state directory, schedule, timezone and delivery destination explicitly. Persist
processed mail IDs outside the package. A fresh job session must not depend on
prior conversation history. Distinguish successful reading from notification
delivery, and check delivery records before retrying a notification.
