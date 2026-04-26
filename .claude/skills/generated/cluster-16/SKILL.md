---
name: cluster-16
description: "Skill for the Cluster_16 area of hermes-agent-self-evolution. 5 symbols across 2 files."
---

# Cluster_16

5 symbols | 2 files | Cohesion: 89%

## When to Use

- Working with code in `evolution/`
- Understanding how test_write_constraints_saves_valid_json, test_write_constraints_with_constraint_result_objects, write_constraints work
- Modifying cluster_16-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `evolution/core/artifacts.py` | write_constraints, _serialize_constraints_data, _serialize_constraint_item |
| `tests/core/test_artifacts.py` | test_write_constraints_saves_valid_json, test_write_constraints_with_constraint_result_objects |

## Entry Points

Start here when exploring this area:

- **`test_write_constraints_saves_valid_json`** (Function) — `tests/core/test_artifacts.py:138`
- **`test_write_constraints_with_constraint_result_objects`** (Function) — `tests/core/test_artifacts.py:173`
- **`write_constraints`** (Function) — `evolution/core/artifacts.py:37`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_write_constraints_saves_valid_json` | Function | `tests/core/test_artifacts.py` | 138 |
| `test_write_constraints_with_constraint_result_objects` | Function | `tests/core/test_artifacts.py` | 173 |
| `write_constraints` | Function | `evolution/core/artifacts.py` | 37 |
| `_serialize_constraints_data` | Function | `evolution/core/artifacts.py` | 42 |
| `_serialize_constraint_item` | Function | `evolution/core/artifacts.py` | 52 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Write_constraints → _serialize_constraint_item` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "test_write_constraints_saves_valid_json"})` — see callers and callees
2. `gitnexus_query({query: "cluster_16"})` — find related execution flows
3. Read key files listed above for implementation details
