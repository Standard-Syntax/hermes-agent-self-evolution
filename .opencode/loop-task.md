# Task

**Slice P1-009 — Add optional apply-to-Hermes branch workflow**

## Description

Add `--apply-to-branch` flag to the evolve_skill CLI that creates a local review branch in the Hermes agent repo with the evolved skill. This is NOT a full PR workflow — it creates a branch and commits the evolved SKILL.md, requiring human review before any merge.

## Changes

1. **Create `evolution/core/git_ops.py`** — Git operations adapter for branch creation, file replacement, and commit
2. **Modify `evolution/skills/evolve_skill.py`** — Add `--apply-to-branch` flag and wire it into the evolution flow
3. **Create `tests/core/test_git_ops.py`** — Test the git_ops module

## Acceptance criteria

- [ ] `--apply-to-branch` flag is added to the CLI
- [ ] `apply_to_branch(skill_name, evolved_skill_text, hermes_path, output_dir)` creates:
  - Branch named `evolution/<skill>/<timestamp>`
  - Replaces the target `skills/<skill_name>/SKILL.md` with evolved version
  - Commits the change
  - Writes PR body to `output_dir/pr_body.md`
- [ ] If `--apply-to-branch` is not provided, no branch is created (no-op)
- [ ] The branch workflow does NOT auto-open or auto-merge a PR
- [ ] Tests pass

## Files to modify

- `evolution/core/git_ops.py` (create new)
- `evolution/skills/evolve_skill.py` (add `--apply-to-branch` flag and call)
- `tests/core/test_git_ops.py` (create new)

## Code context

The evolve_skill.py already has all the pieces: it loads the skill, optimizes it, validates constraints, runs holdout evaluation, and writes output files. We just need to add the optional branch creation step at the end (step 13 in the pipeline).

Key integration point: after `writer.write_all(...)` in evolve_skill.py around line 460, if `apply_to_branch` is True, call `git_ops.apply_to_branch(...)`.

## API Design for git_ops.py

```python
@dataclass
class BranchResult:
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
    timestamp: str,
) -> BranchResult:
    """Create a review branch in hermes_agent_path with evolved skill."""
    ...

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
    """Write PR body markdown to output_dir/pr_body.md and return the path."""
    ...
```

## Loop Summary

### Critic feedback — iteration 1
- [BLOCK] CLI parameter name mismatch: `--apply-to-branch` derives variable `apply_to_branch`, but main() expected `should_apply_to_branch`. Fixed.
- [HIGH] `apply_to_branch()` had 5th mandatory `timestamp` argument not in spec. Made it optional with default.
- [HIGH] File was written before branch creation — if branch creation failed, repo was left corrupted. Fixed by creating branch first, then writing file.
- [MEDIUM] `commit_sha` was parsed incorrectly from git commit stdout. Fixed by using `git rev-parse HEAD` after commit.
- [MEDIUM] Path traversal vulnerability in skill_name. Fixed by resolving path and validating prefix.

### Final verdict: ACCEPTABLE

### Files changed
- `evolution/core/git_ops.py` (created)
- `evolution/skills/evolve_skill.py` (modified)
- `tests/core/test_git_ops.py` (created)

### Test results
11 passed in 0.16s
