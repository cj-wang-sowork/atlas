# ATLAS Enterprise AI Self-Learning Skills System

ATLAS is a portable agent workspace and skill pack for teams that want AI assistants to learn from repeated work without leaking private context. It packages one `SKILL.md`, reusable prompt skills, workspace boot files, and a small zero-dependency Python learning layer.

The same repository can be installed for:

| Runtime | Support model |
| --- | --- |
| OpenClaw | Installs the full workspace into `~/.openclaw/workspace` |
| Claude Code | Adds a project `AGENTS.md` launcher and workspace context |
| Codex CLI | Uses Codex's `AGENTS.md` instruction discovery |
| Qwen Code CLI | Installs a Qwen-compatible `SKILL.md` pack under `~/.qwen/skills` |

## What You Get

- A clear agent boot sequence in `AGENTS.md`
- Persona, memory, tool, identity, and heartbeat templates
- Three reusable skills: brand positioning, web research, and content writing
- A five-layer learning methodology for enterprise, brand, department, team, and personal context
- Python modules for market routing, access control, security checks, pattern learning, and cross-market intelligence
- A POSIX installer that can target OpenClaw, Claude Code, Codex CLI, Qwen Code CLI, or all supported runtimes

## Quick Install

```bash
git clone https://github.com/cj-wang-sowork/atlas-Enterprise-AI-Self-Learning-Skills-System-.git
cd atlas-Enterprise-AI-Self-Learning-Skills-System-
```

Install for one runtime:

```bash
./scripts/install-workspace.sh --target openclaw
./scripts/install-workspace.sh --target claude --dest ~/workspace/your-project
./scripts/install-workspace.sh --target codex --dest ~/workspace/your-project
./scripts/install-workspace.sh --target qwen
```

Install for every supported runtime:

```bash
./scripts/install-workspace.sh --target all --dest ~/workspace/your-project
```

For `--target all`, `--dest` is the project root used by Claude Code and Codex CLI. OpenClaw and Qwen use their default user-level locations unless you run them separately with a custom `--dest`.

## Runtime Details

### OpenClaw

```bash
./scripts/install-workspace.sh --target openclaw
```

Default destination: `~/.openclaw/workspace`

OpenClaw loads the workspace files directly. After installation, customize:

- `SOUL.md` for persona and tone
- `TOOLS.md` for local environment notes
- `MEMORY.md` for curated long-term context
- `skills/` for reusable workflows

### Claude Code

```bash
./scripts/install-workspace.sh --target claude --dest ~/workspace/your-project
```

The installer writes:

- `AGENTS.md` in the project root
- `.atlas-workspace/` with the full workspace bundle
- `.claude/skills/atlas-enterprise-ai-self-learning/SKILL.md`

The generated `AGENTS.md` tells Claude Code to load the workspace context and use the skill pack when the task matches.

### Codex CLI

```bash
./scripts/install-workspace.sh --target codex --dest ~/workspace/your-project
```

Codex reads `AGENTS.md` files before it works. The installer writes a project `AGENTS.md` launcher and `.atlas-workspace/` bundle so Codex can discover the same workflow and skill instructions from the repository root.

### Qwen Code CLI

```bash
./scripts/install-workspace.sh --target qwen
```

Default destination: `~/.qwen/skills/atlas-enterprise-ai-self-learning`

Qwen Code discovers skills from `~/.qwen/skills/` and `.qwen/skills/`. This installer creates a Qwen-compatible skill directory with `SKILL.md`, references, templates, and bundled prompt skills.

Use a custom Qwen skill location if needed:

```bash
./scripts/install-workspace.sh --target qwen --dest ~/.qwen/skills/my-atlas-skill
```

## How To Use

After installation, ask your agent for one of the bundled workflows:

```text
Run brand positioning for our product.
Research competitors in the Japan market.
Write a LinkedIn post for this launch.
Analyze this repository and update the learning notes.
```

For Qwen Code, you can also invoke the skill explicitly:

```bash
qwen --skill atlas-enterprise-ai-self-learning --prompt "Research this market and produce an executive summary"
```

## Methodology

ATLAS separates reusable learning by audience and risk:

| Layer | Purpose | Typical content | Sharing rule |
| --- | --- | --- | --- |
| Enterprise | Organization-wide operating knowledge | Cross-market patterns, standards, policies | Shared broadly |
| Brand | Brand identity and messaging | Voice, positioning, approved claims | Shared with brand owners |
| Department | Function-specific playbooks | Marketing, sales, product, engineering workflows | Internal to department |
| Team | Local execution learning | Experiments, retrospectives, tactical decisions | Team-only |
| Personal | Individual preferences and notes | Private working style, drafts, local context | Never committed |

This design keeps useful patterns portable while keeping sensitive context local. Agents get enough shared memory to improve repeated work, but personal or high-risk information stays out of shared repositories and group sessions.

Read the full methodology in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Architecture

```text
User request
  -> Runtime adapter instructions (OpenClaw, Claude, Codex, Qwen)
  -> Workspace boot sequence (AGENTS, SOUL, TOOLS, MEMORY)
  -> Skill workflow selection (brand, research, content, custom)
  -> Five-layer learning policy
  -> Optional Python learning modules
  -> Output, audit notes, and reusable learning updates
```

Core Python modules:

| Module | Role |
| --- | --- |
| `learn_system.py` | Five-layer learning files and access validation |
| `market_router.py` | Market registration, context, routing, and stats |
| `security_checker.py` | Credential, PII, path, and access marker checks |
| `hermes_adapter.py` | Pattern observation, confidence scoring, and adaptive rules |
| `market_intelligence.py` | Cross-market insights, anomalies, and health reports |

The Python layer is optional. The workspace and skill pack work as agent instructions even when you do not import the Python modules.

## Verify Installation

Run the installer in a temporary directory:

```bash
tmpdir=$(mktemp -d)
./scripts/install-workspace.sh --target claude --dest "$tmpdir/claude-project"
./scripts/install-workspace.sh --target codex --dest "$tmpdir/codex-project"
./scripts/install-workspace.sh --target qwen --dest "$tmpdir/qwen-skill"
```

Verify the Python modules load:

```bash
python3 -m py_compile learn_system.py market_router.py security_checker.py hermes_adapter.py market_intelligence.py
```

## Documentation

| Document | Purpose |
| --- | --- |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Detailed installation and layout guide |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Architecture, learning model, and rationale |
| [docs/LEARN.md](docs/LEARN.md) | Five-layer learning reference |
| [SECURITY.md](SECURITY.md) | Security policy and sensitive-data rules |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow |

## Security Rules

- Never commit API keys, credentials, personal memory, or raw conversation logs.
- Keep `MEMORY.md` for direct owner sessions only.
- Keep personal learning outside shared git history.
- Review `TOOLS.md` before sharing a workspace because it may describe local hosts or operational details.

## License

MIT. See [LICENSE](LICENSE).
