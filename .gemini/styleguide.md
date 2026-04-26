# Code Review Style Guide

Review pull requests for correctness, security, maintainability, test coverage, and performance.

## General review rules

- Prefer small, focused changes.
- Flag unclear naming, dead code, duplicated logic, and overly complex functions.
- Check whether behavior is covered by tests.
- Verify that errors are handled explicitly.
- Do not nitpick formatting if automated formatters already handle it.

## Python rules

- Target Python 3.13.
- Prefer typed function signatures for public functions.
- Prefer Google-style docstrings for public modules, classes, and functions.
- Prefer pathlib over raw string path manipulation.
- Avoid broad `except Exception` unless it is justified and logged.
- Flag unsafe subprocess, file, network, or deserialization behavior.
- Prefer `uv`-managed workflows when dependency commands are relevant.

## Spec-driven review rules

- Check whether implementation matches the related spec, plan, task, or acceptance criteria.
- Flag changes that appear outside the declared task scope.
- Ask for tests that map to acceptance criteria when missing.
- Prefer clear traceability from requirement to test to implementation.
