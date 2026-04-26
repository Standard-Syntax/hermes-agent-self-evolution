---
name: cluster-11
description: "Skill for the Cluster_11 area of hermes-agent-self-evolution. 15 symbols across 2 files."
---

# Cluster_11

15 symbols | 2 files | Cohesion: 75%

## When to Use

- Working with code in `tests/`
- Understanding how write_golden_jsonl, test_golden_loader_same_seed_same_split, test_different_seeds_produce_different_splits work
- Modifying cluster_11-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_dataset_builder.py` | write_golden_jsonl, test_golden_loader_same_seed_same_split, test_different_seeds_produce_different_splits, test_holdout_nonempty_when_input_sufficient, test_very_small_dataset_still_splits (+6) |
| `evolution/core/dataset_builder.py` | to_dict, from_dict, load, load |

## Entry Points

Start here when exploring this area:

- **`write_golden_jsonl`** (Function) — `tests/core/test_dataset_builder.py:50`
- **`test_golden_loader_same_seed_same_split`** (Function) — `tests/core/test_dataset_builder.py:91`
- **`test_different_seeds_produce_different_splits`** (Function) — `tests/core/test_dataset_builder.py:107`
- **`test_holdout_nonempty_when_input_sufficient`** (Function) — `tests/core/test_dataset_builder.py:338`
- **`test_very_small_dataset_still_splits`** (Function) — `tests/core/test_dataset_builder.py:346`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `write_golden_jsonl` | Function | `tests/core/test_dataset_builder.py` | 50 |
| `test_golden_loader_same_seed_same_split` | Function | `tests/core/test_dataset_builder.py` | 91 |
| `test_different_seeds_produce_different_splits` | Function | `tests/core/test_dataset_builder.py` | 107 |
| `test_holdout_nonempty_when_input_sufficient` | Function | `tests/core/test_dataset_builder.py` | 338 |
| `test_very_small_dataset_still_splits` | Function | `tests/core/test_dataset_builder.py` | 346 |
| `test_validation_filters_insufficient_examples` | Function | `tests/core/test_dataset_builder.py` | 358 |
| `test_golden_loader_deduplicates` | Function | `tests/core/test_dataset_builder.py` | 459 |
| `test_golden_loader_filters_secrets` | Function | `tests/core/test_dataset_builder.py` | 473 |
| `test_golden_loader_filters_empty_task_input` | Function | `tests/core/test_dataset_builder.py` | 486 |
| `test_golden_loader_normalizes_invalid_difficulty` | Function | `tests/core/test_dataset_builder.py` | 498 |
| `test_golden_loader_validates_before_splitting` | Function | `tests/core/test_dataset_builder.py` | 510 |
| `to_dict` | Function | `evolution/core/dataset_builder.py` | 28 |
| `from_dict` | Function | `evolution/core/dataset_builder.py` | 38 |
| `load` | Function | `evolution/core/dataset_builder.py` | 62 |
| `load` | Function | `evolution/core/dataset_builder.py` | 225 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → From_dict` | cross_community | 5 |
| `Main → _validate_eval_example` | cross_community | 5 |
| `Main → _contains_secret` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_10 | 10 calls |

## How to Explore

1. `gitnexus_context({name: "write_golden_jsonl"})` — see callers and callees
2. `gitnexus_query({query: "cluster_11"})` — find related execution flows
3. Read key files listed above for implementation details
