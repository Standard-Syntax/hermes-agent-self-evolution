---
description: Sync ez-stack branches and restack safely
agent: build
---

Sync the current ez-stack repo.

Run:
1. `pwd`
2. `git rev-parse --show-toplevel`
3. `ez status --json`
4. `ez sync --autostash`
5. `ez list`
6. `ez log --json`

If there is a rebase conflict, stop and explain the conflicted files. Do not force-push or delete branches.
