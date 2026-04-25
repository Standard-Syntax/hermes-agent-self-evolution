"""Tests for evolution.core.optimizer module.

Verifies:
1. _gepa_available() is cached with @functools.lru_cache(maxsize=1)
2. MIPROv2 fallback passes valset to compile()
3. GEPA optimizer uses max_metric_calls correctly
"""

import functools
from unittest import mock

import dspy
import pytest

from evolution.core.config import EvolutionConfig
from evolution.skills.skill_module import SkillModule


SAMPLE_BODY = "# Sample Skill\n\nDo the thing."


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
        self.compile_calls = []

    def compile(self, module, *, trainset=None, valset=None):
        self.compile_calls.append({"trainset": trainset, "valset": valset})
        return MockOptimizedModule(module, module.skill_text + "\n\n[MIPRO_FALLBACK]")


class TestGepaAvailableCaching:
    """Tests for _gepa_available() caching with lru_cache."""

    def test_gepa_available_is_cached_with_lru_cache(self):
        """_gepa_available() should be decorated with @functools.lru_cache(maxsize=1).

        Without caching, _gepa_available() is called multiple times, each time
        triggering a DSPy GEPA constructor call which is expensive.
        """
        from evolution.core import optimizer

        # Check that the function has lru_cache applied
        assert hasattr(optimizer._gepa_available, "cache_info"), (
            "_gepa_available() must be decorated with @functools.lru_cache "
            "to avoid repeated expensive DSPy GEPA checks"
        )

        # Verify it's the correct cache size
        cache_info = optimizer._gepa_available.cache_info()
        assert cache_info.maxsize == 1, (
            f"lru_cache maxsize should be 1, got {cache_info.maxsize}"
        )

    def test_gepa_available_only_called_once_per_session(self):
        """_gepa_available() should only execute the DSPy check once per session.

        After first call, subsequent calls should return cached result without
        re-executing the dspy.GEPA() check.
        """
        from evolution.core import optimizer

        # Clear any existing cache
        optimizer._gepa_available.cache_clear()

        with mock.patch.object(dspy, "GEPA") as mock_gepa:
            mock_gepa.side_effect = Exception("GEPA not available")

            # First call - should execute dspy.GEPA
            result1 = optimizer._gepa_available()

            # Second call - should NOT execute dspy.GEPA again
            result2 = optimizer._gepa_available()

            # Third call - should still return cached result
            result3 = optimizer._gepa_available()

            # GEPA should have been called only once (first call populated cache)
            assert mock_gepa.call_count == 1, (
                f"_gepa_available() should only call dspy.GEPA once due to caching, "
                f"but was called {mock_gepa.call_count} times"
            )

            # All results should be False (GEPA not available)
            assert result1 is False
            assert result2 is False
            assert result3 is False


class TestMIPROv2FallbackValset:
    """Tests for MIPROv2 fallback correctly passing valset to compile()."""

    def test_mipro_fallback_receives_valset(self):
        """MIPROv2 fallback compile() must receive valset=valset argument.

        When GEPA is unavailable and MIPROv2 is used as fallback,
        the valset must be passed to optimizer.compile() for proper validation
        during the optimization process.
        """
        from evolution.core.optimizer import compile_skill_module

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        baseline_module = SkillModule(SAMPLE_BODY)
        trainset = [mock.MagicMock(spec=dspy.Example)]
        valset = [mock.MagicMock(spec=dspy.Example)]

        mock_mipro = MockMIPROv2(metric=mock.MagicMock(), auto="light")

        with mock.patch("evolution.core.optimizer._gepa_available", return_value=False):
            with mock.patch.object(dspy, "MIPROv2", return_value=mock_mipro):
                optimized_module, fallback_used = compile_skill_module(
                    baseline_module,
                    trainset,
                    valset,
                    config,
                )

                assert fallback_used is True, "Should indicate MIPROv2 fallback was used"

                # Verify compile was called with valset
                assert len(mock_mipro.compile_calls) == 1, (
                    "MIPROv2.compile() should have been called exactly once"
                )

                call_kwargs = mock_mipro.compile_calls[0]
                assert call_kwargs["valset"] is valset, (
                    f"MIPROv2 fallback compile() must receive valset=valset. "
                    f"Expected valset={valset}, got valset={call_kwargs.get('valset')}"
                )

    def test_mipro_fallback_receives_both_trainset_and_valset(self):
        """MIPROv2 fallback compile() must receive both trainset and valset."""
        from evolution.core.optimizer import compile_skill_module

        config = EvolutionConfig(
            iterations=10,
            optimizer_model="openai/gpt-4.1",
            max_metric_calls=150,
        )

        baseline_module = SkillModule(SAMPLE_BODY)
        trainset = [mock.MagicMock(spec=dspy.Example)]
        valset = [mock.MagicMock(spec=dspy.Example)]

        mock_mipro = MockMIPROv2(metric=mock.MagicMock(), auto="light")

        with mock.patch("evolution.core.optimizer._gepa_available", return_value=False):
            with mock.patch.object(dspy, "MIPROv2", return_value=mock_mipro):
                optimized_module, fallback_used = compile_skill_module(
                    baseline_module,
                    trainset,
                    valset,
                    config,
                )

                call_kwargs = mock_mipro.compile_calls[0]

                assert call_kwargs["trainset"] is trainset, (
                    f"MIPROv2 fallback compile() must receive trainset. "
                    f"Expected {trainset}, got {call_kwargs.get('trainset')}"
                )
                assert call_kwargs["valset"] is valset, (
                    f"MIPROv2 fallback compile() must receive valset. "
                    f"Expected {valset}, got {call_kwargs.get('valset')}"
                )


class TestGepaOptimizerMaxMetricCalls:
    """Tests for GEPA optimizer correctly using max_metric_calls."""

    def test_gepa_uses_max_metric_calls_from_config(self):
        """GEPA optimizer must use max_metric_calls from config, not a fixed default."""
        from evolution.core.optimizer import build_gepa_optimizer

        # Test with different max_metric_calls values
        for expected_calls in [10, 50, 100]:
            config = EvolutionConfig(
                iterations=expected_calls,
                optimizer_model="openai/gpt-4.1",
                max_metric_calls=expected_calls,
            )

            with mock.patch.object(dspy, "GEPA", MockGEPA) as mock_gepa_cls:
                with mock.patch.object(dspy, "LM", return_value=mock.MagicMock()):
                    optimizer = build_gepa_optimizer(config)

                    # Verify GEPA was instantiated with correct max_metric_calls
                    mock_gepa_cls.assert_called_once()
                    call_kwargs = mock_gepa_cls.call_args.kwargs
                    assert call_kwargs.get("max_metric_calls") == expected_calls, (
                        f"GEPA should be created with max_metric_calls={expected_calls}, "
                        f"got {call_kwargs.get('max_metric_calls')}"
                    )
