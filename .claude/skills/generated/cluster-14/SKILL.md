---
name: cluster-14
description: "Skill for the Cluster_14 area of hermes-agent-self-evolution. 5 symbols across 2 files."
---

# Cluster_14

5 symbols | 2 files | Cohesion: 89%

## When to Use

- Working with code in `tests/`
- Understanding how test_resolve_hermes_agent_path_returns_set_path, test_resolve_hermes_agent_path_discovers_from_env, test_resolve_hermes_agent_path_raises_when_not_found work
- Modifying cluster_14-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_config.py` | test_resolve_hermes_agent_path_returns_set_path, test_resolve_hermes_agent_path_discovers_from_env, test_resolve_hermes_agent_path_raises_when_not_found |
| `evolution/core/config.py` | resolve_hermes_agent_path, get_hermes_agent_path |

## Entry Points

Start here when exploring this area:

- **`test_resolve_hermes_agent_path_returns_set_path`** (Function) — `tests/core/test_config.py:19`
- **`test_resolve_hermes_agent_path_discovers_from_env`** (Function) — `tests/core/test_config.py:25`
- **`test_resolve_hermes_agent_path_raises_when_not_found`** (Function) — `tests/core/test_config.py:30`
- **`resolve_hermes_agent_path`** (Function) — `evolution/core/config.py:50`
- **`get_hermes_agent_path`** (Function) — `evolution/core/config.py:61`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_resolve_hermes_agent_path_returns_set_path` | Function | `tests/core/test_config.py` | 19 |
| `test_resolve_hermes_agent_path_discovers_from_env` | Function | `tests/core/test_config.py` | 25 |
| `test_resolve_hermes_agent_path_raises_when_not_found` | Function | `tests/core/test_config.py` | 30 |
| `resolve_hermes_agent_path` | Function | `evolution/core/config.py` | 50 |
| `get_hermes_agent_path` | Function | `evolution/core/config.py` | 61 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → Get_hermes_agent_path` | cross_community | 4 |

## How to Explore

1. `gitnexus_context({name: "test_resolve_hermes_agent_path_returns_set_path"})` — see callers and callees
2. `gitnexus_query({query: "cluster_14"})` — find related execution flows
3. Read key files listed above for implementation details
