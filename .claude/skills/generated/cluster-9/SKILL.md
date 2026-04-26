---
name: cluster-9
description: "Skill for the Cluster_9 area of hermes-agent-self-evolution. 5 symbols across 2 files."
---

# Cluster_9

5 symbols | 2 files | Cohesion: 73%

## When to Use

- Working with code in `evolution/`
- Understanding how test_holdout_result_includes_all_required_fields, test_holdout_result_judge_feedback_is_string, score work
- Modifying cluster_9-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `evolution/core/fitness.py` | score, run_holdout_evaluation, _parse_score |
| `tests/core/test_fitness.py` | test_holdout_result_includes_all_required_fields, test_holdout_result_judge_feedback_is_string |

## Entry Points

Start here when exploring this area:

- **`test_holdout_result_includes_all_required_fields`** (Function) — `tests/core/test_fitness.py:299`
- **`test_holdout_result_judge_feedback_is_string`** (Function) — `tests/core/test_fitness.py:328`
- **`score`** (Function) — `evolution/core/fitness.py:62`
- **`run_holdout_evaluation`** (Function) — `evolution/core/fitness.py:222`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_holdout_result_includes_all_required_fields` | Function | `tests/core/test_fitness.py` | 299 |
| `test_holdout_result_judge_feedback_is_string` | Function | `tests/core/test_fitness.py` | 328 |
| `score` | Function | `evolution/core/fitness.py` | 62 |
| `run_holdout_evaluation` | Function | `evolution/core/fitness.py` | 222 |
| `_parse_score` | Function | `evolution/core/fitness.py` | 278 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_holdout_evaluation → _parse_score` | intra_community | 3 |
| `Gepa_metric → _parse_score` | cross_community | 3 |
| `Judge_metric → _parse_score` | cross_community | 3 |

## How to Explore

1. `gitnexus_context({name: "test_holdout_result_includes_all_required_fields"})` — see callers and callees
2. `gitnexus_query({query: "cluster_9"})` — find related execution flows
3. Read key files listed above for implementation details
