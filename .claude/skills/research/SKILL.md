---
name: research
description: "Research topics using web sources. Use for documentation lookup, troubleshooting research, technology evaluation, or fact-checking."
allowed-tools:
  - Task
---

# Workflow: Web Research

**Arguments:** $ARGUMENTS

**Purpose:** Research topics using the researcher agent.

**Role Context:** You are the **Orchestrating Agent**. The user is the **Product Owner** who needs information to make decisions.

## [RESEARCH]

1. **Invoke researcher agent**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/researcher.md

       Research topic: [from arguments]
       Focus: [specific questions if provided]
   ```

## [REPORT]

2. **Return findings to Product Owner**
   - Research summary
   - Verified findings with sources
   - Unresolved questions
   - Confidence assessment
