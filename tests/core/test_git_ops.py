"""Tests for evolution.core.git_ops module.

Verifies:
1. apply_to_branch() creates correct branch name format
2. apply_to_branch() replaces the correct SKILL.md file
3. apply_to_branch() commits the change
4. apply_to_branch() writes PR body to output_dir
5. build_pr_body() writes markdown file with correct content
6. Error case when hermes_path is not a git repo
7. Error case when skill file doesn't exist in hermes_path
"""

import subprocess
from pathlib import Path

import pytest


class TestApplyToBranch:
    """Tests for apply_to_branch() function."""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repo simulating hermes-agent structure."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create skills directory with a test skill
        skills_dir = tmp_path / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Original Skill Content\n")

        # Initial commit
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        return tmp_path

    def test_apply_to_branch_creates_correct_branch_name_format(self, git_repo, tmp_path):
        """apply_to_branch() should create a branch named evolution/<skill>/<timestamp>."""
        from evolution.core.git_ops import apply_to_branch

        skill_name = "test-skill"
        evolved_text = "# Evolved Skill Content\n"
        timestamp = "20240101_120000"
        output_dir = tmp_path / "output"

        result = apply_to_branch(
            skill_name=skill_name,
            evolved_skill_text=evolved_text,
            hermes_path=git_repo,
            output_dir=output_dir,
            timestamp=timestamp,
        )

        assert result.success is True, f"Expected success, got error: {result.error}"
        assert result.branch_name == f"evolution/{skill_name}/{timestamp}", (
            f"Expected branch name 'evolution/{skill_name}/{timestamp}', "
            f"got '{result.branch_name}'"
        )

    def test_apply_to_branch_replaces_correct_skill_file(self, git_repo, tmp_path):
        """apply_to_branch() should replace skills/<skill_name>/SKILL.md with evolved version."""
        from evolution.core.git_ops import apply_to_branch

        skill_name = "test-skill"
        evolved_text = "# EVOLVED SKILL - NEW CONTENT HERE\n"
        timestamp = "20240101_120000"
        output_dir = tmp_path / "output"

        apply_to_branch(
            skill_name=skill_name,
            evolved_skill_text=evolved_text,
            hermes_path=git_repo,
            output_dir=output_dir,
            timestamp=timestamp,
        )

        skill_file_path = git_repo / "skills" / skill_name / "SKILL.md"
        actual_content = skill_file_path.read_text()

        assert actual_content == evolved_text, (
            f"Expected skill file to contain evolved text, got: {actual_content}"
        )

    def test_apply_to_branch_commits_the_change(self, git_repo, tmp_path):
        """apply_to_branch() should commit the changed SKILL.md file."""
        from evolution.core.git_ops import apply_to_branch

        skill_name = "test-skill"
        evolved_text = "# Committed Evolved Content\n"
        timestamp = "20240101_120000"
        output_dir = tmp_path / "output"

        result = apply_to_branch(
            skill_name=skill_name,
            evolved_skill_text=evolved_text,
            hermes_path=git_repo,
            output_dir=output_dir,
            timestamp=timestamp,
        )

        assert result.success is True, f"Expected success, got error: {result.error}"
        assert result.commit_sha, "Expected a commit SHA to be returned"

        # Verify commit exists and contains the right message
        log_result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            cwd=git_repo,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_message = log_result.stdout.strip()
        assert skill_name in commit_message, (
            f"Expected commit message to contain skill name '{skill_name}', "
            f"got: {commit_message}"
        )

    def test_apply_to_branch_writes_pr_body_to_output_dir(self, git_repo, tmp_path):
        """apply_to_branch() should write PR body to output_dir/pr_body.md."""
        from evolution.core.git_ops import apply_to_branch

        skill_name = "test-skill"
        evolved_text = "# Evolved Skill Content\n"
        timestamp = "20240101_120000"
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result = apply_to_branch(
            skill_name=skill_name,
            evolved_skill_text=evolved_text,
            hermes_path=git_repo,
            output_dir=output_dir,
            timestamp=timestamp,
        )

        assert result.success is True, f"Expected success, got error: {result.error}"
        assert result.pr_body_path is not None, "Expected pr_body_path to be set"
        assert result.pr_body_path.exists(), (
            f"Expected pr_body.md to exist at {result.pr_body_path}"
        )

        pr_body_content = result.pr_body_path.read_text()
        assert skill_name in pr_body_content, (
            "Expected PR body to contain skill name"
        )

    def test_apply_to_branch_error_when_hermes_path_not_git_repo(self, tmp_path):
        """apply_to_branch() should return error when hermes_path is not a git repo."""
        from evolution.core.git_ops import apply_to_branch

        # Create a non-git directory
        not_git = tmp_path / "not-a-git-repo"
        not_git.mkdir()
        (not_git / "somefile.txt").write_text("content")

        result = apply_to_branch(
            skill_name="test-skill",
            evolved_skill_text="# Evolved",
            hermes_path=not_git,
            output_dir=tmp_path / "output",
            timestamp="20240101_120000",
        )

        assert result.success is False, "Expected failure when hermes_path is not a git repo"
        assert result.error is not None, "Expected an error message"
        assert "not a git repository" in result.error.lower() or "git" in result.error.lower()

    def test_apply_to_branch_error_when_skill_file_missing(self, git_repo, tmp_path):
        """apply_to_branch() should return error when skill file doesn't exist."""
        from evolution.core.git_ops import apply_to_branch

        result = apply_to_branch(
            skill_name="nonexistent-skill",
            evolved_skill_text="# Evolved",
            hermes_path=git_repo,
            output_dir=tmp_path / "output",
            timestamp="20240101_120000",
        )

        assert result.success is False, "Expected failure when skill file doesn't exist"
        assert result.error is not None, "Expected an error message"


