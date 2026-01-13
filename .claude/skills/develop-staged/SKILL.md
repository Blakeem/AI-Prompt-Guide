---
name: develop-staged
description: "Orchestrate multi-agent staged development with manual verification. Use for features, fixes, or prototypes where manual verification is preferred over automated testing."
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

# Workflow: Multi-Agent Development with Manual Verification

**Arguments:** $ARGUMENTS

## Overview

This workflow uses staged task execution with manual review between stages. The coordinator (you) manages the todo list and delegates implementation tasks to the `mid-level-developer` or `senior-developer` agents via the Task tool.

## [SETUP]

1. **Analyze requirements, break into work units**
   - What are the distinct implementation steps?
   - What dependencies exist between steps?

2. **Create task list with TodoWrite**
   - Specific, verifiable steps
   - Order by dependencies
   - Include acceptance criteria for each

3. **Identify relevant context files**
   - Specs, existing code, patterns to follow
   - Note file paths for subagent context

## [TASK LOOP]

**For each task:**

4. **Select appropriate agent**
   - `mid-level-developer` (Sonnet) - standard implementation
   - `senior-developer` (Opus) - complex logic, architecture decisions

5. **Delegate via Task tool**
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet (or opus for senior-developer)
   - prompt: Include task description, file paths, acceptance criteria
   - Ask agent to respond "Done" or "Blocked: [reason]"
   ```

6. **[CLEAN SLATE REVIEW]** - Review code changes directly:
   - **Security:** input validation, auth checks, data exposure
   - **Performance:** Big O complexity, unnecessary iterations, resource leaks
   - **Correctness:** edge cases, null handling, error paths
   - **Patterns:** consistency with codebase idioms, SOLID principles

7. **Verify against acceptance criteria**
   - If issues: create fix task, return to step 4
   - If passed: continue

8. **Stage changes:** `git add <modified_files>`

9. **Mark task complete in TodoWrite**

10. **If more tasks remain:** return to step 4

## [COMPLETION]

11. **Execute project testing procedures**
    - Run test suite
    - Build verification
    - Lint/type checks

12. **Verify all acceptance criteria met**

13. **Report:** "Development complete. Ready for review."

## Agent Delegation Pattern

When delegating to an agent, provide:

```markdown
## Task
[Clear task description]

## Context Files
- [path/to/relevant/file.ts]
- [path/to/spec.md]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Instructions
Implement this task following existing patterns. Read the context files first.
Respond with "Done" when complete or "Blocked: [reason]" if you cannot proceed.
```

## Review Checklist

After each subagent completes:

- [ ] Changes match acceptance criteria
- [ ] No security issues introduced
- [ ] Performance is acceptable
- [ ] Code follows existing patterns
- [ ] Error handling is appropriate
