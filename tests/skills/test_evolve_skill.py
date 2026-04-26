"""Tests for the GEPA optimizer adapter in evolution.core.optimizer.

These tests verify:
1. build_gepa_optimizer() creates GEPA with correct DSPy API (max_metric_calls, reflection_lm)
2. compile_skill_module() returns (module, fallback_used) tuple
3. Metrics are properly recorded including optimizer_fallback_used
"""

from pathlib import Path
from unittest import mock

import dspy
import pytest

from evolution.core.config import EvolutionConfig
from evolution.core.dataset_builder import EvalDataset, EvalExample
from evolution.skills.skill_module import SkillModule


# Sample skill for testing
SAMPLE_BODY = "# Sample Skill\n\nDo the thing."
SAMPLE_FRONTMATTER = "name: test-skill\ndescription: A test skill"


class MockOptimizedModule:
    """Mock optimized module that simulates GEPA's mutation."""

    def __init__(self, original_module: SkillModule, mutated_skill_text: str):
        for attr in dir(original_module):
            if not attr.startswith("_"):
                try:
                    setattr(self, attr, getattr(original_module, attr))
                except AttributeError:
                    pass
        self.skill_text = mutated_skill_text

    def forward(self, task_input: str):
        return dspy.Prediction(output="mock output")


class MockGEPA:
    """Mock GEPA optimizer that mirrors the real GEPA API."""

    def __init__(
        self,
        metric,
        *,
        auto=None,
        max_metric_calls=None,
        max_full_evals=None,
        reflection_lm=None,
    ):
        self.metric = metric
        self.auto = auto
        self.max_metric_calls = max_metric_calls
        self.max_full_evals = max_full_evals
        self.reflection_lm = reflection_lm

    def compile(self, module, *, trainset=None, valset=None):
        return MockOptimizedModule(module, module.skill_text + "\n\n[OPTIMIZED]")


class MockMIPROv2:
    """Mock MIPROv2 optimizer for fallback testing."""

    def __init__(self, metric, *, auto=None):
        self.metric = metric
        self.auto = auto

    def compile(self, module, *, trainset=None, valset=None):
        return MockOptimizedModule(module, module.skill_text + "\n\n[MIPRO_FALLBACK]")


class TestBuildGepaOptimizer:
    """Tests for build_gepa_optimizer() function."""

    def test_build_gepa_optimizer_uses_max_metric_calls(self):
        """GEPA must be created with max_metric_calls, NOT max_steps.

        The bug: evolve_skill.py uses max_steps which is not a valid GEPA parameter.
        Valid budget parameters are: auto, max_full_evals, OR max_metric_calls (exactly one).
        """
        from evolution.core.optimizer import build_gepa_optimizer

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        with mock.patch.object(dspy, "GEPA", MockGEPA):
            with mock.patch.object(dspy, "LM", return_value=mock.MagicMock()):
                optimizer = build_gepa_optimizer(config)

                # Inspect the actual optimizer instance attributes, not mock call metadata
                assert optimizer.max_metric_calls == 150, (
                    f"Expected max_metric_calls=150, got {optimizer.max_metric_calls}"
                )
                assert optimizer.auto is None, (
                    "auto should be None when max_metric_calls is specified"
                )

    def test_build_gepa_optimizer_sets_reflection_lm(self):
        """GEPA requires reflection_lm parameter for reflective analysis."""
        from evolution.core.optimizer import build_gepa_optimizer

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        with mock.patch.object(dspy, "GEPA", MockGEPA):
            with mock.patch.object(dspy, "LM", return_value=mock.MagicMock()) as mock_lm:
                optimizer = build_gepa_optimizer(config)

                # Inspect the actual optimizer instance for reflection_lm
                assert optimizer.reflection_lm is not None, (
                    "GEPA must have reflection_lm set"
                )
                # Verify dspy.LM was called with the optimizer model
                mock_lm.assert_called_once_with("openai/gpt-4.1")

    def test_build_gepa_optimizer_rejects_multiple_budget_params(self):
        """GEPA requires exactly ONE of: auto, max_full_evals, or max_metric_calls.

        This test verifies the API is used correctly - we should only pass one.
        """
        from evolution.core.optimizer import build_gepa_optimizer

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        with mock.patch.object(dspy, "GEPA", MockGEPA):
            with mock.patch.object(dspy, "LM", return_value=mock.MagicMock()):
                optimizer = build_gepa_optimizer(config)

                # Inspect actual optimizer instance to verify only one budget param is set
                assert optimizer.max_metric_calls is not None
                assert optimizer.auto is None
                assert optimizer.max_full_evals is None


