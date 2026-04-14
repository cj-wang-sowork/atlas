# Workspace Deep Dive — Token Optimization & Security

> For marketing teams running OpenClaw at scale. Understanding workspace file costs lets you run more agents for less money.

---

## How OpenClaw Loads Files

Every agent response reads certain workspace files and injects them into the system prompt. Every file in the boot sequence costs tokens on **every single turn**.

### Token Budget

| Constraint | Limit |
|------------|-------|
| Per file hard cap | 20,000 chars (truncated if exceeded) |
| Total across all bootstrap files | ~150,000 chars |
| Recommended per file | 10,000–15,000 chars |

### File Loading Reference

| File | When Loaded | Sub-agents See It? |
|------|-------------|-------------------|
| AGENTS.md | Every turn | Yes |
| SOUL.md | Every turn | Yes |
| IDENTITY.md | Every turn | Yes |
| TOOLS.md | Every turn | Yes |
| USER.md | Every turn (main only) | No |
| HEARTBEAT.md | Heartbeat turns only | Depends |
| MEMORY.md | Main sessions only — MUST be gated | Never (if gated) |
| skills/*.md | On demand | On demand |
| docs/*.md | On demand | On demand |

---

## Token Optimization: Push Detail Down the Stack

```
Instead of: Full brand guidelines in SOUL.md (costs tokens every turn)
Do this:    Brand essence in SOUL.md + full guide in docs/brand-in-soul.md

Instead of: All campaign rules inline in AGENTS.md
Do this:    Reference only in AGENTS.md + detail in docs/

Instead of: Market data tables in TOOLS.md
Do this:    Key shortcuts in TOOLS.md + detail in docs/markets.md
```

### Audit Command

```bash
# Check all workspace file sizes
wc -c ~/.openclaw/workspace/*.md

# Include subdirectories
find ~/.openclaw/workspace -name "*.md" -exec wc -c {} + | sort -rn | head -20

# Target: no single bootstrap file over 15,000 chars
```

---

## Security Gates (Critical)

### The MEMORY.md Gate (Non-Negotiable)

Your AGENTS.md boot sequence MUST include this pattern:

```markdown
## Boot Sequence

1. Read SOUL.md
2. Read IDENTITY.md
3. Read TOOLS.md
4. Read USER.md
5. **Main session only:** Read MEMORY.md
6. Read memory/[today].md and memory/[yesterday].md
```

Without "Main session only", MEMORY.md loads in group chats — exposing client names, campaign strategies, and sensitive intel.

### Group Chat Rules (Add to AGENTS.md)

```markdown
## Groups

In group chats:
- Never share MEMORY.md content
- Never reveal client names or campaign specifics
- Only respond to direct @mentions
```

---

## Memory Distillation

```
Daily:   Agent writes raw session notes to memory/YYYY-MM-DD.md
Weekly:  Review logs, promote key rules to MEMORY.md
Monthly: Delete logs older than 30 days, trim MEMORY.md
```

### What Belongs in MEMORY.md

```
✅ "Singapore market requires formal tone — casual copy underperforms by 40%"
✅ "Campaign template V2 outperforms V1 — always use V2 as baseline"
✅ "Never use urgency language in the Japan market"

❌ "Wrote 3 LinkedIn posts today" (raw log → daily notes)
❌ "Remember to check campaign stats" (task → checklist)
```

---

## Related Files

| File | What it covers |
|------|---------------|
| AGENTS.md | Boot sequence template |
| SOUL.md | 5 persona templates |
| TOOLS.md | Environment cheat sheet |
| USER.md | Human profile template |
| IDENTITY.md | Agent identity card |
| HEARTBEAT.md | Periodic task template |
| docs/brand-in-soul.md | Brand positioning in SOUL.md |
| docs/vm-setup-guide.md | VM provisioning guide |
| examples/marketing-team/ | 3-agent setup with cost breakdown |

---

*Part of [openclaw-workspace-sowork](https://github.com/cj-wang-sowork/openclaw-workspace-sowork)*
