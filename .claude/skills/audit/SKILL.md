---
name: audit
description: "Comprehensive code audit with parallel specialist agents. Use for production readiness review, PR review, or targeted quality analysis."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - TodoWrite
---

# Workflow: Code Audit

**Arguments:** $ARGUMENTS

## [SETUP]

1. **Define scope:**
   - **Full codebase:** Default - audit entire project
   - **Targeted:** Specific files, directories, PR diff, or component
   - User provides scope or defaults to full

2. **Select issue types (3-6 recommended)**
   - Must include at least one from Essential
   - Add Common types based on scope/concerns

## [PARALLEL ANALYSIS]

3. **Launch parallel agents, one per issue type**

   For each issue type, use Task tool with:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: Include issue type, scope, and analysis instructions
   ```

4. **Each specialist scans and documents findings with:**
   - Location (file:line)
   - Severity (Critical/High/Medium/Low)
   - Impact description
   - Concrete fix recommendation

## [SYNTHESIS]

5. **Consolidate findings:**
   - Flag hot spots (issues found by multiple specialists)
   - Identify cross-cutting patterns
   - Generate prioritized action plan by severity
   - Summarize: severity counts, blocking items, recommendations

## Issue Types

### Essential (include at least one)

| Type | Focus |
|------|-------|
| **Security Vulnerabilities** | Injection, auth flaws, data exposure, OWASP top 10 |
| **Error Handling** | Uncaught exceptions, missing guards, silent failures |
| **Data Validation** | Input sanitization, type coercion, boundary checks |

### Common (select as needed)

| Type | Focus |
|------|-------|
| **Performance** | Big O complexity, unnecessary iterations, memory leaks |
| **Complexity** | Deep nesting, long functions, cyclomatic complexity |
| **Test Coverage** | Missing tests, untested edge cases, brittle tests |
| **Maintainability** | Readability, documentation, code organization |
| **Resource Management** | Unclosed handles, memory allocation, connection pooling |
| **Concurrency** | Race conditions, deadlocks, thread safety |
| **Anti-Patterns** | Magic numbers, duplication, tight coupling, god objects |

## Specialist Agent Prompt Template

```markdown
## Audit Assignment: [Issue Type]

You are auditing code for [Issue Type] issues.

## Scope
[Files/directories to analyze]

## Issue Type Focus
[Specific things to look for]

## Your Task

Scan the codebase and document ALL findings:

For each issue found:
- **Location:** file:line
- **Severity:** Critical/High/Medium/Low
- **Issue:** Brief description
- **Impact:** What could go wrong
- **Fix:** Concrete recommendation

## Severity Guidelines
- **Critical:** Security vulnerabilities, data loss risk - must fix
- **High:** Logic errors, performance issues - should fix
- **Medium:** Code smells, moderate improvements - consider fixing
- **Low:** Style, optimizations - nice to have
```

## Output Format

```markdown
## Audit Report: [Scope]

### Summary
- **Critical:** X issues
- **High:** Y issues
- **Medium:** Z issues
- **Low:** W issues

### Blocking Issues (Critical/High)

#### [Issue 1]
- **Location:** `path/to/file.ts:42`
- **Severity:** Critical
- **Issue:** [Description]
- **Impact:** [What could go wrong]
- **Fix:** [Recommendation]

### Hot Spots
[Files/areas with multiple issues across specialists]

### Cross-Cutting Patterns
[Systemic issues that appear throughout]

### Prioritized Action Plan
1. [Most critical fix]
2. [Second priority]
3. ...

### Recommendations
[Overall suggestions for code health]
```

## Quality Dimensions

| Dimension | Check For |
|-----------|-----------|
| **Correctness** | Logic errors, edge cases, off-by-one, null handling |
| **Security** | Validation, auth, sensitive data, injection vectors |
| **Performance** | Big O complexity, unnecessary work, resource efficiency |
| **Patterns** | Consistency with codebase idioms, SOLID principles |
| **Simplicity** | Over-engineering, unnecessary abstraction, clarity |
