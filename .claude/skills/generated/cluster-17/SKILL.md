---
name: cluster-17
description: "Skill for the Cluster_17 area of hermes-agent-self-evolution. 4 symbols across 2 files."
---

# Cluster_17

4 symbols | 2 files | Cohesion: 86%

## When to Use

- Working with code in `tests/`
- Understanding how test_write_holdout_results_saves_multiple_lines, test_write_holdout_results_each_line_is_valid_json, test_write_holdout_results_empty_list work
- Modifying cluster_17-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_artifacts.py` | test_write_holdout_results_saves_multiple_lines, test_write_holdout_results_each_line_is_valid_json, test_write_holdout_results_empty_list |
| `evolution/core/artifacts.py` | write_holdout_results |

## Entry Points

Start here when exploring this area:

- **`test_write_holdout_results_saves_multiple_lines`** (Function) — `tests/core/test_artifacts.py:206`
- **`test_write_holdout_results_each_line_is_valid_json`** (Function) — `tests/core/test_artifacts.py:237`
- **`test_write_holdout_results_empty_list`** (Function) — `tests/core/test_artifacts.py:261`
- **`write_holdout_results`** (Function) — `evolution/core/artifacts.py:63`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_write_holdout_results_saves_multiple_lines` | Function | `tests/core/test_artifacts.py` | 206 |
| `test_write_holdout_results_each_line_is_valid_json` | Function | `tests/core/test_artifacts.py` | 237 |
| `test_write_holdout_results_empty_list` | Function | `tests/core/test_artifacts.py` | 261 |
| `write_holdout_results` | Function | `evolution/core/artifacts.py` | 63 |

## How to Explore

1. `gitnexus_context({name: "test_write_holdout_results_saves_multiple_lines"})` — see callers and callees
2. `gitnexus_query({query: "cluster_17"})` — find related execution flows
3. Read key files listed above for implementation details
