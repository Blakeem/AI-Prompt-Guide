---
name: develop-staged-tdd
description: "Orchestrate multi-agent staged development with TDD and quality gates. Use for features or fixes requiring test-driven development."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - TodoWrite
---

# Workflow: Multi-Agent Development with TDD

**Arguments:** $ARGUMENTS

## Overview

This workflow combines staged development with Test-Driven Development. Each implementation task follows the Red-Green-Refactor cycle, with quality gates enforced between stages.

## [SETUP]

1. **Analyze requirements, decompose into work units**
   - What needs to be built?
   - What tests will verify each unit?

2. **Create task list with TodoWrite**
   - Each task includes: implementation + tests
   - Testable acceptance criteria
   - Dependencies between tasks

3. **Identify context files**
   - Test patterns in the codebase
   - Existing specs and implementations

## [EXECUTION LOOP]

**For each task:**

4. **Select appropriate agent**
   - `mid-level-developer` (Sonnet) - standard implementation
   - `senior-developer` (Opus) - complex logic

5. **Delegate via Task tool with TDD instructions**
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet (or opus)
   - prompt: Include TDD cycle instructions
   ```

6. **Agent executes TDD cycle:**
   - **Red:** Write failing test first
   - **Green:** Minimal implementation to pass
   - **Refactor:** Improve while tests pass

7. **[CLEAN SLATE REVIEW]** - Review code changes:
   - **Security:** input validation, auth checks, data exposure
   - **Performance:** Big O complexity, resource management
   - **Correctness:** edge cases, null handling, error paths
   - **Patterns:** codebase consistency, SOLID principles
   - **Test Quality:** coverage, assertions, isolation

8. **Run quality gates:**
   - All tests pass
   - Lint checks pass
   - Type checks pass (if applicable)
   - If fail: create fix task, return to step 4

9. **Stage changes:** `git add <modified_files>`

10. **Mark task complete in TodoWrite**

11. **If more tasks remain:** return to step 4

## [FINALIZATION]

12. **Run full test suite + project gates**

13. **Verify all acceptance criteria met**

14. **Report:** "Development complete. Ready for review."

## TDD Agent Prompt Template

```markdown
## Task
[Clear task description]

## TDD Cycle
Follow this cycle strictly:

1. **RED** - Write a failing test first
   - Test should verify the expected behavior
   - Run test to confirm it fails

2. **GREEN** - Write minimal code to pass
   - Implement just enough to make the test pass
   - Do not add extra functionality

3. **REFACTOR** - Improve while green
   - Clean up code while tests pass
   - Improve readability, remove duplication

## Context Files
- [path/to/test-patterns.ts]
- [path/to/implementation.ts]

## Acceptance Criteria
- [ ] Tests written before implementation
- [ ] All tests pass
- [ ] Code follows existing patterns

Respond with "Done" when complete or "Blocked: [reason]" if stuck.
```

## Quality Standards

**TDD Cycle:**
- Red (failing test) -> Green (minimal impl) -> Refactor (improve)

**Test Quality:**
- Assert behavior (not internal state)
- Deterministic, order-independent
- One concept per test
- Clear, descriptive names

**Quality Gates (must pass):**
- All tests pass
- Lint clean
- Type checks pass
- Coverage maintained or improved
