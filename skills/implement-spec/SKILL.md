---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
license: MIT
metadata:
  version: "1.0.0"
---

Implement the spec on one **integration branch** and resolve its tickets according to the issue tracker's conventions. Start every subagent with a fresh context window.

For prerequisites and workflow examples, see the [workflow reference](references/workflow.md).

## Prepare

1. Read the spec, the tickets, and the tracker conventions. If the tracker is missing, ask the user to run `/setup-matt-pocock-skills` before dispatch. Identify the blocking edges and the evidence each dependency requires. A dependency that requires acceptance is satisfied when that acceptance is verified.
2. Create the integration branch in its own worktree and record the starting commit for final review. When several tickets need the same missing facts, use a read-only exploration subagent and have it return a path to shared notes outside the repository.

## Dispatch and wait

3. Run implementers in the background for independent tickets whose blockers are satisfied, using the available capacity.
4. Give each ticket its own branch and worktree from the current integration tip. Pass the worktree path, branch, and exact base SHA at dispatch, along with pointers to the spec, ticket, required checks, and relevant notes or commits.

   - Before editing or testing, confirm the assigned path and branch. A new worktree's `HEAD` must equal the assigned base SHA. For a resumed ticket, use `git merge-base --is-ancestor <base-sha> HEAD` to confirm its commits build on that base.
   - If the check fails, stop ticket work and report the expected base and actual `HEAD` to the coordinator. The coordinator directs the implementer to the verified checkout when the assignment is correct. If the assigned worktree itself has the wrong base, the coordinator creates a replacement branch and worktree with `git worktree add -b <replacement-branch> <replacement-path> <base-sha>`. Preserve the original branch, commits, and local changes. Carry over any identified ticket work and verify the replacement before resuming.
   - Once the base is verified, call the Skill tool with `tdd`. Incorporate the current integration tip before delivery and run the relevant checks in the verified worktree.
5. Ask implementers to communicate at **delivery, a concrete blocker, or a decision or authorization request**. A delivery includes the candidate commit SHA and test or acceptance evidence. A blocking report includes the obstacle and the action needed. Send a message to a running implementer only when a confirmed blocker, a change in approval, or a user change of scope needs its attention. Use `followup_task` or its equivalent after a child turn ends and a concrete next task is ready.
6. While children run, advance independent work. When their results are needed, use the runtime's supported wait behavior.

   - If automatic wake-up on native child completion is enabled and known to work in this runtime, end the turn with a short status. Continue when the notification opens the next turn.
   - Otherwise, use the native wait tool with a minutes-long timeout when supported. An ordinary timeout means no event arrived. Continue waiting and query agent status only to investigate a specific anomaly.
   - When progress depends on a user decision and independent work is exhausted, surface the decision and the affected tickets.

## Integrate and release dependent tickets

7. When an implementer delivers, use a merger subagent to verify the candidate commit, ticket scope, and check results, then merge it into the integration branch.
8. Open the draft PR after the first merge if the tracker uses PRs to close work or the user requested a PR. Recompute the ready tickets as integration and acceptance evidence arrive, then fill free implementation slots. A draft PR may keep an integrated ticket open in the tracker. Use the spec's completion conditions to decide which dependencies are satisfied during the run.

## Finish

9. Once all tickets are integrated, call the Skill tool with `code-review` on the integration branch against the recorded starting commit. If it raises findings, send them to one fresh implementer, integrate the fixes, and rerun the affected checks.
10. When required checks, review fixes, and acceptance are complete, mark the draft PR ready or resolve the tickets through the configured tracker. Report the integration branch, PR if applicable, and any unresolved tickets with their blockers. Remove clean worktrees whose work is integrated.
