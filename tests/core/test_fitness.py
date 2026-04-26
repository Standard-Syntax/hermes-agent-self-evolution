"""Tests for fitness functions.

Tests three metric modes:
- fast_metric: cheap deterministic smoke metric
- judge_metric: LLM-as-judge with structured feedback
- gepa_metric: GEPA-compatible metric with feedback when trace available
"""

import pytest
from unittest import mock

import dspy

from evolution.core.fitness import (
    FitnessScore,
    LLMJudge,
    skill_fitness_metric,
)
from evolution.core.config import EvolutionConfig


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def config():
    return EvolutionConfig()


@pytest.fixture
def judge(config):
    return LLMJudge(config)


@pytest.fixture
def sample_example():
    """A dspy.Example with typical fields used in fitness evaluation."""
    return dspy.Example(
        task_input="Write a function to parse JSON",
        expected_behavior="The function should handle invalid JSON gracefully and return None for parse errors",
        agent_output="def parse_json(json_str):\n    try:\n        return json.loads(json_str)\n    except json.JSONDecodeError:\n        return None",
    )


@pytest.fixture
def empty_example():
    return dspy.Example(
        task_input="Some task",
        expected_behavior="Expected behavior text",
        agent_output="",
    )


@pytest.fixture
def prediction_with_output():
    """A dspy.Prediction with an output field."""
    return dspy.Prediction(
        output="The agent's response output here"
    )


# ----------------------------------------------------------------------
# Tests for fast_metric()
# ----------------------------------------------------------------------


class TestFastMetric:
    """Tests for the fast_metric function.

    fast_metric should be a cheap deterministic metric suitable for
    quick iterations during optimization (replaces skill_fitness_metric).
    """

    def test_fast_metric_exists(self):
        """fast_metric function should exist in fitness module."""
        from evolution.core.fitness import fast_metric
        assert callable(fast_metric)

    def test_fast_metric_returns_float(self, sample_example, prediction_with_output):
        """fast_metric should return a float."""
        from evolution.core.fitness import fast_metric
        result = fast_metric(sample_example, prediction_with_output)
        assert isinstance(result, float)

    def test_fast_metric_in_valid_range(self, sample_example, prediction_with_output):
        """fast_metric should return a value between 0 and 1."""
        from evolution.core.fitness import fast_metric
        result = fast_metric(sample_example, prediction_with_output)
        assert 0.0 <= result <= 1.0

    def test_fast_metric_empty_output_returns_zero(self, empty_example):
        """fast_metric should return 0.0 for empty output."""
        from evolution.core.fitness import fast_metric
        prediction = dspy.Prediction(output="")
        result = fast_metric(empty_example, prediction)
        assert result == 0.0

    def test_fast_metric_deterministic(self, sample_example, prediction_with_output):
        """fast_metric should produce the same result for the same inputs."""
        from evolution.core.fitness import fast_metric
        result1 = fast_metric(sample_example, prediction_with_output)
        result2 = fast_metric(sample_example, prediction_with_output)
        assert result1 == result2

    def test_fast_metric_no_llm_calls(self, sample_example, prediction_with_output):
        """fast_metric should not make any LLM calls."""
        from evolution.core.fitness import fast_metric
        with mock.patch("dspy.LM") as mock_lm:
            fast_metric(sample_example, prediction_with_output)
            mock_lm.assert_not_called()

    def test_fast_metric_keyword_overlap(self):
        """fast_metric should score higher when expected keywords are present."""
        from evolution.core.fitness import fast_metric
        example = dspy.Example(
            task_input="Task",
            expected_behavior="return the sum of two numbers",
            agent_output="def add(a, b): return a + b",
        )
        prediction = dspy.Prediction(output=example.agent_output)
        result = fast_metric(example, prediction)
        # Some keyword overlap should give a decent score
        assert result > 0.3


# ----------------------------------------------------------------------
# Tests for judge_metric()
# ----------------------------------------------------------------------


class TestJudgeMetric:
    """Tests for the judge_metric function.

    judge_metric uses LLMJudge to score and returns a full FitnessScore
    with feedback for holdout evaluation.
    """

    def test_judge_metric_exists(self):
        """judge_metric function should exist in fitness module."""
        from evolution.core.fitness import judge_metric
        assert callable(judge_metric)

    def test_judge_metric_returns_fitness_score(self, sample_example, prediction_with_output, config):
        """judge_metric should return a FitnessScore object."""
        from evolution.core.fitness import judge_metric
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = judge_metric(sample_example, prediction_with_output, config)
            assert isinstance(result, FitnessScore)

    def test_judge_metric_has_feedback(self, sample_example, prediction_with_output, config):
        """judge_metric should return a FitnessScore with non-empty feedback."""
        from evolution.core.fitness import judge_metric
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = judge_metric(sample_example, prediction_with_output, config)
            assert isinstance(result.feedback, str)
            assert len(result.feedback) > 0

    def test_judge_metric_scores_in_valid_range(self, sample_example, prediction_with_output, config):
        """All score fields should be in 0-1 range."""
        from evolution.core.fitness import judge_metric
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = judge_metric(sample_example, prediction_with_output, config)
            assert 0.0 <= result.correctness <= 1.0
            assert 0.0 <= result.procedure_following <= 1.0
            assert 0.0 <= result.conciseness <= 1.0

    def test_judge_metric_uses_llm(self, sample_example, prediction_with_output, config):
        """judge_metric should actually call the LLM judge."""
        from evolution.core.fitness import judge_metric
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            judge_metric(sample_example, prediction_with_output, config)
            mock_score.assert_called_once()


