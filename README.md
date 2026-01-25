# AI-Prompt-Guide

Structured workflows and specialized agents for AI-assisted development using Claude Code.

## Philosophy

This project uses a **multi-agent orchestration** approach:

- **Main agent** handles planning, coordination, and quality gates
- **Subagents** execute individual tasks and respond tersely (done/blockers)
- **Skills** are thin dispatchers that orchestrate subagents
- Context stays focused where needed instead of accumulated in one thread

## Quick Start

Use slash commands to invoke workflows:

```
/develop      # Plan and execute development work
/brainstorm   # Generate design variations
/research     # Research topics using web sources
/api-docs     # Document external APIs
/audit        # Run comprehensive code audit
/decide       # Make structured decisions
/spec-feature # Define internal feature specs
```

## Installation

### Manual Installation
Clone this repository and copy the `.claude/` folder and `agents/` folder to your project:
```bash
git clone https://github.com/Blakeem/AI-Prompt-Guide.git
cp -r AI-Prompt-Guide/.claude /path/to/your/project/
cp -r AI-Prompt-Guide/agents /path/to/your/project/
```

## User Commands

These commands are entry points for users to invoke workflows:

| Command | Description |
|---------|-------------|
| `/develop` | Start development planning workflow with context gathering, decisions, and execution plan |
| `/brainstorm` | Generate 2-4 design variations using specialized design agents |
| `/research` | Research topics using web-researcher agent with source verification |
| `/api-docs` | Document external APIs with endpoints, auth, errors, and rate limits |
| `/audit` | Run parallel specialist agents for security, performance, complexity analysis |
| `/decide` | Make structured decisions with trade-off evaluation |
| `/spec-feature` | Define internal feature specifications before development |

## Skills

Skills are workflows that orchestrate subagents. Some are user-facing, others are internal.

### User-Facing Skills

| Skill | Purpose |
|-------|---------|
| `develop` | Planning phase - assess requirements, gather context, create execution plan |
| `brainstorm` | Generate design variations through different perspectives |
| `research` | Web research with source verification and confidence assessment |
| `decide` | Structured decision-making with trade-off analysis |
| `audit` | Comprehensive codebase audit with parallel specialists |
| `spec-feature` | Internal feature specification with requirements gathering |
| `spec-external` | External API documentation from official sources |

### Internal Skills

| Skill | Purpose |
|-------|---------|
| `initiate-plan` | Execute development plans using sonnet/opus subagents |
| `initiate-plan-staged` | Execute plans with git staging as quality gates |

## Agents

Specialized agents for different task types:

| Agent | Model | Purpose |
|-------|-------|---------|
| `sonnet-developer` | Sonnet | Standard development - features, bugs, tests, refactoring |
| `opus-developer` | Opus | Complex/architectural work, intricate debugging |
| `sonnet-designer` | Sonnet | Component-level design variations |
| `opus-designer` | Opus | Large-scale architectural design |
| `decider` | Sonnet/Opus | Structured decision-making between options |
| `code-reviewer` | Sonnet | Focused review of specific files/changes |
| `api-spec-researcher` | Sonnet | External API research and documentation |
| `web-researcher` | Sonnet | General web research with source verification |
| `document-cleanup` | Haiku | Document splitting and index generation |

## Project Structure

```
AI-Prompt-Guide/
├── .claude/
│   ├── commands/         # User-facing slash commands
│   │   ├── develop.md
│   │   ├── brainstorm.md
│   │   ├── research.md
│   │   ├── api-docs.md
│   │   ├── audit.md
│   │   ├── decide.md
│   │   └── spec-feature.md
│   └── skills/           # Workflow skills
│       ├── develop/
│       ├── brainstorm/
│       ├── research/
│       ├── decide/
│       ├── audit/
│       ├── spec-feature/
│       ├── spec-external/
│       ├── initiate-plan/
│       └── initiate-plan-staged/
├── agents/               # Agent definitions
│   ├── sonnet-developer.md
│   ├── opus-developer.md
│   ├── sonnet-designer.md
│   ├── opus-designer.md
│   ├── decider.md
│   ├── code-reviewer.md
│   ├── api-spec-researcher.md
│   ├── web-researcher.md
│   └── document-cleanup.md
├── CLAUDE.md             # Project context for Claude
└── README.md
```

## How It Works

1. **User invokes a command** (e.g., `/develop add user authentication`)
2. **Command directs to skill** which orchestrates the workflow
3. **Skill spawns subagents** for specific tasks (research, development, review)
4. **Subagents respond tersely** ("done" or blockers) to minimize context
5. **Main agent coordinates** quality gates and reports results

This approach keeps context focused - subagents only load the instructions they need, and the main agent stays lean for coordination.

## License

MIT
