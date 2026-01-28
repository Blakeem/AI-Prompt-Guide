# AI-Prompt-Guide

Structured workflows and specialized agents for AI-assisted development.

## Philosophy

This project uses a multi-agent orchestration approach with agile role patterns:

- **Orchestrating Agent** handles planning, coordination, and quality gates
- **Subagents** (Developer, Code Reviewer, QA Verifier, etc.) execute individual tasks and respond tersely (done/blockers)
- **Skills** are thin dispatchers that orchestrate subagents
- **Product Owner** (user) provides requirements, approves plans, and makes business decisions
- Context stays focused where needed instead of accumulated in one thread

## Roles

| Role | Agent(s) | Responsibility |
|------|----------|----------------|
| **Architect** | `architect` | Structural decisions, trade-off evaluation |
| **Senior Developer** | `senior-developer` | Complex/architectural implementation |
| **Developer** | `developer` | Standard implementation tasks |
| **Senior UX Developer** | `senior-ux-developer` | System-level UX architecture |
| **UX Developer** | `ux-developer` | Component-level UX design |
| **Code Reviewer** | `code-reviewer` | Code quality, security, maintainability |
| **QA Verifier** | `qa-verifier` | Acceptance criteria verification |
| **Researcher** | `researcher` | Web research with source verification |
| **API Researcher** | `api-researcher` | External API documentation |
| **Document Organizer** | `document-organizer` | Document splitting and indexing |

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
3. Coordinate quality gates (Code Review + QA Verification)
4. Keep you updated on progress

For other workflows, browse `.claude/skills/` or let Claude suggest the appropriate skill.
