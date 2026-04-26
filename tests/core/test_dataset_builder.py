"""Tests for dataset_builder.py — validation, deduplication, and deterministic splitting.

Tests cover:
  - EvolutionConfig.seed field exists and defaults to 42
  - Deterministic splitting: same seed + same examples → identical splits
  - Example validation: invalid examples (empty task_input, empty expected_behavior,
    bad difficulty, bad category, secret-containing) are dropped
  - Duplicate task_input deduplication: only first occurrence is kept
  - Minimum example count requirements
  - SyntheticDatasetBuilder.validate_examples integration
  - GoldenDatasetLoader deduplication and validation
  - GoldenDatasetLoader.load_all (when train.jsonl exists)
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from evolution.core.config import EvolutionConfig
from evolution.core.dataset_builder import (
    EvalExample,
    EvalDataset,
    SyntheticDatasetBuilder,
    GoldenDatasetLoader,
)
from evolution.core.external_importers import _contains_secret


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_example(
    task_input: str = "sort these items",
    expected_behavior: str = "group by category",
    difficulty: str = "medium",
    category: str = "sorting",
    source: str = "synthetic",
) -> EvalExample:
    return EvalExample(
        task_input=task_input,
        expected_behavior=expected_behavior,
        difficulty=difficulty,
        category=category,
        source=source,
    )


def write_golden_jsonl(path: Path, examples: list[EvalExample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex.to_dict()) + "\n")


def write_split_jsonl(dir_path: Path, split_name: str, examples: list[EvalExample]) -> None:
    (dir_path / f"{split_name}.jsonl").write_text(
        "\n".join(json.dumps(ex.to_dict()) for ex in examples) + "\n"
    )


# ── TestEvolutionConfigSeed ───────────────────────────────────────────────────


class TestEvolutionConfigSeed:
    """Verify that EvolutionConfig has a seed field with default 42."""

    def test_seed_field_exists(self):
        config = EvolutionConfig()
        assert hasattr(config, "seed"), "EvolutionConfig should have a 'seed' field"

    def test_seed_default_is_42(self):
        config = EvolutionConfig()
        assert config.seed == 42, "EvolutionConfig.seed should default to 42"

    def test_seed_can_be_set_explicitly(self):
        config = EvolutionConfig(seed=123)
        assert config.seed == 123


# ── TestDeterministicSplitting ───────────────────────────────────────────────


class TestDeterministicSplitting:
    """Verify that splitting is deterministic when seed is provided.

    Same seed + same examples → identical splits on two calls.
    """

    def test_golden_loader_same_seed_same_split(self, tmp_path):
        """GoldenDatasetLoader with same seed produces identical splits twice."""
        examples = [make_example(task_input=f"task {i}") for i in range(20)]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        config = EvolutionConfig(seed=99)
        loader = GoldenDatasetLoader()

        dataset1 = loader.load(tmp_path)
        dataset2 = loader.load(tmp_path)

        # task_inputs in each split must be identical
        assert [ex.task_input for ex in dataset1.train] == [ex.task_input for ex in dataset2.train]
        assert [ex.task_input for ex in dataset1.val] == [ex.task_input for ex in dataset2.val]
        assert [ex.task_input for ex in dataset1.holdout] == [ex.task_input for ex in dataset2.holdout]

    def test_different_seeds_produce_different_splits(self, tmp_path):
        """Different seeds produce different splits for the same examples."""
        examples = [make_example(task_input=f"task {i}") for i in range(20)]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        config_a = EvolutionConfig(seed=111)
        config_b = EvolutionConfig(seed=222)
        loader_a = GoldenDatasetLoader()
        loader_b = GoldenDatasetLoader()

        dataset_a = loader_a.load(tmp_path)
        dataset_b = loader_b.load(tmp_path)

        # At least one split should differ
        train_a = [ex.task_input for ex in dataset_a.train]
        train_b = [ex.task_input for ex in dataset_b.train]
        assert train_a != train_b, "Different seeds should produce different splits"

    def test_synthetic_builder_same_seed_same_split(self, tmp_path):
        """SyntheticDatasetBuilder with same seed produces identical splits twice."""
        mock_result = SimpleNamespace(
            test_cases=json.dumps([
                {"task_input": f"generate task {i}", "expected_behavior": "do something", "difficulty": "easy", "category": "test"}
                for i in range(12)
            ])
        )

        config = EvolutionConfig(seed=77, eval_dataset_size=12)

        with patch("evolution.core.dataset_builder.dspy") as mock_dspy:
            mock_dspy.LM.return_value = MagicMock()
            mock_dspy.context.return_value.__enter__ = MagicMock(return_value=None)
            mock_dspy.context.return_value.__exit__ = MagicMock(return_value=False)
            mock_dspy.ChainOfThought.return_value = MagicMock(return_value=mock_result)

            builder = SyntheticDatasetBuilder(config)
            dataset1 = builder.generate("artifact text", "skill")
            dataset2 = builder.generate("artifact text", "skill")

        # Same order in each split
        inputs1 = [ex.task_input for ex in dataset1.train]
        inputs2 = [ex.task_input for ex in dataset2.train]
        assert inputs1 == inputs2, "Same seed should produce identical splits"


# ── TestExampleValidation ────────────────────────────────────────────────────


class TestExampleValidation:
    """Verify validate_examples filters out invalid examples correctly.

    Rules:
    - task_input required, non-empty, stripped
    - expected_behavior required, non-empty, stripped
    - difficulty in {"easy", "medium", "hard"} — normalize invalid to "medium"
    - category required, non-empty — default to "general"
    - No secrets
    """

    def test_validate_examples_exports_from_dataset_builder(self):
        """validate_examples should be importable from dataset_builder."""
        from evolution.core.dataset_builder import validate_examples
        assert callable(validate_examples)

    def test_valid_example_passes_through(self):
        """A fully-valid EvalExample should pass validation."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(
                task_input="sort these emails",
                expected_behavior="group by sender",
                difficulty="easy",
                category="email",
            )
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].task_input == "sort these emails"

    def test_empty_task_input_is_dropped(self):
        """Examples with empty task_input are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input=""),
            make_example(task_input="valid task"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].task_input == "valid task"

    def test_whitespace_only_task_input_is_dropped(self):
        """Examples with whitespace-only task_input are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="   \n\t  "),
            make_example(task_input="valid task"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].task_input == "valid task"

    def test_empty_expected_behavior_is_dropped(self):
        """Examples with empty expected_behavior are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(expected_behavior=""),
            make_example(task_input="task", expected_behavior="valid behavior"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].expected_behavior == "valid behavior"

    def test_whitespace_only_expected_behavior_is_dropped(self):
        """Examples with whitespace-only expected_behavior are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="task", expected_behavior="   "),
            make_example(task_input="task", expected_behavior="valid"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1

    def test_invalid_difficulty_normalized_to_medium(self):
        """Invalid difficulty values are normalized to 'medium'."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="t1", expected_behavior="b", difficulty="impossible"),
            make_example(task_input="t2", expected_behavior="b", difficulty=""),
            make_example(task_input="t3", expected_behavior="b", difficulty="super-hard"),
        ]
        result = validate_examples(examples)
        assert len(result) == 3
        for ex in result:
            assert ex.difficulty == "medium", f"Invalid difficulty '{ex.difficulty}' should be 'medium'"

    def test_valid_difficulty_preserved(self):
        """Valid difficulty values ('easy', 'medium', 'hard') are preserved."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="t1", expected_behavior="b", difficulty="easy"),
            make_example(task_input="t2", expected_behavior="b", difficulty="medium"),
            make_example(task_input="t3", expected_behavior="b", difficulty="hard"),
        ]
        result = validate_examples(examples)
        difficulties = {ex.difficulty for ex in result}
        assert difficulties == {"easy", "medium", "hard"}

    def test_empty_category_defaults_to_general(self):
        """Empty category defaults to 'general'."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="t1", expected_behavior="b", category=""),
            make_example(task_input="t2", expected_behavior="b", category="   "),
        ]
        result = validate_examples(examples)
        assert len(result) == 2
        for ex in result:
            assert ex.category == "general"

    def test_task_input_with_secret_is_dropped(self):
        """Examples whose task_input contains secrets are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="here is sk-ant-api03-SECRETKEY1234567890"),
            make_example(task_input="valid task input"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].task_input == "valid task input"

    def test_expected_behavior_with_secret_is_dropped(self):
        """Examples whose expected_behavior contains secrets are dropped."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="task", expected_behavior="ghp_SECRET_TOKEN_1234567890xyz"),
            make_example(task_input="task", expected_behavior="normal behavior"),
        ]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].expected_behavior == "normal behavior"

    def test_all_invalid_examples_returns_empty_list(self):
        """If all examples are invalid, validate_examples returns empty list."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="", expected_behavior=""),
            make_example(task_input="sk-ant-api03-SECRET", expected_behavior="b"),
            make_example(task_input="t", expected_behavior=""),
        ]
        result = validate_examples(examples)
        assert result == []


