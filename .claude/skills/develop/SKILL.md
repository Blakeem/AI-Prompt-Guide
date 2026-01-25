---
name: develop
description: "Orchestrate planning phase for development work. Gathers context, makes decisions, and creates execution plans."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
  - EnterPlanMode
---

# Workflow: Development Planning

**Arguments:** $ARGUMENTS

**Purpose:** Gather information and create a plan for development work. This skill handles research and planning, NOT execution.

## [GIT READINESS CHECK]

1. **Check git status before proceeding**
   - Run `git rev-parse --is-inside-work-tree` to check if this is a git repo
   - Run `git status --porcelain` to check for uncommitted changes

2. **Handle git state**
   - If NOT a git repo and task appears complex (multi-step, architectural changes):
     - Use `AskUserQuestion`: "This isn't a git repo. Would you like to initialize git for change tracking? (Recommended for complex work)"
     - If yes: run `git init`
   - If there ARE uncommitted changes:
     - Note this for the staging question below

## [ASSESS REQUIREMENTS]

3. **Identify what is known vs unknown**

   Before spawning subagents, categorize:

   **Known with confidence:**
   - Requirements clearly stated in the task
   - Patterns/conventions visible in the codebase

   **Uncertain - needs research:**
   - Technical approaches with multiple valid options
   - External API behaviors not yet documented

   **Uncertain - needs decision:**
   - Trade-offs between approaches
   - Architectural choices with long-term implications

   **Uncertain - needs user input:**
   - Business requirements not specified
   - Preferences for specific technologies

4. **Route uncertainties appropriately**
   - Research items → GATHER CONTEXT with targeted subagents
   - Decision items → queue for DECISIONS phase (decider agent)
   - User items → queue for CLARIFY phase

## [GATHER CONTEXT]

5. **Spawn exploration subagents as needed**
   - Use `Task` tool to explore codebase, find patterns, understand architecture
   - Parallel exploration for independent areas

6. **Research unknowns**
   - Use `web-researcher` agent for external documentation
   - Read relevant files to understand existing patterns

## [INTEGRATION PLANNING] (when task involves external APIs/systems)

7. **For integration work, apply Spec-First methodology:**
   - Map entry points: candidate integration surfaces
   - Choose sync vs async by latency/throughput/ordering needs
   - Propose 2-4 compliant designs; prefer smallest solution meeting all constraints
   - Quick conformance checklist: inputs, outputs, errors, timeouts, retries, idempotency

## [DECISIONS]

8. **Use `decider` agent for decisions with trade-offs**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/decider.md

       Decision: [What we're deciding]
       Constraints: [Non-negotiables]
       Stakes: [low|medium|high]
   ```

## [CLARIFY]

9. **Ask user questions after research**
   - Use `AskUserQuestion` tool to clarify requirements
   - Present options discovered during research
   - Confirm approach before planning

10. **For complex tasks, ask about staging approach**

   Determine if task is complex (multi-step, risky changes, architectural work).

   If complex, use `AskUserQuestion` with these options:
   - If uncommitted changes exist:
     ```
     "This task is complex. Would you like to use staged development with git checkpoints?

     Note: You have uncommitted changes.

     Options:
     1. Yes, use staged development (will commit changes at checkpoints)
     2. Yes, but first let me commit my current changes
     3. No, proceed without checkpoints"
     ```
   - If no uncommitted changes:
     ```
     "This task is complex. Would you like to use staged development with git checkpoints?

     Staged development commits at each milestone, making it easy to review or rollback.

     Options:
     1. Yes, use staged development
     2. No, proceed without checkpoints"
     ```

   Record user choice for plan header.

## [PLAN]

11. **Enter plan mode for any non-trivial work**
    - Use `EnterPlanMode` tool
    - Plan file header depends on task complexity and user choice:
      - **Simple tasks OR user chose no staging:** Start with "Run `/initiate-plan` skill first"
      - **Complex tasks with staging:** Start with "Run `/initiate-plan-staged` skill first"

12. **Plan describes WHAT to do, not HOW subagents will do it**
   - Clear task breakdown
   - Dependencies between tasks
   - Acceptance criteria
   - Files likely to be affected

## Plan File Template (Simple/No Staging)

```markdown
Run `/initiate-plan` skill first to execute this plan.

## Summary
[Brief description of what this plan accomplishes]

## Tasks

### 1. [Task Name]
- **Description:** [What needs to be done]
- **Files:** [Files likely affected]
- **Acceptance:** [How to verify completion]
- **Complexity:** [simple|medium|complex]

### 2. [Task Name]
...

## Dependencies
- Task 2 depends on Task 1
- Tasks 3 and 4 can run in parallel

## Notes
[Any context for execution]
```

## Plan File Template (Complex with Staging)

```markdown
Run `/initiate-plan-staged` skill first to execute this plan.

## Summary
[Brief description of what this plan accomplishes]

## Stages

### Stage 1: [Stage Name]
**Checkpoint:** [What should be committable after this stage]

#### Tasks
1. [Task Name]
   - **Description:** [What needs to be done]
   - **Files:** [Files likely affected]
   - **Acceptance:** [How to verify completion]

### Stage 2: [Stage Name]
**Checkpoint:** [What should be committable after this stage]

#### Tasks
1. [Task Name]
...

## Dependencies
- Stage 2 depends on Stage 1
- Tasks within a stage can run in parallel if independent

## Rollback Points
- After Stage 1: [What can be safely rolled back to]
- After Stage 2: [What can be safely rolled back to]

## Notes
[Any context for execution]
```
