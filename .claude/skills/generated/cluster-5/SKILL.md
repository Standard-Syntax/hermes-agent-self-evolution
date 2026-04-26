---
name: cluster-5
description: "Skill for the Cluster_5 area of hermes-agent-self-evolution. 6 symbols across 2 files."
---

# Cluster_5

6 symbols | 2 files | Cohesion: 91%

## When to Use

- Working with code in `tests/`
- Understanding how test_mipro_fallback_receives_valset, test_mipro_fallback_receives_both_trainset_and_valset, test_gepa_uses_max_metric_calls_from_config work
- Modifying cluster_5-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_optimizer.py` | test_mipro_fallback_receives_valset, test_mipro_fallback_receives_both_trainset_and_valset, test_gepa_uses_max_metric_calls_from_config |
| `evolution/core/optimizer.py` | _gepa_available, build_gepa_optimizer, compile_skill_module |

## Entry Points

Start here when exploring this area:

- **`test_mipro_fallback_receives_valset`** (Function) — `tests/core/test_optimizer.py:133`
- **`test_mipro_fallback_receives_both_trainset_and_valset`** (Function) — `tests/core/test_optimizer.py:176`
- **`test_gepa_uses_max_metric_calls_from_config`** (Function) — `tests/core/test_optimizer.py:216`
- **`build_gepa_optimizer`** (Function) — `evolution/core/optimizer.py:25`
- **`compile_skill_module`** (Function) — `evolution/core/optimizer.py:47`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_mipro_fallback_receives_valset` | Function | `tests/core/test_optimizer.py` | 133 |
| `test_mipro_fallback_receives_both_trainset_and_valset` | Function | `tests/core/test_optimizer.py` | 176 |
| `test_gepa_uses_max_metric_calls_from_config` | Function | `tests/core/test_optimizer.py` | 216 |
| `build_gepa_optimizer` | Function | `evolution/core/optimizer.py` | 25 |
| `compile_skill_module` | Function | `evolution/core/optimizer.py` | 47 |
| `_gepa_available` | Function | `evolution/core/optimizer.py` | 16 |

## How to Explore

1. `gitnexus_context({name: "test_mipro_fallback_receives_valset"})` — see callers and callees
2. `gitnexus_query({query: "cluster_5"})` — find related execution flows
3. Read key files listed above for implementation details
