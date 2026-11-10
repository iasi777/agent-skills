# Agent Skills

[中文](README.md)

Individually installable agent skills, primarily for Hermes workflows. Each package includes its own instructions, scripts and references.

| Skill | Version | Purpose |
| --- | --- | --- |
| [writing-skills](skills/writing-skills/SKILL.md) | 0.7.0 | Author and maintain Hermes skills; locate explicit runtime/profile targets and check installation conflicts |
| [cf-temp-mail-agent-mail](skills/cf-temp-mail-agent-mail/SKILL.md) | 1.0.0 | Create mailboxes, read messages, extract codes and manage mail through cloudflare_temp_email; sending and other features depend on server configuration |
| [github](skills/github/SKILL.md) | 2.0.1 | Local backup of the GitHub component, including PR session identity instructions and excluding gpt's custom deployed-issue tracking rules |

`github` is distributed with this collection. Install or restore the complete directory; see [NOTICE.md](NOTICE.md) for provenance and licensing.

## Install into Hermes

Replace `<profile>` with an explicitly selected existing profile; use `default` when that is your intended profile.
Run inside the host or container where Hermes operates. Install either package:

```sh
hermes -p <profile> skills install iasi777/agent-skills/skills/writing-skills
hermes -p <profile> skills install iasi777/agent-skills/skills/cf-temp-mail-agent-mail
```

Optionally register the collection for future discovery:

```sh
hermes -p <profile> skills tap add iasi777/agent-skills
```

Adding a tap does not install its skills. Hermes's standard third-party scanning and prompts still apply.
The repository uses the officially supported [`skills/<name>/SKILL.md` layout](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/#publishing-a-custom-skill-tap).

For manual installation, clone this repository and copy the complete chosen skill folder into the resolved
`<profile-home>/skills/`. Inspect existing destinations first and preserve local changes; copying SKILL.md alone is insufficient.

## Initial configuration

- **writing-skills**: follow [target lookup](skills/writing-skills/references/target-lookup.md). Copy the example to `~/.config/writing-skills/hermes-targets.json` and supply your SSH alias, container, Python, code directory and `data_root`. The lookup only inspects; installation stays in the skill workflow.
- **Mailbox management**: configure the API base and required credentials as described in [the skill](skills/cf-temp-mail-agent-mail/SKILL.md). Use private files inside the actual runtime. This repository does not provide a mail service or default account.

Keep runtime configuration, credentials, verification codes, mail contents and task state outside skill directories. Only placeholder configuration examples belong in Git.

## Local checks

Python 3.10 or newer is required; no extra Python packages are needed:

```sh
python3 -B scripts/check.py
python3 -B -m unittest discover -s skills/writing-skills/tests -v
python3 -B skills/cf-temp-mail-agent-mail/scripts/mailbox.py --help
```

GitHub Actions runs these checks on pushes and pull requests. Unit tests use temporary files and synthetic Hermes APIs;
they do not connect to real servers, create mailboxes or send messages. Validate live deployments separately through each skill's procedure.

## Maintenance and provenance

This repository is the collection's maintenance and publishing source. Keep each skill's `metadata.version` independent.
Maintain the local checkout at `~/projects/agent-skills/`. The owner's local Codex writing-skills installation links directly to this source.
Independent client installations and the original application-repository copy still need explicit updates.

Before editing writing-skills, retain one previous directory backup at `~/.local/state/writing-skills/backups/previous`.
Verify the replacement backup before retiring the older copy. Keep backups outside Git and skill discovery directories.

The general skills listed above are included. `cf-temp-mail-agent-read` is a separate personal reader and is not part of this collection.
The mailbox application remains independent; see [provenance and licenses](NOTICE.md).

Add individually installable packages under `skills/<name>/`. See [CHANGELOG_EN.md](CHANGELOG_EN.md) for changes.
