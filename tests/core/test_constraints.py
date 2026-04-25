"""Tests for constraint validators."""

import pytest
from evolution.core.constraints import ConstraintValidator
from evolution.core.config import EvolutionConfig


@pytest.fixture
def validator():
    config = EvolutionConfig()
    return ConstraintValidator(config)


class TestSizeConstraints:
    def test_skill_under_limit(self, validator):
        result = validator._check_size("x" * 1000, "skill")
        assert result.passed

    def test_skill_over_limit(self, validator):
        result = validator._check_size("x" * 20_000, "skill")
        assert not result.passed
        assert "exceeded" in result.message

    def test_tool_description_under_limit(self, validator):
        result = validator._check_size("Search files by content", "tool_description")
        assert result.passed

    def test_tool_description_over_limit(self, validator):
        result = validator._check_size("x" * 600, "tool_description")
        assert not result.passed


class TestGrowthConstraints:
    def test_acceptable_growth(self, validator):
        baseline = "x" * 1000
        evolved = "x" * 1100  # 10% growth
        result = validator._check_growth(evolved, baseline, "skill")
        assert result.passed

    def test_excessive_growth(self, validator):
        baseline = "x" * 1000
        evolved = "x" * 1300  # 30% growth
        result = validator._check_growth(evolved, baseline, "skill")
        assert not result.passed

    def test_shrinkage_is_ok(self, validator):
        baseline = "x" * 1000
        evolved = "x" * 800  # 20% smaller
        result = validator._check_growth(evolved, baseline, "skill")
        assert result.passed


class TestNonEmpty:
    def test_non_empty_passes(self, validator):
        result = validator._check_non_empty("some content")
        assert result.passed

    def test_empty_fails(self, validator):
        result = validator._check_non_empty("")
        assert not result.passed

    def test_whitespace_only_fails(self, validator):
        result = validator._check_non_empty("   \n  ")
        assert not result.passed


class TestSkillStructure:
    def test_valid_skill(self, validator):
        skill = "---\nname: test-skill\ndescription: A test skill\n---\n\n# Test\nContent here"
        result = validator._check_skill_structure(skill)
        assert result.passed

    def test_missing_frontmatter(self, validator):
        skill = "# Test\nContent without frontmatter"
        result = validator._check_skill_structure(skill)
        assert not result.passed

    def test_missing_name(self, validator):
        skill = "---\ndescription: A test skill\n---\n\n# Test"
        result = validator._check_skill_structure(skill)
        assert not result.passed

    def test_missing_description(self, validator):
        skill = "---\nname: test-skill\n---\n\n# Test"
        result = validator._check_skill_structure(skill)
        assert not result.passed


class TestValidateAll:
    def test_valid_skill_passes_all(self, validator):
        skill = "---\nname: test\ndescription: Test skill\n---\n\n# Procedure\n1. Do thing"
        results = validator.validate_all(skill, "skill")
        assert all(r.passed for r in results)

    def test_empty_skill_fails(self, validator):
        results = validator.validate_all("", "skill")
        failed = [r for r in results if not r.passed]
        assert len(failed) > 0


class TestBodyOnlyValidation:
    """Tests for validating body-only markdown (the evolved skill body).

    Bug: evolve_skill.py calls validate_all(skill["body"], "skill") which incorrectly
    applies skill_structure checks to body-only markdown that has no frontmatter.
    After fix, body-only should pass size/growth/non_empty but fail structure.
    """

    def test_body_only_should_pass_size_growth_nonempty(self, validator):
        """Body-only markdown should pass size, growth, and non_empty checks."""
        body_text = "# My Evolved Skill\n\n## Procedure\n1. Do new thing"
        results = validator.validate_all(body_text, "skill")
        size_result = next(r for r in results if r.constraint_name == "size_limit")
        non_empty_result = next(r for r in results if r.constraint_name == "non_empty")
        assert size_result.passed, "Body should pass size check"
        assert non_empty_result.passed, "Body should pass non_empty check"

    def test_body_only_should_fail_structure_only(self, validator):
        """Body-only markdown should fail ONLY structure check (no frontmatter)."""
        body_text = "# My Evolved Skill\n\n## Procedure\n1. Do new thing"
        results = validator.validate_all(body_text, "skill")
        failed = [r for r in results if not r.passed]
        # Should fail structure but pass other checks
        structure_result = next(r for r in results if r.constraint_name == "skill_structure")
        assert not structure_result.passed, "Body without frontmatter should fail structure check"
        # The bug: currently body-only fails ALL constraints because structure check
        # is applied to body without frontmatter

    def test_body_only_with_baseline_growth_check(self, validator):
        """Body-only validation should use baseline for growth check."""
        baseline = "# Original\n\nOriginal content here" * 10
        evolved = "# Evolved\n\nEvolved content here" * 11  # ~10% growth
        results = validator.validate_all(evolved, "skill", baseline_text=baseline)
        growth_result = next(r for r in results if r.constraint_name == "growth_limit")
        assert growth_result.passed, "Small growth should pass"


