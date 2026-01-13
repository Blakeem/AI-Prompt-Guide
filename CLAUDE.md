# AI-Prompt-Guide

Structured workflows and specialized agents for AI-assisted development.

## Available Skills

Invoke with `/skill-name` or let Claude auto-discover based on context.

### Development
- `/develop` - Simple development with anti-pattern detection
- `/develop-fix` - Bug fixing with root cause analysis
- `/develop-staged` - Multi-agent staged development
- `/develop-staged-tdd` - Multi-agent TDD development
- `/coverage` - Add test coverage to existing code

### Decision & Planning
- `/decide` - Structured decision making with trade-off analysis
- `/decide-lensed` - Multi-perspective decision analysis
- `/plan` - Structured planning and information assessment
- `/brainstorm` - Generate multiple design variations
- `/brainstorm-refs` - Brainstorm with document references

### Documentation & Audit
- `/audit` - Code audit with specialist agents
- `/spec-feature` - Document internal feature specification
- `/spec-external` - Document external API specification

## Agents

Located in `agents/` folder. Use via Task tool:

- **web-researcher** (Sonnet) - Web research and fact verification
- **document-cleanup** (Haiku) - Document splitting and organization
- **mid-level-developer** (Sonnet) - General development tasks
- **senior-developer** (Opus) - Complex architecture and debugging

## Agent Usage

To spawn an agent, use the Task tool:

```
Task tool with:
- subagent_type: "general-purpose" (or appropriate type)
- prompt: Include "Use the methodology from agents/[agent-name].md"
- model: sonnet|opus|haiku (match the agent's model)
```

## Web Page Download

Use `WebFetch` tool to download web pages as markdown:
1. WebFetch fetches and converts HTML to markdown
2. Use Write tool to save the content
3. Use document-cleanup agent to split large docs

## Document Organization

After splitting large documents, the document-cleanup agent creates a summary index:

| File | Keywords | Summary |
|------|----------|---------|
| file.md | key1, key2 | Brief description |

This enables quick file discovery without reading full context.
