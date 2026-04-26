---
name: cluster-6
description: "Skill for the Cluster_6 area of hermes-agent-self-evolution. 10 symbols across 2 files."
---

# Cluster_6

10 symbols | 2 files | Cohesion: 95%

## When to Use

- Working with code in `tests/`
- Understanding how test_fast_metric_returns_float, test_fast_metric_in_valid_range, test_fast_metric_empty_output_returns_zero work
- Modifying cluster_6-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_fitness.py` | test_fast_metric_returns_float, test_fast_metric_in_valid_range, test_fast_metric_empty_output_returns_zero, test_fast_metric_deterministic, test_fast_metric_no_llm_calls (+3) |
| `evolution/core/fitness.py` | fast_metric, skill_fitness_metric |

## Entry Points

Start here when exploring this area:

- **`test_fast_metric_returns_float`** (Function) — `tests/core/test_fitness.py:80`
- **`test_fast_metric_in_valid_range`** (Function) — `tests/core/test_fitness.py:86`
- **`test_fast_metric_empty_output_returns_zero`** (Function) — `tests/core/test_fitness.py:92`
- **`test_fast_metric_deterministic`** (Function) — `tests/core/test_fitness.py:99`
- **`test_fast_metric_no_llm_calls`** (Function) — `tests/core/test_fitness.py:106`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_fast_metric_returns_float` | Function | `tests/core/test_fitness.py` | 80 |
| `test_fast_metric_in_valid_range` | Function | `tests/core/test_fitness.py` | 86 |
| `test_fast_metric_empty_output_returns_zero` | Function | `tests/core/test_fitness.py` | 92 |
| `test_fast_metric_deterministic` | Function | `tests/core/test_fitness.py` | 99 |
| `test_fast_metric_no_llm_calls` | Function | `tests/core/test_fitness.py` | 106 |
| `test_fast_metric_keyword_overlap` | Function | `tests/core/test_fitness.py` | 113 |
| `test_skill_fitness_metric_still_works` | Function | `tests/core/test_fitness.py` | 362 |
| `test_skill_fitness_metric_empty_output` | Function | `tests/core/test_fitness.py` | 368 |
| `fast_metric` | Function | `evolution/core/fitness.py` | 105 |
| `skill_fitness_metric` | Function | `evolution/core/fitness.py` | 130 |

## How to Explore

1. `gitnexus_context({name: "test_fast_metric_returns_float"})` — see callers and callees
2. `gitnexus_query({query: "cluster_6"})` — find related execution flows
3. Read key files listed above for implementation details
