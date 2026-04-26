---
name: cluster-13
description: "Skill for the Cluster_13 area of hermes-agent-self-evolution. 5 symbols across 2 files."
---

# Cluster_13

5 symbols | 2 files | Cohesion: 80%

## When to Use

- Working with code in `tests/`
- Understanding how test_synthetic_builder_same_seed_same_split, test_invalid_examples_filtered_from_synthetic_output, test_synthetic_output_deduplicated work
- Modifying cluster_13-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_dataset_builder.py` | test_synthetic_builder_same_seed_same_split, test_invalid_examples_filtered_from_synthetic_output, test_synthetic_output_deduplicated, test_synthetic_invalid_difficulty_normalized |
| `evolution/core/dataset_builder.py` | generate |

## Entry Points

Start here when exploring this area:

- **`test_synthetic_builder_same_seed_same_split`** (Function) — `tests/core/test_dataset_builder.py:125`
- **`test_invalid_examples_filtered_from_synthetic_output`** (Function) — `tests/core/test_dataset_builder.py:394`
- **`test_synthetic_output_deduplicated`** (Function) — `tests/core/test_dataset_builder.py:416`
- **`test_synthetic_invalid_difficulty_normalized`** (Function) — `tests/core/test_dataset_builder.py:435`
- **`generate`** (Function) — `evolution/core/dataset_builder.py:159`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_synthetic_builder_same_seed_same_split` | Function | `tests/core/test_dataset_builder.py` | 125 |
| `test_invalid_examples_filtered_from_synthetic_output` | Function | `tests/core/test_dataset_builder.py` | 394 |
| `test_synthetic_output_deduplicated` | Function | `tests/core/test_dataset_builder.py` | 416 |
| `test_synthetic_invalid_difficulty_normalized` | Function | `tests/core/test_dataset_builder.py` | 435 |
| `generate` | Function | `evolution/core/dataset_builder.py` | 159 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_10 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_synthetic_builder_same_seed_same_split"})` — see callers and callees
2. `gitnexus_query({query: "cluster_13"})` — find related execution flows
3. Read key files listed above for implementation details
