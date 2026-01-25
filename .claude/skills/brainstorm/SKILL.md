---
name: brainstorm
description: "Generate multiple distinct design variations using parallel agents. Use when exploring creative approaches to design problems."
allowed-tools:
  - Read
  - Task
  - AskUserQuestion
---

# Workflow: Parallel Design Ideation

**Arguments:** $ARGUMENTS

## [SETUP]

1. **Clarify the design problem**
   - Use `AskUserQuestion` if the problem/goal is unclear
   - Identify any reference documents to include

2. **Determine lenses (3-5)**
   - Lenses are design perspectives that focus each subagent's optimization criteria
   - Each parallel subagent receives ONE lens to optimize their design for
   - User-provided lenses OR generate based on problem type
   - Examples: "minimal-clean", "feature-rich", "performance-first", "accessibility-focused", "mobile-first", "extensible", "coverage-focused"

3. **Choose model based on complexity**
   - **Large/architectural designs** → `opus-designer` agent
   - **Component-level/iterative designs** → `sonnet-designer` agent

## [PARALLEL GENERATION]

4. **Launch parallel agents (one per lens)**

   Each subagent receives ONE lens to focus their design optimization.

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: opus OR sonnet (based on step 3)
   - prompt: |
       Use the methodology from agents/[opus|sonnet]-designer.md

       Lens: [Lens Name]
       Design Problem: [Description]
       Universal Constraints: [Constraints all must satisfy]
       Reference Documents: [Paths if any]

       Generate ONE complete design optimized for this lens.
   ```

   Note: Agents use terse mode by default.

## [COLLECTION]

5. **Present comparison to user for review**
   - Summary of each variation and its lens optimization
   - Key differentiators between approaches
   - Request user selection (or hybrid approach)
   - User reviews the variations before selection
