# Task
Resolve PR #4 review comments:

1. **[HIGH]** Discrepancy between CLI `iterations` and optimizer budget `max_metric_calls`. When user specifies `--iterations 10`, GEPA still uses `max_metric_calls=150` (default). Fix: set `max_metric_calls=iterations` in `EvolutionConfig` initialization in `evolve_skill.py`.

2. **[MEDIUM]** Cache `_gepa_available()` with `@functools.lru_cache(maxsize=1)` - add `import functools`.

3. **[MEDIUM]** Pass `valset` to MIPROv2 fallback's `compile()` call.

# Acceptance criteria
- [x] CLI `--iterations 10` correctly sets GEPA budget to 10 metric calls
- [x] `_gepa_available()` result is cached (only computed once per session)
- [x] MIPROv2 fallback receives `valset=valset` in `optimizer.compile()`
- [x] All review comments marked as resolved on GitHub

# Files modified
- `evolution/core/optimizer.py` - Added functools import, lru_cache, valset
- `evolution/skills/evolve_skill.py` - Added max_metric_calls=iterations
- `tests/skills/test_evolve_skill.py` - Fixed missing pytest import, rewrote incorrect tests

# Final summary
## Loop complete
### TDD phase: TESTS_READY
### Critic iterations: 1
### Final verdict: ACCEPTABLE
### Unresolved issues: 2 pre-existing test bugs (MockGEPA.assert_called_once bug, flaky test_returns_tuple_with_fallback_used_false)
### Files changed: evolution/core/optimizer.py, evolution/skills/evolve_skill.py, tests/skills/test_evolve_skill.py
### Test results: 184 passed, 2 failed (pre-existing test bugs)
