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

## [READ PLAN]

1. **Load current plan file**
   - Read the plan created by `/develop` skill
   - Extract tasks, dependencies, and complexity levels

2. **Create TodoWrite tracking**
   - Mirror plan tasks in TodoWrite for progress tracking

## [EXECUTE TASKS]

3. **Assign tasks to subagents based on complexity**

   **Simple/component work** → `sonnet-developer` agent:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/sonnet-developer.md

       Task: [Task description]
       Files: [Files to modify]
       Acceptance: [Criteria]

       Respond in terse mode: done/blockers only.
   ```

   **Complex/architectural work** → `opus-developer` agent:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: opus
   - prompt: |
       Use the methodology from agents/opus-developer.md

       Task: [Task description]
       Files: [Files to modify]
       Acceptance: [Criteria]

       Respond in terse mode: done/blockers only.
   ```

4. **Respect task dependencies**
   - Run independent tasks in parallel
   - Wait for dependencies before starting dependent tasks

## [CODE REVIEW]

5. **Run `code-reviewer` after changes**

   **Required for:**
   - All opus-level work
   - Sonnet work touching critical paths

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/code-reviewer.md

       Review files: [List of changed files]
       Focus: [Production quality, security, maintainability]
   ```

6. **Handle review findings**
   - Required fixes: assign back to appropriate developer agent
   - Optional improvements: note for user follow-up

## [UPDATE & REPORT]

7. **Update plan file with progress**
   - Use `Edit` tool to mark completed tasks
   - Note any blockers or deviations

8. **Report summary to orchestrator**
   - Tasks completed
   - Blockers encountered
   - Review status
   - Files modified
