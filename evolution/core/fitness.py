"""Fitness functions for evaluating evolved artifacts.

Uses LLM-as-judge with rubrics to score agent outputs.
Supports length penalties and multi-dimensional scoring.
"""

import dspy
from dataclasses import dataclass

from evolution.core.config import EvolutionConfig


@dataclass
class FitnessScore:
    """Multi-dimensional fitness score."""
    correctness: float = 0.0  # Did the agent produce correct output? (0-1)
    procedure_following: float = 0.0  # Did it follow the skill's procedure? (0-1)
    conciseness: float = 0.0  # Was it appropriately concise? (0-1)
    length_penalty: float = 0.0  # Penalty for being too verbose (0-1, 0 = no penalty)
    feedback: str = ""  # Textual feedback for GEPA's reflective analysis

    @property
    def composite(self) -> float:
        """Weighted composite score."""
        raw = (
            0.5 * self.correctness
            + 0.3 * self.procedure_following
            + 0.2 * self.conciseness
        )
        return max(0.0, raw - self.length_penalty)


class LLMJudge:
    """LLM-as-judge scorer with rubric-based evaluation.

    Scores agent outputs on multiple dimensions and provides
    textual feedback that GEPA can use for reflective mutation.
    """

    class JudgeSignature(dspy.Signature):
        """Evaluate an agent's response against an expected behavior rubric.

        Score the response on three dimensions (0.0 to 1.0 each):
        1. correctness: Did the response correctly address the task?
        2. procedure_following: Did it follow the expected approach/procedure?
        3. conciseness: Was it appropriately concise without omitting important info?

        Also provide specific, actionable feedback on what could be improved.
        """
        task_input: str = dspy.InputField(desc="The task the agent was given")
        expected_behavior: str = dspy.InputField(desc="Rubric describing what a good response looks like")
        agent_output: str = dspy.InputField(desc="The agent's actual response")
        skill_text: str = dspy.InputField(desc="The skill/instructions the agent was following")
        correctness: float = dspy.OutputField(desc="Score 0.0-1.0: Did the response correctly address the task?")
        procedure_following: float = dspy.OutputField(desc="Score 0.0-1.0: Did it follow the expected procedure?")
        conciseness: float = dspy.OutputField(desc="Score 0.0-1.0: Appropriately concise?")
        feedback: str = dspy.OutputField(desc="Specific, actionable feedback on what could be improved")

    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.judge = dspy.ChainOfThought(self.JudgeSignature)

    def score(
        self,
        task_input: str,
        expected_behavior: str,
        agent_output: str,
        skill_text: str,
        artifact_size: int | None = None,
        max_size: int | None = None,
    ) -> FitnessScore:
        """Score an agent output using LLM-as-judge."""

        lm = dspy.LM(self.config.eval_model)

        with dspy.context(lm=lm):
            result = self.judge(
                task_input=task_input,
                expected_behavior=expected_behavior,
                agent_output=agent_output,
                skill_text=skill_text,
            )

        # Parse scores (clamp to 0-1)
        correctness = _parse_score(result.correctness)
        procedure_following = _parse_score(result.procedure_following)
        conciseness = _parse_score(result.conciseness)

        # Length penalty
        length_penalty = 0.0
        if artifact_size is not None and max_size is not None:
            ratio = artifact_size / max_size
            if ratio > 0.9:
                # Penalty ramps from 0 at 90% to 0.3 at 100%+
                length_penalty = min(0.3, (ratio - 0.9) * 3.0)

        return FitnessScore(
            correctness=correctness,
            procedure_following=procedure_following,
            conciseness=conciseness,
            length_penalty=length_penalty,
            feedback=str(result.feedback),
        )


def fast_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """DSPy-compatible fast metric for skill optimization.

    Cheap deterministic smoke metric for quick iterations during optimization.
    Uses simple keyword overlap to estimate fitness.
    Returns a float 0-1 score.
    """
    agent_output = getattr(prediction, "output", "") or ""
    expected = getattr(example, "expected_behavior", "") or ""

    if not agent_output.strip():
        return 0.0

    score = 0.5  # Base score for non-empty output

    # Simple keyword overlap as a fast proxy
    expected_words = set(expected.lower().split())
    output_words = set(agent_output.lower().split())
    if expected_words:
        overlap = len(expected_words & output_words) / len(expected_words)
        score = 0.3 + (0.7 * overlap)

    return min(1.0, max(0.0, score))


