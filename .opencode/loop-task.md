# Task
Slice P1-008 — Add output artifacts and PR-ready summary

## Description
Create a dedicated `ArtifactWriter` in `evolution/core/artifacts.py` and wire it into `evolve_skill.py` so all Phase 1 runs produce a complete, reviewable artifact bundle.

## Required artifacts
| File | Description |
|------|-------------|
| `baseline_skill.md` | Full baseline SKILL.md |
| `evolved_skill.md` | Full evolved SKILL.md |
| `diff.patch` | Unified diff of baseline→evolved |
| `metrics.json` | All numeric results + optimizer metadata |
| `constraints.json` | Baseline/evolved constraint results + test/benchmark results |
| `holdout_results.jsonl` | One JSON line per holdout example with scores + feedback |
| `run_config.json` | Full EvolutionConfig snapshot (resolved values) |
| `pr_summary.md` | Human-reviewable summary (skill name, dataset source, train/val/holdout counts, baseline/evolved scores, improvement %, constraint results, test results, benchmark results if available, human review checklist) |

## `ArtifactWriter` interface
```python
class ArtifactWriter:
    def __init__(self, output_dir: Path): ...

    def write_baseline(self, skill_raw: str) -> None: ...
    def write_evolved(self, skill_raw: str) -> None: ...
    def write_diff(self, baseline_raw: str, evolved_raw: str) -> None: ...
    def write_metrics(self, metrics: dict) -> None: ...
    def write_constraints(self, constraints_data: dict) -> None: ...
    def write_holdout_results(self, holdout_results: list[dict]) -> None: ...
    def write_run_config(self, config: EvolutionConfig) -> None: ...
    def write_pr_summary(self, pr_summary_data: dict) -> None: ...
    def write_all(self, *, output_dir, skill_name, timestamp, baseline_raw, evolved_raw, metrics, constraints_data, holdout_results, config, pr_summary_data) -> None: ...
```

## `pr_summary.md` template
```markdown
# PR Summary — {skill_name}

## Skill
- **Name**: {skill_name}
- **Dataset source**: {eval_source}
- **Train / Val / Holdout**: {train_count} / {val_count} / {holdout_count}

## Results
- **Baseline holdout score**: {baseline_score:.3f}
- **Evolved holdout score**: {evolved_score:.3f}
- **Improvement**: {improvement:+.3f} ({improvement_pct:+.1f}%)

## Constraints
{constraint_results_table}

## Tests
- **Test suite**: {test_passed} ({test_message})
- **Benchmark**: {benchmark_passed} (regression: {benchmark_regression})

## Human Review Checklist
- [ ] Evolved skill body is sensibly different from baseline
- [ ] Improvement is meaningful, not noise
- [ ] Constraints all pass
- [ ] Test suite passes (if --run-tests was used)
- [ ] No secrets or sensitive content introduced
- [ ] Skill remains usable by a human agent
```

## Changes to `evolve_skill.py`
- Replace inline artifact-writing code (lines ~333-411) with calls to `ArtifactWriter`
- `holdout_results.jsonl` must be written with all per-example judge feedback
- `diff.patch` must be a proper unified diff

## Acceptance criteria
- [ ] `ArtifactWriter` class exists in `evolution/core/artifacts.py`
- [ ] `ArtifactWriter.write_all()` produces all 8 artifact files
- [ ] `diff.patch` is a valid unified diff (readable by `patch -p1`)
- [ ] `holdout_results.jsonl` contains all per-example results from holdout evaluation
- [ ] `pr_summary.md` contains all fields in the template
- [ ] `evolve_skill.py` uses `ArtifactWriter` instead of inline file writes
- [ ] `tests/core/test_artifacts.py` covers all `ArtifactWriter` methods
- [ ] `uv run pytest tests/core/test_artifacts.py -q` passes
- [ ] `uv run ruff check evolution/core/artifacts.py` passes
- [ ] `uv run ty check evolution/core/artifacts.py` passes

## Files to create/modify
- `evolution/core/artifacts.py` (create)
- `evolution/skills/evolve_skill.py` (modify)
- `tests/core/test_artifacts.py` (create)

## Code context
`evolve_skill.py` currently writes artifacts inline (lines 333-411). The constraint data structure uses `ConstraintResult` dataclass (passed, constraint_name, message, details). Holdout results come from `run_holdout_evaluation()` which returns dicts with task_input, baseline_output, evolved_output, baseline_score, evolved_score, judge_feedback.