class TestBuildPrBody:
    """Tests for build_pr_body() function."""

    def test_build_pr_body_writes_markdown_file(self, tmp_path):
        """build_pr_body() should write a markdown file to output_dir/pr_body.md."""
        from evolution.core.git_ops import build_pr_body

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result_path = build_pr_body(
            skill_name="test-skill",
            baseline_score=0.5,
            evolved_score=0.7,
            improvement_pct=40.0,
            constraint_passed=True,
            test_passed=True,
            holdout_count=10,
            output_dir=output_dir,
        )

        assert result_path == output_dir / "pr_body.md"
        assert result_path.exists(), f"Expected pr_body.md to exist at {result_path}"

    def test_build_pr_body_contains_skill_name(self, tmp_path):
        """build_pr_body() should include the skill name in the PR body."""
        from evolution.core.git_ops import build_pr_body

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result_path = build_pr_body(
            skill_name="my-awesome-skill",
            baseline_score=0.5,
            evolved_score=0.7,
            improvement_pct=40.0,
            constraint_passed=True,
            test_passed=True,
            holdout_count=10,
            output_dir=output_dir,
        )

        content = result_path.read_text()
        assert "my-awesome-skill" in content, (
            f"Expected PR body to contain skill name 'my-awesome-skill', got: {content}"
        )

    def test_build_pr_body_contains_score_improvement(self, tmp_path):
        """build_pr_body() should include baseline/evolved scores and improvement."""
        from evolution.core.git_ops import build_pr_body

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result_path = build_pr_body(
            skill_name="test-skill",
            baseline_score=0.5,
            evolved_score=0.7,
            improvement_pct=40.0,
            constraint_passed=True,
            test_passed=True,
            holdout_count=10,
            output_dir=output_dir,
        )

        content = result_path.read_text()
        # Check that scores are present
        assert "0.5" in content or "0.50" in content, (
            f"Expected baseline score in PR body, got: {content}"
        )
        assert "0.7" in content or "0.70" in content, (
            f"Expected evolved score in PR body, got: {content}"
        )
        assert "40" in content, (
            f"Expected improvement percentage in PR body, got: {content}"
        )

    def test_build_pr_body_contains_constraint_and_test_status(self, tmp_path):
        """build_pr_body() should include constraint_passed and test_passed status."""
        from evolution.core.git_ops import build_pr_body

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result_path = build_pr_body(
            skill_name="test-skill",
            baseline_score=0.5,
            evolved_score=0.7,
            improvement_pct=40.0,
            constraint_passed=True,
            test_passed=True,
            holdout_count=10,
            output_dir=output_dir,
        )

        content = result_path.read_text()
        # Check that constraint and test status are present
        assert "constraint" in content.lower(), (
            f"Expected constraint status in PR body, got: {content}"
        )

    def test_build_pr_body_contains_holdout_count(self, tmp_path):
        """build_pr_body() should include the holdout count."""
        from evolution.core.git_ops import build_pr_body

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        result_path = build_pr_body(
            skill_name="test-skill",
            baseline_score=0.5,
            evolved_score=0.7,
            improvement_pct=40.0,
            constraint_passed=True,
            test_passed=True,
            holdout_count=25,
            output_dir=output_dir,
        )

        content = result_path.read_text()
        assert "25" in content, (
            f"Expected holdout count '25' in PR body, got: {content}"
        )
