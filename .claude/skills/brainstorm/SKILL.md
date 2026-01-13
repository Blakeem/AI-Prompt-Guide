---
name: brainstorm
description: "Generate multiple distinct design variations for user review. Use when you need multiple creative approaches to a design problem."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - TodoWrite
  - AskUserQuestion
---

# Workflow: Parallel Ideation

**Arguments:** $ARGUMENTS

**Purpose:** Generate N distinct design variations, each with a different theme/approach. User reviews and selects.

## [SETUP]

1. **Clarify the design problem/goal**
   - What are we designing?
   - What constraints must all variations satisfy?

2. **Determine themes (3-5 for meaningful variety)**
   - **User-provided:** User specifies themes
   - **Coordinator-generated:** If not provided, create themes based on the problem

3. **Define universal constraints**
   - What must ALL variations satisfy?

## [PARALLEL GENERATION]

4. **Launch parallel agents, one per theme**

   For each theme, use Task tool with:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: Include theme assignment and generation instructions
   ```

5. **Each agent generates ONE complete design:**
   - Optimized for their assigned theme
   - Documents approach, key decisions, trade-offs
   - Explains why this theme led to these choices
   - Does NOT evaluate or compare (pure creative generation)

## [COLLECTION]

6. **Present all variations to user:**
   - Summary of each with theme focus
   - Key differentiators between variations
   - User reviews and selects (or requests hybrid)

## Example Themes by Problem Type

| Problem | Example Themes |
|---------|---------------|
| Test design | coverage-focused, edge-case-hunter, integration-heavy, performance-oriented, security-first |
| API design | RESTful-minimal, GraphQL-flexible, RPC-performant, event-driven |
| Architecture | monolith-simple, microservices-scalable, serverless-elastic, modular-monolith |
| Implementation | imperative-clear, functional-composable, OOP-extensible |
| UI/UX | minimal-clean, feature-rich, mobile-first, accessibility-focused |

## Theme Agent Prompt Template

```markdown
## Theme Assignment: [Theme Name]

You are generating a design optimized for the "[Theme Name]" approach.

## Design Problem
[Description of what we're designing]

## Universal Constraints
[Constraints all variations must satisfy]

## Your Task

Generate ONE complete design that embodies the [Theme Name] philosophy.

Document:
1. **Approach:** High-level description of your design
2. **Key Decisions:** Major choices you made and why
3. **Trade-offs:** What you prioritized and what you sacrificed
4. **Theme Justification:** How this theme shaped your choices

Do NOT compare to other approaches. Focus purely on making the best [Theme Name] design possible.
```

## Output Format

```markdown
## Brainstorm Results: [Design Problem]

### Variation 1: [Theme Name]
**Approach:** [Brief description]
**Key Decisions:**
- [Decision 1]
- [Decision 2]
**Trade-offs:** [What this approach sacrifices]

### Variation 2: [Theme Name]
...

### Variation N: [Theme Name]
...

---

## Key Differentiators

| Aspect | Variation 1 | Variation 2 | Variation 3 |
|--------|-------------|-------------|-------------|
| [Aspect] | [How V1 handles] | [How V2 handles] | [How V3 handles] |

## Your Choice

Which variation would you like to proceed with? You can also request a hybrid combining elements from multiple variations.
```
