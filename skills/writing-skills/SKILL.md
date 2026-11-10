---
name: writing-skills
description: "Use when creating, revising, splitting, or reviewing a workflow skill for Hermes: defining executable steps, writing a description that triggers reliably, or deciding what belongs in SKILL.md versus bundled files. Also use when someone says 'turn this workflow into a skill' or 'my skill never fires'. Not for one-off prompts, always-on project instructions, or MCP tool schemas."
license: MIT
metadata:
  version: "0.6.0"
---

# writing-skills

Create reusable workflow skills for Hermes. Use the Agent Skills format as a
base, with Hermes extensions where needed. Keep reusable procedures separate
from task configuration and runtime data.

## 1. Authoring workflow

1. Collect the intended workflow, inputs, outputs, and available real-run feedback.
2. Draft the name and description using section 2.
3. Define the execution contract using section 3.
4. Place instructions and resources using section 4; add platform integration
   using section 5 when needed.
5. Review the checklist in section 6.
6. When deployment is requested, deploy to the user-specified profile using
   section 5 and report the actual destination and status.
7. Improve from actual Hermes use using section 7.

For a new skill, copy [assets/SKILL.template.md](assets/SKILL.template.md).
For revisions, preserve useful existing structure and change what the workflow
requires. Operational improvements come from actual Hermes runs and feedback.

## 2. Format and description

A skill folder contains `SKILL.md` with YAML frontmatter and Markdown body.
Optional directories are `scripts/`, `references/`, and `assets/`.

- `name`: 1–64 lowercase letters, digits, and single separating hyphens; match
  the folder name. No leading or trailing hyphen.
- `description`: 1–1024 characters describing the task and when to use it.
- Optional portable fields: `license`, `compatibility`, `metadata`, and
  experimental `allowed-tools`. Tool support varies by client.
- `compatibility`: up to 500 characters, only for real environment needs.
- Portable `metadata` is a string map. Hermes also accepts nested
  `metadata.hermes` and platform-specific fields; consult section 5.
- Keep the authoring version under `metadata.version` as a project convention.
  Do not assume it controls runtime behaviour.

Put discovery cues in the description, where the agent can see them before
loading the body. Open with "Use when ...", name concrete user intents and
outputs, and distinguish nearby tasks when ambiguity exists. Keep it to a few
sentences. Body-only trigger instructions cannot help initial discovery.

## 3. Execution contract

Cover these points in the body or a directly linked resource. Keep simple
workflows brief; mark state and recovery as not applicable when appropriate.

| Item | Required content |
| --- | --- |
| Inputs | Sources, required parameters, defaults, behaviour when missing |
| Preconditions | Required tools, credentials, files, and access |
| Steps | Action, output, observable completion condition for each step |
| Authority | Allowed operations and targets, limits, decisions still needed |
| State and recovery | Storage location, saved progress, where to resume |
| Failure handling | Retryable failures, retry limit, stop conditions |
| Delivery | Output format, destination, evidence of completion |

Act within existing user authorization. Request confirmation only when an
operation exceeds that scope or a required decision is missing. Complete
independent preparation first and present a concrete result for review.
When input is unavailable, preserve useful progress and report the blocker.

Keep three kinds of information separate:

- **Skill:** reusable procedure, decisions, and completion criteria.
- **Task configuration:** schedule, timezone, input sources, delivery target.
- **Run state:** progress, outputs, processed-item identifiers, pending decisions.

Store runtime data outside the skill package in an explicit configured location.
Recurring jobs must obtain inputs from configuration or persisted state rather
than previous conversation history. For repeated writes or sends, specify how
to recognize an already completed operation. After an ambiguous timeout, check
the actual result before retrying. Distinguish output creation from delivery
confirmation in the reported outcome.

## 4. Writing and layering

| Content | Location |
| --- | --- |
| Discovery cues and scope | `description` |
| Procedure, decisions, defaults, common gotchas | `SKILL.md` body |
| Details needed for one branch or platform | `references/<topic>.md` |
| Exact or fragile reusable logic | `scripts/<name>` |
| Templates and files copied into output | `assets/<file>` |

- Write imperative steps with observable completion conditions. Explain the
  reason for non-obvious rules and use concrete examples where helpful.
- Choose one default and state the condition for alternatives. Match precision
  to consequences: exact commands for operations that require exact execution.
- Aim below 500 lines and 5,000 tokens for the body. Keep every-run essentials
  inline; disclose branch-specific detail through conditional links.
- Link main workflows and branch entry references directly from SKILL.md.
  Branch-specific scripts and templates may be linked from that branch's reference;
  state when to run or copy them. Resolve links relative to the containing file,
  and state the working directory for executable commands.
- Keep reference chains short: branch references should lead directly to their
  resources, without further reference hops. Give files over 100 lines a contents
  list so the agent can locate relevant sections.
- For scripts, specify whether to run or read them, dependencies, arguments,
  exit codes, and error handling. Prefer non-interactive execution and `--help`.
- Put changing platform details in dated references. Keep gotchas grounded in
  observed failures and place them beside the relevant step when possible.

## 5. Hermes integration and portability

When creating or revising a Hermes workflow, read
[references/hermes.md](references/hermes.md) for deployment, platform fields, scheduling,
and runtime integration. Confirm support in the installed version before
using extensions. Generic validators may reject valid Hermes fields.

Before deployment, require an explicit target profile name from the user.
Reuse a name already supplied for this task; otherwise ask which profile to
use and explain that deployment needs an explicit target. Continue independent
authoring while awaiting the answer. Do not infer the profile from the active
session or fall back to the default profile. Resolve the named profile's actual
Hermes home before writing deployment files. Run the fixed lookup described in
[references/target-lookup.md](references/target-lookup.md), passing the explicit
profile and skill name. It reads external runtime configuration and reports the
destination and conflicts; keep copying and updating in the deployment workflow.

In the delivery report, include the source location, target profile, resolved
deployment path, deployment status, and any same-name conflicts found. If only
authoring was requested or deployment did not occur, state that it is not deployed.

When publishing to other clients, read
[references/portability.md](references/portability.md) for client paths and
extensions. Keep reusable instructions shared and isolate platform details;
check compatibility for each intended client.

## 6. Pre-share checklist

- [ ] Folder name matches `name` and naming constraints.
- [ ] Description states concrete intents and scope within 1024 characters.
- [ ] Frontmatter matches the target client; version is under metadata.
- [ ] Execution contract covers the workflow without irrelevant machinery.
- [ ] Authorization boundaries respect existing user approval.
- [ ] Task configuration and run state are separate from the skill package.
- [ ] Resource links resolve and state when to read, run, or copy their target.
- [ ] Examples use placeholders; no credentials or private deployment data ship.
- [ ] Body is concise; platform details are isolated and dated.
- [ ] If deploying, the user specified the profile and its actual home is resolved.
- [ ] Delivery report distinguishes authored files from deployed files.

## 7. Maintenance from actual use

Use actual Hermes execution and specific user feedback to identify changes.
Record the failed step, expected result, observed result, and useful evidence
outside the skill package; update the instruction responsible for the issue.

Add a gotcha only for a reproducible or generalizable failure. Merge it into an
existing rule when possible, and remove obsolete or redundant guidance. Bump
`metadata.version` on behavioural changes; keep the name stable unless a rename
is requested.
