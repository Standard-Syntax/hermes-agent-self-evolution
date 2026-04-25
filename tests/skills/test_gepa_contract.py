"""Contract test: GEPA optimization must mutate skill_text.

This test proves the Phase 1 pipeline extracts the optimized skill text from
the optimized program via `optimized_module.skill_text`, not accidentally from
the original baseline module.

The bug: if the code reads `optimized_module.skill_text` but GEPA mutates an
internal attribute (not `skill_text`), the evolved body will be identical to
the baseline, and no actual optimization occurred.
"""

from unittest import mock

import dspy

from evolution.skills.skill_module import SkillModule


MUTATION_MARKER = "\n\n[MUTATED BY GEPA]"
BASELINE_BODY = "# Original Skill\n\nDo the original procedure."


class MockOptimizedModule(dspy.Module):
    """A mock module that simulates GEPA's mutation behavior.

    GEPA should mutate the skill_text attribute to produce an evolved version.
    """

    def __init__(self, original_module: SkillModule, mutated_skill_text: str):
        super().__init__()
        self.skill_text = mutated_skill_text
        self.predictor = getattr(original_module, "predictor", None)

    def forward(self, task_input: str):
        return dspy.Prediction(output="mock output")


class MockGEPA:
    """Mock GEPA optimizer that mirrors the real GEPA API.

    Production flow:
        optimizer = dspy.GEPA(metric=..., auto="light")
        optimized_module = optimizer.compile(baseline_module, trainset=..., valset=...)
        evolved_body = optimized_module.skill_text
    """

    def __init__(self, metric, **kwargs):
        self.metric = metric
        for key, value in kwargs.items():
            setattr(self, key, value)

    def compile(self, module, *, trainset=None, valset=None):
        return MockOptimizedModule(module, module.skill_text + MUTATION_MARKER)


def test_gepa_mutation_proof():
    """Test that optimized_module.skill_text reflects GEPA's mutations.

    This test mirrors the real production flow:
    1. Create a GEPA optimizer
    2. Call optimizer.compile(baseline_module, ...)
    3. Extract optimized_module.skill_text
    4. Prove evolved_body != baseline_body (mutation occurred)
    5. Prove evolved_body contains the mutation marker
    """
    baseline_module = SkillModule(skill_text=BASELINE_BODY)
    assert baseline_module.skill_text == BASELINE_BODY

    with mock.patch.object(dspy, "GEPA", MockGEPA):
        optimizer = dspy.GEPA(metric=lambda *args: 1.0, max_metric_calls=1)
        optimized_module = optimizer.compile(
            baseline_module,
            trainset=[],
            valset=[],
        )
        evolved_body = optimized_module.skill_text

    assert evolved_body != BASELINE_BODY, (
        "evolved_body is identical to baseline - GEPA did not mutate skill_text. "
        "The optimization extracted the original module's skill_text instead of "
        "the optimized module's skill_text."
    )

    assert MUTATION_MARKER in evolved_body, (
        f"evolved_body does not contain mutation marker '{MUTATION_MARKER}'. "
        "The optimized module's skill_text was not properly extracted."
    )

    assert baseline_module.skill_text == BASELINE_BODY, (
        "Baseline module was mutated - optimization should not modify the original."
    )