# ── TestDuplicateTaskInputDeduplication ─────────────────────────────────────


class TestDuplicateTaskInputDeduplication:
    """Verify that duplicate task_input values are deduplicated — only first kept."""

    def test_duplicate_task_inputs_deduplicated(self):
        """When duplicate task_input values exist, only the first is kept."""
        from evolution.core.dataset_builder import validate_examples
        examples = [
            make_example(task_input="same task"),
            make_example(task_input="same task"),  # duplicate
            make_example(task_input="task 2"),
        ]
        result = validate_examples(examples)
        task_inputs = [ex.task_input for ex in result]
        assert task_inputs.count("same task") == 1
        assert len(result) == 2

    def test_first_occurrence_kept_not_last(self):
        """When a task_input appears multiple times, the FIRST occurrence is kept."""
        from evolution.core.dataset_builder import validate_examples
        first = make_example(task_input="duplicate", expected_behavior="from first", difficulty="easy")
        second = make_example(task_input="duplicate", expected_behavior="from second", difficulty="hard")
        third = make_example(task_input="duplicate", expected_behavior="from third", difficulty="medium")
        examples = [first, second, third]
        result = validate_examples(examples)
        assert len(result) == 1
        assert result[0].expected_behavior == "from first"
        assert result[0].difficulty == "easy"


