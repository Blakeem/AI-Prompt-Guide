---
name: develop-fix
description: "Systematic bug fixing with root cause analysis and regression prevention. Use when debugging issues, fixing bugs, or resolving errors with minimal scope."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
---

# Workflow: Bug Fix with Root Cause Analysis

**Arguments:** $ARGUMENTS

## [REPRODUCE & ANALYZE]

1. **Reproduce and document**
   - Expected vs actual behavior
   - Reproduction steps
   - Error messages
   - Observations

2. **Map data flow**
   - Input -> Processing -> Output
   - Identify all components involved

3. **Locate failure point**
   - Pinpoint function/line
   - Capture state at failure
   - Apply root cause analysis (Five Whys technique):
     - WHY does bug occur?
     - What assumption violated?
     - What condition unhandled?
     - Is this symptomatic of deeper issue?
     - Could it recur elsewhere?

## [SCOPE & PLAN]

4. **Define minimal scope**
   - SMALLEST effective change
   - List files: MUST change / MIGHT change / SHOULD NOT change

5. **Scan for anti-patterns**
   - Check bug vicinity for common patterns (see Anti-Pattern Detection below)

6. **Evaluate approaches**
   - IF multiple fixes exist, use `/decide` skill
   - Prioritize: correctness > root cause > minimal scope > no regression

7. **Create task plan**
   - Use `TodoWrite` with specific testable steps
   - Include verification and regression tests

## [IMPLEMENT & VERIFY]

8. **Implement minimal fix**
   - Necessary changes only
   - Follow conventions
   - Add WHY comments
   - Avoid unrelated refactoring

9. **Verify comprehensively**
   - [ ] Reproduction steps pass
   - [ ] Edge cases handled
   - [ ] Related functionality intact
   - [ ] No new issues

10. **Document and report**
    - Code comments (WHY/root cause/constraints)
    - Findings summary
    - Anti-patterns flagged
    - Architecture suggestions if design flaw detected

## Root Cause Analysis

**Five Whys Technique:** Ask "Why?" iteratively until reaching root cause (not symptom)

**Common Root Causes:**
- Assumption violations (unguaranteed data/state)
- Edge case gaps (boundary condition failures)
- Race conditions (async ordering)
- State inconsistency (sync failures)
- Missing error handling (broken error paths)
- Design flaws (architectural mismatch)

## Anti-Pattern Detection

| Category | Signs | Fix |
|----------|-------|-----|
| Null/Undefined | Unchecked access, missing guards | Defensive checks |
| State & Data | Stale data, direct mutation | Immutable patterns |
| Async & Timing | Unhandled errors, resource leaks | Proper cleanup |
| Logic | Off-by-one, wrong operators | Boundary checks |

## Minimal Fix Scope

| Category | Examples |
|----------|----------|
| **Must Change** | Bug-causing code + related tests |
| **Might Change** | Dependent code, related error handling |
| **Should Not** | Unrelated functionality, style, refactoring |
| **Document Only** | Technical debt, architecture improvements |

## Regression Prevention Checklist

- [ ] Bug fixed (reproduction passes)
- [ ] Edge cases handled
- [ ] Related features intact
- [ ] No new errors/warnings
- [ ] Minimal scope maintained

## Code Comment Patterns

- "Fix: handles [case] because [root cause]"
- "Previously failed when [condition] - now checks [guard]"
- "Root cause: assumed [X] but [Y] can occur when [condition]"
