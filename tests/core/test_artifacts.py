"""Tests for ArtifactWriter — Phase 1 artifact bundle writer.

These tests verify that ArtifactWriter produces all required artifacts:
- baseline_skill.md, evolved_skill.md
- diff.patch (unified diff)
- metrics.json
- constraints.json
- holdout_results.jsonl
- run_config.json
- pr_summary.md
"""

import json
import tempfile
from pathlib import Path


from evolution.core.config import EvolutionConfig
from evolution.core.constraints import ConstraintResult


class TestArtifactWriterInstantiation:
    """Test that ArtifactWriter can be instantiated."""

    def test_instantiate_with_path(self):
        """ArtifactWriter takes a Path as output_dir."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            assert writer is not None
            assert hasattr(writer, "output_dir")


class TestWriteBaseline:
    """Test write_baseline() saves baseline skill markdown."""

    def test_write_baseline_saves_and_reads_back(self):
        """write_baseline writes baseline_skill.md and it can be read back."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            skill_content = "# Baseline Skill\n\nSome content here."
            writer.write_baseline(skill_content)

            output_path = Path(tmpdir) / "baseline_skill.md"
            assert output_path.exists(), "baseline_skill.md should be created"
            assert output_path.read_text() == skill_content


class TestWriteEvolved:
    """Test write_evolved() saves evolved skill markdown."""

    def test_write_evolved_saves_and_reads_back(self):
        """write_evolved writes evolved_skill.md and it can be read back."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            skill_content = "# Evolved Skill\n\nImproved content."
            writer.write_evolved(skill_content)

            output_path = Path(tmpdir) / "evolved_skill.md"
            assert output_path.exists(), "evolved_skill.md should be created"
            assert output_path.read_text() == skill_content


class TestWriteDiff:
    """Test write_diff() produces a valid unified diff."""

    def test_write_diff_produces_unified_diff(self):
        """write_diff produces a file starting with ---/+++ markers."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            baseline = "line one\nline two\nline three\n"
            evolved = "line one\nline two modified\nline three\n"
            writer.write_diff(baseline, evolved)

            output_path = Path(tmpdir) / "diff.patch"
            assert output_path.exists(), "diff.patch should be created"
            content = output_path.read_text()
            # Unified diff must start with --- and +++
            assert content.startswith("---"), "Diff should start with '---'"
            assert "+++" in content, "Diff should contain '+++' markers"

    def test_write_diff_produces_readable_patch_format(self):
        """diff.patch is readable by patch -p1 (proper unified diff)."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            baseline = "original line\n" * 5
            evolved = "original line\nmodified line\n" * 5
            writer.write_diff(baseline, evolved)

            output_path = Path(tmpdir) / "diff.patch"
            content = output_path.read_text()
            # Should have proper unified diff headers
            lines = content.splitlines()
            assert any(line.startswith("--- a/") for line in lines), (
                "Diff should use '--- a/' style header"
            )
            assert any(line.startswith("+++ b/") for line in lines), (
                "Diff should use '+++ b/' style header"
            )


class TestWriteMetrics:
    """Test write_metrics() saves numeric results as JSON."""

    def test_write_metrics_saves_valid_json(self):
        """write_metrics writes metrics.json that parses back correctly."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            metrics = {
                "baseline_score": 0.65,
                "evolved_score": 0.78,
                "improvement": 0.13,
                "optimizer_metadata": {"model": "openai/gpt-4.1", "calls": 42},
            }
            writer.write_metrics(metrics)

            output_path = Path(tmpdir) / "metrics.json"
            assert output_path.exists(), "metrics.json should be created"
            parsed = json.loads(output_path.read_text())
            assert parsed["baseline_score"] == 0.65
            assert parsed["evolved_score"] == 0.78
            assert parsed["improvement"] == 0.13


