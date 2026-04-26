---
name: skills
description: "Skill for the Skills area of hermes-agent-self-evolution. 24 symbols across 4 files."
---

# Skills

24 symbols | 4 files | Cohesion: 61%

## When to Use

- Working with code in `tests/`
- Understanding how test_parses_frontmatter, test_parses_body, test_raw_contains_everything work
- Modifying skills-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/skills/test_skill_module.py` | test_parses_frontmatter, test_parses_body, test_raw_contains_everything, test_path_is_stored, test_roundtrip_load_evolve_reassemble (+7) |
| `evolution/core/constraints.py` | validate_all, _check_growth, _check_non_empty, validate_skill, _check_size (+2) |
| `evolution/skills/skill_module.py` | load_skill, reassemble_skill, find_skill |
| `evolution/skills/evolve_skill.py` | evolve, main |

## Entry Points

Start here when exploring this area:

- **`test_parses_frontmatter`** (Function) — `tests/skills/test_skill_module.py:32`
- **`test_parses_body`** (Function) — `tests/skills/test_skill_module.py:41`
- **`test_raw_contains_everything`** (Function) — `tests/skills/test_skill_module.py:50`
- **`test_path_is_stored`** (Function) — `tests/skills/test_skill_module.py:57`
- **`test_roundtrip_load_evolve_reassemble`** (Function) — `tests/skills/test_skill_module.py:184`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_parses_frontmatter` | Function | `tests/skills/test_skill_module.py` | 32 |
| `test_parses_body` | Function | `tests/skills/test_skill_module.py` | 41 |
| `test_raw_contains_everything` | Function | `tests/skills/test_skill_module.py` | 50 |
| `test_path_is_stored` | Function | `tests/skills/test_skill_module.py` | 57 |
| `test_roundtrip_load_evolve_reassemble` | Function | `tests/skills/test_skill_module.py` | 184 |
| `load_skill` | Function | `evolution/skills/skill_module.py` | 13 |
| `test_roundtrip` | Function | `tests/skills/test_skill_module.py` | 66 |
| `test_preserves_frontmatter` | Function | `tests/skills/test_skill_module.py` | 76 |
| `test_evolved_body_replaces_original` | Function | `tests/skills/test_skill_module.py` | 85 |
| `test_reassembled_skill_is_valid_full_skill` | Function | `tests/skills/test_skill_module.py` | 102 |
| `reassemble_skill` | Function | `evolution/skills/skill_module.py` | 115 |
| `test_reassembled_skill_passes_structure_check` | Function | `tests/skills/test_skill_module.py` | 116 |
| `test_body_only_fails_structure_validation` | Function | `tests/skills/test_skill_module.py` | 137 |
| `validate_all` | Function | `evolution/core/constraints.py` | 30 |
| `test_validate_skill_for_reassembled_flow` | Function | `tests/skills/test_skill_module.py` | 160 |
| `validate_skill` | Function | `evolution/core/constraints.py` | 55 |
| `find_skill` | Function | `evolution/skills/skill_module.py` | 56 |
| `evolve` | Function | `evolution/skills/evolve_skill.py` | 35 |
| `main` | Function | `evolution/skills/evolve_skill.py` | 502 |
| `run_test_suite` | Function | `evolution/core/constraints.py` | 83 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → From_dict` | cross_community | 5 |
| `Main → _validate_eval_example` | cross_community | 5 |
| `Main → _contains_secret` | cross_community | 5 |
| `Main → Get_hermes_agent_path` | cross_community | 4 |
| `Validate_skill → _check_size` | cross_community | 3 |
| `Validate_skill → _check_growth` | cross_community | 3 |
| `Validate_skill → _check_non_empty` | cross_community | 3 |
| `Validate_skill → _check_skill_structure` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_15 | 3 calls |
| Cluster_11 | 2 calls |
| Cluster_14 | 1 calls |
| Cluster_13 | 1 calls |
| Cluster_22 | 1 calls |
| Cluster_5 | 1 calls |
| Cluster_9 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_parses_frontmatter"})` — see callers and callees
2. `gitnexus_query({query: "skills"})` — find related execution flows
3. Read key files listed above for implementation details
