# Hermes workflow integration

Checked against official documentation on 2026-11-10. Confirm support in the
installed Hermes version before relying on fields or commands.

## Deployment to the specified profile

Apply the explicit-profile requirement in SKILL.md before deployment. Use the
[fixed target lookup](target-lookup.md) to resolve the configured host/container,
named profile home and skill destination, and inspect same-name conflicts. This
is the default entry point; follow its configuration and error handling instead
of rediscovering runtime locations. If the name cannot be resolved, report the
missing target; do not silently create a profile or select another one.

Deploy the complete skill folder to:

```text
<resolved-profile-home>/skills/<skill-name>/
```

Include SKILL.md and its referenced scripts, assets, and reference files.
`$HERMES_HOME/skills/` denotes this location only when HERMES_HOME belongs to
the specified target profile. `~/.hermes/skills/` is the usual default-profile
location, not a universal destination. Resolve paths in the target runtime
environment, rather than assuming the authoring machine's paths apply there.

Inspect an existing same-name destination before updating it and preserve
unrelated files. Check for a project skill that could shadow the deployed
profile copy in the intended execution context; report any such conflict.
Keep profile-specific paths in deployment configuration and the delivery
report rather than hardcoding them in reusable workflow instructions.

The location where Codex loads this authoring skill is separate from the Hermes
destination of the skills it produces. Installing the authoring skill does not
deploy generated skills to Hermes.

## Platform fields

Use only extensions needed by the workflow:

- `metadata.hermes.requires_tools` and `requires_toolsets`: declare tools or
  toolsets needed for discovery. These declarations do not grant permission.
- `platforms`: restrict discovery to supported operating systems.
- `required_environment_variables`: declare required variable names and setup
  guidance. Store credential values in the runtime environment, not the skill.
- `metadata.hermes.config`: describe settings needed by the workflow.
- `metadata.hermes.blueprint`: optionally supply automation defaults such as
  schedule, delivery, and prompt. Keep deployment-specific values in task
  configuration; a blueprint is not authorization to create a scheduled job.

Hermes supports nested metadata and additional top-level fields beyond the
portable Agent Skills format. Do not reject those solely because a generic
validator expects a string-only metadata map. Keep `metadata.version` as this
project's authoring convention, rather than assuming it controls Hermes runtime.

## Scheduling and execution

Attach a skill to a job through the installed Hermes cron interface. A job can
attach multiple skills; specify their responsibilities and order when outputs
of one become inputs to another. Loading several skills alone does not define
an execution sequence.

Scheduled runs start fresh agent sessions. Provide inputs through task
configuration or persisted state. Configure schedule, timezone, and delivery
explicitly for the intended deployment. Keep task creation and maintenance
outside the recurring procedure; cron executions cannot create more cron jobs.

For deterministic scheduled work, consider Hermes no-agent script execution.
Use agent-backed execution when the workflow needs interpretation or judgment.
Select only the mechanism the workflow actually needs.

## Operational boundaries

Check prerequisites before doing work. Missing credentials or configuration
should produce a concrete blocker with preserved progress. Set up secrets in
an appropriate interactive setup context before unattended execution.

Use Hermes scheduling and delivery records where available. Keep business
progress and deduplication data separately when needed; scheduler recovery
does not establish whether an external business operation succeeded.

Report execution and delivery outcomes separately. A generated artifact does
not prove it reached its destination. If a send outcome is unknown, inspect
available evidence before attempting another send.

Refine these instructions from actual Hermes runs and specific user feedback.

## Sources

- [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)
- [Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/)
- [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)
- [Scheduled Tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [Cron Internals](https://hermes-agent.nousresearch.com/docs/developer-guide/cron-internals)
