"""Git operations adapter for branch creation, file replacement, and commit.

Used by the evolution workflow to create review branches with evolved skills.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess
from datetime import datetime


@dataclass
class BranchResult:
    """Result of an apply_to_branch operation."""

    success: bool
    branch_name: str
    commit_sha: str
    pr_body_path: Path | None
    error: str | None


def apply_to_branch(
    skill_name: str,
    evolved_skill_text: str,
    hermes_path: Path,
    output_dir: Path,
    timestamp: str | None = None,
) -> BranchResult:
    """Create a review branch in hermes_agent_path with evolved skill.

    Creates a branch named `evolution/<skill_name>/<timestamp>`,
    replaces `skills/<skill_name>/SKILL.md` with evolved_skill_text,
    commits the change, and writes PR body to output_dir/pr_body.md.

    Args:
        skill_name: Name of the skill being evolved.
        evolved_skill_text: New content for the skill's SKILL.md file.
        hermes_path: Path to the hermes-agent repository.
        output_dir: Directory where PR body will be written.
        timestamp: Optional timestamp string for branch naming. Defaults to current time.

    Returns:
        BranchResult with success status, branch name, commit SHA, and PR body path.
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    branch_name = f"evolution/{skill_name}/{timestamp}"

    # Verify hermes_path is a git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=hermes_path,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip() != "true":
            return BranchResult(
                success=False,
                branch_name=branch_name,
                commit_sha="",
                pr_body_path=None,
                error="Not a git repository",
            )
    except subprocess.CalledProcessError:
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error="Not a git repository",
        )

    # Compute and validate skill file path - prevent path traversal
    skill_file_path = hermes_path / "skills" / skill_name / "SKILL.md"
    try:
        skill_file_path = skill_file_path.resolve()
        expected_prefix = (hermes_path / "skills").resolve()
        if not str(skill_file_path).startswith(str(expected_prefix)):
            return BranchResult(
                success=False,
                branch_name=branch_name,
                commit_sha="",
                pr_body_path=None,
                error="Invalid skill name: path traversal detected",
            )
    except (OSError, ValueError):
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error="Invalid skill name",
        )

    # Verify skill file exists
    if not skill_file_path.exists():
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error=f"Skill file not found: {skill_file_path}",
        )

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create and checkout the new branch FIRST (before any file modifications)
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=hermes_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error=f"Failed to create branch: {e.stderr}",
        )

    # Now write the evolved skill file (on the new branch)
    try:
        skill_file_path.write_text(evolved_skill_text)
    except OSError as e:
        # Attempt to return to original branch and report error
        subprocess.run(
            ["git", "checkout", "-"],
            cwd=hermes_path,
            capture_output=True,
        )
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error=f"Failed to write skill file: {e}",
        )

    # Stage and commit the changed skill file
    try:
        subprocess.run(
            ["git", "add", str(skill_file_path)],
            cwd=hermes_path,
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"Evolve skill: {skill_name}", "--allow-empty"],
            cwd=hermes_path,
            capture_output=True,
            text=True,
            check=True,
        )
        # Get the actual commit SHA using git rev-parse
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=hermes_path,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_sha = sha_result.stdout.strip()
    except subprocess.CalledProcessError as e:
        subprocess.run(
            ["git", "checkout", "-"],
            cwd=hermes_path,
            capture_output=True,
        )
        return BranchResult(
            success=False,
            branch_name=branch_name,
            commit_sha="",
            pr_body_path=None,
            error=f"Failed to commit: {e.stderr}",
        )

    # Write PR body placeholder (caller should overwrite with actual metrics via build_pr_body)
    pr_body_path = output_dir / "pr_body.md"
    pr_body_path.write_text(f"# Evolution Result for {skill_name}\n\n")

    return BranchResult(
        success=True,
        branch_name=branch_name,
        commit_sha=commit_sha,
        pr_body_path=pr_body_path,
        error=None,
    )


def build_pr_body(
    skill_name: str,
    baseline_score: float,
    evolved_score: float,
    improvement_pct: float,
    constraint_passed: bool,
    test_passed: bool | None,
    holdout_count: int,
    output_dir: Path,
) -> Path:
    """Write PR body markdown to output_dir/pr_body.md and return the path.

    Args:
        skill_name: Name of the evolved skill.
        baseline_score: Baseline evaluation score.
        evolved_score: Evolved skill evaluation score.
        improvement_pct: Percentage improvement from baseline to evolved.
        constraint_passed: Whether constraints were satisfied.
        test_passed: Whether tests passed (None if not run).
        holdout_count: Number of holdout examples evaluated.
        output_dir: Directory where pr_body.md will be written.

    Returns:
        Path to the created pr_body.md file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pr_body_path = output_dir / "pr_body.md"

    constraint_status = "✓ Passed" if constraint_passed else "✗ Failed"
    test_status = "✓ Passed" if test_passed is True else ("✗ Failed" if test_passed is False else "Not run")

    content = f"""# Evolve Skill: {skill_name}

## Summary
This PR introduces an evolved version of the **{skill_name}** skill.

## Performance

| Metric | Value |
|--------|-------|
| Baseline Score | {baseline_score:.3f} |
| Evolved Score | {evolved_score:.3f} |
| Improvement | {improvement_pct:+.1f}% |

## Validation

| Check | Status |
|-------|--------|
| Constraints | {constraint_status} |
| Tests | {test_status} |
| Holdout Examples | {holdout_count} |

## Changes
The skill content has been optimized using GEPA to improve performance on the evaluation dataset.
"""
    pr_body_path.write_text(content)
    return pr_body_path
