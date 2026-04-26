---
name: cluster-22
description: "Skill for the Cluster_22 area of hermes-agent-self-evolution. 4 symbols across 2 files."
---

# Cluster_22

4 symbols | 2 files | Cohesion: 75%

## When to Use

- Working with code in `evolution/`
- Understanding how build_dataset_from_external, main, save work
- Modifying cluster_22-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `evolution/core/external_importers.py` | build_dataset_from_external, _load_skill_text, main |
| `evolution/core/dataset_builder.py` | save |

## Entry Points

Start here when exploring this area:

- **`build_dataset_from_external`** (Function) — `evolution/core/external_importers.py:605`
- **`main`** (Function) — `evolution/core/external_importers.py:742`
- **`save`** (Function) — `evolution/core/dataset_builder.py:53`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `build_dataset_from_external` | Function | `evolution/core/external_importers.py` | 605 |
| `main` | Function | `evolution/core/external_importers.py` | 742 |
| `save` | Function | `evolution/core/dataset_builder.py` | 53 |
| `_load_skill_text` | Function | `evolution/core/external_importers.py` | 695 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _is_relevant_to_skill` | cross_community | 4 |
| `Main → _parse_scoring_json` | cross_community | 4 |
| `Main → _validate_eval_example` | cross_community | 4 |
| `Main → Save` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_21 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "build_dataset_from_external"})` — see callers and callees
2. `gitnexus_query({query: "cluster_22"})` — find related execution flows
3. Read key files listed above for implementation details