class TestCompileSkillModule:
    """Tests for compile_skill_module() function."""

    def test_returns_tuple_with_fallback_used_false(self):
        """compile_skill_module returns (module, fallback_used) tuple."""
        from evolution.core.optimizer import compile_skill_module

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        baseline_module = SkillModule(SAMPLE_BODY)
        trainset = []
        valset = []

        with mock.patch.object(dspy, "GEPA", MockGEPA):
            optimized_module, fallback_used = compile_skill_module(
                baseline_module,
                trainset,
                valset,
                config,
            )

            assert isinstance(optimized_module, MockOptimizedModule), (
                "First return value should be the optimized module"
            )
            assert fallback_used is False, (
                "fallback_used should be False when GEPA succeeds"
            )

    def test_returns_tuple_with_fallback_used_true_on_gepa_failure(self):
        """fallback_used is True when GEPA is unavailable (not just on compile failure)."""
        from evolution.core.optimizer import compile_skill_module

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        baseline_module = SkillModule(SAMPLE_BODY)
        trainset = []
        valset = []

        # Mock _gepa_available to return False to simulate GEPA being unavailable
        # in this DSPy version (not just a compile failure)
        with mock.patch("evolution.core.optimizer._gepa_available", return_value=False):
            with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                optimized_module, fallback_used = compile_skill_module(
                    baseline_module,
                    trainset,
                    valset,
                    config,
                )

                assert isinstance(optimized_module, MockOptimizedModule), (
                    "Should return a valid optimized module even on fallback"
                )
                assert fallback_used is True, (
                    "fallback_used should be True when GEPA is unavailable"
                )

    def test_fallback_module_contains_mipro_marker(self):
        """When falling back to MIPROv2, the result should indicate MIPRO was used."""
        from evolution.core.optimizer import compile_skill_module

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        baseline_module = SkillModule(SAMPLE_BODY)
        trainset = []
        valset = []

        # Mock _gepa_available to return False to simulate GEPA being unavailable
        # in this DSPy version (not just a compile failure)
        with mock.patch("evolution.core.optimizer._gepa_available", return_value=False):
            with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                optimized_module, fallback_used = compile_skill_module(
                    baseline_module,
                    trainset,
                    valset,
                    config,
                )

                # The mock MIPROv2 appends [MIPRO_FALLBACK] to the skill text
                assert "[MIPRO_FALLBACK]" in optimized_module.skill_text, (
                    "Fallback result should indicate MIPRO was used"
                )


