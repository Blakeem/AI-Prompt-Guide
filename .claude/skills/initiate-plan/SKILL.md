---
name: initiate-plan
description: "Execute development plans using sonnet/opus subagents. Run this after /develop creates a plan."
allowed-tools:
  - Read
  - Task
  - TodoWrite
  - Edit
---

# Workflow: Execute Development Plan

**Arguments:** $ARGUMENTS

**Purpose:** Execute development plans using appropriate subagents based on task complexity.

**Role Context:** You are the **Orchestrating Agent** coordinating Developer, Code Reviewer, and QA Verifier roles. The user is the **Product Owner**.

## [READ PLAN]

1. **Load current plan file**
   - Read the plan created by `/develop` skill
   - Extract tasks, dependencies, and complexity levels

2. **Create TodoWrite tracking**
   - Mirror plan tasks in TodoWrite for progress tracking

## [EXECUTE TASKS]

3. **Assign tasks to subagents based on complexity**

   **Simple/component work** → `developer` agent:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/developer.md

       Task: [Task description]
       Files: [Files to modify]
       Acceptance: [Criteria]

       Respond in terse mode: done/blockers only.
   ```

   **Complex/architectural work** → `senior-developer` agent:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: opus
   - prompt: |
       Use the methodology from agents/senior-developer.md

       Task: [Task description]
       Files: [Files to modify]
       Acceptance: [Criteria]

       Respond in terse mode: done/blockers only.
   ```

4. **Respect task dependencies**
   - Run independent tasks in parallel
   - Wait for dependencies before starting dependent tasks

## [CODE REVIEW] (Mandatory)

**Every implementation gets reviewed.** This is not optional.

5. **Run `code-reviewer` after implementation**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/code-reviewer.md

       Review files: [List of changed files]
       Focus: [Production standards, security, maintainability]
   ```

6. **Handle review findings with iteration loop**

   **If FAIL or PASS WITH FIXES:**
   - Assign required fixes back to appropriate Developer agent
   - Developer addresses specific issues raised (no over-correction)
   - Re-run code review
   - Repeat until PASS

   **If PASS:**
   - Proceed to QA verification

   Optional improvements: note for Product Owner follow-up.

## [QA VERIFICATION]

7. **Run `qa-verifier` after code review passes**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/qa-verifier.md

       Acceptance criteria: [From task/plan]
       Changed files: [List of files]

       Verify implementation meets all acceptance criteria.
   ```

8. **Handle verification results**

   **If NOT MET or PARTIAL with blocking gaps:**
   - Identify which criteria failed
   - Assign back to Developer with specific gaps
   - After fix, re-run code review, then QA verification
   - Repeat until VERIFIED

   **If VERIFIED:**
   - Task is complete

## [UPDATE & REPORT]

9. **Update plan file with progress**
   - Use `Edit` tool to mark completed tasks
   - Note any blockers or deviations

10. **Report summary to Product Owner**
    - Tasks completed
    - Blockers encountered
    - Review status (all passed)
    - QA verification status (all verified)
    - Files modified
