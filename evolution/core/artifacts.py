"""Artifact writer for Phase 1 evolution output bundle."""

import difflib
import json
from pathlib import Path

from evolution.core.config import EvolutionConfig


class ArtifactWriter:
    """Writes all Phase 1 evolution artifact files to an output directory."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def write_baseline(self, skill_raw: str) -> None:
        """Write baseline_skill.md."""
        (self.output_dir / "baseline_skill.md").write_text(skill_raw)

    def write_evolved(self, skill_raw: str) -> None:
        """Write evolved_skill.md."""
        (self.output_dir / "evolved_skill.md").write_text(skill_raw)

    def write_diff(self, baseline_raw: str, evolved_raw: str) -> None:
        """Write diff.patch as a unified diff."""
        diff_lines = difflib.unified_diff(
            baseline_raw.splitlines(keepends=True),
            evolved_raw.splitlines(keepends=True),
            fromfile="a/baseline_skill.md",
            tofile="b/evolved_skill.md",
        )
        (self.output_dir / "diff.patch").write_text("".join(diff_lines))

    def write_metrics(self, metrics: dict) -> None:
        """Write metrics.json."""
        (self.output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    def write_constraints(self, constraints_data: dict) -> None:
        """Write constraints.json, handling ConstraintResult objects."""
        serialized = self._serialize_constraints_data(constraints_data)
        (self.output_dir / "constraints.json").write_text(json.dumps(serialized, indent=2))

    def _serialize_constraints_data(self, constraints_data: dict) -> dict:
        """Serialize constraint data, converting ConstraintResult objects to dicts."""
        result = {}
        for key, value in constraints_data.items():
            if isinstance(value, list):
                result[key] = [self._serialize_constraint_item(item) for item in value]
            else:
                result[key] = value
        return result

    def _serialize_constraint_item(self, item) -> dict:
        """Serialize a single constraint item (dict or ConstraintResult)."""
        if hasattr(item, "passed"):  # ConstraintResult dataclass
            return {
                "passed": item.passed,
                "constraint_name": item.constraint_name,
                "message": item.message,
                "details": item.details,
            }
        return item  # already a dict

    def write_holdout_results(self, holdout_results: list[dict]) -> None:
        """Write holdout_results.jsonl (JSONL format)."""
        lines = [json.dumps(record) for record in holdout_results]
        content = "\n".join(lines)
        if content:
            content += "\n"
        (self.output_dir / "holdout_results.jsonl").write_text(content)

    def write_run_config(self, config: EvolutionConfig) -> None:
        """Write run_config.json with resolved config values."""
        # Use __dict__ to serialize public fields (exclude private/methods)
        config_dict = {
            k: v for k, v in config.__dict__.items() if not k.startswith("_")
        }
        # Path objects need to be converted to strings for JSON serialization
        for k, v in config_dict.items():
            if isinstance(v, Path):
                config_dict[k] = str(v)
        (self.output_dir / "run_config.json").write_text(json.dumps(config_dict, indent=2))

    def write_pr_summary(self, pr_summary_data: dict) -> None:
        """Write pr_summary.md from pr_summary_data dict."""
        content = self._build_pr_summary(pr_summary_data)
        (self.output_dir / "pr_summary.md").write_text(content)

    def _build_pr_summary(self, data: dict) -> str:
        """Build PR summary markdown from data dict."""
        skill_name = data.get("skill_name", "unknown")
        eval_source = data.get("eval_source", "unknown")
        train_count = data.get("train_count", 0)
        val_count = data.get("val_count", 0)
        holdout_count = data.get("holdout_count", 0)
        baseline_score = data.get("baseline_score", 0.0)
        evolved_score = data.get("evolved_score", 0.0)
        improvement = data.get("improvement", 0.0)
        improvement_pct = data.get("improvement_pct", 0.0)
        constraint_results_table = data.get("constraint_results_table", "")
        test_passed = data.get("test_passed", False)
        test_message = data.get("test_message", "")
        benchmark_passed = data.get("benchmark_passed", False)
        benchmark_regression = data.get("benchmark_regression", 0.0)

        lines = [
            f"# PR Summary — {skill_name}",
            "",
            "## Skill",
            f"- **Name**: {skill_name}",
            f"- **Dataset source**: {eval_source}",
            f"- **Train / Val / Holdout**: {train_count} / {val_count} / {holdout_count}",
            "",
            "## Results",
            f"- **Baseline holdout score**: {baseline_score:.3f}",
            f"- **Evolved holdout score**: {evolved_score:.3f}",
            f"- **Improvement**: {improvement:+.3f} ({improvement_pct:+.1f}%)",
            "",
            "## Constraints",
            constraint_results_table,
            "",
            "## Tests",
            f"- **Test suite**: {test_passed} ({test_message})",
            f"- **Benchmark**: {benchmark_passed} (regression: {benchmark_regression})",
            "",
            "## Human Review Checklist",
            "- [ ] Evolved skill body is sensibly different from baseline",
            "- [ ] Improvement is meaningful, not noise",
            "- [ ] Constraints all pass",
            "- [ ] Test suite passes (if --run-tests was used)",
            "- [ ] No secrets or sensitive content introduced",
            "- [ ] Skill remains usable by a human agent",
        ]
        return "\n".join(lines)

    def write_all(
        self,
        *,
        output_dir,
        skill_name,
        timestamp,
        baseline_raw,
        evolved_raw,
        metrics,
        constraints_data,
        holdout_results,
        config,
        pr_summary_data,
    ) -> None:
        """Write all artifact files. output_dir argument overrides self.output_dir."""
        original_output_dir = self.output_dir
        try:
            if output_dir is not None:
                self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.write_baseline(baseline_raw)
            self.write_evolved(evolved_raw)
            self.write_diff(baseline_raw, evolved_raw)
            self.write_metrics(metrics)
            self.write_constraints(constraints_data)
            self.write_holdout_results(holdout_results)
            self.write_run_config(config)
            self.write_pr_summary(pr_summary_data)
        finally:
            self.output_dir = original_output_dir