class TestEvolveMetrics:
    """Tests for metrics recording in evolve()."""

    def test_metrics_include_optimizer_fields(self, tmp_path):
        """Metrics JSON must include optimizer, optimizer_fallback_used, optimizer_model, eval_model, max_metric_calls."""
        import os
        import json
        from evolution.skills.evolve_skill import evolve

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            # Create mock modules that bypass DSPy LM calls
            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.core.fitness.skill_fitness_metric",
                                                return_value=0.8,
                                            ):
                                                evolve(
                                                    skill_name="test-skill",
                                                    iterations=10,
                                                    eval_source="synthetic",
                                                    optimizer_model="openai/gpt-4.1",
                                                    eval_model="openai/gpt-4.1-mini",
                                                    hermes_repo=str(tmp_path),
                                                    dry_run=False,
                                                )
        finally:
            os.chdir(original_cwd)

        metrics_files = list((tmp_path / "output").rglob("metrics.json"))
        assert len(metrics_files) > 0, "metrics.json should have been written"


        metrics = json.loads(metrics_files[0].read_text())

        # Verify all required optimizer fields are present
        assert "optimizer" in metrics, "Metrics must include 'optimizer' field"
        assert "optimizer_fallback_used" in metrics, (
            "Metrics must include 'optimizer_fallback_used' field"
        )
        assert "optimizer_model" in metrics, "Metrics must include 'optimizer_model' field"
        assert "eval_model" in metrics, "Metrics must include 'eval_model' field"
        assert "max_metric_calls" in metrics, (
            "Metrics must include 'max_metric_calls' field"
        )

        # Verify values
        assert metrics["optimizer"] == "GEPA", (
            f"optimizer should be 'GEPA', got '{metrics.get('optimizer')}'"
        )
        assert metrics["optimizer_model"] == "openai/gpt-4.1"
        assert metrics["eval_model"] == "openai/gpt-4.1-mini"
        assert metrics["max_metric_calls"] == 150

    def test_optimizer_fallback_used_records_fallback(self, tmp_path):
        """When GEPA fails and MIPROv2 is used, optimizer_fallback_used should be True."""
        import os
        from evolution.skills.evolve_skill import evolve

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            # Create mock modules that bypass DSPy LM calls
            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), True),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.core.fitness.skill_fitness_metric",
                                                return_value=0.8,
                                            ):
                                                evolve(
                                                    skill_name="test-skill",
                                                    iterations=10,
                                                    eval_source="synthetic",
                                                    optimizer_model="openai/gpt-4.1",
                                                    eval_model="openai/gpt-4.1-mini",
                                                    hermes_repo=str(tmp_path),
                                                    dry_run=False,
                                                )
        finally:
            os.chdir(original_cwd)

        metrics_files = list((tmp_path / "output").rglob("metrics.json"))
        assert len(metrics_files) > 0, "metrics.json should have been written"

        import json

        metrics = json.loads(metrics_files[0].read_text())

        assert metrics["optimizer_fallback_used"] is True, (
            "optimizer_fallback_used should be True when MIPROv2 fallback is used"
        )
        assert metrics["optimizer"] == "GEPA", (
            "optimizer field should still say 'GEPA' (the intended optimizer)"
        )


class TestGepaAdapterExists:
    """Sanity checks that the adapter module exists and has the required functions."""

    def test_optimizer_module_exists(self):
        """evolution.core.optimizer must exist as a module."""
        from evolution.core import optimizer

        assert hasattr(optimizer, "build_gepa_optimizer"), (
            "evolution.core.optimizer must have build_gepa_optimizer function"
        )
        assert hasattr(optimizer, "compile_skill_module"), (
            "evolution.core.optimizer must have compile_skill_module function"
        )

    def test_gepa_available_function_exists(self):
        """evolution.core.optimizer must have _gepa_available() function."""
        from evolution.core import optimizer

        assert hasattr(optimizer, "_gepa_available"), (
            "evolution.core.optimizer must have _gepa_available function"
        )


