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
