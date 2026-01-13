---
name: decide-lensed
description: "Multi-perspective decision analysis with parallel specialist agents. Use for complex decisions requiring multiple viewpoints or when trade-offs span different quality dimensions."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - TodoWrite
  - AskUserQuestion
---

# Workflow: Multi-Perspective Decision Making

**Arguments:** $ARGUMENTS

**Purpose:** Analyze a decision from multiple quality perspectives using parallel agents, then synthesize into a recommendation.

**Prerequisite:** Consider using `/plan` first to assess information gaps.

## [SETUP]

1. **Define decision specification:**
   - Problem statement
   - Non-negotiable constraints
   - Evaluation criteria (4-6) with weights
   - Evidence requirements
   - Context file paths (if any)

2. **Select lenses (3-5 from standard set below)**
   - Each lens analyzes the problem from its perspective
   - Choose lenses relevant to the decision type

## [PARALLEL ANALYSIS]

3. **Launch parallel agents, one per lens**

   For each lens, use Task tool with:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: Include lens assignment and analysis instructions
   ```

4. **Each specialist agent:**
   - Generates 2-4 options optimized for their lens
   - Documents: description, assumptions, pros/cons, evidence
   - Builds decision matrix with lens-specific weights (0-10)
   - Recommends best option with rationale

## [SYNTHESIS]

5. **Integrate recommendations:**
   - Verify options are meaningfully distinct
   - Enforce non-negotiables, drop violators
   - Identify hybridization opportunities
   - Build global decision matrix with project weights
   - Select winner (highest score or justified choice)

6. **Document decision:**
   - Why this wins
   - Why NOT others (key discriminators)
   - Trade-offs accepted
   - Follow-up actions needed

## Standard Lenses

| Lens | Focus Areas |
|------|-------------|
| **Performance** | Runtime efficiency, memory, throughput, algorithmic complexity |
| **UX/Ergonomics** | API clarity, cognitive load, sensible defaults, developer experience |
| **Maintainability** | Readability, minimal churn, code longevity, team velocity |
| **Pattern Consistency** | Alignment with existing idioms, error handling, conventions |
| **Risk/Security** | Failure modes, dependency risks, attack surface, production readiness |
| **Simplicity Baseline** | Minimal complexity, boring solutions, proven approaches |

## Lens Agent Prompt Template

```markdown
## Lens Assignment: [Lens Name]

You are analyzing this decision from the [Lens Name] perspective.

## Problem Statement
[Description of the decision]

## Non-Negotiables
[Constraints that cannot be violated]

## Your Task

1. Generate 2-4 options optimized for [lens focus areas]
2. For each option document:
   - Description
   - Assumptions/preconditions
   - Pros (from your lens perspective)
   - Cons (from your lens perspective)
   - Evidence/examples

3. Build a decision matrix scoring each option 0-10 on:
   - [Lens-specific criteria]

4. Recommend the best option from your perspective with rationale
```

## Synthesis Output Format

```markdown
## Decision: [Problem Statement]

### Lens Analyses Summary
| Lens | Recommended Option | Key Insight |
|------|-------------------|-------------|
| Performance | Option A | [insight] |
| Maintainability | Option B | [insight] |
| ... | ... | ... |

### Global Decision Matrix
| Criterion (weight) | Option A | Option B | Option C |
|--------------------|----------|----------|----------|
| [Criterion] (X)    | score    | score    | score    |
| **Total**          | **XX**   | **XX**   | **XX**   |

### Decision: [Selected Option]

**Rationale:** [Why this wins]

**Trade-offs:** [What we're accepting]

**Discriminators:** [Why NOT the others]

**Follow-up Actions:** [Next steps]
```
