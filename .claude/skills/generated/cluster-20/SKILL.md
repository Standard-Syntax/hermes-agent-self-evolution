---
name: cluster-20
description: "Skill for the Cluster_20 area of hermes-agent-self-evolution. 6 symbols across 1 files."
---

# Cluster_20

6 symbols | 1 files | Cohesion: 91%

## When to Use

- Working with code in `evolution/`
- Understanding how extract_messages, extract_messages, extract_messages work
- Modifying cluster_20-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `evolution/core/external_importers.py` | _contains_secret, extract_messages, extract_messages, _read_copilot_workspace, _parse_copilot_events (+1) |

## Entry Points

Start here when exploring this area:

- **`extract_messages`** (Function) — `evolution/core/external_importers.py:167`
- **`extract_messages`** (Function) — `evolution/core/external_importers.py:224`
- **`extract_messages`** (Function) — `evolution/core/external_importers.py:348`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `extract_messages` | Function | `evolution/core/external_importers.py` | 167 |
| `extract_messages` | Function | `evolution/core/external_importers.py` | 224 |
| `extract_messages` | Function | `evolution/core/external_importers.py` | 348 |
| `_contains_secret` | Function | `evolution/core/external_importers.py` | 77 |
| `_read_copilot_workspace` | Function | `evolution/core/external_importers.py` | 259 |
| `_parse_copilot_events` | Function | `evolution/core/external_importers.py` | 272 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _contains_secret` | cross_community | 5 |
| `Extract_messages → _contains_secret` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "extract_messages"})` — see callers and callees
2. `gitnexus_query({query: "cluster_20"})` — find related execution flows
3. Read key files listed above for implementation details
