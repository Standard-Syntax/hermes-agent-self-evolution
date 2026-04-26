"""GEPA optimizer adapter for DSPy skill evolution.

Provides a clean interface for building GEPA optimizers with the current DSPy API,
handling version compatibility and fallback to MIPROv2 when GEPA is unavailable.
"""

import functools

import dspy

from evolution.core.config import EvolutionConfig
from evolution.core.fitness import gepa_metric
from evolution.skills.skill_module import SkillModule


@functools.lru_cache(maxsize=1)
def _gepa_available() -> bool:
    """Check if GEPA is available in this DSPy version."""
    try:
        dspy.GEPA(metric=lambda: 1.0, max_metric_calls=1)  # type: ignore[invalid-argument-type]
        return True
    except Exception:
        return False


def build_gepa_optimizer(config: EvolutionConfig) -> dspy.GEPA:
    """Build a GEPA optimizer with current DSPy API.

    Uses max_metric_calls as budget (not max_steps which is not valid).
    GEPA requires exactly ONE of: auto, max_full_evals, or max_metric_calls.

    Args:
        config: EvolutionConfig with optimizer_model and max_metric_calls

    Returns:
        dspy.GEPA configured with max_metric_calls and reflection_lm
    """
    # Bind config into gepa_metric via functools.partial since GEPA metric
    # signature doesn't include config (it expects gold, pred, trace, pred_name, pred_trace)
    gepa_metric_with_config = functools.partial(gepa_metric, config=config)
    return dspy.GEPA(
        metric=gepa_metric_with_config,  # type: ignore[invalid-argument-type]
        max_metric_calls=config.max_metric_calls,
        reflection_lm=dspy.LM(config.optimizer_model),
    )


def compile_skill_module(
    baseline_module: SkillModule,
    trainset: list[dspy.Example],
    valset: list[dspy.Example],
    config: EvolutionConfig,
) -> tuple[dspy.Module, bool]:
    """Compile a skill module using GEPA, handling version compatibility.

    Tries to use GEPA first if available, falls back to MIPROv2 only if GEPA
    is unavailable in this DSPy version.

    Args:
        baseline_module: The SkillModule to optimize
        trainset: Training examples
        valset: Validation examples
        config: EvolutionConfig

    Returns:
        tuple of (optimized_module, fallback_used) where fallback_used indicates
        if MIPROv2 was used instead of GEPA.

    Raises:
        Exception: Re-raises any compilation errors (bad metric, invalid data,
            etc.) to avoid masking real failures.
    """
    if not _gepa_available():
        # GEPA unavailable in this DSPy version - use MIPROv2 fallback
        # Bind config into gepa_metric via functools.partial
        gepa_metric_with_config = functools.partial(gepa_metric, config=config)
        optimizer = dspy.MIPROv2(
            metric=gepa_metric_with_config,
            auto="light",
        )
        optimized_module = optimizer.compile(
            baseline_module,
            trainset=trainset,
            valset=valset,
        )
        return optimized_module, True  # Fallback was used

    # GEPA is available - try to use it
    optimizer = build_gepa_optimizer(config)
    optimized_module = optimizer.compile(
        baseline_module,
        trainset=trainset,
        valset=valset,
    )
    return optimized_module, False  # No fallback
