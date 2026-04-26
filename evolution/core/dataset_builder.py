"""Evaluation dataset generation for hermes-agent-self-evolution.

Sources:
A) Synthetic generation — LLM reads a skill/tool/prompt and generates test cases
B) SessionDB mining — extract real usage patterns and score with LLM-as-judge
C) Golden sets — hand-curated JSONL files
"""

import json
import random
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import dspy

from evolution.core.config import EvolutionConfig


SECRET_PATTERNS = re.compile(
    r'('
    r'sk-ant-api\S+'
    r'|sk-or-v1-\S+'
    r'|sk-\S{20,}'
    r'|ghp_\S+'
    r'|ghu_\S+'
    r'|xoxb-\S+'
    r'|xapp-\S+'
    r'|ntn_\S+'
    r'|AKIA[0-9A-Z]{16}'
    r'|Bearer\s+\S{20,}'
    r'|-----BEGIN\s+(RSA\s+)?PRIVATE\sKEY-----'
    r'|ANTHROPIC_API_KEY'
    r'|OPENAI_API_KEY'
    r'|OPENROUTER_API_KEY'
    r'|SLACK_BOT_TOKEN'
    r'|GITHUB_TOKEN'
    r'|AWS_SECRET_ACCESS_KEY'
    r'|DATABASE_URL'
    r'|\bpassword\s*[=:]\s*\S+'
    r'|\bsecret\s*[=:]\s*\S+'
    r'|\btoken\s*[=:]\s*\S{10,}'
    r')',
    re.IGNORECASE,
)

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def _contains_secret(text: str) -> bool:
    return bool(SECRET_PATTERNS.search(text))


def _validate_eval_example(
    task_input: str,
    expected_behavior: str,
    difficulty: str,
    category: str,
) -> Optional[dict]:
    if not task_input or not task_input.strip():
        return None
    if not expected_behavior or not expected_behavior.strip():
        return None
    difficulty = difficulty.strip().lower() if difficulty else "medium"
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = "medium"
    category = category.strip() if category else "general"
    if not category:
        category = "general"
    task_input = task_input.strip()[:2000]
    return {
        "task_input": task_input,
        "expected_behavior": expected_behavior.strip(),
        "difficulty": difficulty,
        "category": category,
    }