class TestWriteConstraints:
    """Test write_constraints() saves constraint results as JSON."""

    def test_write_constraints_saves_valid_json(self):
        """write_constraints writes constraints.json that parses back correctly."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            constraints_data = {
                "baseline_results": [
                    {
                        "passed": True,
                        "constraint_name": "size_limit",
                        "message": "OK",
                        "details": None,
                    }
                ],
                "evolved_results": [
                    {
                        "passed": True,
                        "constraint_name": "size_limit",
                        "message": "OK",
                        "details": None,
                    }
                ],
                "test_passed": True,
                "benchmark_passed": True,
            }
            writer.write_constraints(constraints_data)

            output_path = Path(tmpdir) / "constraints.json"
            assert output_path.exists(), "constraints.json should be created"
            parsed = json.loads(output_path.read_text())
            assert "baseline_results" in parsed
            assert "evolved_results" in parsed
            assert isinstance(parsed["baseline_results"], list)

    def test_write_constraints_with_constraint_result_objects(self):
        """write_constraints handles ConstraintResult dataclass objects."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            baseline_results = [
                ConstraintResult(passed=True, constraint_name="size_limit", message="OK", details=None)
            ]
            evolved_results = [
                ConstraintResult(
                    passed=True,
                    constraint_name="growth_limit",
                    message="Within limit",
                    details="10% growth",
                )
            ]
            writer.write_constraints({
                "baseline_results": baseline_results,
                "evolved_results": evolved_results,
                "test_passed": True,
                "benchmark_passed": True,
            })

            output_path = Path(tmpdir) / "constraints.json"
            parsed = json.loads(output_path.read_text())
            assert parsed["evolved_results"][0]["constraint_name"] == "growth_limit"
            assert parsed["evolved_results"][0]["details"] == "10% growth"


class TestWriteHoldoutResults:
    """Test write_holdout_results() saves valid JSONL."""

    def test_write_holdout_results_saves_multiple_lines(self):
        """write_holdout_results writes multiple JSON lines (one per example)."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            holdout_results = [
                {
                    "task_input": "input1",
                    "baseline_output": "baseline_out1",
                    "evolved_output": "evolved_out1",
                    "baseline_score": 0.6,
                    "evolved_score": 0.75,
                    "judge_feedback": "Evolved is better.",
                },
                {
                    "task_input": "input2",
                    "baseline_output": "baseline_out2",
                    "evolved_output": "evolved_out2",
                    "baseline_score": 0.5,
                    "evolved_score": 0.55,
                    "judge_feedback": "Slight improvement.",
                },
            ]
            writer.write_holdout_results(holdout_results)

            output_path = Path(tmpdir) / "holdout_results.jsonl"
            assert output_path.exists(), "holdout_results.jsonl should be created"
            lines = output_path.read_text().strip().splitlines()
            assert len(lines) == 2, "Should have one line per holdout example"

    def test_write_holdout_results_each_line_is_valid_json(self):
        """Each line in holdout_results.jsonl is parseable as JSON."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            holdout_results = [
                {
                    "task_input": "test input",
                    "baseline_output": "baseline output",
                    "evolved_output": "evolved output",
                    "baseline_score": 0.7,
                    "evolved_score": 0.8,
                    "judge_feedback": "Good improvement.",
                }
            ]
            writer.write_holdout_results(holdout_results)

            output_path = Path(tmpdir) / "holdout_results.jsonl"
            for line in output_path.read_text().strip().splitlines():
                parsed = json.loads(line)
                assert "baseline_score" in parsed
                assert "evolved_score" in parsed

    def test_write_holdout_results_empty_list(self):
        """write_holdout_results with [] produces a valid empty JSONL file."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            writer.write_holdout_results([])

            output_path = Path(tmpdir) / "holdout_results.jsonl"
            assert output_path.exists()
            content = output_path.read_text()
            assert content.strip() == "", "Empty list should produce empty (or blank) file"


class TestWriteRunConfig:
    """Test write_run_config() saves a config snapshot as JSON."""

    def test_write_run_config_saves_json(self):
        """write_run_config writes run_config.json with resolved config values."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            config = EvolutionConfig(
                iterations=20,
                max_metric_calls=300,
                optimizer_model="openai/gpt-4.1",
                eval_model="openai/gpt-4.1-mini",
                judge_model="openai/gpt-4.1",
                run_pytest=True,
                seed=123,
            )
            writer.write_run_config(config)

            output_path = Path(tmpdir) / "run_config.json"
            assert output_path.exists(), "run_config.json should be created"
            parsed = json.loads(output_path.read_text())
            assert parsed["iterations"] == 20
            assert parsed["max_metric_calls"] == 300
            assert parsed["seed"] == 123