class TestCheckSkillStructureYAML:
    """Tests proving _check_skill_structure uses weak string matching instead of YAML.

    Bug: Uses "name:" in text[:500] instead of proper yaml.safe_load() parsing.
    This causes false positives when "name:" appears in markdown body content.
    """

    def test_string_matching_false_positive(self, validator):
        """Current implementation incorrectly passes when 'name:' appears in body.

        This test proves the bug: if 'name:' appears in markdown content,
        weak string matching sees it and incorrectly passes structure check.
        """
        # This skill has 'name:' only in markdown content, NOT in frontmatter
        # Frontmatter has no name field, but string matching finds 'name:' in body
        skill_with_name_in_body = """---
description: A test skill
---

# My Procedure
Use the name: parameter to configure this.
"""
        result = validator._check_skill_structure(skill_with_name_in_body)
        # BUG: weak string matching finds "name:" in body and incorrectly passes
        # After fix: should FAIL because frontmatter YAML has no name key
        assert not result.passed, (
            "Bug: weak string matching passes when 'name:' appears in body content. "
            "Should use yaml.safe_load() to parse frontmatter properly."
        )

    def test_string_matching_false_positive_description_in_body(self, validator):
        """Current implementation incorrectly passes when 'description:' appears in body."""
        skill_with_desc_in_body = """---
name: test-skill
---

# Procedure
The description: field is required for documentation.
"""
        result = validator._check_skill_structure(skill_with_desc_in_body)
        # BUG: weak string matching finds "description:" in body
        assert not result.passed, (
            "Bug: weak string matching should fail when description is only in body"
        )

    def test_proper_yaml_parsing_required(self, validator):
        """Frontmatter with invalid YAML structure should fail properly.

        Using yaml.safe_load() would catch that this frontmatter lacks
        required fields even if string matching would find them elsewhere.
        """
        # Frontmatter has neither name nor description as proper YAML keys
        invalid_frontmatter = """---
# This is a comment, not a name field
title: Some Title
---

# Content
"""
        result = validator._check_skill_structure(invalid_frontmatter)
        assert not result.passed, "Should fail - no name/description in frontmatter YAML"


class TestValidateSkillMethod:
    """Tests for the new validate_skill method that separates concerns.

    After fix: validate_skill(full_text, body_text, baseline_body_text) should:
    - validate_all(full_text, "skill_file") for structure validation
    - validate_all(body_text, "skill_body") for size/growth/non_empty checks
    """

    def test_validate_skill_method_exists(self, validator):
        """The validator should have a validate_skill method."""
        assert hasattr(validator, "validate_skill"), (
            "validate_skill method should exist to separate full skill vs body validation"
        )

    def test_validate_skill_separates_concerns(self, validator):
        """validate_skill should run correct validations for full skill vs body."""
        full_skill = "---\nname: test\ndescription: Test\n---\n\n# Body"
        body = "# Body content"
        results = validator.validate_skill(full_skill, body)
        # After fix: this should work without incorrectly applying structure check to body

    def test_validate_skill_with_baseline(self, validator):
        """validate_skill should use baseline_body_text for growth check."""
        baseline_body = "# Original\nContent" * 10
        evolved_body = "# Evolved\nNew Content" * 11
        full_skill = "---\nname: test\ndescription: Test\n---\n\n" + evolved_body
        results = validator.validate_skill(
            full_skill, evolved_body, baseline_body_text=baseline_body
        )
        # Should check growth against baseline_body_text, not full_skill

    def test_validate_skill_full_skill_passes(self, validator):
        """A valid full SKILL.md should pass all constraints."""
        full_skill = """---
name: test-skill
description: A valid test skill
---

# Procedure
1. Do the thing
"""
        body = "# Procedure\n1. Do the thing"
        results = validator.validate_skill(full_skill, body)
        assert all(r.passed for r in results), "Valid full skill should pass"

    def test_validate_skill_body_only_fails_structure(self, validator):
        """Body-only should fail structure check when reassembled."""
        frontmatter = "name: test\ndescription: Test"
        body = "# Evolved body"
        full_skill = f"---\n{frontmatter}\n---\n\n{body}"
        results = validator.validate_skill(full_skill, body)
        # Structure should pass because full_skill has valid frontmatter
        structure_result = next(r for r in results if r.constraint_name == "skill_structure")
        assert structure_result.passed


class TestSkillBodyArtifactType:
    """Tests for 'skill_body' artifact type handling.

    After fix: validate_all(text, "skill_body") should skip structure check
    since body-only markdown has no frontmatter.
    """

    def test_skill_body_skips_structure_check(self, validator):
        """skill_body type should not run structure validation."""
        body_only = "# Just markdown\nNo frontmatter here"
        results = validator.validate_all(body_only, "skill_body")
        # Should NOT have a skill_structure result at all
        structure_results = [r for r in results if r.constraint_name == "skill_structure"]
        assert len(structure_results) == 0, (
            "skill_body should skip structure check - no frontmatter to validate"
        )

    def test_skill_body_passes_size_check(self, validator):
        """skill_body should still validate size."""
        body = "# Body\n" + "x" * 100
        results = validator.validate_all(body, "skill_body")
        size_result = next(r for r in results if r.constraint_name == "size_limit")
        assert size_result.passed

    def test_skill_body_respects_size_limit(self, validator):
        """skill_body should fail if over size limit."""
        body = "# Body\n" + "x" * 20_000
        results = validator.validate_all(body, "skill_body")
        size_result = next(r for r in results if r.constraint_name == "size_limit")
        assert not size_result.passed

    def test_skill_body_growth_check(self, validator):
        """skill_body should support growth checking with baseline."""
        baseline = "# Original\n" + "x" * 1000
        evolved = "# Evolved\n" + "x" * 1100  # 10% growth
        results = validator.validate_all(evolved, "skill_body", baseline_text=baseline)
        growth_result = next(r for r in results if r.constraint_name == "growth_limit")
        assert growth_result.passed
