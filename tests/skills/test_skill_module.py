"""Tests for skill module loading and parsing."""

import pytest
from pathlib import Path
from evolution.skills.skill_module import load_skill, reassemble_skill


SAMPLE_SKILL = """---
name: test-skill
description: A skill for testing things
version: 1.0.0
metadata:
  hermes:
    tags: [testing]
---

# Test Skill — Testing Things

## When to Use
Use this when you need to test things.

## Procedure
1. First, do the thing
2. Then, verify it worked
3. Report results

## Pitfalls
- Don't forget to check edge cases
"""


class TestLoadSkill:
    def test_parses_frontmatter(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(SAMPLE_SKILL)
        skill = load_skill(skill_file)

        assert skill["name"] == "test-skill"
        assert skill["description"] == "A skill for testing things"
        assert "version: 1.0.0" in skill["frontmatter"]

    def test_parses_body(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(SAMPLE_SKILL)
        skill = load_skill(skill_file)

        assert "# Test Skill" in skill["body"]
        assert "## Procedure" in skill["body"]
        assert "Don't forget" in skill["body"]

    def test_raw_contains_everything(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(SAMPLE_SKILL)
        skill = load_skill(skill_file)

        assert skill["raw"] == SAMPLE_SKILL

    def test_path_is_stored(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(SAMPLE_SKILL)
        skill = load_skill(skill_file)

        assert skill["path"] == skill_file


class TestReassembleSkill:
    def test_roundtrip(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(SAMPLE_SKILL)
        skill = load_skill(skill_file)

        reassembled = reassemble_skill(skill["frontmatter"], skill["body"])
        assert "---" in reassembled
        assert "name: test-skill" in reassembled
        assert "# Test Skill" in reassembled

    def test_preserves_frontmatter(self):
        frontmatter = "name: my-skill\ndescription: Does stuff"
        body = "# My Skill\nDo the thing."
        result = reassemble_skill(frontmatter, body)

        assert result.startswith("---\n")
        assert "name: my-skill" in result
        assert "# My Skill" in result

    def test_evolved_body_replaces_original(self):
        frontmatter = "name: my-skill\ndescription: Does stuff"
        evolved_body = "# EVOLVED\nNew and improved procedure."
        result = reassemble_skill(frontmatter, evolved_body)

        assert "EVOLVED" in result
        assert "New and improved" in result


class TestEvolvedSkillReassembly:
    """Tests for the evolved skill reassembly and validation flow.

    This tests the full loop: load skill -> evolve body -> reassemble -> validate.
    The bug: evolved body (markdown only) fails structure validation because
    validate_all(body, "skill") applies frontmatter checks to body-only content.
    """

    def test_reassembled_skill_is_valid_full_skill(self, tmp_path):
        """Reassembled skill should be a valid full SKILL.md with frontmatter."""
        frontmatter = "name: test-skill\ndescription: A test skill"
        evolved_body = "# EVOLVED\nNew procedure content"
        reassembled = reassemble_skill(frontmatter, evolved_body)

        # Should have proper frontmatter markers
        assert reassembled.startswith("---\n")
        assert "---\n\n" in reassembled  # frontmatter ends, body begins
        # Should be valid for structure validation
        assert "name: test-skill" in reassembled
        assert "description: A test skill" in reassembled
        assert "# EVOLVED" in reassembled

    def test_reassembled_skill_passes_structure_check(self, tmp_path):
        """Reassembled skill should pass structure validation.

        This is the key test: after reassembly, the evolved body combined
        with original frontmatter should pass all constraints.
        """
        from evolution.core.constraints import ConstraintValidator
        from evolution.core.config import EvolutionConfig

        frontmatter = "name: evolved-skill\ndescription: An evolved skill"
        evolved_body = "# EVOLVED\nNew improved procedure."
        reassembled = reassemble_skill(frontmatter, evolved_body)

        val = ConstraintValidator(EvolutionConfig())
        results = val.validate_all(reassembled, "skill")
        structure_result = next(r for r in results if r.constraint_name == "skill_structure")
        assert structure_result.passed, (
            "Reassembled skill should pass structure check. "
            "Bug: current code validates body-only as 'skill' which fails."
        )

    def test_body_only_fails_structure_validation(self, tmp_path):
        """Body-only markdown should fail structure validation.

        This proves the bug: when evolve_skill.py calls validate_all(skill["body"], "skill"),
        it incorrectly fails because body has no frontmatter.
        """
        from evolution.core.constraints import ConstraintValidator
        from evolution.core.config import EvolutionConfig

        body_only = "# EVOLVED\nNew improved procedure."
        val = ConstraintValidator(EvolutionConfig())

        results = val.validate_all(body_only, "skill")
        structure_result = next(r for r in results if r.constraint_name == "skill_structure")

        # The bug manifests here: body-only fails structure check
        # because the code expects frontmatter that body doesn't have
        assert not structure_result.passed, (
            "Body-only markdown should fail structure check (no frontmatter). "
            "This proves the bug exists - after fix, body-only validation "
            "should use 'skill_body' type or validate_skill() method."
        )

    def test_validate_skill_for_reassembled_flow(self, tmp_path):
        """Test that validate_skill handles reassembled skill correctly.

        After fix: validate_skill(reassembled, evolved_body) should:
        1. Check structure on full_text (reassembled)
        2. Check size/growth on body_text (evolved_body)
        """
        from evolution.core.constraints import ConstraintValidator
        from evolution.core.config import EvolutionConfig

        frontmatter = "name: test\ndescription: Test skill"
        evolved_body = "# EVOLVED\nNew content" * 100
        reassembled = reassemble_skill(frontmatter, evolved_body)

        val = ConstraintValidator(EvolutionConfig())

        if hasattr(val, "validate_skill"):
            results = val.validate_skill(reassembled, evolved_body)
            # Should pass: full skill has valid frontmatter, body is reasonable size
            assert any(r.passed for r in results if r.constraint_name == "skill_structure")
        else:
            # Before fix: validate_skill doesn't exist - this is the bug
            pytest.fail("validate_skill method should exist after fix")

    def test_roundtrip_load_evolve_reassemble(self, tmp_path):
        """Full roundtrip: load -> extract body -> evolve -> reassemble -> should be valid.

        This simulates the evolution flow and validates the result.
        """
        from evolution.skills.skill_module import load_skill, reassemble_skill

        original_skill = """---
name: roundtrip-test
description: Testing roundtrip
---

# Original Procedure
1. Do original thing
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(original_skill)

        # Load skill (splits into frontmatter + body)
        skill = load_skill(skill_file)
        assert skill["body"] == "# Original Procedure\n1. Do original thing"
        assert skill["frontmatter"] == "name: roundtrip-test\ndescription: Testing roundtrip"

        # Simulate evolution: body changes, frontmatter stays same
        evolved_body = "# EVOLVED Procedure\n1. Do evolved thing better"
        reassembled = reassemble_skill(skill["frontmatter"], evolved_body)

        # Reassembled should be a valid skill file
        assert reassembled.startswith("---\n")
        assert "---\n\n" in reassembled
        assert "name: roundtrip-test" in reassembled
        assert "# EVOLVED Procedure" in reassembled

        # The reassembled skill should have the evolved body
        assert "original thing" not in reassembled  # old body replaced
        assert "evolved thing" in reassembled  # new body present
