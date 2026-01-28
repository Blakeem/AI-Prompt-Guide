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

**Role Context:** You are the **Orchestrating Agent** coordinating Developer, Code Reviewer, and QA Verifier roles. The user is the **Product Owner**.

## [PRE-FLIGHT CHECK]

1. **Verify git is ready**
   ```bash
   git status --porcelain
   ```
   - Working state should be clean OR only contain planned changes
   - If unexpected changes exist, stop and report to Product Owner

2. **Load current plan file**
   - Read the plan created by `/develop` skill
   - Extract tasks, dependencies, and complexity levels
   - Identify which files each task will modify (to prevent conflicts)

## [EXECUTE TASKS]

3. **For each step/task in the plan:**

   ### a. Assign to Developer Subagent

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
       Do NOT stage changes - Orchestrating Agent handles staging.
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
       Do NOT stage changes - Orchestrating Agent handles staging.
   ```

   ### b. Handle New Files

   For any new files created by the subagent:
   ```bash
   git add -N <new-file>
   ```
   This marks intent-to-add so new files appear in `git diff` without staging content.

   ### c. Code Review (Mandatory)

   Run `code-reviewer` on changes:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/code-reviewer.md

       Review changes shown in git diff.
       Focus: [Production standards, security, maintainability]
   ```

   ### d. Handle Review Findings (Iteration Loop)

   **If FAIL or PASS WITH FIXES:**
   - Assign required fixes back to Developer with specific feedback
   - Developer addresses specific issues (no over-correction)
   - Re-run code review
   - Repeat until PASS

   **If PASS:**
   - Proceed to QA verification

   ### e. QA Verification

   Run `qa-verifier` after code review passes:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/qa-verifier.md

       Acceptance criteria: [From task/plan]
       Changed files: [List of files]

       Verify implementation meets acceptance criteria.
   ```

   **If NOT MET or PARTIAL with blocking gaps:**
   - Assign back to Developer with specific gaps
   - After fix, re-run code review, then QA verification
   - Repeat until VERIFIED

   ### f. Stage Changes (Quality Gate)

   Once both code review PASSES and QA VERIFIES:
   ```bash
   git add <files-modified-in-this-step>
   ```
   **Orchestrating Agent stages changes** - this is the quality gate.
   Subagents do NOT stage - only the Orchestrating Agent controls staging.

   ### g. Next Step

   The next step's `git diff` now only shows its own changes.
   This prevents regression and keeps reviews focused.

4. **Respect task dependencies**
   - Run independent tasks in parallel when files don't overlap
   - Wait for dependencies before starting dependent tasks
   - **Critical:** Divide work so subagents don't work on same files simultaneously

## [REPORT]

5. **Report summary to Product Owner after all steps complete**
   - Tasks completed
   - Blockers encountered
   - Review status (all passed)
   - QA verification status (all verified)
   - Files modified (now all staged)
   - Ready for commit message suggestion

## Important Notes

- **Orchestrating Agent = quality gatekeeper**: Only the Orchestrating Agent stages changes
- **Subagents = workers**: They develop and respond terse, never stage
- **Git diff = review tool**: Minimizes context vs reading file contents
- **`git add -N`**: Makes new files visible in diff without committing content
- **File isolation**: Prevent multiple subagents from editing same file simultaneously
- **Staged changes persist**: Each step's staged changes are preserved for final commit
- **Review is mandatory**: Every implementation gets code review AND QA verification
