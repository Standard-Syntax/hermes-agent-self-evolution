"""Debug script for artifact test."""
import tempfile
from pathlib import Path

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

    # Find the Human Review Checklist section
    idx = content.find("Human Review Checklist")
    if idx >= 0:
        section = content[idx:idx+500]
        print("Human Review section:")
        print(repr(section))
        print()

    # Check for []
    print("[] in content:", "[]" in content)

    # Show every position where [ appears
    for i, c in enumerate(content):
        if c == '[':
            print(f"  [{i}]: {repr(content[max(0,i-2):i+3])}")
