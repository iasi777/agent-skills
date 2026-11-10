---
name: my-skill
description: "Use when [user intents]: [what the skill produces]. Not for [nearby tasks]."
license: MIT
metadata:
  version: "0.1.0"
---

<!-- Rename folder and name together. Replace placeholders and remove this
comment. Keep only relevant sections; mark recovery as not applicable for a
stateless workflow. Add Hermes fields only when the workflow needs them. -->

# [Skill title]

[What this workflow does and what the user receives.]

## Inputs and prerequisites

- Inputs: [sources, required parameters, defaults, behaviour when missing].
- Requirements: [tools, credentials by variable name, files, access].
- Task configuration: [where input sources, delivery target, and any schedule
  and timezone are configured].

## Authorization

[Allowed operations, targets, and limits from user authorization. Identify any
operation requiring a further decision. Respect existing approval; prepare a
concrete result before requesting a decision outside that scope.]

## Workflow

1. **[Action].** [Input, procedure, output, and observable completion condition.]
2. **[Action].** [Default decision and the condition for an alternative.]
3. **Deliver.** [Destination, output format, and evidence of completion.]

## State and failure handling

- State: [location outside the skill package; progress and results to save].
- Resume: [how to locate saved progress and select the next step].
- Repeated operations: [how to recognize completed writes or sends].
- Failure: [retryable cases, retry limit, stop conditions, and what to report].
- Unknown result: [how to check whether an operation succeeded before retrying].

## Output

[Output structure and acceptance criteria. Report output creation and delivery
confirmation separately when delivery is part of the workflow.]

## Gotchas

- [Reproducible or generalizable issue observed in actual use, with its remedy.]

## Resources

- When [condition], read `references/<topic>.md`.
- For [output], copy `assets/<file>`.
