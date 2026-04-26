---
name: cluster-12
description: "Skill for the Cluster_12 area of hermes-agent-self-evolution. 5 symbols across 1 files."
---

# Cluster_12

5 symbols | 1 files | Cohesion: 50%

## When to Use

- Working with code in `tests/`
- Understanding how write_split_jsonl, test_loads_pre_split_dataset_correctly, test_load_all_does_not_shuffle work
- Modifying cluster_12-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_dataset_builder.py` | write_split_jsonl, test_loads_pre_split_dataset_correctly, test_load_all_does_not_shuffle, test_load_all_skips_missing_splits, test_pre_split_files_still_validated |

## Entry Points

Start here when exploring this area:

- **`write_split_jsonl`** (Function) — `tests/core/test_dataset_builder.py:57`
- **`test_loads_pre_split_dataset_correctly`** (Function) — `tests/core/test_dataset_builder.py:535`
- **`test_load_all_does_not_shuffle`** (Function) — `tests/core/test_dataset_builder.py:556`
- **`test_load_all_skips_missing_splits`** (Function) — `tests/core/test_dataset_builder.py:569`
- **`test_pre_split_files_still_validated`** (Function) — `tests/core/test_dataset_builder.py:579`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `write_split_jsonl` | Function | `tests/core/test_dataset_builder.py` | 57 |
| `test_loads_pre_split_dataset_correctly` | Function | `tests/core/test_dataset_builder.py` | 535 |
| `test_load_all_does_not_shuffle` | Function | `tests/core/test_dataset_builder.py` | 556 |
| `test_load_all_skips_missing_splits` | Function | `tests/core/test_dataset_builder.py` | 569 |
| `test_pre_split_files_still_validated` | Function | `tests/core/test_dataset_builder.py` | 579 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_11 | 4 calls |
| Cluster_10 | 4 calls |

## How to Explore

1. `gitnexus_context({name: "write_split_jsonl"})` — see callers and callees
2. `gitnexus_query({query: "cluster_12"})` — find related execution flows
3. Read key files listed above for implementation details
