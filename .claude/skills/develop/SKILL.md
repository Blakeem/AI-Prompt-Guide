---
name: develop
description: "Simple development with anti-pattern detection and regression prevention. Use for single-file or small scope features without needing multi-agent coordination."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
---

# Workflow: Simple Development with Best Practices

**Arguments:** $ARGUMENTS

## [ANALYZE]

1. **Understand Requirements**
   - Goal, expected behavior, affected files, unchanged scope

2. **Define Boundaries**
   - Files to change vs observe-only
   - Dependencies and scope limits

3. **Anti-Pattern Scan**
   - Check for: magic values, duplication, deep nesting, state mismanagement, silent failures, resource leaks, tight coupling
   - Flag problematic patterns for refactoring if in scope

4. **Select Approach**
   - IF multiple viable approaches: use `/decide` skill
   - Prioritize: correctness > best practices > simplicity
   - Align with existing patterns

## [IMPLEMENT]

5. **Create TODO List**
   - Use `TodoWrite` with specific, verifiable steps
   - Align with scope boundaries from step 2

6. **Execute Changes**
   - Follow existing conventions
   - Avoid anti-patterns:
     - Named constants (no magic values)
     - DRY (don't repeat yourself)
     - Single responsibility
     - Defensive programming
     - Proper cleanup
   - Comment complex logic and design rationale
   - Maintain minimal scope

## [VERIFY]

7. **Test Implementation**
   - Primary: Changed functionality
   - Secondary: Related functionality (regression)
   - Boundary: Edge cases and error handling
   - Verify unchanged areas untouched

8. **Document Findings**
   - Anti-patterns discovered/addressed
   - Technical debt created/removed
   - Suggested improvements (out of scope)

9. **Report Completion**
   - Changes summary
   - Files modified
   - Anti-patterns handled
   - Regression results
   - Future recommendations

## Impact Checkpoints

**Scope Control:**
- Change only what's necessary
- Document (don't implement) broader improvements

**Regression Prevention:**
- Test dependencies: what uses modified functionality?
- Anticipate side effects
- Validate edge cases

## Anti-Pattern Reference

| Pattern | Problem | Solution |
|---------|---------|----------|
| Magic values | Hard to maintain | Named constants |
| Duplication | Multiple update points | Extract shared function |
| Deep nesting | Hard to follow | Early returns, extraction |
| Silent failures | Hidden bugs | Explicit error handling |
| Resource leaks | Memory/handle issues | Proper cleanup |
| Tight coupling | Hard to test/change | Dependency injection |
