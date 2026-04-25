---
description: Start an isolated ez-stack worktree for a task
agent: build
---

Start a new ez-stack task worktree.

Task/branch name: $ARGUMENTS

Rules:
1. Run `ez list` first.
2. Create an independent worktree from main:
   `cd $(ez create $ARGUMENTS --from main)`
3. Immediately run:
   `pwd`
   `git rev-parse --show-toplevel`
   `ez status --json`
4. Work only inside the active worktree root.
5. Do not use raw `git checkout -b`, `git commit`, `git push`, or `gh pr create`.
