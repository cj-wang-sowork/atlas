# Example: Marketing Team on OpenClaw

A complete, real-world example of running a 3-agent marketing team using OpenClaw on a single VM.

This example shows how SoWork uses OpenClaw to power an AI marketing team — adapted and generalized for community use.

---

## Overview

**Setup:** 1 VM (cloud or local) running OpenClaw Gateway, with 3 agent workspaces configured for different marketing roles.

**Agents:**
- **CMO Agent** — strategy, positioning, campaign briefs
- **Content Agent** — writing, editing, social posts, copy
- **Intel Agent** — market research, competitor tracking, news monitoring

**Channels:** Slack (primary), with outputs delivered to a shared Slack channel

---

## Architecture

```
Slack / LINE / Telegram
        │
        ▼
OpenClaw Gateway (VM)
        │
        ├── CMO Agent workspace (~/.openclaw/workspaces/cmo/)
        │       └── SOUL: senior brand strategist
        │       └── Skills: brand-positioning.md
        │
        ├── Content Agent workspace (~/.openclaw/workspaces/content/)
        │       └── SOUL: senior copywriter
        │       └── Skills: content-writer.md
        │
        └── Intel Agent workspace (~/.openclaw/workspaces/intel/)
                └── SOUL: research analyst
                └── Skills: web-research.md
```

---

## Setup Guide

### Step 1: Provision Your VM

Any Linux VM works. Recommended minimum:
- **2 vCPU, 4GB RAM** for 3 agents
- **Ubuntu 22.04** or 24.04
- **Node.js 22+** installed

Cloud options: DigitalOcean ($24/mo), Hetzner (€8/mo), Azure B2s (~$35/mo).

```bash
# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install OpenClaw globally
npm install -g openclaw@latest
```

### Step 2: Run OpenClaw Onboard

```bash
openclaw onboard --install-daemon
```

Follow the prompts to configure your gateway, connect Slack, and set your model.

### Step 3: Create Agent Workspaces

```bash
# Create workspace directories
mkdir -p ~/.openclaw/workspaces/cmo
mkdir -p ~/.openclaw/workspaces/content
mkdir -p ~/.openclaw/workspaces/intel

# Copy skill files to each workspace
cp skills/brand-positioning.md ~/.openclaw/workspaces/cmo/skills/
cp skills/content-writer.md ~/.openclaw/workspaces/content/skills/
cp skills/web-research.md ~/.openclaw/workspaces/intel/skills/
```

### Step 4: Configure Agents

In your `~/.openclaw/openclaw.json`, configure multi-agent routing:

```json
{
  "agents": {
    "cmo": {
      "workspace": "~/.openclaw/workspaces/cmo",
      "model": "anthropic/claude-sonnet-4",
      "soul": "Senior brand strategist. Thinks in positioning, audiences, and growth."
    },
    "content": {
      "workspace": "~/.openclaw/workspaces/content",
      "model": "anthropic/claude-sonnet-4",
      "soul": "Senior copywriter. Writes punchy, clear marketing content."
    },
    "intel": {
      "workspace": "~/.openclaw/workspaces/intel",
      "model": "google/gemini-2.5-pro",
      "soul": "Research analyst. Synthesizes market data and competitor insights."
    }
  },
  "channels": {
    "slack": {
      "botToken": "xoxb-YOUR-TOKEN",
      "appToken": "xapp-YOUR-TOKEN"
    }
  }
}
```

### Step 5: Workspace Files

Copy the template files from this repo into each workspace:

```bash
# CMO workspace
cp AGENTS.md ~/.openclaw/workspaces/cmo/AGENTS.md
cp SOUL.md ~/.openclaw/workspaces/cmo/SOUL.md  # customize for strategist persona

# Content workspace
cp AGENTS.md ~/.openclaw/workspaces/content/AGENTS.md
cp SOUL.md ~/.openclaw/workspaces/content/SOUL.md  # customize for writer persona

# Intel workspace
cp AGENTS.md ~/.openclaw/workspaces/intel/AGENTS.md
cp SOUL.md ~/.openclaw/workspaces/intel/SOUL.md  # customize for analyst persona
```

---

## Example Workflows

### Workflow 1: Brand Positioning Sprint

```
You → CMO Agent:  "Run a brand positioning analysis for [Brand]. Competitors: X, Y, Z."
CMO Agent:        [runs brand-positioning.md skill, produces framework]

You → Intel Agent: "Research competitors X, Y, Z. Focus on positioning and recent moves."
Intel Agent:      [runs web-research.md, produces competitor report]

You → CMO Agent:  "Update the positioning using the Intel report."
CMO Agent:        [synthesizes, outputs final positioning]

You → Content Agent: "Write 5 LinkedIn posts using this positioning."
Content Agent:    [runs content-writer.md, delivers 5 options]
```

### Workflow 2: Weekly Market Intel

Set up a cron job with OpenClaw:

```json
{
  "cron": {
    "weekly-intel": {
      "schedule": "0 9 * * MON",
      "agent": "intel",
      "message": "Run weekly market research. Topics: AI marketing tools, competitor news, industry trends. Deliver summary to #marketing-intel Slack channel."
    }
  }
}
```

Every Monday at 9am, your Intel Agent automatically delivers a market briefing to Slack.

### Workflow 3: Content Calendar

```
You → Content Agent: "Generate 20 LinkedIn posts for [Month]. Use our brand positioning from MEMORY.md. Mix: 40% educational, 30% product, 30% thought leadership."
Content Agent:    [produces 20 posts in a structured document]
```

---

## Cost Estimate

Running 3 agents on a $24/mo DigitalOcean droplet:

| Item | Monthly cost |
|------|-------------|
| VM (2vCPU / 4GB) | ~$24 |
| Claude Sonnet (2 agents, ~50 sessions/mo) | ~$15-30 |
| Gemini Pro (Intel agent, ~100 searches/mo) | ~$5-10 |
| **Total** | **~$45-65/mo** |

Compare: a junior marketing hire costs $3,000-5,000/mo. An AI marketing team costs $50-65/mo.

---

## Files in This Example

```
examples/marketing-team/
└── README.md     ← you are here (setup guide + architecture)
```

The actual skill files are in the `skills/` directory at the repo root:
- `skills/brand-positioning.md`
- `skills/content-writer.md`
- `skills/web-research.md`

---

## Credits

This architecture was developed and battle-tested by the [SoWork](https://sowork.ai) team running AI marketing operations across 13 markets.

Adapted and open-sourced for the OpenClaw community.

---

*Part of the [openclaw-workspace-sowork](https://github.com/biombacj-cell/openclaw-workspace-sowork) collection.*