# ----------------------------------------------------------------------
# Tests for gepa_metric()
# ----------------------------------------------------------------------


class TestGepaMetric:
    """Tests for the gepa_metric function.

    gepa_metric is compatible with dspy.GEPA(metric=...).
    When trace is available (feedback mode), returns dspy.Prediction(score, feedback).
    When trace is None (validation calls), returns float.
    """

    def test_gepa_metric_exists(self):
        """gepa_metric function should exist in fitness module."""
        from evolution.core.fitness import gepa_metric
        assert callable(gepa_metric)

    def test_gepa_metric_with_trace_returns_prediction(self, sample_example, prediction_with_output, config):
        """gepa_metric should return dspy.Prediction when trace is provided."""
        from evolution.core.fitness import gepa_metric
        trace = {}  # Non-None trace indicates feedback mode
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = gepa_metric(sample_example, prediction_with_output, trace, config=config)
            assert isinstance(result, dspy.Prediction)

    def test_gepa_metric_with_trace_has_score_and_feedback(self, sample_example, prediction_with_output, config):
        """gepa_metric Prediction should have score and feedback fields."""
        from evolution.core.fitness import gepa_metric
        trace = {}
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = gepa_metric(sample_example, prediction_with_output, trace, config=config)
            assert hasattr(result, "score")
            assert hasattr(result, "feedback")

    def test_gepa_metric_without_trace_returns_float(self, sample_example, prediction_with_output):
        """gepa_metric should return float when trace is None (validation mode)."""
        from evolution.core.fitness import gepa_metric
        result = gepa_metric(sample_example, prediction_with_output, trace=None)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_gepa_metric_score_in_valid_range(self, sample_example, prediction_with_output, config):
        """gepa_metric score should be in 0-1 range."""
        from evolution.core.fitness import gepa_metric
        trace = {}
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = gepa_metric(sample_example, prediction_with_output, trace, config=config)
            assert 0.0 <= result.score <= 1.0

    def test_gepa_metric_validation_call_deterministic(self, sample_example, prediction_with_output):
        """gepa_metric with trace=None should be deterministic (uses fast_metric logic)."""
        from evolution.core.fitness import gepa_metric
        result1 = gepa_metric(sample_example, prediction_with_output, trace=None)
        result2 = gepa_metric(sample_example, prediction_with_output, trace=None)
        assert result1 == result2


# ----------------------------------------------------------------------
# Tests for holdout evaluation output format
# ----------------------------------------------------------------------


class TestHoldoutEvaluationOutput:
    """Tests for holdout evaluation output format.

    Holdout evaluation should output a dict with:
    - task_input
    - baseline_output
    - evolved_output
    - baseline_score
    - evolved_score
    - judge_feedback
    """

    def test_holdout_result_has_required_fields(self):
        """Holdout result dict should have all required fields."""
        from evolution.core.fitness import run_holdout_evaluation
        # Check function exists and returns expected structure
        assert callable(run_holdout_evaluation)

    def test_holdout_result_includes_all_required_fields(self, config):
        """Holdout result should include all required fields with correct types."""
        from evolution.core.fitness import run_holdout_evaluation
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = run_holdout_evaluation(
                baseline_output="baseline output",
                evolved_output="evolved output",
                task_input="task",
                expected_behavior="expected behavior",
                skill_text="skill text",
                config=config,
            )
            assert isinstance(result, dict)
            assert "task_input" in result
            assert "baseline_output" in result
            assert "evolved_output" in result
            assert "baseline_score" in result
            assert "evolved_score" in result
            assert "judge_feedback" in result
            assert isinstance(result["baseline_score"], float)
            assert isinstance(result["evolved_score"], float)
            assert isinstance(result["judge_feedback"], str)

    def test_holdout_result_judge_feedback_is_string(self, config):
        """judge_feedback should be a non-empty string when present."""
        from evolution.core.fitness import run_holdout_evaluation
        with mock.patch.object(LLMJudge, "score") as mock_score:
            mock_score.return_value = FitnessScore(
                correctness=0.8,
                procedure_following=0.7,
                conciseness=0.9,
                feedback="Good job",
            )
            result = run_holdout_evaluation(
                baseline_output="baseline output",
                evolved_output="evolved output",
                task_input="task",
                expected_behavior="expected behavior",
                skill_text="skill text",
                config=config,
            )
            assert isinstance(result["judge_feedback"], str)
            assert len(result["judge_feedback"]) > 0


# ----------------------------------------------------------------------
# Backward compatibility tests for skill_fitness_metric
# ----------------------------------------------------------------------


class TestSkillFitnessMetricBackwardCompat:
    """Tests ensuring skill_fitness_metric behavior is preserved in fast_metric.

    After refactoring, skill_fitness_metric may be deprecated but should
    still work or fast_metric should be its direct replacement.
    """

    def test_skill_fitness_metric_still_works(self, sample_example, prediction_with_output):
        """skill_fitness_metric should still function (or fast_metric replaces it)."""
        result = skill_fitness_metric(sample_example, prediction_with_output)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_skill_fitness_metric_empty_output(self, empty_example):
        """skill_fitness_metric returns 0 for empty output."""
        prediction = dspy.Prediction(output="")
        result = skill_fitness_metric(empty_example, prediction)
        assert result == 0.0
