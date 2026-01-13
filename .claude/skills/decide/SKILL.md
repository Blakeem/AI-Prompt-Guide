---
name: decide
description: "Choose between multiple approaches with structured trade-off analysis. Use when you have multiple valid implementation approaches or architecture/optimization decisions with trade-offs."
allowed-tools:
  - Read
  - Glob
  - Grep
  - TodoWrite
  - AskUserQuestion
---

# Workflow: Structured Decision Making

**Arguments:** $ARGUMENTS

**Prerequisite:** Consider using the `/plan` skill first to assess information gaps and map consequences before generating options.

## Decision Process

1. **Identify decision point and constraints**
   - What exactly are we deciding?
   - What are the non-negotiable requirements?

2. **Generate 2-4 viable options**
   - Include a simple baseline option
   - Each option should be meaningfully different

3. **Document each option:**

| Aspect | Details |
|--------|---------|
| Description | What this approach entails |
| Assumptions | What must be true for this to work |
| Pros | Benefits and strengths |
| Cons | Drawbacks and risks |
| Evidence | Supporting documentation or examples |
| Pattern alignment | How it fits existing codebase patterns |

4. **Select 4-6 evaluation criteria**
   - Correctness
   - Risk
   - Maintainability
   - Testability
   - Simplicity
   - Performance
   - Pattern consistency

5. **Create decision matrix**
   - Score 0-10 per criterion
   - Apply weights:
     - Critical: 3-5
     - Important: 2
     - Nice-to-have: 1
   - Calculate weighted sum

6. **Select highest-scoring option**

7. **Document disqualifiers for rejected options**
   - Why was each option not chosen?
   - What would change your decision?

8. **Record decision rationale**

## Rules

- Non-negotiable failures score 0
- Simple losing to complex requires explicit justification
- If scores are close, prefer the simpler option

## Output Format

```markdown
## Decision: [What we're deciding]

### Options Considered

#### Option 1: [Name]
- **Description:** [brief explanation]
- **Pros:** [list]
- **Cons:** [list]

[Repeat for each option]

### Evaluation Matrix

| Criterion (weight) | Option 1 | Option 2 | Option 3 |
|--------------------|----------|----------|----------|
| Correctness (5)    | 8 (40)   | 9 (45)   | 7 (35)   |
| Simplicity (3)     | 9 (27)   | 5 (15)   | 7 (21)   |
| ...                | ...      | ...      | ...      |
| **Total**          | **XX**   | **XX**   | **XX**   |

### Decision: [Selected option]

**Rationale:** [Why this option wins]

**Rejected options:** [Key disqualifiers for each]
```
