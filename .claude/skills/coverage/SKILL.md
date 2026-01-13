---
name: coverage
description: "Add comprehensive test coverage to existing code. Use when adding tests to legacy code or improving coverage for critical code paths."
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

# Workflow: Add Test Coverage

**Arguments:** $ARGUMENTS

## [SETUP] Analysis & Task Creation

1. **Analyze code and identify coverage gaps**
   - What code paths are untested?
   - What has the highest regression risk?
   - Prioritize by: critical paths > business logic > edge cases

2. **Create task list with TodoWrite**
   - Concise, focused test tasks
   - Specify scope: public APIs, business logic, error paths

3. **Identify test patterns in the codebase**
   - How are existing tests structured?
   - What testing frameworks/utilities are used?

## [EXECUTION] Per-Task Loop

4. **For each test task, delegate to agent:**

   Use Task tool with:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: Include test task, AAA pattern instructions, context files
   ```

5. **Agent executes:**
   - Reads existing test patterns
   - Writes tests using AAA pattern:
     - **Arrange:** Set up inputs and mocks
     - **Act:** Execute the code under test
     - **Assert:** Verify outputs and behavior
   - Runs test suite to verify tests pass

6. **Coordinator reviews against TEST STANDARDS:**
   - If issues: create fix task, repeat
   - If passed: `git add <test_files>`
   - Mark task complete in TodoWrite
   - Continue to next task

## [VERIFICATION] Final Quality Gate

7. **Run full test suite** - no regressions

8. **Verify coverage improvement**

9. **Report:** "Test coverage improved. Ready for review."

## Test Standards

### What to Test (Regression Prevention)

**DO Test:**
- Public APIs and interfaces
- I/O transformations
- Business rules and logic
- Critical workflows
- Error handling paths

**DON'T Test:**
- Private implementation details
- Library/framework internals
- Trivial getters/setters
- Highly volatile code (still changing)

### Mock External Dependencies

- APIs and network calls
- Databases and data stores
- File system operations
- Time and randomness

### Quality Gates

- [ ] Assert behavior (not internal state)
- [ ] Tests are deterministic
- [ ] Tests are order-independent
- [ ] One concept per test
- [ ] Clear, descriptive test names
- [ ] Minimal setup complexity

## Test Agent Prompt Template

```markdown
## Test Task
[Description of what to test]

## Target Code
[path/to/code-to-test.ts]

## Existing Test Patterns
[path/to/existing-tests.test.ts] - Follow this style

## Your Task

Write comprehensive tests using the AAA pattern:

1. **Arrange** - Set up inputs, mocks, and preconditions
2. **Act** - Execute the code under test
3. **Assert** - Verify outputs and expected behavior

Cover:
- Happy path scenarios
- Edge cases and boundary conditions
- Error handling paths

Run the tests to verify they pass.

Respond with "Done" when complete or "Blocked: [reason]" if stuck.
```

## Output Format

```markdown
## Coverage Report

### Tests Added
| File | Tests | Coverage Focus |
|------|-------|----------------|
| [test file] | X tests | [what's covered] |

### Coverage Improvement
- Before: X%
- After: Y%
- Delta: +Z%

### Untested Areas (if any)
[Areas still needing coverage and why they were skipped]

### Recommendations
[Suggestions for further coverage improvement]
```