class TestWritePrSummary:
    """Test write_pr_summary() saves a human-readable markdown summary."""

    def test_write_pr_summary_saves_markdown(self):
        """write_pr_summary writes pr_summary.md."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test-skill",
                "eval_source": "synthetic",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.650,
                "evolved_score": 0.780,
                "improvement": 0.130,
                "improvement_pct": 20.0,
                "constraint_results_table": "| Constraint | Status |\n|---|---|\n| size_limit | PASS |",
                "test_passed": True,
                "test_message": "All tests passed",
                "benchmark_passed": True,
                "benchmark_regression": 0.01,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            assert output_path.exists(), "pr_summary.md should be created"
            content = output_path.read_text()
            assert "test-skill" in content
            assert "synthetic" in content

    def test_pr_summary_contains_skill_name(self):
        """pr_summary.md contains the skill name."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "my-awesome-skill",
                "eval_source": "dataset_v1",
                "train_count": 8,
                "val_count": 4,
                "holdout_count": 4,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "| Constraint | Status |\n|---|---|\n| size | PASS |",
                "test_passed": True,
                "test_message": "OK",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "my-awesome-skill" in content

    def test_pr_summary_contains_dataset_source(self):
        """pr_summary.md contains the dataset source."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "production_logs_2025",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "",
                "test_passed": False,
                "test_message": "1 failed",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "production_logs_2025" in content

    def test_pr_summary_contains_train_val_holdout_counts(self):
        """pr_summary.md shows train / val / holdout split counts."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 20,
                "val_count": 10,
                "holdout_count": 10,
                "baseline_score": 0.5,
                "evolved_score": 0.7,
                "improvement": 0.2,
                "improvement_pct": 40.0,
                "constraint_results_table": "",
                "test_passed": True,
                "test_message": "All pass",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "20" in content and "10" in content
            assert "Train / Val / Holdout" in content

    def test_pr_summary_contains_baseline_and_evolved_scores(self):
        """pr_summary.md shows both baseline and evolved holdout scores."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.600,
                "evolved_score": 0.750,
                "improvement": 0.150,
                "improvement_pct": 25.0,
                "constraint_results_table": "",
                "test_passed": True,
                "test_message": "OK",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "0.600" in content or "0.6" in content
            assert "0.750" in content or "0.75" in content

    def test_pr_summary_contains_improvement_percent(self):
        """pr_summary.md shows improvement percentage."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.7,
                "improvement": 0.2,
                "improvement_pct": 40.0,
                "constraint_results_table": "",
                "test_passed": True,
                "test_message": "OK",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "+40.0%" in content or "40.0%" in content

    def test_pr_summary_contains_constraint_results(self):
        """pr_summary.md contains constraint results table."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "| Constraint | Status |\n|---|---|\n| size_limit | PASS |\n| growth_limit | PASS |",
                "test_passed": True,
                "test_message": "OK",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "size_limit" in content
            assert "growth_limit" in content

    def test_pr_summary_contains_test_results(self):
        """pr_summary.md shows test suite pass/fail status."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "",
                "test_passed": False,
                "test_message": "1 failed, 3 passed",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "test_passed" in content.lower() or "failed" in content.lower()

    def test_pr_summary_contains_benchmark_results(self):
        """pr_summary.md shows benchmark regression status."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "",
                "test_passed": True,
                "test_message": "All pass",
                "benchmark_passed": True,
                "benchmark_regression": 0.01,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "benchmark" in content.lower()

    def test_pr_summary_contains_human_review_checklist(self):
        """pr_summary.md contains the human review checklist."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            pr_summary_data = {
                "skill_name": "test",
                "eval_source": "src",
                "train_count": 10,
                "val_count": 5,
                "holdout_count": 5,
                "baseline_score": 0.5,
                "evolved_score": 0.6,
                "improvement": 0.1,
                "improvement_pct": 20.0,
                "constraint_results_table": "",
                "test_passed": True,
                "test_message": "OK",
                "benchmark_passed": True,
                "benchmark_regression": 0.0,
            }
            writer.write_pr_summary(pr_summary_data)

            output_path = Path(tmpdir) / "pr_summary.md"
            content = output_path.read_text()
            assert "Human Review Checklist" in content or "Human Review" in content
            assert "- [" in content and "- [" in content  # markdown checkboxes


