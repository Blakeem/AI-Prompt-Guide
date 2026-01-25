---
name: initiate-plan-staged
description: "Execute development plans using git staging as quality gates between steps. Run this after /develop creates a plan."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - Bash
  - Edit
---

# Workflow: Execute Development Plan with Staged Quality Gates

**Arguments:** $ARGUMENTS

**Purpose:** Execute multi-step development plans with git staging as quality gates between steps. After each step passes review, changes are staged so the next git diff only shows new changes.

## [PRE-FLIGHT CHECK]

1. **Verify git is ready**
   ```bash
   git status --porcelain
   ```
   - Working state should be clean OR only contain planned changes
   - If unexpected changes exist, stop and report to user

2. **Load current plan file**
   - Read the plan created by `/develop` skill
   - Extract tasks, dependencies, and complexity levels
   - Identify which files each task will modify (to prevent conflicts)

## [EXECUTE TASKS]

3. **For each step/task in the plan:**

   ### a. Assign to Developer Subagent

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
       Do NOT stage changes - main agent handles staging.
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
       Do NOT stage changes - main agent handles staging.
   ```

   ### b. Handle New Files

   For any new files created by the subagent:
   ```bash
   git add -N <new-file>
   ```
   This marks intent-to-add so new files appear in `git diff` without staging content.

   ### c. Review Changes via Git Diff

   ```bash
   git diff
   ```
   - Review output for production readiness
   - Check for: correctness, security, maintainability, edge cases
   - Using git diff minimizes context compared to reading full files

   ### d. Fix Issues (if found)

   If review finds issues:
   - Assign back to developer subagent with specific feedback
   - Repeat review cycle until changes pass
   - Loop continues until production ready

   ### e. Stage Changes (Quality Gate)

   Once review passes:
   ```bash
   git add <files-modified-in-this-step>
   ```
   **Main orchestrating agent stages changes** - this is the quality gate.
   Subagents do NOT stage - only the main agent controls staging.

   ### f. Next Step

   The next step's `git diff` now only shows its own changes.
   This prevents regression and keeps reviews focused.

4. **Respect task dependencies**
   - Run independent tasks in parallel when files don't overlap
   - Wait for dependencies before starting dependent tasks
   - **Critical:** Divide work so subagents don't work on same files simultaneously

## [REPORT]

5. **Report summary after all steps complete**
   - Tasks completed
   - Blockers encountered
   - Files modified (now all staged)
   - Ready for commit message suggestion

## Important Notes

- **Main agent = quality gatekeeper**: Only the main agent stages changes
- **Subagents = workers**: They develop and respond terse, never stage
- **Git diff = review tool**: Minimizes context vs reading file contents
- **`git add -N`**: Makes new files visible in diff without committing content
- **File isolation**: Prevent multiple subagents from editing same file simultaneously
- **Staged changes persist**: Each step's staged changes are preserved for final commit