def skill_fitness_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Backward-compatible wrapper for fast_metric.

    Deprecated: Use fast_metric instead.
    """
    return fast_metric(example, prediction, trace)


def judge_metric(
    example: dspy.Example,
    prediction: dspy.Prediction,
    config: EvolutionConfig,
) -> FitnessScore:
    """LLM-as-judge metric for holdout evaluation.

    Uses LLMJudge to score and returns full FitnessScore with feedback.
    Suitable for holdout evaluation where detailed feedback is needed.

    Args:
        example: dspy.Example with task_input, expected_behavior, skill_text
        prediction: dspy.Prediction with output field
        config: EvolutionConfig for LLM judge setup

    Returns:
        FitnessScore with correctness, procedure_following, conciseness,
        length_penalty, and feedback fields
    """
    task_input = getattr(example, "task_input", "") or ""
    expected_behavior = getattr(example, "expected_behavior", "") or ""
    skill_text = getattr(example, "skill_text", "") or ""
    agent_output = getattr(prediction, "output", "") or ""

    judge = LLMJudge(config)
    return judge.score(
        task_input=task_input,
        expected_behavior=expected_behavior,
        agent_output=agent_output,
        skill_text=skill_text,
    )


def gepa_metric(
    example: dspy.Example,
    prediction: dspy.Prediction,
    trace=None,
    pred_name: str | None = None,
    pred_trace: dict | None = None,
    config: EvolutionConfig | None = None,
) -> float | dspy.Prediction:
    """GEPA-compatible metric for dspy.GEPA(metric=...).

    When trace is available (feedback mode), returns dspy.Prediction(score, feedback).
    When trace is None (validation calls), returns float for fast scoring.

    Args:
        example: dspy.Example with task_input, expected_behavior, skill_text
        prediction: dspy.Prediction with output field
        trace: When provided, returns Prediction with feedback; when None, returns float
        pred_name: Ignored (for GEPA compatibility)
        pred_trace: Ignored (for GEPA compatibility)
        config: EvolutionConfig for LLM judge setup (required in feedback mode)

    Returns:
        dspy.Prediction(score, feedback) when trace available, float otherwise
    """
    agent_output = getattr(prediction, "output", "") or ""

    if trace is not None:
        # Feedback mode - return Prediction with score and feedback
        # This requires LLM judge which needs config
        if config is None:
            config = EvolutionConfig()
        task_input = getattr(example, "task_input", "") or ""
        expected_behavior = getattr(example, "expected_behavior", "") or ""
        skill_text = getattr(example, "skill_text", "") or ""

        judge = LLMJudge(config)
        fitness_score = judge.score(
            task_input=task_input,
            expected_behavior=expected_behavior,
            agent_output=agent_output,
            skill_text=skill_text,
        )
        return dspy.Prediction(
            score=fitness_score.composite,
            feedback=fitness_score.feedback,
        )
    else:
        # Validation mode - return float for fast scoring
        return fast_metric(example, prediction, trace)


def run_holdout_evaluation(
    baseline_output: str,
    evolved_output: str,
    task_input: str,
    expected_behavior: str,
    skill_text: str,
    config: EvolutionConfig,
) -> dict[str, str | float]:
    """Run holdout evaluation comparing baseline and evolved outputs.

    Uses LLM-as-judge to score both outputs and provide feedback.

    Args:
        baseline_output: The baseline agent's output
        evolved_output: The evolved agent's output
        task_input: The task description
        expected_behavior: The expected behavior rubric
        skill_text: The skill/instructions the agent was following
        config: EvolutionConfig for LLM judge setup

    Returns:
        Dict with task_input, baseline_output, evolved_output, baseline_score,
        evolved_score, and judge_feedback fields
    """
    judge = LLMJudge(config)

    baseline_fitness = judge.score(
        task_input=task_input,
        expected_behavior=expected_behavior,
        agent_output=baseline_output,
        skill_text=skill_text,
    )

    evolved_fitness = judge.score(
        task_input=task_input,
        expected_behavior=expected_behavior,
        agent_output=evolved_output,
        skill_text=skill_text,
    )

    # Build feedback comparing both outputs
    judge_feedback = (
        f"Baseline (score={baseline_fitness.composite:.2f}): {baseline_fitness.feedback}\n"
        f"Evolved (score={evolved_fitness.composite:.2f}): {evolved_fitness.feedback}"
    )

    return {
        "task_input": task_input,
        "baseline_output": baseline_output,
        "evolved_output": evolved_output,
        "baseline_score": baseline_fitness.composite,
        "evolved_score": evolved_fitness.composite,
        "judge_feedback": judge_feedback,
    }


def _parse_score(value) -> float:
    """Parse a score value, handling various LLM output formats."""
    if isinstance(value, (int, float)):
        return min(1.0, max(0.0, float(value)))
    try:
        return min(1.0, max(0.0, float(str(value).strip())))
    except (ValueError, TypeError):
        return 0.5  # Default to neutral on parse failure
