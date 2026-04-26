# Agent Rules

# Python Agent Orchestration

This repo uses an OpenCode Python TDD loop with three context tools:

- Sourcebot MCP for multi-repo search.
- GitNexus MCP for architecture, impact, and dependency graph context.
- Serena MCP for symbol-aware current-repo navigation and targeted edits.

Use `/py-loop <task>` for implementation work.

## Tool selection

- Prefer GitNexus for impact analysis before refactors.
- Prefer Serena for exact symbols and references.
- Prefer Sourcebot for cross-repo patterns or examples.
- Do not call every context tool by default.
- Keep `.opencode/loop-task.md` concise and evidence-focused.

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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **hermes-agent-self-evolution** (1120 symbols, 1926 relationships, 17 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/hermes-agent-self-evolution/context` | Codebase overview, check index freshness |
| `gitnexus://repo/hermes-agent-self-evolution/clusters` | All functional areas |
| `gitnexus://repo/hermes-agent-self-evolution/processes` | All execution flows |
| `gitnexus://repo/hermes-agent-self-evolution/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |
| Work in the Skills area (24 symbols) | `.claude/skills/generated/skills/SKILL.md` |
| Work in the Cluster_10 area (15 symbols) | `.claude/skills/generated/cluster-10/SKILL.md` |
| Work in the Cluster_11 area (15 symbols) | `.claude/skills/generated/cluster-11/SKILL.md` |
| Work in the Cluster_15 area (14 symbols) | `.claude/skills/generated/cluster-15/SKILL.md` |
| Work in the Cluster_18 area (12 symbols) | `.claude/skills/generated/cluster-18/SKILL.md` |
| Work in the Cluster_6 area (10 symbols) | `.claude/skills/generated/cluster-6/SKILL.md` |
| Work in the Cluster_5 area (6 symbols) | `.claude/skills/generated/cluster-5/SKILL.md` |
| Work in the Cluster_8 area (6 symbols) | `.claude/skills/generated/cluster-8/SKILL.md` |
| Work in the Cluster_20 area (6 symbols) | `.claude/skills/generated/cluster-20/SKILL.md` |
| Work in the Cluster_7 area (5 symbols) | `.claude/skills/generated/cluster-7/SKILL.md` |
| Work in the Cluster_9 area (5 symbols) | `.claude/skills/generated/cluster-9/SKILL.md` |
| Work in the Cluster_12 area (5 symbols) | `.claude/skills/generated/cluster-12/SKILL.md` |
| Work in the Cluster_13 area (5 symbols) | `.claude/skills/generated/cluster-13/SKILL.md` |
| Work in the Cluster_14 area (5 symbols) | `.claude/skills/generated/cluster-14/SKILL.md` |
| Work in the Cluster_16 area (5 symbols) | `.claude/skills/generated/cluster-16/SKILL.md` |
| Work in the Cluster_17 area (4 symbols) | `.claude/skills/generated/cluster-17/SKILL.md` |
| Work in the Cluster_21 area (4 symbols) | `.claude/skills/generated/cluster-21/SKILL.md` |
| Work in the Cluster_22 area (4 symbols) | `.claude/skills/generated/cluster-22/SKILL.md` |

<!-- gitnexus:end -->
