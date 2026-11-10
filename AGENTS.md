# Agent guidance

- Start with README.md / README_EN.md for layout, installation and check commands.
- Edit reusable packages under skills/. Keep task configuration and runtime state outside this repository.
- Before changing a skill, read its SKILL.md and relevant references. Keep package names stable and bump metadata.version for behavioral changes.
- Preserve third-party notices listed in NOTICE.md. Keep docs and changelogs in both languages consistent.
- Run the checks documented in README.md before committing. Live runtime validation is separate from offline tests.
- Use English Conventional Commit messages. Publishing does not deploy changes into an existing Hermes profile.
