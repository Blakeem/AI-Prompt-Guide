---
name: develop-staged
description: "Orchestrate complex development work with git staging as quality gates between steps. Use for multi-step tasks requiring checkpoints."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---

# Workflow: Development with Staged Quality Gates

**Arguments:** $ARGUMENTS

**Purpose:** Orchestrate complex, multi-step development work with git staging as quality gates between steps. After each step passes review, changes are staged so the next git diff only shows new changes.

**When to use:** Choose `/develop-staged` over `/develop` when:
- Task has multiple distinct steps/phases
- You want rollback capability between steps
- Changes are risky or architectural
- You want focused code reviews (one step at a time)

**Role Context:** You are the **Orchestrating Agent**. The user is the **Product Owner** who provides requirements and approves significant work.

## Delegation Principle

The Orchestrating Agent coordinates but NEVER implements directly. All work flows through subagents:
- Codebase exploration → Explore agents
- External research → researcher agent
- Decisions → architect agent
- Implementation → developer/senior-developer agents
- Quality gates → code-reviewer and qa-verifier agents

**Ask the Product Owner (user) only for:**
- Business requirements clarification
- Feature preference decisions
- Approval to proceed with significant work

**Do NOT ask the Product Owner for:**
- Technical implementation decisions (use architect agent)
- Code review (use code-reviewer agent)
- Verification (use qa-verifier agent)

---

## [PRE-FLIGHT CHECK]

1. **Verify git is ready**
   ```bash
   git status --porcelain
   ```
   - Working state should be clean OR only contain planned changes
   - If unexpected uncommitted changes exist, use `AskUserQuestion` to ask Product Owner how to proceed

2. **Check if this is a git repo**
   - Run `git rev-parse --is-inside-work-tree`
   - If NOT a git repo:
     - Use `AskUserQuestion`: "This isn't a git repo. Staged development requires git for checkpoints. Initialize git?"
     - If yes: run `git init`
     - If no: suggest using `/develop` instead

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
   - Research items → GATHER CONTEXT (only if needed)
   - Decision items → DECISIONS phase (architect agent)
   - User items → CLARIFY phase

5. **Break work into logical steps**
   - Each step should be independently reviewable and committable
   - Identify files each step will modify (to prevent conflicts)
   - Steps execute sequentially; tasks within a step can be parallel

## [GATHER CONTEXT] (Conditional)

**Research Depth Principle:**
Research should be proportional to task unfamiliarity, not task size.
- "Build a REST API with CRUD endpoints" → minimal research (well-established patterns)
- "Integrate Stripe's new 2026 API" → research required (new/evolving)
- "Add a button" → no research needed
- "Implement WebAuthn passwordless login" → research likely needed (security-critical, evolving standards)

6. **Only spawn exploration/research subagents when:**
   - Task involves unfamiliar technologies
   - External APIs/systems need investigation
   - Newer tools/libraries (recent releases) might exist for the task
   - User explicitly requests research
   - Codebase patterns are unclear

   **Skip research for:**
   - Well-defined tasks with clear requirements
   - Familiar patterns and technologies
   - Simple modifications to existing code

7. **When research IS needed:**
   - Use `Task` tool with Explore agents to explore codebase
   - Use `researcher` agent for external documentation
   - Read relevant files to understand existing patterns

## [INTEGRATION PLANNING] (when task involves external APIs/systems)

8. **For integration work, apply Spec-First methodology:**
   - Map entry points: candidate integration surfaces
   - Choose sync vs async by latency/throughput/ordering needs
   - Propose 2-4 compliant designs; prefer smallest solution meeting all constraints
   - Quick conformance checklist: inputs, outputs, errors, timeouts, retries, idempotency

## [DECISIONS]

9. **Use `architect` agent for decisions with trade-offs**

   ```
   Task tool with:
   - subagent_type: "ai-prompt-guide:architect"
   - prompt: |
       Decision: [What we're deciding]
       Constraints: [Non-negotiables]
       Stakes: [low|medium|high]
   ```

