# Installation Guide

This guide explains how to install ATLAS for OpenClaw, Claude Code, Codex CLI, and Qwen Code CLI.

## Requirements

- macOS, Linux, or WSL
- `sh`, `cp`, `mv`, and `mkdir`
- Python 3, used only for safe path normalization in the installer
- Git, if you clone the repository

No Python packages are required for the workspace or installer.

## Clone

```bash
git clone https://github.com/cj-wang-sowork/atlas-Enterprise-AI-Self-Learning-Skills-System-.git
cd atlas-Enterprise-AI-Self-Learning-Skills-System-
```

## Installer Syntax

```bash
./scripts/install-workspace.sh --target TARGET [--dest PATH] [--force]
```

Targets:

| Target | Destination behavior |
| --- | --- |
| `openclaw` | Installs the workspace to `~/.openclaw/workspace` unless `--dest` is provided |
| `claude` | Installs into a project root passed with `--dest` |
| `codex` | Installs into a project root passed with `--dest` |
| `qwen` | Installs a skill pack to `~/.qwen/skills/atlas-enterprise-ai-self-learning` unless `--dest` is provided |
| `all` | Installs OpenClaw, Claude, Codex, and Qwen. `--dest` is required for the Claude/Codex project root |

By default, existing files are moved to a timestamped backup. Use `--force` only when you intentionally want to replace existing files.

## OpenClaw

```bash
./scripts/install-workspace.sh --target openclaw
```

Default layout:

```text
~/.openclaw/workspace/
  AGENTS.md
  SOUL.md
  TOOLS.md
  MEMORY.md
  SKILL.md
  skills/
  docs/
  examples/
  scripts/
```

OpenClaw should load `AGENTS.md` on each main session. Customize `SOUL.md`, `TOOLS.md`, and `MEMORY.md` after installation.

## Claude Code

```bash
./scripts/install-workspace.sh --target claude --dest ~/workspace/your-project
```

The installer writes:

```text
your-project/
  AGENTS.md
  .atlas-workspace/
    AGENTS.md
    SOUL.md
    TOOLS.md
    MEMORY.md
    skills/
    docs/
  .claude/
    skills/
      atlas-enterprise-ai-self-learning/
        SKILL.md
        references/
        templates/
        assets/
```

If `AGENTS.md` already exists, the installer refuses to overwrite it unless `--force` is passed. Merge manually if the project already has important agent rules.

## Codex CLI

```bash
./scripts/install-workspace.sh --target codex --dest ~/workspace/your-project
```

Codex CLI reads `AGENTS.md` from the project instruction chain. The installer writes:

```text
your-project/
  AGENTS.md
  .atlas-workspace/
    AGENTS.md
    SOUL.md
    TOOLS.md
    MEMORY.md
    skills/
    docs/
```

Start Codex from the project root:

```bash
cd ~/workspace/your-project
codex
```

Verify discovery by asking Codex to summarize the active project instructions.

## Qwen Code CLI

```bash
./scripts/install-workspace.sh --target qwen
```

Default layout:

```text
~/.qwen/skills/
  atlas-enterprise-ai-self-learning/
    SKILL.md
    references/
    templates/
    assets/
```

Use a project-local Qwen skill by choosing a project path:

```bash
./scripts/install-workspace.sh --target qwen --dest ~/workspace/your-project/.qwen/skills/atlas-enterprise-ai-self-learning
```

Then run:

```bash
qwen --list-skills
qwen --skill atlas-enterprise-ai-self-learning --prompt "Run brand positioning for this repo"
```

## Install Everything

```bash
./scripts/install-workspace.sh --target all --dest ~/workspace/your-project
```

This performs:

1. OpenClaw install to `~/.openclaw/workspace`
2. Claude Code project install to `~/workspace/your-project`
3. Codex project install to `~/workspace/your-project`
4. Qwen global skill install to `~/.qwen/skills/atlas-enterprise-ai-self-learning`

Claude Code and Codex both use the same project `AGENTS.md` launcher. Running `all` is intended for one project that should be usable by both tools.

## Optional Python Module Check

The Python files are optional, but you can verify they compile:

```bash
python3 -m py_compile learn_system.py market_router.py security_checker.py hermes_adapter.py market_intelligence.py
```

Use them directly from the repository root:

```python
from market_router import MarketRouter, MarketConfig
from security_checker import SecurityChecker
from hermes_adapter import HermesAdapter

router = MarketRouter()
checker = SecurityChecker()
adapter = HermesAdapter(market_router=router, security_checker=checker)
```

## Troubleshooting

### The installer says the destination overlaps the source repository

Choose a destination outside the cloned repository. The installer blocks source-over-destination installs to prevent recursive copies.

### The installer refuses to overwrite `AGENTS.md`

The project already has agent instructions. Merge the generated launcher manually or rerun with `--force` after confirming replacement is safe.

### Qwen cannot find the skill

Check that the skill directory contains `SKILL.md` and is inside one of Qwen's skill locations:

- `~/.qwen/skills/`
- `.qwen/skills/`

Refresh Qwen's memory or restart the session if needed.

### Codex does not load the instructions

Start Codex from the project root or pass the correct working directory. Confirm the root contains `AGENTS.md`.
