---
name: cluster-10
description: "Skill for the Cluster_10 area of hermes-agent-self-evolution. 15 symbols across 2 files."
---

# Cluster_10

15 symbols | 2 files | Cohesion: 75%

## When to Use

- Working with code in `tests/`
- Understanding how make_example, test_valid_example_passes_through, test_empty_task_input_is_dropped work
- Modifying cluster_10-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_dataset_builder.py` | make_example, test_valid_example_passes_through, test_empty_task_input_is_dropped, test_whitespace_only_task_input_is_dropped, test_empty_expected_behavior_is_dropped (+9) |
| `evolution/core/dataset_builder.py` | validate_examples |

## Entry Points

Start here when exploring this area:

- **`make_example`** (Function) — `tests/core/test_dataset_builder.py:34`
- **`test_valid_example_passes_through`** (Function) — `tests/core/test_dataset_builder.py:171`
- **`test_empty_task_input_is_dropped`** (Function) — `tests/core/test_dataset_builder.py:186`
- **`test_whitespace_only_task_input_is_dropped`** (Function) — `tests/core/test_dataset_builder.py:197`
- **`test_empty_expected_behavior_is_dropped`** (Function) — `tests/core/test_dataset_builder.py:208`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `make_example` | Function | `tests/core/test_dataset_builder.py` | 34 |
| `test_valid_example_passes_through` | Function | `tests/core/test_dataset_builder.py` | 171 |
| `test_empty_task_input_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 186 |
| `test_whitespace_only_task_input_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 197 |
| `test_empty_expected_behavior_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 208 |
| `test_whitespace_only_expected_behavior_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 219 |
| `test_invalid_difficulty_normalized_to_medium` | Function | `tests/core/test_dataset_builder.py` | 229 |
| `test_valid_difficulty_preserved` | Function | `tests/core/test_dataset_builder.py` | 242 |
| `test_empty_category_defaults_to_general` | Function | `tests/core/test_dataset_builder.py` | 254 |
| `test_task_input_with_secret_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 266 |
| `test_expected_behavior_with_secret_is_dropped` | Function | `tests/core/test_dataset_builder.py` | 277 |
| `test_all_invalid_examples_returns_empty_list` | Function | `tests/core/test_dataset_builder.py` | 288 |
| `test_duplicate_task_inputs_deduplicated` | Function | `tests/core/test_dataset_builder.py` | 306 |
| `test_first_occurrence_kept_not_last` | Function | `tests/core/test_dataset_builder.py` | 319 |
| `validate_examples` | Function | `evolution/core/dataset_builder.py` | 88 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _validate_eval_example` | cross_community | 5 |
| `Main → _contains_secret` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_21 | 1 calls |
| Cluster_20 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "make_example"})` — see callers and callees
2. `gitnexus_query({query: "cluster_10"})` — find related execution flows
3. Read key files listed above for implementation details
