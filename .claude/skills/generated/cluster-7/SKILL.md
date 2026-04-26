---
name: cluster-7
description: "Skill for the Cluster_7 area of hermes-agent-self-evolution. 5 symbols across 2 files."
---

# Cluster_7

5 symbols | 2 files | Cohesion: 89%

## When to Use

- Working with code in `tests/`
- Understanding how test_judge_metric_returns_fitness_score, test_judge_metric_has_feedback, test_judge_metric_scores_in_valid_range work
- Modifying cluster_7-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_fitness.py` | test_judge_metric_returns_fitness_score, test_judge_metric_has_feedback, test_judge_metric_scores_in_valid_range, test_judge_metric_uses_llm |
| `evolution/core/fitness.py` | judge_metric |

## Entry Points

Start here when exploring this area:

- **`test_judge_metric_returns_fitness_score`** (Function) — `tests/core/test_fitness.py:144`
- **`test_judge_metric_has_feedback`** (Function) — `tests/core/test_fitness.py:157`
- **`test_judge_metric_scores_in_valid_range`** (Function) — `tests/core/test_fitness.py:171`
- **`test_judge_metric_uses_llm`** (Function) — `tests/core/test_fitness.py:186`
- **`judge_metric`** (Function) — `evolution/core/fitness.py:138`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_judge_metric_returns_fitness_score` | Function | `tests/core/test_fitness.py` | 144 |
| `test_judge_metric_has_feedback` | Function | `tests/core/test_fitness.py` | 157 |
| `test_judge_metric_scores_in_valid_range` | Function | `tests/core/test_fitness.py` | 171 |
| `test_judge_metric_uses_llm` | Function | `tests/core/test_fitness.py` | 186 |
| `judge_metric` | Function | `evolution/core/fitness.py` | 138 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Judge_metric → _parse_score` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_9 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_judge_metric_returns_fitness_score"})` — see callers and callees
2. `gitnexus_query({query: "cluster_7"})` — find related execution flows
3. Read key files listed above for implementation details
