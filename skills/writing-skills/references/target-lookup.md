# Fixed Hermes target lookup

Contents: [Run](#run) · [Configuration](#configuration) ·
[Results and recovery](#results-and-recovery) · [Validation](#validation)

Verified against the configured runtime on 2026-11-10. Use this lookup when
writing-skills needs an installation destination. It does not install skills,
create profiles, switch defaults, or invoke a model.

## Run

From the writing-skills directory, run [the query script](../scripts/hermes_target.py):

```sh
python3 -B scripts/hermes_target.py --profile <user-specified-profile> --skill <skill-folder-name>
```

The profile is required, including `default` when explicitly intended. Accepted
names contain letters, digits, hyphens or underscores, begin with a letter/digit,
and have at most 64 characters. `--target <name>` overrides the configured
runtime; a default runtime never supplies a default profile.

Add `--project-dir <absolute-runtime-path>` for a known project. This checks its
`.hermes/skills` and `.agents/skills` in addition to the profile's skill directory.
Run `--help` for arguments. Dependencies: local Python 3, SSH for remote targets,
Podman for configured containers, and the target's Hermes Python environment.
The query streams [the runtime probe](../scripts/hermes_probe.py); do not run the
probe separately as a deployment command.

## Configuration

Read `~/.config/writing-skills/hermes-targets.json`, or pass `--config <path>`.
When registering an environment, copy [the example](../assets/hermes-targets.example.json)
and replace placeholders with verified values. Keep the actual file outside the
skill package, with mode 0600 in a 0700 directory. Credentials stay in existing
SSH/runtime secret management; this config holds aliases and paths.

`schema_version` is 1. `default_target` names an entry in `targets`. Each target
requires `transport` (`ssh` or `local`), absolute `hermes_root` (code directory),
`python` (Hermes interpreter), and `data_root` (instance data root) paths.
Use SSH `host` for `ssh`; optional `container` names a Podman container.
Omit `container` for a host installation. Example: code under `/opt/hermes`, data
under `/opt/data`. Existing configurations must add `data_root`; it is never inferred.

The probe pins its own `HERMES_HOME` to `data_root` before importing Hermes,
then checks the resolved profile against that instance. This affects only the
query process. A supplied profile home in place of an instance root, or a profile
symlink leading elsewhere, is rejected. The caller's environment stays unchanged.

If configuration is missing, ask which runtime to register while continuing
independent skill authoring. Do not scan unrelated homes or choose another runtime.
SSH uses normal host-key setup; the helper does not enroll or bypass unknown keys.

## Results and recovery

Stdout is one JSON object; stderr is reserved for CLI usage errors. Results include
the runtime, data root, profile home, destination, execution UID, inspected roots,
conflicts and coverage limits. Static SKILL.md metadata is parsed using Hermes's
`agent.skill_utils.parse_frontmatter`, including its fallback semantics. The helper
compares both folder and declared names, without executing skill templates or shell
snippets. It does not print skill bodies or read profile secrets and `.env` files.

| Exit | Meaning | Next step |
| --- | --- | --- |
| 0 | Profile located; no conflict in fully inspected roots | Use the returned destination in the authorized deployment workflow |
| 1 | Configuration, runtime, profile or incomplete inspection | Fix the reported layer and rerun against the same target |
| 2 | Invalid/missing arguments | Correct the command; never infer a profile |
| 3 | Existing destination or same-name skill | Inspect before updating; preserve unrelated files and report conflicts |

Without `--skill`, `conflict_check` is `not_requested`. With it, the walker uses
Hermes's cache/support-directory exclusions and propagates traversal errors.
Symlinked subdirectories and SKILL.md files are reported without following them;
these make `conflict_check: partial` and `error: skill_scan_incomplete`. Known
conflicts still return exit 3; otherwise incomplete inspection returns exit 1.
Unreadable or invalid metadata also cannot produce a clean result.

External skill roots, legacy flat Markdown skills, project trust and effective
Hermes discovery are outside coverage. A clean result applies to inspected roots.

`config_missing`/`config_invalid` concern the config; `ssh_unavailable` concerns
SSH; `runtime_unavailable` concerns the configured command/container.
`data_root_not_found`, `profile_not_found` and `profile_root_mismatch` concern
the configured instance/profile. Missing profiles are never created.
`unsupported_hermes_profile_api`/`unsupported_hermes_skill_api` require checking
the installed Hermes version; do not guess paths or silently skip name checks.
`runtime_permission_denied`/`skill_metadata_invalid` require fixing inspection access/data.

Python `-B` prevents bytecode writes. SSH is noninteractive with strict host-key
checking. The total deadline defaults to 30 seconds (`--timeout`, 1–120 seconds);
there are no automatic retries. Failed subprocess output is not echoed.

Use returned runtime/container paths with that runtime's file permissions for
later copy operations. Installation remains separate. Report location checks,
installed-file checks, skill discovery and model execution as distinct evidence.

## Validation

After helper changes, run from the skill directory:

```sh
python3 -B -m unittest discover -s tests -v
```

Tests use synthetic Hermes APIs and temporary directories. Separately validate
installed API compatibility with a live lookup and isolated temporary fixtures.
