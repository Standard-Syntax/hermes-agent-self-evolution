---
name: cluster-8
description: "Skill for the Cluster_8 area of hermes-agent-self-evolution. 6 symbols across 2 files."
---

# Cluster_8

6 symbols | 2 files | Cohesion: 83%

## When to Use

- Working with code in `tests/`
- Understanding how test_gepa_metric_with_trace_returns_prediction, test_gepa_metric_with_trace_has_score_and_feedback, test_gepa_metric_without_trace_returns_float work
- Modifying cluster_8-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_fitness.py` | test_gepa_metric_with_trace_returns_prediction, test_gepa_metric_with_trace_has_score_and_feedback, test_gepa_metric_without_trace_returns_float, test_gepa_metric_score_in_valid_range, test_gepa_metric_validation_call_deterministic |
| `evolution/core/fitness.py` | gepa_metric |

## Entry Points

Start here when exploring this area:

- **`test_gepa_metric_with_trace_returns_prediction`** (Function) — `tests/core/test_fitness.py:218`
- **`test_gepa_metric_with_trace_has_score_and_feedback`** (Function) — `tests/core/test_fitness.py:232`
- **`test_gepa_metric_without_trace_returns_float`** (Function) — `tests/core/test_fitness.py:247`
- **`test_gepa_metric_score_in_valid_range`** (Function) — `tests/core/test_fitness.py:254`
- **`test_gepa_metric_validation_call_deterministic`** (Function) — `tests/core/test_fitness.py:268`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_gepa_metric_with_trace_returns_prediction` | Function | `tests/core/test_fitness.py` | 218 |
| `test_gepa_metric_with_trace_has_score_and_feedback` | Function | `tests/core/test_fitness.py` | 232 |
| `test_gepa_metric_without_trace_returns_float` | Function | `tests/core/test_fitness.py` | 247 |
| `test_gepa_metric_score_in_valid_range` | Function | `tests/core/test_fitness.py` | 254 |
| `test_gepa_metric_validation_call_deterministic` | Function | `tests/core/test_fitness.py` | 268 |
| `gepa_metric` | Function | `evolution/core/fitness.py` | 171 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Gepa_metric → _parse_score` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_9 | 1 calls |
| Cluster_6 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_gepa_metric_with_trace_returns_prediction"})` — see callers and callees
2. `gitnexus_query({query: "cluster_8"})` — find related execution flows
3. Read key files listed above for implementation details
