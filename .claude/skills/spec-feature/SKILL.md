---
name: spec-feature
description: "Document internal feature specification. Use when defining requirements, API contracts, or acceptance criteria for new internal features."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - TodoWrite
  - AskUserQuestion
---

# Workflow: Document Internal Feature Specification

**Arguments:** $ARGUMENTS

**Role Context:** You are the **Orchestrating Agent**. The user is the **Product Owner** who defines requirements and priorities.

## [Requirements Phase]

1. **Gather requirements from Product Owner**
   - Purpose and rationale
   - User behavior and interactions
   - Use cases (primary and secondary)
   - Priorities (must-have vs nice-to-have)

2. **Systematically analyze for gaps**
   - UX details
   - Edge cases
   - Scope boundaries
   - Error scenarios

## [Clarification Loop]

**WHILE gaps exist:**

3. **Ask Product Owner about:**
   - UX interactions
   - Specific requirements
   - Edge case handling
   - Priorities

4. **Use `/decide` skill for technical choices**

5. **Update requirements based on answers**

6. **IF gaps remain:** Return to step 3

## [Specification Creation]

7. **Create specification document**
   - Use Write tool to create the spec file

8. **Structure the specification with these sections:**
   - Overview & rationale
   - Functionality with API signatures
   - Request/response formats with examples
   - Error conditions & edge cases
   - Performance requirements
   - Security requirements
   - Dependencies and references

## [Acceptance Criteria]

9. **Document criteria**
   - Happy path scenarios
   - Edge cases
   - Error handling
   - Performance/security boundaries

10. **Document implementation approach**
    - Selected approach from decide workflow
    - Key technical decisions
    - Rationale for choices

## Specification Template

```markdown
# Feature: [Name]

## Overview
[Purpose and rationale]

## Functionality

### [Feature Area 1]
**API Signature:**
```
function name(params): returnType
```

**Request Format:**
```json
{ "field": "value" }
```

**Response Format:**
```json
{ "result": "value" }
```

### Error Handling
| Error | Code | Handling |
|-------|------|----------|
| [Type] | [Code] | [Action] |

## Acceptance Criteria

### Happy Path
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Edge Cases
- [ ] [Case 1]

### Error Handling
- [ ] [Error scenario 1]

## Implementation Notes
[Key decisions and rationale]
```

## Principles

**Decision Boundaries:**
- Product Owner decides: UX, scope, priorities, business rules
- Architect decides: Implementation, technical trade-offs (use `/decide`)

**Quality Standards:**
- Unambiguous requirements
- Complete coverage
- Measurable criteria
- Validated assumptions