class TestWriteAll:
    """Test write_all() produces all artifact files."""

    def test_write_all_produces_all_eight_files(self):
        """write_all() creates all 8 artifact files."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            config = EvolutionConfig(iterations=5, seed=99)
            holdout_results = [
                {
                    "task_input": "input",
                    "baseline_output": "baseline",
                    "evolved_output": "evolved",
                    "baseline_score": 0.5,
                    "evolved_score": 0.6,
                    "judge_feedback": "OK",
                }
            ]
            writer.write_all(
                output_dir=Path(tmpdir),
                skill_name="all-test-skill",
                timestamp="2025-01-01T00:00:00",
                baseline_raw="# Baseline",
                evolved_raw="# Evolved",
                metrics={"baseline_score": 0.5, "evolved_score": 0.6},
                constraints_data={
                    "baseline_results": [],
                    "evolved_results": [],
                    "test_passed": True,
                    "benchmark_passed": True,
                },
                holdout_results=holdout_results,
                config=config,
                pr_summary_data={
                    "skill_name": "all-test-skill",
                    "eval_source": "test",
                    "train_count": 10,
                    "val_count": 5,
                    "holdout_count": 5,
                    "baseline_score": 0.5,
                    "evolved_score": 0.6,
                    "improvement": 0.1,
                    "improvement_pct": 20.0,
                    "constraint_results_table": "",
                    "test_passed": True,
                    "test_message": "OK",
                    "benchmark_passed": True,
                    "benchmark_regression": 0.0,
                },
            )

            expected_files = [
                "baseline_skill.md",
                "evolved_skill.md",
                "diff.patch",
                "metrics.json",
                "constraints.json",
                "holdout_results.jsonl",
                "run_config.json",
                "pr_summary.md",
            ]
            for fname in expected_files:
                path = Path(tmpdir) / fname
                assert path.exists(), f"{fname} should be created by write_all()"

    def test_write_all_baseline_and_evolved_are_correct_content(self):
        """write_all saves correct baseline and evolved content."""
        from evolution.core.artifacts import ArtifactWriter

        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ArtifactWriter(Path(tmpdir))
            config = EvolutionConfig()
            writer.write_all(
                output_dir=Path(tmpdir),
                skill_name="content-test",
                timestamp="2025-01-01",
                baseline_raw="# Baseline Content",
                evolved_raw="# Evolved Content",
                metrics={},
                constraints_data={
                    "baseline_results": [],
                    "evolved_results": [],
                    "test_passed": True,
                    "benchmark_passed": True,
                },
                holdout_results=[],
                config=config,
                pr_summary_data={
                    "skill_name": "content-test",
                    "eval_source": "src",
                    "train_count": 5,
                    "val_count": 2,
                    "holdout_count": 2,
                    "baseline_score": 0.5,
                    "evolved_score": 0.5,
                    "improvement": 0.0,
                    "improvement_pct": 0.0,
                    "constraint_results_table": "",
                    "test_passed": True,
                    "test_message": "OK",
                    "benchmark_passed": True,
                    "benchmark_regression": 0.0,
                },
            )

            baseline_content = (Path(tmpdir) / "baseline_skill.md").read_text()
            evolved_content = (Path(tmpdir) / "evolved_skill.md").read_text()
            assert baseline_content == "# Baseline Content"
            assert evolved_content == "# Evolved Content"