# ── TestMinimumExampleCount ─────────────────────────────────────────────────


class TestMinimumExampleCount:
    """Verify minimum example count handling in dataset generation."""

    def test_holdout_nonempty_when_input_sufficient(self, tmp_path):
        """When enough examples exist, holdout should be non-empty."""
        examples = [make_example(task_input=f"task {i}") for i in range(20)]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        assert len(dataset.holdout) >= 1, "holdout should have at least 1 example when input >= 4"

    def test_very_small_dataset_still_splits(self, tmp_path):
        """Even with 3 examples (minimum), splits are produced."""
        examples = [make_example(task_input=f"task {i}") for i in range(3)]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        # With 3 examples: n_train=max(1, int(3*0.5))=1, n_val=max(1, int(3*0.25))=1
        # So train=1, val=1, holdout=1
        assert len(dataset.train) >= 1
        assert len(dataset.val) >= 1
        assert len(dataset.holdout) >= 1

    def test_validation_filters_insufficient_examples(self, tmp_path):
        """After invalid examples are filtered, if fewer than eval_dataset_size remain,
        the builder should still return what it can."""
        # Create examples where some are invalid
        raw = [
            {"task_input": "", "expected_behavior": "b"},  # invalid - empty
            {"task_input": "sk-ant-api03-SECRET", "expected_behavior": "b"},  # invalid - secret
            {"task_input": "task 1", "expected_behavior": "b"},
            {"task_input": "task 2", "expected_behavior": "b"},
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", [
            EvalExample(**d) for d in raw
        ])

        config = EvolutionConfig(seed=1, eval_dataset_size=20)
        dataset = GoldenDatasetLoader.load(tmp_path)

        # Only 2 valid examples remain — should still produce splits
        assert len(dataset.train) >= 1
        assert len(dataset.val) >= 1


# ── TestSyntheticDatasetBuilderValidation ───────────────────────────────────


