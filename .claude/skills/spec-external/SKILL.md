---
name: spec-external
description: "Document 3rd party APIs from official sources. Use when integrating SDKs, webhooks, auth flows."
allowed-tools:
  - Read
  - Task
---

# Workflow: External API Documentation

**Arguments:** $ARGUMENTS

**Purpose:** Research and document external APIs using specialized subagents.

**Role Context:** You are the **Orchestrating Agent**. The user is the **Product Owner** who needs API documentation for integration work.

## [RESEARCH]

1. **Invoke api-researcher agent**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: sonnet
   - prompt: |
       Use the methodology from agents/api-researcher.md

       Service: [from arguments]
       Endpoints: [specific endpoints or "all"]
       Output: docs/specs/[service-name]/raw-spec.md
       Context: [how API will be used, if provided]
   ```

   Agent researches official docs and creates raw specification.

## [ORGANIZE]

2. **Invoke document-organizer agent**

   ```
   Task tool with:
   - subagent_type: "general-purpose"
   - model: haiku
   - prompt: |
       Use the methodology from agents/document-organizer.md

       Input: docs/specs/[service-name]/raw-spec.md
       Task: Split by endpoint, create _INDEX.md with keywords
       Output: docs/specs/[service-name]/
   ```

   Agent organizes docs for easy reference during development.

## [REPORT]

3. **Return completion to Product Owner**
   - "Done: docs/specs/[service-name]/_INDEX.md"
   - Or blockers if research/organization failed
