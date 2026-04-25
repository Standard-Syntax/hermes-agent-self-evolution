---
description: Delete a finished ez-stack worktree
agent: build
---

Finish and delete an ez-stack worktree.

Branch/task name: $ARGUMENTS

Before deleting:
1. Run `ez status`.
2. Confirm there are no uncommitted changes.
3. Run `ez pr-link` if a PR exists.
4. Delete the worktree:
   `cd $(ez delete $ARGUMENTS --yes)`
5. Run `ez list`.

Do not use raw `git branch -D` or manually remove `.worktrees`.
