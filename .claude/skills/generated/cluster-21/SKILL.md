---
name: cluster-21
description: "Skill for the Cluster_21 area of hermes-agent-self-evolution. 4 symbols across 1 files."
---

# Cluster_21

4 symbols | 1 files | Cohesion: 75%

## When to Use

- Working with code in `evolution/`
- Understanding how filter_and_score work
- Modifying cluster_21-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `evolution/core/external_importers.py` | _validate_eval_example, _is_relevant_to_skill, filter_and_score, _parse_scoring_json |

## Entry Points

Start here when exploring this area:

- **`filter_and_score`** (Function) — `evolution/core/external_importers.py:448`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `filter_and_score` | Function | `evolution/core/external_importers.py` | 448 |
| `_validate_eval_example` | Function | `evolution/core/external_importers.py` | 82 |
| `_is_relevant_to_skill` | Function | `evolution/core/external_importers.py` | 120 |
| `_parse_scoring_json` | Function | `evolution/core/external_importers.py` | 545 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _validate_eval_example` | cross_community | 5 |
| `Main → _is_relevant_to_skill` | cross_community | 4 |
| `Main → _parse_scoring_json` | cross_community | 4 |
| `Main → _validate_eval_example` | cross_community | 4 |

## How to Explore

1. `gitnexus_context({name: "filter_and_score"})` — see callers and callees
2. `gitnexus_query({query: "cluster_21"})` — find related execution flows
3. Read key files listed above for implementation details