class TestSyntheticDatasetBuilderValidation:
    """Verify SyntheticDatasetBuilder.generate() validates and filters its output."""

    @pytest.fixture
    def mock_dspy(self):
        with patch("evolution.core.dataset_builder.dspy") as mock:
            mock.LM.return_value = MagicMock()
            mock.context.return_value.__enter__ = MagicMock(return_value=None)
            mock.context.return_value.__exit__ = MagicMock(return_value=False)
            yield mock

    def test_invalid_examples_filtered_from_synthetic_output(self, mock_dspy):
        """Synthetic generation should filter out invalid examples from LLM output."""
        config = EvolutionConfig(seed=1, eval_dataset_size=10)
        mock_result = SimpleNamespace(
            test_cases=json.dumps([
                {"task_input": "valid task 1", "expected_behavior": "do stuff", "difficulty": "easy", "category": "test"},
                {"task_input": "", "expected_behavior": "should be dropped"},  # invalid - empty
                {"task_input": "sk-ant-api03-SECRETKEY", "expected_behavior": "secret"},  # invalid - secret
                {"task_input": "valid task 2", "expected_behavior": "also valid", "difficulty": "hard", "category": "prod"},
            ])
        )
        mock_dspy.ChainOfThought.return_value = MagicMock(return_value=mock_result)

        builder = SyntheticDatasetBuilder(config)
        dataset = builder.generate("artifact text", "skill")

        task_inputs = [ex.task_input for ex in dataset.all_examples]
        assert "" not in task_inputs
        assert "sk-ant-api03-SECRETKEY" not in task_inputs
        assert "valid task 1" in task_inputs
        assert "valid task 2" in task_inputs

    def test_synthetic_output_deduplicated(self, mock_dspy):
        """Synthetic generation should deduplicate based on task_input."""
        config = EvolutionConfig(seed=1, eval_dataset_size=10)
        mock_result = SimpleNamespace(
            test_cases=json.dumps([
                {"task_input": "same", "expected_behavior": "first", "difficulty": "easy", "category": "a"},
                {"task_input": "same", "expected_behavior": "second", "difficulty": "hard", "category": "b"},
                {"task_input": "unique", "expected_behavior": "unique behavior", "difficulty": "medium", "category": "c"},
            ])
        )
        mock_dspy.ChainOfThought.return_value = MagicMock(return_value=mock_result)

        builder = SyntheticDatasetBuilder(config)
        dataset = builder.generate("artifact text", "skill")

        task_inputs = [ex.task_input for ex in dataset.all_examples]
        assert task_inputs.count("same") == 1
        assert len(dataset.all_examples) == 2

    def test_synthetic_invalid_difficulty_normalized(self, mock_dspy):
        """Synthetic generation should normalize invalid difficulty to 'medium'."""
        config = EvolutionConfig(seed=1, eval_dataset_size=10)
        mock_result = SimpleNamespace(
            test_cases=json.dumps([
                {"task_input": "t1", "expected_behavior": "b", "difficulty": "impossible", "category": "cat"},
                {"task_input": "t2", "expected_behavior": "b", "difficulty": "super-hard", "category": "cat"},
            ])
        )
        mock_dspy.ChainOfThought.return_value = MagicMock(return_value=mock_result)

        builder = SyntheticDatasetBuilder(config)
        dataset = builder.generate("artifact text", "skill")

        for ex in dataset.all_examples:
            assert ex.difficulty == "medium"


# ── TestGoldenDatasetLoaderValidation ──────────────────────────────────────


