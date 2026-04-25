---
description: Review, sync, commit, and push the current ez-stack worktree
agent: build
---

Ship the current ez-stack task.

Commit message: $ARGUMENTS

Required flow:
1. Run `pwd` and `git rev-parse --show-toplevel`.
2. Run `ez diff --stat`.
3. Run `ez diff --name-only`.
4. Run `ez status`.
5. Run the repo's focused tests or validation commands.
6. Run `ez sync --autostash`.
7. If all changes are tracked files, run:
   `ez push -am "$ARGUMENTS"`
8. If intentional new files are present, run:
   `ez push -Am "$ARGUMENTS"`
9. Report the PR URL using `ez pr-link`.

Do not use raw `git commit`, `git push`, or `gh pr create`.
