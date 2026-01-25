---
name: decide
description: "Structured decision making using the decider agent. Use when weighing multiple approaches or options."
allowed-tools:
  - Read
  - Task
---

# Workflow: Decision Dispatch

**Arguments:** $ARGUMENTS

**Purpose:** Invoke the `decider` agent for structured trade-off analysis.

## Usage

1. **Invoke decider agent**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/decider.md

       Decision: [What we're deciding]
       Constraints: [Non-negotiable requirements]
       Stakes: [low|medium|high]
       Context: [Relevant background]
   ```

   Note: Agent returns terse decision by default.

2. **Apply decision**
   - Can be used standalone for ad-hoc decisions
   - Can update existing plan files with decision outcome

## When to Use

- Multiple viable implementation approaches
- Architecture/optimization decisions with trade-offs
- Technology or pattern selection
- Any decision requiring structured analysis
