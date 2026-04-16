# openclaw-workspace-sowork

> **The only OpenClaw workspace built for marketing teams — with real production numbers.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20for-OpenClaw-orange)](https://github.com/openclaw/openclaw)
[![SoWork](https://img.shields.io/badge/by-SoWork.ai-blue)](https://sowork.ai)
[![DeepEval](https://img.shields.io/badge/DeepEval-0.940-brightgreen)](https://sowork.ai)

**13 markets · $50/mo · DeepEval 0.940 · 3 agents on 1 VM**

Built and battle-tested by [SoWork](https://sowork.ai). Open-sourced for the OpenClaw community.

---

## What is this?

Most OpenClaw workspaces are empty scaffolding. This one has **actual content you can use immediately:**

- ✅ **3 ready-to-use skills** — brand positioning, web research, content writing
- ✅ **Complete workspace system** — AGENTS + SOUL + TOOLS + USER + IDENTITY + HEARTBEAT + MEMORY
- ✅ **Cross-agent quick installer** — one script for Claude Code, OpenClaw, and Hermes
- ✅ **A complete marketing team example** — 3 agents running on 1 VM, with cost breakdown
- ✅ **VM setup guide** — step-by-step from a $6/mo VPS to a running OpenClaw agent
- ✅ **Brand-in-SOUL guide** — how to embed brand positioning into your agent's identity
- ✅ **Security-gated MEMORY** — MEMORY.md never leaks to group chats or sub-agents

Clone it. Customize it. Run it.

---

## Quick Start

```bash
# 1) Clone the repo
git clone https://github.com/cj-wang-sowork/openclaw-workspace-sowork.git
cd openclaw-workspace-sowork

# 2) Install to your target runtime
./scripts/install-workspace.sh --target openclaw
./scripts/install-workspace.sh --target claude --dest ~/workspace/your-project
./scripts/install-workspace.sh --target hermes
```

### Install Targets

| Target | What it installs | Default destination |
|--------|------------------|---------------------|
| Claude Code | `AGENTS.md` launcher + `.sowork-workspace/` context bundle in a project root | `--dest` required |
| OpenClaw | Full workspace bundle | `~/.openclaw/workspace` |
| Hermes | Skill pack with workspace templates + references | `~/.hermes/skills/openclaw-imports/openclaw-workspace-sowork` |

Note: the Claude installer refuses to overwrite an existing `AGENTS.md` unless you pass `--force`.

### One command for all 3

```bash
./scripts/install-workspace.sh --target all --dest ~/workspace/your-project
```

For `--target all`, `--dest` applies to the Claude Code project only. OpenClaw and Hermes still install to their default paths.

Then start OpenClaw if needed:

```bash
openclaw onboard --install-daemon
openclaw gateway --port 18789
```

---

## Production Numbers

This template is extracted from real operations at SoWork — not a toy example:

| Metric | Value |
|--------|-------|
| Markets served | 13 simultaneously |
| Infrastructure cost | ~$50/month |
| Agents on 1 VM | 3 (brand, research, content) |
| DeepEval brand consistency | **0.940** |
| Token efficiency | Full bootstrap under 150k chars |
| VM minimum spec | $6/mo VPS |

---

## What's Included

### Skills (drop into `~/.openclaw/workspace/skills/`)

| Skill | What it does | Trigger |
|-------|-------------|---------|
| `skills/brand-positioning.md` | Brand analysis + campaign strategy | `@assistant Run brand positioning for [Brand]` |
| `skills/web-research.md` | Market research + competitor analysis | `@assistant Research [topic]` |
| `skills/content-writer.md` | Brand-aligned content for any platform | `@assistant Write [content type] for [platform]` |

### Workspace Files (drop into `~/.openclaw/workspace/`)

| File | Purpose | Loaded When |
|------|---------|------------|
| `AGENTS.md` | Boot sequence, routing rules, checklist table | Every turn |
| `SOUL.md` | Persona, tone, Brand-in-SOUL methodology | Every turn |
| `TOOLS.md` | SSH hosts, API config, TTS voices, environment | Every turn |
| `USER.md` | Team profile, preferences | Main sessions only |
| `IDENTITY.md` | Name, emoji, avatar, self-description | Every turn |
| `HEARTBEAT.md` | Periodic health tasks, content pipeline checks | Heartbeat turns |
| `MEMORY.md` | Long-term memory template for persistent context | Main sessions only (security-gated) |

### Examples & Docs

| Path | What it contains |
|------|-----------------|
| `examples/marketing-team/` | 3-agent team setup with full cost breakdown |
| `docs/workspace-deep-dive.md` | Token optimization, security gates, file design guide |
| `scripts/` | Quick installer for Claude Code, OpenClaw, and Hermes |

---

## Directory Structure

```
~/.openclaw/workspace/          ← clone here
├── AGENTS.md                   # Boot sequence + routing rules
├── SOUL.md                     # Persona + Brand-in-SOUL
├── TOOLS.md                    # Environment config (SSH, TTS, APIs)
├── USER.md                     # Team context (main sessions only)
├── IDENTITY.md                 # Name, emoji, avatar
├── HEARTBEAT.md                # Periodic tasks
├── MEMORY.md                   # Iron-law rules (security-gated)
├── SKILL.md                    # Skills registry entry point
├── skills/
│   ├── brand-positioning.md
│   ├── web-research.md
│   └── content-writer.md
├── memory/                     # Daily session logs
├── examples/
│   └── marketing-team/         # 3-agent team example
├── docs/
│   └── workspace-deep-dive.md  # Deep-dive guide
├── scripts/                    # Quick installer and automation tools
└── outputs/                    # Agent output storage
```

---

## The Brand-in-SOUL Concept

Unlike generic workspace templates, this repo introduces **Brand-in-SOUL**: embedding your brand's positioning, tone, and values directly into the agent's `SOUL.md` — so every output is brand-consistent without prompt engineering on every message.

Result: **DeepEval brand consistency score of 0.940** across 13 different markets.

---

## Security

- `MEMORY.md` is **never loaded** in group chats or sub-agent sessions
- Boot sequence in `AGENTS.md` explicitly gates: *"Main session only: Read MEMORY.md"*
- All workspace files are plain Markdown — no executable code, no external calls

---

## Install via Skills CLI (OpenClaw)

```bash
npx skills add cj-wang-sowork/openclaw-workspace-sowork
```

Requires: [Node.js](https://nodejs.org) + [skills CLI](https://github.com/VoltAgent/awesome-openclaw-skills)

If you want the full multi-agent bundle for Claude Code, OpenClaw, or Hermes, use `./scripts/install-workspace.sh` instead.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome for new skills, workspace templates, and examples.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [CJ Wang](https://sowork.ai) · Founder @ SoWork.ai · AI × Marketing × Open Source*


## Market-Agnostic Design

Unlike traditional marketing workspaces, openclaw-workspace-sowork is **completely market-independent**:

- ✅ **No market hardcoding** — Same workspace for 13+ markets, 6 languages, any industry
- - ✅ **Pluggable learning layers** — Enterprise learnings shared across all markets
  - - ✅ **Scalable architecture** — Add markets without duplicating agents or infrastructure
    - - ✅ **Zero market lock-in** — SOUL.md, AGENTS.md, TOOLS.md work globally
     
      - See [docs/LEARN.md](docs/LEARN.md) for five-layer learning architecture supporting any market, department, or team.
     
      - ## Five-Layer Learning System
     
      - This workspace implements **Hermes-inspired five-layer learning** for systematic knowledge building:
     
      - ```
        Enterprise → Brand → Department → Team → Personal
        (public)  (internal) (team-only) (private) (local)
        ```

        Each layer has separate access controls and security gates:
        - **Enterprise**: Organization-wide patterns (public)
        - - **Brand**: Brand identity & positioning (internal)
          - - **Department**: Department-specific strategies (team-only)
            - - **Team**: Direct team learnings (private)
              - - **Personal**: Individual agent learnings (never committed)
               
                - **See [docs/LEARN.md](docs/LEARN.md) for complete architecture and implementation.**
               
                - ## Security & Compliance
               
                - - 📋 **SECURITY.md** — Vulnerability disclosure, data isolation, five-layer security model
                  - - 🔐 **MEMORY.md** — Security-gated context, never leaks to group chats
                    - - 🛡️ **Enhanced .gitignore** — Blocks personal learnings, agent conversations, credentials
                      - - ✅ **Zero dependencies** — Pure configuration, no supply chain risk
                        - - 🌍 **GDPR/SOC2 ready** — Separate data layers prevent PII leakage
                         
                          - **See [SECURITY.md](SECURITY.md) for full security policy.**
