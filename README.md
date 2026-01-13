# AI-Prompt-Guide

Structured workflows and specialized agents for AI-assisted development using Claude Code.

## Installation

### Via Claude Code Plugin (Recommended)
```bash
claude plugin add ai-prompt-guide
```

### Manual Installation
Clone this repository and copy the `.claude/` folder and `agents/` folder to your project:
```bash
git clone https://github.com/Blakeem/AI-Prompt-Guide.git
cp -r AI-Prompt-Guide/.claude /path/to/your/project/
cp -r AI-Prompt-Guide/agents /path/to/your/project/
```

## Quick Start

Once installed, use skills with slash commands:

```
/develop         # Start simple development workflow
/plan            # Structured planning before implementation
/decide          # Make structured decisions with trade-offs
/audit           # Run code audit with specialist agents
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `/develop` | Simple development with anti-pattern detection |
| `/develop-fix` | Bug fixing with root cause analysis |
| `/develop-staged` | Multi-agent staged development |
| `/develop-staged-tdd` | Multi-agent TDD development |
| `/decide` | Structured decision making |
| `/decide-lensed` | Multi-perspective decision analysis |
| `/brainstorm` | Generate design variations |
| `/brainstorm-refs` | Brainstorm with document references |
| `/audit` | Code audit with specialist agents |
| `/coverage` | Add test coverage |
| `/plan` | Structured planning |
| `/spec-feature` | Document internal feature |
| `/spec-external` | Document external API |

## Agents

Specialized agents for different task types:

| Agent | Model | Use Case |
|-------|-------|----------|
| `web-researcher` | Sonnet | Research, fact-checking, documentation lookup |
| `document-cleanup` | Haiku | Document splitting, index generation |
| `mid-level-developer` | Sonnet | General development tasks |
| `senior-developer` | Opus | Architecture, complex debugging |

## Project Structure

```
AI-Prompt-Guide/
├── .claude/
│   ├── skills/           # Workflow skills
│   │   ├── develop/
│   │   ├── plan/
│   │   └── ...
│   ├── commands/         # Simple commands
│   └── settings.local.json
├── agents/               # Agent definitions
│   ├── web-researcher.md
│   ├── document-cleanup.md
│   ├── mid-level-developer.md
│   └── senior-developer.md
├── plugin.json           # Extension manifest
├── CLAUDE.md            # Project documentation
└── README.md
```

## Web Page Download

Claude Code can download web pages as markdown:

1. Use `WebFetch` tool to fetch and convert HTML
2. Use `Write` tool to save the markdown file
3. Use `document-cleanup` agent to split large docs

## Document Organization

For large documentation sets, the `document-cleanup` agent creates summary indexes:

```markdown
| File | Keywords | Summary |
|------|----------|---------|
| auth.md | login, JWT, session | Authentication endpoints |
| users.md | CRUD, validation | User management API |
```

## License

MIT