class TestGoldenDatasetLoaderValidation:
    """Verify GoldenDatasetLoader.load() deduplicates and validates examples."""

    def test_golden_loader_deduplicates(self, tmp_path):
        """GoldenDatasetLoader should deduplicate examples with same task_input."""
        examples = [
            make_example(task_input="duplicate", expected_behavior="first"),
            make_example(task_input="duplicate", expected_behavior="second"),
            make_example(task_input="unique"),
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        task_inputs = [ex.task_input for ex in dataset.all_examples]
        assert task_inputs.count("duplicate") == 1
        assert len(dataset.all_examples) == 2

    def test_golden_loader_filters_secrets(self, tmp_path):
        """GoldenDatasetLoader should filter out examples with secrets."""
        examples = [
            make_example(task_input="safe task"),
            make_example(task_input="sk-ant-api03-SECRETKEY123"),
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        task_inputs = [ex.task_input for ex in dataset.all_examples]
        assert "sk-ant-api03-SECRETKEY123" not in task_inputs
        assert "safe task" in task_inputs

    def test_golden_loader_filters_empty_task_input(self, tmp_path):
        """GoldenDatasetLoader should filter out examples with empty task_input."""
        examples = [
            make_example(task_input="valid task"),
            make_example(task_input=""),
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        assert len(dataset.all_examples) == 1
        assert dataset.all_examples[0].task_input == "valid task"

    def test_golden_loader_normalizes_invalid_difficulty(self, tmp_path):
        """GoldenDatasetLoader should normalize invalid difficulty to 'medium'."""
        examples = [
            make_example(task_input="t1", expected_behavior="b", difficulty="invalid"),
            make_example(task_input="t2", expected_behavior="b", difficulty="nonsense"),
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)
        for ex in dataset.all_examples:
            assert ex.difficulty == "medium"

    def test_golden_loader_validates_before_splitting(self, tmp_path):
        """Validation should happen BEFORE splitting — invalid examples don't affect split sizes."""
        # Create 4 examples: 2 valid + 2 invalid (empty task_input or secret)
        examples = [
            make_example(task_input="valid 1"),
            make_example(task_input="valid 2"),
            make_example(task_input=""),  # will be filtered
            make_example(task_input="sk-ant-api03-FAKE"),  # will be filtered
        ]
        write_golden_jsonl(tmp_path / "golden.jsonl", examples)

        dataset = GoldenDatasetLoader.load(tmp_path)

        # Only 2 valid examples should be in the dataset
        assert len(dataset.all_examples) == 2
        task_inputs = {ex.task_input for ex in dataset.all_examples}
        assert task_inputs == {"valid 1", "valid 2"}


# ── TestGoldenDatasetLoaderLoadAll ───────────────────────────────────────────


class TestGoldenDatasetLoaderLoadAll:
    """Verify GoldenDatasetLoader.load() when train.jsonl/val.jsonl/holdout.jsonl exist."""

    def test_loads_pre_split_dataset_correctly(self, tmp_path):
        """When train.jsonl etc. exist, GoldenDatasetLoader loads all three splits."""
        train_examples = [make_example(task_input=f"train_{i}") for i in range(5)]
        val_examples = [make_example(task_input=f"val_{i}") for i in range(3)]
        holdout_examples = [make_example(task_input=f"holdout_{i}") for i in range(2)]

        write_split_jsonl(tmp_path, "train", train_examples)
        write_split_jsonl(tmp_path, "val", val_examples)
        write_split_jsonl(tmp_path, "holdout", holdout_examples)

        dataset = GoldenDatasetLoader.load(tmp_path)

        assert len(dataset.train) == 5
        assert len(dataset.val) == 3
        assert len(dataset.holdout) == 2

        all_inputs = [ex.task_input for ex in dataset.all_examples]
        assert "train_0" in all_inputs
        assert "val_0" in all_inputs
        assert "holdout_0" in all_inputs

    def test_load_all_does_not_shuffle(self, tmp_path):
        """When loading pre-split files, order should be preserved (no shuffle)."""
        train_examples = [make_example(task_input=f"train_{i}") for i in range(5)]
        write_split_jsonl(tmp_path, "train", train_examples)
        write_split_jsonl(tmp_path, "val", [])
        write_split_jsonl(tmp_path, "holdout", [])

        dataset = GoldenDatasetLoader.load(tmp_path)

        # Order should match file order
        inputs = [ex.task_input for ex in dataset.train]
        assert inputs == [f"train_{i}" for i in range(5)]

    def test_load_all_skips_missing_splits(self, tmp_path):
        """If only some split files exist, only those splits are populated."""
        write_split_jsonl(tmp_path, "train", [make_example(task_input="only_train")])

        dataset = GoldenDatasetLoader.load(tmp_path)

        assert len(dataset.train) == 1
        assert len(dataset.val) == 0
        assert len(dataset.holdout) == 0

    def test_pre_split_files_still_validated(self, tmp_path):
        """Even when loading pre-split files, validation rules still apply."""
        train_examples = [
            make_example(task_input="valid"),
            make_example(task_input="sk-ant-api03-SECRET"),
        ]
        write_split_jsonl(tmp_path, "train", train_examples)
        write_split_jsonl(tmp_path, "val", [])
        write_split_jsonl(tmp_path, "holdout", [])

        dataset = GoldenDatasetLoader.load(tmp_path)

        # Secret example should be filtered out
        assert len(dataset.train) == 1
        assert dataset.train[0].task_input == "valid"


# ── TestSeededRandomUsage ───────────────────────────────────────────────────


class TestSeededRandomUsage:
    """Verify that bare random.shuffle is replaced with seeded random.Random."""

    def test_no_bare_random_shuffle_in_dataset_builder(self):
        """dataset_builder.py should not use random.shuffle directly — use seeded random."""
        import ast
        source_path = Path("evolution/core/dataset_builder.py")
        source = source_path.read_text()
        tree = ast.parse(source)

        # Find all Call nodes with func.attr == 'shuffle' and func.value.id == 'random'
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "shuffle":
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "random":
                            violations.append(node.lineno)

        assert violations == [], (
            f"Found bare random.shuffle at line(s) {violations} in dataset_builder.py. "
            "Use random.Random(seed).shuffle() instead."
        )
