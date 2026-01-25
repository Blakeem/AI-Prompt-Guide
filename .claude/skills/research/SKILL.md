---
name: research
description: "Research topics using web sources. Use for documentation lookup, troubleshooting research, technology evaluation, or fact-checking."
allowed-tools:
  - Task
---

# Workflow: Web Research

**Arguments:** $ARGUMENTS

**Purpose:** Research topics using the web-researcher agent.

## [RESEARCH]

1. **Invoke web-researcher agent**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/web-researcher.md

       Research topic: [from arguments]
       Focus: [specific questions if provided]
   ```

## [REPORT]

2. **Return findings**
   - Research summary
   - Verified findings with sources
   - Unresolved questions
   - Confidence assessment