@dataclass
class EvalExample:
    """A single evaluation example."""
    task_input: str  # What the user asks
    expected_behavior: str  # Rubric — what a good response looks like
    difficulty: str = "medium"  # easy, medium, hard
    category: str = "general"  # Category for stratified eval
    source: str = "synthetic"  # synthetic, sessiondb, golden

    def to_dict(self) -> dict:
        return {
            "task_input": self.task_input,
            "expected_behavior": self.expected_behavior,
            "difficulty": self.difficulty,
            "category": self.category,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EvalExample":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class EvalDataset:
    """Train/val/holdout split of evaluation examples."""
    train: list[EvalExample] = field(default_factory=list)
    val: list[EvalExample] = field(default_factory=list)
    holdout: list[EvalExample] = field(default_factory=list)

    @property
    def all_examples(self) -> list[EvalExample]:
        return self.train + self.val + self.holdout

    def save(self, path: Path):
        """Save dataset splits to JSONL files."""
        path.mkdir(parents=True, exist_ok=True)
        for split_name, split_data in [("train", self.train), ("val", self.val), ("holdout", self.holdout)]:
            with open(path / f"{split_name}.jsonl", "w") as f:
                for ex in split_data:
                    f.write(json.dumps(ex.to_dict()) + "\n")

    @classmethod
    def load(cls, path: Path) -> "EvalDataset":
        """Load dataset splits from JSONL files."""
        dataset = cls()
        for split_name in ["train", "val", "holdout"]:
            split_file = path / f"{split_name}.jsonl"
            if split_file.exists():
                examples = []
                with open(split_file) as f:
                    for line in f:
                        if line.strip():
                            examples.append(EvalExample.from_dict(json.loads(line)))
                setattr(dataset, split_name, examples)
        return dataset

    def to_dspy_examples(self, split: str = "train") -> list[dspy.Example]:
        """Convert a split to DSPy Example objects."""
        data = getattr(self, split)
        return [
            dspy.Example(
                task_input=ex.task_input,
                expected_behavior=ex.expected_behavior,
            ).with_inputs("task_input")
            for ex in data
        ]


def validate_examples(examples: list[EvalExample]) -> list[EvalExample]:
    """Validate and deduplicate a list of EvalExample objects.

    Applies the following rules:
    - Drops examples with empty/whitespace-only task_input
    - Drops examples with empty/whitespace-only expected_behavior
    - Normalizes invalid difficulty to 'medium'
    - Defaults empty category to 'general'
    - Drops examples containing secrets in task_input or expected_behavior
    - Deduplicates by task_input (first occurrence wins)
    """
    seen_task_inputs: set[str] = set()
    validated: list[EvalExample] = []
    for ex in examples:
        result = _validate_eval_example(
            ex.task_input, ex.expected_behavior, ex.difficulty, ex.category
        )
        if result is None:
            continue
        if _contains_secret(result["task_input"]) or _contains_secret(result["expected_behavior"]):
            continue
        if result["task_input"] in seen_task_inputs:
            continue
        seen_task_inputs.add(result["task_input"])
        validated.append(EvalExample(
            task_input=result["task_input"],
            expected_behavior=result["expected_behavior"],
            difficulty=result["difficulty"],
            category=result["category"],
            source=ex.source,
        ))
    return validated


class SyntheticDatasetBuilder:
    """Generate evaluation datasets using a strong LLM.

    Reads the target artifact (skill file, tool description, etc.)
    and generates realistic (task_input, expected_behavior) pairs.
    """

    class GenerateTestCases(dspy.Signature):
        """Generate realistic evaluation test cases for an agent skill or tool.

        Given the full text of a skill/tool description, generate diverse test cases
        that would exercise different aspects of the skill. Each test case should include:
        - A realistic task_input (what a user would actually ask)
        - An expected_behavior rubric (what a good response should contain/do, NOT exact text)
        - A difficulty level (easy, medium, hard)
        - A category (what aspect of the skill this tests)
        """
        artifact_text: str = dspy.InputField(desc="The full text of the skill/tool/prompt being tested")
        artifact_type: str = dspy.InputField(desc="Type: 'skill', 'tool_description', or 'prompt_section'")
        num_cases: int = dspy.InputField(desc="Number of test cases to generate")
        test_cases: str = dspy.OutputField(desc="JSON array of test cases, each with: task_input, expected_behavior, difficulty, category")

    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.generator = dspy.ChainOfThought(self.GenerateTestCases)

    def generate(
        self,
        artifact_text: str,
        artifact_type: str = "skill",
        num_cases: Optional[int] = None,
    ) -> EvalDataset:
        """Generate a full eval dataset with train/val/holdout splits."""

        n = num_cases or self.config.eval_dataset_size

        # Configure DSPy to use the judge model for generation
        lm = dspy.LM(self.config.judge_model)

        with dspy.context(lm=lm):
            result = self.generator(
                artifact_text=artifact_text,
                artifact_type=artifact_type,
                num_cases=n,
            )

        # Parse the generated test cases
        try:
            cases_raw = json.loads(result.test_cases)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            match = re.search(r'\[.*\]', result.test_cases, re.DOTALL)
            if match:
                cases_raw = json.loads(match.group())
            else:
                raise ValueError(f"Could not parse test cases from LLM output: {result.test_cases[:200]}")

        examples = [
            EvalExample(
                task_input=c.get("task_input", ""),
                expected_behavior=c.get("expected_behavior", ""),
                difficulty=c.get("difficulty", "medium"),
                category=c.get("category", "general"),
                source="synthetic",
            )
            for c in cases_raw
            if c.get("task_input") and c.get("expected_behavior")
        ]

        examples = validate_examples(examples)

        rng = random.Random(self.config.seed)
        rng.shuffle(examples)
        n_total = len(examples)
        n_train = max(1, int(n_total * self.config.train_ratio))
        n_val = max(1, int(n_total * self.config.val_ratio))

        return EvalDataset(
            train=examples[:n_train],
            val=examples[n_train:n_train + n_val],
            holdout=examples[n_train + n_val:],
        )


class GoldenDatasetLoader:
    """Load hand-curated evaluation datasets from JSONL files.

    Class-method style (production): GoldenDatasetLoader.load(path)
    With explicit config: GoldenDatasetLoader.load(path, config)
    """

    def __init__(self, config: EvolutionConfig | None = None):
        self.config = config if config is not None else EvolutionConfig()

    def _load(self, path: Path) -> EvalDataset:
        """Internal load implementation."""
        if (path / "train.jsonl").exists():
            ds = EvalDataset.load(path)
            ds.train = validate_examples(ds.train)
            ds.val = validate_examples(ds.val)
            ds.holdout = validate_examples(ds.holdout)
            return ds

        golden_file = path if path.suffix == ".jsonl" else path / "golden.jsonl"
        if not golden_file.exists():
            raise FileNotFoundError(f"No golden dataset found at {golden_file}")

        examples = []
        with open(golden_file) as f:
            for line in f:
                if line.strip():
                    examples.append(EvalExample.from_dict(json.loads(line)))

        examples = validate_examples(examples)

        rng = random.Random(self.config.seed)
        rng.shuffle(examples)
        n = len(examples)
        n_train = max(1, int(n * 0.5))
        n_val = max(1, int(n * 0.25))

        return EvalDataset(
            train=examples[:n_train],
            val=examples[n_train:n_train + n_val],
            holdout=examples[n_train + n_val:],
        )

    @staticmethod
    def load(path: Path, config: EvolutionConfig | None = None) -> EvalDataset:
        """Load a golden dataset.

        Class-method style (production): GoldenDatasetLoader.load(path)
        or GoldenDatasetLoader.load(path, config) for seeded splitting.
        """
        cfg = config if config is not None else EvolutionConfig()
        loader = GoldenDatasetLoader(cfg)
        return loader._load(path)