class TestEvolutionConfigIterationsBudget:
    """Tests that CLI --iterations correctly sets GEPA budget (max_metric_calls).

    PR #4 Review Comment [HIGH]: Discrepancy between CLI `iterations` and
    optimizer budget `max_metric_calls`. When user specifies `--iterations 10`,
    GEPA still uses `max_metric_calls=150` (default). Fix: set
    `max_metric_calls=iterations` in `EvolutionConfig` initialization.

    The fix is verified via source code inspection since evolve() is the
    actual code path and EvolutionConfig is a dataclass.
    """

    def test_evolve_source_code_passes_max_metric_calls_equal_to_iterations(self):
        """Verify evolve() creates EvolutionConfig with max_metric_calls=iterations.

        This is verified by inspecting the source code of evolve_skill.evolve().
        The line should be:
            config = EvolutionConfig(..., max_metric_calls=iterations, ...)
        """
        import inspect
        from evolution.skills.evolve_skill import evolve

        source = inspect.getsource(evolve)
        assert 'max_metric_calls=iterations' in source, (
            "evolve() should pass max_metric_calls=iterations to EvolutionConfig. "
            "Source should contain: config = EvolutionConfig(..., max_metric_calls=iterations, ...)"
        )


class TestGateEnforcement:
    """Tests that gates are enforced in evolve().

    These tests verify:
    1. run_test_suite() is called when run_tests=True
    2. Failed test gate produces correct JSON with status=failed, failed_gate=test_suite, deployable=false
    3. Improvement threshold (≥10%) is enforced as a gate
    4. constraints.json is written to output bundle
    5. deployable=false when any gate fails
    """

    def test_run_tests_gate_is_called(self, tmp_path):
        """When run_tests=True, validator.run_test_suite() must be called after optimization.

        The bug: run_tests parameter exists but run_test_suite() is never invoked.
        The fix: After holdout evaluation, call validator.run_test_suite(resolved_hermes_path).
        """
        import os
        import json
        from unittest.mock import MagicMock, patch, call
        from evolution.skills.evolve_skill import evolve
        from evolution.core.constraints import ConstraintResult, ConstraintValidator
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:

            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.core.fitness.skill_fitness_metric",
                                                return_value=0.8,
                                            ):
                                                # Mock run_holdout_evaluation to avoid real API calls
                                                # Uses 15% improvement (0.8 → 0.92) to clear the ≥10% threshold gate
                                                # Note: 0.9 - 0.8 = 0.09999... < 0.10 due to floating point, so use 0.92
                                                with mock.patch(
                                                    "evolution.skills.evolve_skill.run_holdout_evaluation",
                                                    return_value={
                                                        "baseline_score": 0.8,
                                                        "evolved_score": 0.92,
                                                        "judge_feedback": "Mock feedback",
                                                    },
                                                ):
                                                    # Mock run_test_suite to return a passing result
                                                    # Must patch ConstraintValidator class before evolve() instantiates it
                                                    mock_test_result = ConstraintResult(
                                                        passed=True,
                                                        constraint_name="test_suite",
                                                        message="All tests passed",
                                                    )
                                                    mock_validator_instance = MagicMock()
                                                    mock_validator_instance.run_test_suite = MagicMock(return_value=mock_test_result)
                                                    with mock.patch(
                                                        "evolution.skills.evolve_skill.ConstraintValidator",
                                                        return_value=mock_validator_instance,
                                                    ):
                                                        evolve(
                                                            skill_name="test-skill",
                                                            iterations=10,
                                                            eval_source="synthetic",
                                                            optimizer_model="openai/gpt-4.1",
                                                            eval_model="openai/gpt-4.1-mini",
                                                            hermes_repo=str(tmp_path),
                                                            run_tests=True,  # Enable test gate
                                                            dry_run=False,
                                                        )

                                                        # Assert run_test_suite was called
                                                        assert mock_validator_instance.run_test_suite.called, (
                                                            "validator.run_test_suite() must be called when run_tests=True. "
                                                            "Current code never calls this method."
                                                        )
        finally:
            os.chdir(original_cwd)

    def test_failed_test_gate_produces_correct_json(self, tmp_path):
        """When tests fail, metrics.json must contain status=failed, failed_gate=test_suite, deployable=false.

        The bug: Even when run_tests=True and tests fail, the run is not marked as failed.
        The fix: When tests fail, set metrics["status"]="failed", metrics["failed_gate"]="test_suite",
        metrics["deployable"]=False.
        """
        import os
        import json
        from unittest.mock import MagicMock, patch
        from evolution.skills.evolve_skill import evolve
        from evolution.core.constraints import ConstraintResult, ConstraintValidator
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:

            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.core.fitness.skill_fitness_metric",
                                                return_value=0.8,
                                                ):
                                                    # Uses 15% improvement (0.8 → 0.92) to clear the ≥10% threshold gate
                                                    # Note: 0.9 - 0.8 = 0.09999... < 0.10 due to floating point, so use 0.92
                                                    with mock.patch(
                                                        "evolution.skills.evolve_skill.run_holdout_evaluation",
                                                        return_value={
                                                            "baseline_score": 0.8,
                                                            "evolved_score": 0.92,
                                                            "judge_feedback": "Mock feedback",
                                                        },
                                                    ):
                                                        # Mock run_test_suite to return a FAILING result
                                                        # Must patch ConstraintValidator class before evolve() instantiates it
                                                        mock_test_result = ConstraintResult(
                                                            passed=False,
                                                            constraint_name="test_suite",
                                                            message="Test suite failed",
                                                            details="3 tests failed",
                                                        )
                                                        mock_validator_instance = MagicMock()
                                                        mock_validator_instance.run_test_suite = MagicMock(return_value=mock_test_result)
                                                        with mock.patch(
                                                            "evolution.skills.evolve_skill.ConstraintValidator",
                                                            return_value=mock_validator_instance,
                                                        ):
                                                            evolve(
                                                                skill_name="test-skill",
                                                                iterations=10,
                                                            eval_source="synthetic",
                                                            optimizer_model="openai/gpt-4.1",
                                                            eval_model="openai/gpt-4.1-mini",
                                                            hermes_repo=str(tmp_path),
                                                            run_tests=True,
                                                            dry_run=False,
                                                        )

                                                    metrics_files = list((tmp_path / "output").rglob("metrics.json"))
            assert len(metrics_files) > 0, "metrics.json should have been written"

            metrics = json.loads(metrics_files[0].read_text())

            # When test gate fails, metrics must contain these fields
            assert metrics.get("status") == "failed", (
                f"metrics.json must have status='failed' when tests fail, got: {metrics.get('status')}"
            )
            assert metrics.get("failed_gate") == "test_suite", (
                f"metrics.json must have failed_gate='test_suite' when tests fail, got: {metrics.get('failed_gate')}"
            )
            assert metrics.get("deployable") is False, (
                f"metrics.json must have deployable=false when tests fail, got: {metrics.get('deployable')}"
            )
        finally:
            os.chdir(original_cwd)

    def test_improvement_threshold_gate(self, tmp_path):
        """Evolution must fail (not proceed) if improvement is less than 10%.

        The bug: Lines 305-310 just print a message but don't enforce the threshold.
        The fix: When improvement < 0.1 (10%), set status=failed, failed_gate="improvement_threshold".
        """
        import os
        import json
        from unittest.mock import MagicMock, patch
        from evolution.skills.evolve_skill import evolve
        from evolution.core.constraints import ConstraintResult, ConstraintValidator
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        # Small improvement (5%) - should fail the threshold
        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:

            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            # baseline_score = 0.8, evolved_score = 0.84 (5% improvement)
                                            # This should trigger the improvement threshold gate (< 10%)
                                            with mock.patch(
                                                "evolution.skills.evolve_skill.run_holdout_evaluation",
                                                return_value={
                                                    "baseline_score": 0.8,
                                                    "evolved_score": 0.84,
                                                    "judge_feedback": "Mock feedback",
                                                },
                                            ):
                                                evolve(
                                                    skill_name="test-skill",
                                                    iterations=10,
                                                    eval_source="synthetic",
                                                    optimizer_model="openai/gpt-4.1",
                                                    eval_model="openai/gpt-4.1-mini",
                                                    hermes_repo=str(tmp_path),
                                                    run_tests=False,
                                                    dry_run=False,
                                                )

                                    metrics_files = list((tmp_path / "output").rglob("metrics.json"))
            assert len(metrics_files) > 0, "metrics.json should have been written"

            metrics = json.loads(metrics_files[0].read_text())

            # When improvement is < 10%, the gate should fail
            # Improvement is 0.84 - 0.8 = 0.04 = 4% which is < 10%
            improvement = metrics.get("improvement", 0)
            assert improvement < 0.1, "Test setup error: improvement should be < 10%"

            assert metrics.get("status") == "failed", (
                f"metrics.json must have status='failed' when improvement < 10%, got: {metrics.get('status')}"
            )
            assert metrics.get("failed_gate") == "improvement_threshold", (
                f"metrics.json must have failed_gate='improvement_threshold' when improvement < 10%, "
                f"got: {metrics.get('failed_gate')}"
            )
            assert metrics.get("deployable") is False, (
                f"metrics.json must have deployable=false when improvement threshold not met, "
                f"got: {metrics.get('deployable')}"
            )
        finally:
            os.chdir(original_cwd)

    def test_constraints_json_written(self, tmp_path):
        """Output bundle must include constraints.json with constraint results.

        The bug: No constraints.json is written - only constraints_passed boolean in metrics.json.
        The fix: Save evolved_constraints and baseline_constraints to constraints.json.
        """
        import os
        import json
        from unittest.mock import MagicMock, patch
        from evolution.skills.evolve_skill import evolve
        from evolution.core.constraints import ConstraintResult, ConstraintValidator
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:

            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.skills.evolve_skill.run_holdout_evaluation",
                                                return_value={
                                                    "baseline_score": 0.8,
                                                    "evolved_score": 0.92,
                                                    "judge_feedback": "Mock feedback",
                                                },
                                            ):
                                                evolve(
                                                    skill_name="test-skill",
                                                    iterations=10,
                                                    eval_source="synthetic",
                                                    optimizer_model="openai/gpt-4.1",
                                                    eval_model="openai/gpt-4.1-mini",
                                                    hermes_repo=str(tmp_path),
                                                    run_tests=False,
                                                    dry_run=False,
                                                )

                                    # Check that constraints.json exists in output
            constraints_files = list((tmp_path / "output").rglob("constraints.json"))
            assert len(constraints_files) > 0, (
                "constraints.json must be written to output bundle. "
                "Current code does not write this file."
            )

            constraints = json.loads(constraints_files[0].read_text())

            # constraints.json should contain both baseline and evolved constraint results
            assert "baseline_constraints" in constraints, (
                "constraints.json must contain 'baseline_constraints' key"
            )
            assert "evolved_constraints" in constraints, (
                "constraints.json must contain 'evolved_constraints' key"
            )
            assert isinstance(constraints["baseline_constraints"], list), (
                "baseline_constraints must be a list"
            )
            assert isinstance(constraints["evolved_constraints"], list), (
                "evolved_constraints must be a list"
            )
        finally:
            os.chdir(original_cwd)

    def test_deployable_false_when_gate_fails(self, tmp_path):
        """When any gate fails, deployable must be false in the output.

        This test uses the test gate failure scenario (run_tests=True with failing tests).
        The deployable field must be False in the output JSON.
        """
        import os
        import json
        from unittest.mock import MagicMock, patch
        from evolution.skills.evolve_skill import evolve
        from evolution.core.constraints import ConstraintResult, ConstraintValidator
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            eval_model="openai/gpt-4.1-mini",
            max_metric_calls=150,
        )

        mock_dataset = EvalDataset(
            train=[
                EvalExample(
                    task_input="test input 1",
                    expected_behavior="expected behavior 1",
                    difficulty="easy",
                    category="test",
                )
            ],
            val=[
                EvalExample(
                    task_input="test input 2",
                    expected_behavior="expected behavior 2",
                    difficulty="medium",
                    category="test",
                )
            ],
            holdout=[
                EvalExample(
                    task_input="test input 3",
                    expected_behavior="expected behavior 3",
                    difficulty="hard",
                    category="test",
                )
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:

            class MockSkillModule(dspy.Module):
                def __init__(self, skill_text=SAMPLE_BODY):
                    super().__init__()
                    self.skill_text = skill_text

                def forward(self, task_input):
                    return dspy.Prediction(output="mock output")

                def __call__(self, task_input=None, **kwargs):
                    return self.forward(task_input)

            with mock.patch.object(dspy, "GEPA", MockGEPA):
                with mock.patch.object(dspy, "MIPROv2", MockMIPROv2):
                    with mock.patch(
                        "evolution.skills.evolve_skill.SyntheticDatasetBuilder",
                    ) as MockDatasetBuilder:
                        MockDatasetBuilder.return_value.generate.return_value = mock_dataset

                        with mock.patch(
                            "evolution.skills.evolve_skill.find_skill",
                            return_value=tmp_path / "SKILL.md",
                        ):
                            with mock.patch(
                                "evolution.skills.evolve_skill.load_skill",
                                return_value={
                                    "path": tmp_path / "SKILL.md",
                                    "raw": f"---\n{SAMPLE_FRONTMATTER}\n---\n\n{SAMPLE_BODY}",
                                    "frontmatter": SAMPLE_FRONTMATTER,
                                    "body": SAMPLE_BODY,
                                    "name": "test-skill",
                                    "description": "A test skill",
                                },
                            ):
                                with mock.patch(
                                    "evolution.skills.evolve_skill.compile_skill_module",
                                    return_value=(MockSkillModule(SAMPLE_BODY), False),
                                ):
                                    with mock.patch(
                                        "evolution.skills.evolve_skill.EvolutionConfig",
                                        return_value=config,
                                    ):
                                        with mock.patch(
                                            "evolution.skills.evolve_skill.SkillModule",
                                            MockSkillModule,
                                        ):
                                            with mock.patch(
                                                "evolution.skills.evolve_skill.run_holdout_evaluation",
                                                return_value={
                                                    "baseline_score": 0.8,
                                                    "evolved_score": 0.92,
                                                    "judge_feedback": "Mock feedback",
                                                },
                                            ):
                                                # Mock test suite to FAIL
                                                mock_test_result = ConstraintResult(
                                                    passed=False,
                                                    constraint_name="test_suite",
                                                    message="Test suite failed",
                                                    details="Some tests failed",
                                                )
                                                mock_validator_instance = MagicMock()
                                                mock_validator_instance.run_test_suite = MagicMock(return_value=mock_test_result)
                                                with mock.patch(
                                                    "evolution.skills.evolve_skill.ConstraintValidator",
                                                    return_value=mock_validator_instance,
                                                ):
                                                    evolve(
                                                        skill_name="test-skill",
                                                        iterations=10,
                                                        eval_source="synthetic",
                                                        optimizer_model="openai/gpt-4.1",
                                                        eval_model="openai/gpt-4.1-mini",
                                                        hermes_repo=str(tmp_path),
                                                        run_tests=True,
                                                        dry_run=False,
                                                    )

                                    metrics_files = list((tmp_path / "output").rglob("metrics.json"))
            assert len(metrics_files) > 0, "metrics.json should have been written"

            metrics = json.loads(metrics_files[0].read_text())

            # deployable must be false when test gate fails
            assert metrics.get("deployable") is False, (
                f"When any gate fails, deployable must be False. Got: {metrics.get('deployable')}"
            )
            # Also verify the status is failed
            assert metrics.get("status") == "failed", (
                f"When any gate fails, status must be 'failed'. Got: {metrics.get('status')}"
            )
        finally:
            os.chdir(original_cwd)
