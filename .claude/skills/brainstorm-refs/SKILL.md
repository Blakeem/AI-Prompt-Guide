---
name: brainstorm-refs
description: "Generate multiple distinct design variations with document references. Use when you need multiple creative approaches that must incorporate existing specs, constraints, or project documentation."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - TodoWrite
  - AskUserQuestion
---

# Workflow: Parallel Ideation with References

**Arguments:** $ARGUMENTS

**Purpose:** Generate N distinct design variations, each incorporating referenced documentation. User reviews and selects.

## [SETUP]

1. **Clarify the design problem/goal**
   - What are we designing?
   - What constraints must all variations satisfy?

2. **Identify relevant documents to reference**
   - Specs: `path/to/api-spec.md`
   - Constraints: `path/to/constraints.md`
   - Patterns: `path/to/patterns.md`

3. **Determine themes (3-5 for variety)**
   - **User-provided:** User specifies themes
   - **Coordinator-generated:** If not provided, create themes based on the problem

4. **Define universal constraints from references**

## [PARALLEL GENERATION]

5. **Launch parallel agents, one per theme**

   For each theme, use Task tool with:
   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: Include theme, document paths, and generation instructions
   ```

6. **Each agent:**
   - Reads referenced documents first
   - Generates ONE complete design optimized for their theme
   - Incorporates constraints from referenced specs
   - Documents: approach, key decisions, trade-offs, how references informed choices

## [COLLECTION]

7. **Present all variations to user:**
   - Summary of each with theme focus
   - Key differentiators between variations
   - How each addressed the referenced constraints
   - User reviews and selects (or requests hybrid)

## Example Themes by Problem Type

| Problem | Example Themes |
|---------|---------------|
| Test design | coverage-focused, edge-case-hunter, integration-heavy, performance-oriented, security-first |
| API design | RESTful-minimal, GraphQL-flexible, RPC-performant, event-driven |
| Architecture | monolith-simple, microservices-scalable, serverless-elastic, modular-monolith |
| Implementation | imperative-clear, functional-composable, OOP-extensible |

## Theme Agent Prompt Template

```markdown
## Theme Assignment: [Theme Name]

You are generating a design optimized for the "[Theme Name]" approach.

## Design Problem
[Description of what we're designing]

## Reference Documents to Read First
- [path/to/spec.md] - Read this for API requirements
- [path/to/constraints.md] - Read this for constraints

Use the Read tool to load these documents before designing.

## Universal Constraints
[Constraints all variations must satisfy]

## Your Task

1. Read the referenced documents
2. Generate ONE complete design that:
   - Embodies the [Theme Name] philosophy
   - Satisfies all constraints from references
   - Works within documented limits

Document:
1. **Approach:** High-level description
2. **Key Decisions:** Major choices and why
3. **Reference Integration:** How specs/constraints shaped the design
4. **Trade-offs:** What you prioritized and sacrificed
```

## Output Format

```markdown
## Brainstorm Results: [Design Problem]

### Referenced Documents
- [path/to/spec.md] - [Brief summary of relevant constraints]
- [path/to/constraints.md] - [Brief summary]

### Variation 1: [Theme Name]
**Approach:** [Brief description]
**Key Decisions:**
- [Decision 1]
- [Decision 2]
**Reference Integration:** [How this variation addresses spec requirements]
**Trade-offs:** [What this approach sacrifices]

### Variation 2: [Theme Name]
...

---

## Constraint Compliance

| Constraint | V1 | V2 | V3 |
|------------|----|----|-----|
| [From spec] | [How addressed] | [How addressed] | [How addressed] |

## Your Choice

Which variation would you like to proceed with?
```
