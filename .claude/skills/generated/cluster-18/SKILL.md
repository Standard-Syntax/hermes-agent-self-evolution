---
name: cluster-18
description: "Skill for the Cluster_18 area of hermes-agent-self-evolution. 12 symbols across 2 files."
---

# Cluster_18

12 symbols | 2 files | Cohesion: 96%

## When to Use

- Working with code in `tests/`
- Understanding how test_write_pr_summary_saves_markdown, test_pr_summary_contains_skill_name, test_pr_summary_contains_dataset_source work
- Modifying cluster_18-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/core/test_artifacts.py` | test_write_pr_summary_saves_markdown, test_pr_summary_contains_skill_name, test_pr_summary_contains_dataset_source, test_pr_summary_contains_train_val_holdout_counts, test_pr_summary_contains_baseline_and_evolved_scores (+5) |
| `evolution/core/artifacts.py` | write_pr_summary, _build_pr_summary |

## Entry Points

Start here when exploring this area:

- **`test_write_pr_summary_saves_markdown`** (Function) — `tests/core/test_artifacts.py:306`
- **`test_pr_summary_contains_skill_name`** (Function) — `tests/core/test_artifacts.py:336`
- **`test_pr_summary_contains_dataset_source`** (Function) — `tests/core/test_artifacts.py:364`
- **`test_pr_summary_contains_train_val_holdout_counts`** (Function) — `tests/core/test_artifacts.py:392`
- **`test_pr_summary_contains_baseline_and_evolved_scores`** (Function) — `tests/core/test_artifacts.py:421`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_write_pr_summary_saves_markdown` | Function | `tests/core/test_artifacts.py` | 306 |
| `test_pr_summary_contains_skill_name` | Function | `tests/core/test_artifacts.py` | 336 |
| `test_pr_summary_contains_dataset_source` | Function | `tests/core/test_artifacts.py` | 364 |
| `test_pr_summary_contains_train_val_holdout_counts` | Function | `tests/core/test_artifacts.py` | 392 |
| `test_pr_summary_contains_baseline_and_evolved_scores` | Function | `tests/core/test_artifacts.py` | 421 |
| `test_pr_summary_contains_improvement_percent` | Function | `tests/core/test_artifacts.py` | 450 |
| `test_pr_summary_contains_constraint_results` | Function | `tests/core/test_artifacts.py` | 478 |
| `test_pr_summary_contains_test_results` | Function | `tests/core/test_artifacts.py` | 507 |
| `test_pr_summary_contains_benchmark_results` | Function | `tests/core/test_artifacts.py` | 535 |
| `test_pr_summary_contains_human_review_checklist` | Function | `tests/core/test_artifacts.py` | 563 |
| `write_pr_summary` | Function | `evolution/core/artifacts.py` | 83 |
| `_build_pr_summary` | Function | `evolution/core/artifacts.py` | 88 |

## How to Explore

1. `gitnexus_context({name: "test_write_pr_summary_saves_markdown"})` — see callers and callees
2. `gitnexus_query({query: "cluster_18"})` — find related execution flows
3. Read key files listed above for implementation details
