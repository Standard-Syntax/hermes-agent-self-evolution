---
name: cluster-15
description: "Skill for the Cluster_15 area of hermes-agent-self-evolution. 14 symbols across 2 files."
---

# Cluster_15

14 symbols | 2 files | Cohesion: 87%

## When to Use

- Working with code in `tests/`
- Understanding how test_write_baseline_saves_and_reads_back, test_write_evolved_saves_and_reads_back, test_write_diff_produces_unified_diff work
- Modifying cluster_15-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_artifacts.py` | test_write_baseline_saves_and_reads_back, test_write_evolved_saves_and_reads_back, test_write_diff_produces_unified_diff, test_write_diff_produces_readable_patch_format, test_write_metrics_saves_valid_json (+3) |
| `evolution/core/artifacts.py` | write_baseline, write_evolved, write_diff, write_metrics, write_run_config (+1) |

## Entry Points

Start here when exploring this area:

- **`test_write_baseline_saves_and_reads_back`** (Function) — `tests/core/test_artifacts.py:37`
- **`test_write_evolved_saves_and_reads_back`** (Function) — `tests/core/test_artifacts.py:54`
- **`test_write_diff_produces_unified_diff`** (Function) — `tests/core/test_artifacts.py:71`
- **`test_write_diff_produces_readable_patch_format`** (Function) — `tests/core/test_artifacts.py:88`
- **`test_write_metrics_saves_valid_json`** (Function) — `tests/core/test_artifacts.py:113`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_write_baseline_saves_and_reads_back` | Function | `tests/core/test_artifacts.py` | 37 |
| `test_write_evolved_saves_and_reads_back` | Function | `tests/core/test_artifacts.py` | 54 |
| `test_write_diff_produces_unified_diff` | Function | `tests/core/test_artifacts.py` | 71 |
| `test_write_diff_produces_readable_patch_format` | Function | `tests/core/test_artifacts.py` | 88 |
| `test_write_metrics_saves_valid_json` | Function | `tests/core/test_artifacts.py` | 113 |
| `test_write_run_config_saves_json` | Function | `tests/core/test_artifacts.py` | 278 |
| `test_write_all_produces_all_eight_files` | Function | `tests/core/test_artifacts.py` | 596 |
| `test_write_all_baseline_and_evolved_are_correct_content` | Function | `tests/core/test_artifacts.py` | 660 |
| `write_baseline` | Function | `evolution/core/artifacts.py` | 15 |
| `write_evolved` | Function | `evolution/core/artifacts.py` | 19 |
| `write_diff` | Function | `evolution/core/artifacts.py` | 23 |
| `write_metrics` | Function | `evolution/core/artifacts.py` | 33 |
| `write_run_config` | Function | `evolution/core/artifacts.py` | 71 |
| `write_all` | Function | `evolution/core/artifacts.py` | 135 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_16 | 1 calls |
| Cluster_17 | 1 calls |
| Cluster_18 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_write_baseline_saves_and_reads_back"})` — see callers and callees
2. `gitnexus_query({query: "cluster_15"})` — find related execution flows
3. Read key files listed above for implementation details
