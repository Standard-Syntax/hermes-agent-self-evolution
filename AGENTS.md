# Agent Rules

## Version control

This repo is managed by ez-stack.

If `.git/ez/stack.json` exists, use `ez` for all branch, commit, sync, and PR operations.

Do not use these directly:
- `git checkout -b`
- `git commit`
- `git push`
- `gh pr create`
- `git diff main...HEAD`

Use these instead:
- Create independent task worktree: `cd $(ez create <branch-name> --from main)`
- Create stacked child branch: `cd $(ez create <branch-name>)`
- Commit specific files: `ez commit -m "<message>" -- <path1> <path2>`
- Commit all tracked changes: `ez commit -am "<message>"`
- Commit tracked and untracked changes: `ez commit -Am "<message>"`
- Inspect changed files: `ez diff --stat` and `ez diff --name-only`
- Sync before pushing: `ez sync --autostash`
- Push/create/update PR: `ez push` or `ez push -am "<message>"`
- Push full stack: `ez submit`
- Delete finished worktree: `cd $(ez delete <branch-name> --yes)`

## Worktree discipline

Use one ez worktree per agent task.

For independent work, always create from main:

```bash
cd $(ez create <task-branch> --from main)
```
After ez create, ez switch, ez sync, or ez delete, immediately re-anchor file operations:

pwd
git rev-parse --show-toplevel
ez status --json

Read and write files only inside the active worktree root.

Before pushing

Always run:

ez diff --stat
ez diff --name-only
ez status
ez sync --autostash

Then push with:

ez push -am "<conventional commit message>"

Use ez push -Am only when new untracked files intentionally belong in the PR