## [CLARIFY]

10. **Ask Product Owner questions when needed**
    - Use `AskUserQuestion` tool to clarify business requirements
    - Present options discovered during research
    - Focus on product decisions, not technical implementation details

## [EXECUTE STEPS]

**For each step in the plan:**

### a. Assign to Developer Subagent

11. **Simple/component work** → `developer` agent:
    ```
    Task tool with:
    - subagent_type: "ai-prompt-guide:developer"
    - prompt: |
        Task: [Task description]
        Files: [Files to modify]
        Acceptance: [Criteria]

        Respond in terse mode: done/blockers only.
        Do NOT stage changes - Orchestrating Agent handles staging.
    ```

    **Complex/architectural work** → `senior-developer` agent:
    ```
    Task tool with:
    - subagent_type: "ai-prompt-guide:senior-developer"
    - prompt: |
        Task: [Task description]
        Files: [Files to modify]
        Acceptance: [Criteria]

        Respond in terse mode: done/blockers only.
        Do NOT stage changes - Orchestrating Agent handles staging.
    ```

### b. Handle New Files

12. **For any new files created by the subagent:**
    ```bash
    git add -N <new-file>
    ```
    This marks intent-to-add so new files appear in `git diff` without staging content.

### c. Code Review (Mandatory)

13. **Run `code-reviewer` on this step's changes:**

    ```
    Task tool with:
    - subagent_type: "ai-prompt-guide:code-reviewer"
    - prompt: |
        Review changes shown in git diff.
        Focus: [Production standards, security, maintainability]
    ```

### d. Handle Review Findings (Iteration Loop)

14. **If FAIL or PASS WITH FIXES:**
    - Assign required fixes back to Developer with specific feedback
    - Developer addresses specific issues (no over-correction)
    - Re-run code review
    - Repeat until PASS

    **If PASS:**
    - Proceed to QA verification

### e. QA Verification

15. **Run `qa-verifier` after code review passes:**

    ```
    Task tool with:
    - subagent_type: "ai-prompt-guide:qa-verifier"
    - prompt: |
        Acceptance criteria: [From task/requirements]
        Changed files: [List of files]

        Verify implementation meets acceptance criteria.
    ```

    **If NOT MET or PARTIAL with blocking gaps:**
    - Assign back to Developer with specific gaps
    - After fix, re-run code review, then QA verification
    - Repeat until VERIFIED

### f. Stage Changes (Quality Gate)

16. **Once both code review PASSES and QA VERIFIES:**
    ```bash
    git add <files-modified-in-this-step>
    ```
    **Orchestrating Agent stages changes** - this is the quality gate.
    Subagents do NOT stage - only the Orchestrating Agent controls staging.

### g. Next Step

17. **The next step's `git diff` now only shows its own changes.**
    This prevents regression and keeps reviews focused.

## [PARALLEL EXECUTION RULES]

18. **Within a single step:**
    - Run independent tasks in parallel when files don't overlap
    - **Critical:** Divide work so subagents don't work on same files simultaneously

19. **Between steps:**
    - Steps execute sequentially (each step depends on previous staging)
    - Wait for step N to complete and stage before starting step N+1

## [REPORT]

20. **Report summary to Product Owner after all steps complete**
    - Steps completed
    - Blockers encountered (if any)
    - Review status (all passed)
    - QA verification status (all verified)
    - Files modified (now all staged)
    - Ready for commit (suggest `/commit` if appropriate)

## Important Notes

- **Orchestrating Agent = quality gatekeeper**: Only the Orchestrating Agent stages changes
- **Subagents = workers**: They develop and respond terse, never stage
- **Git diff = review tool**: Minimizes context vs reading file contents
- **`git add -N`**: Makes new files visible in diff without committing content
- **File isolation**: Prevent multiple subagents from editing same file simultaneously
- **Staged changes persist**: Each step's staged changes are preserved for final commit
- **Review is mandatory**: Every implementation gets code review AND QA verification
