# AI-Prompt-Guide

Structured workflows and specialized agents for AI-assisted development.

## Philosophy

This project uses a multi-agent orchestration approach to save context:

- **Main agent** handles planning, coordination, and quality gates
- **Subagents** execute individual tasks and respond tersely (done/blockers)
- **Skills** are thin dispatchers that orchestrate subagents
- Context stays focused where needed instead of accumulated in one thread

## Structure

**Skills** (`.claude/skills/`)
- Invoke with `/skill-name` (e.g., `/develop`, `/audit`, `/decide`)
- Each skill contains its own documentation and workflow
- Auto-discovered by Claude based on task context

**Agents** (`agents/`)
- Specialized personas for specific task types
- Used via Task tool with appropriate model (sonnet/opus/haiku)
- Contains methodology and behavioral instructions

## Getting Started

Run `/develop` with your task description. The skill will:
1. Assess requirements and create a plan
2. Spawn subagents to execute tasks
3. Coordinate quality gates and integration
4. Keep you updated on progress

For other workflows, browse `.claude/skills/` or let Claude suggest the appropriate skill.
