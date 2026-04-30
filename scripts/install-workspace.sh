#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET=""
DEST=""
FORCE=0

usage() {
  cat <<'EOF'
Usage:
  ./scripts/install-workspace.sh --target openclaw [--dest PATH] [--force]
  ./scripts/install-workspace.sh --target claude --dest PATH [--force]
  ./scripts/install-workspace.sh --target codex --dest PATH [--force]
  ./scripts/install-workspace.sh --target qwen [--dest PATH] [--force]
  ./scripts/install-workspace.sh --target hermes [--dest PATH] [--force]
  ./scripts/install-workspace.sh --target all --dest PATH [--force]

Targets:
  openclaw  Install the workspace files into ~/.openclaw/workspace by default
  claude    Install an AGENTS.md launcher, .atlas-workspace/, and .claude/skills/ into a Claude Code project root (requires --dest)
  codex     Install an AGENTS.md launcher plus .atlas-workspace/ into a Codex CLI project root (requires --dest)
  qwen      Install a Qwen skill pack into ~/.qwen/skills/atlas-enterprise-ai-self-learning by default
  hermes    Install a Hermes skill pack into ~/.hermes/skills/openclaw-imports/openclaw-workspace-sowork by default
  all       Install openclaw + claude + codex + qwen + hermes (requires --dest for Claude/Codex)

Options:
  --target TARGET   One of: openclaw, claude, codex, qwen, hermes, all
  --dest PATH       Destination path (required for claude/codex, optional otherwise)
  --force           Overwrite existing files instead of creating timestamped backups
  -h, --help        Show this help message
EOF
}

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

normalize_path() {
  python3 - "$1" <<'PY'
import os
import sys
print(os.path.realpath(os.path.expanduser(sys.argv[1])))
PY
}

ensure_safe_destination() {
  candidate=$(normalize_path "$1")
  source_root=$(normalize_path "$REPO_ROOT")

  case "$candidate" in
    "$source_root"|"$source_root"/*)
      fail "Destination $candidate overlaps the source repository $source_root. Choose a different --dest outside the cloned repo."
      ;;
  esac
}

backup_or_remove() {
  path=$1
  if [ ! -e "$path" ]; then
    return 0
  fi

  if [ "$FORCE" -eq 1 ]; then
    rm -rf "$path"
    return 0
  fi

  stamp=$(date +%Y%m%d-%H%M%S)
  mv "$path" "$path.bak.$stamp"
  log "Backed up existing $(basename "$path") -> $path.bak.$stamp"
}

copy_item() {
  src=$1
  dest_dir=$2
  [ -e "$src" ] || return 0
  base=$(basename "$src")
  mkdir -p "$dest_dir"
  backup_or_remove "$dest_dir/$base"
  cp -R "$src" "$dest_dir/$base"
}

copy_workspace_bundle() {
  bundle_dest=$1
  mkdir -p "$bundle_dest"

  for item in \
    AGENTS.md \
    HEARTBEAT.md \
    IDENTITY.md \
    MEMORY.md \
    README.md \
    SKILL.md \
    SOUL.md \
    TOOLS.md \
    USER.md \
    CONTRIBUTING.md \
    LICENSE \
    docs \
    examples \
    memory \
    outputs \
    scripts \
    skills
  do
    copy_item "$REPO_ROOT/$item" "$bundle_dest"
  done
}

copy_skill_pack() {
  skill_dest=$1
  mkdir -p "$skill_dest/references" "$skill_dest/templates/workspace" "$skill_dest/assets"

  backup_or_remove "$skill_dest/SKILL.md"
  cp "$REPO_ROOT/SKILL.md" "$skill_dest/SKILL.md"

  for item in AGENTS.md HEARTBEAT.md IDENTITY.md MEMORY.md SOUL.md TOOLS.md USER.md; do
    backup_or_remove "$skill_dest/templates/workspace/$item"
    cp "$REPO_ROOT/$item" "$skill_dest/templates/workspace/$item"
  done

  for item in README.md docs/INSTALLATION.md docs/METHODOLOGY.md docs/LEARN.md docs/workspace-deep-dive.md; do
    src="$REPO_ROOT/$item"
    [ -e "$src" ] || continue
    dest_name=$(basename "$item")
    backup_or_remove "$skill_dest/references/$dest_name"
    cp "$src" "$skill_dest/references/$dest_name"
  done

  backup_or_remove "$skill_dest/assets/skills"
  cp -R "$REPO_ROOT/skills" "$skill_dest/assets/skills"
}

write_project_launcher() {
  launcher_root=$1
  runtime_name=$2
  launcher_path="$launcher_root/AGENTS.md"
  backup_or_remove "$launcher_path"
  cat > "$launcher_path" <<'EOF'
# AGENTS.md - ATLAS bootstrap

At the start of each session, load and follow these workspace files:

- `./.atlas-workspace/AGENTS.md`
- `./.atlas-workspace/SOUL.md`
- `./.atlas-workspace/TOOLS.md`
- `./.atlas-workspace/USER.md`
- `./.atlas-workspace/IDENTITY.md`
- `./.atlas-workspace/HEARTBEAT.md`
- `./.atlas-workspace/MEMORY.md` for direct owner sessions only

Use the reusable skill prompts from `./.atlas-workspace/skills/` when the task matches.
Read `./.atlas-workspace/docs/METHODOLOGY.md` when architecture or learning policy matters.
Treat `./.atlas-workspace/` as agent context, not application source code, unless the user explicitly asks you to edit it.
EOF
  log "$runtime_name launcher written -> $launcher_path"
}

install_openclaw() {
  openclaw_dest=${1:-"$HOME/.openclaw/workspace"}
  ensure_safe_destination "$openclaw_dest"
  log "Installing OpenClaw workspace -> $openclaw_dest"
  copy_workspace_bundle "$openclaw_dest"
  log "OpenClaw install complete."
}

install_claude() {
  project_root=$1
  [ -n "$project_root" ] || fail "Claude target requires --dest /path/to/project"
  ensure_safe_destination "$project_root"
  mkdir -p "$project_root"

  if [ -e "$project_root/AGENTS.md" ] && [ "$FORCE" -ne 1 ]; then
    fail "Refusing to overwrite $project_root/AGENTS.md. Move it, merge it manually, or rerun with --force."
  fi

  claude_workspace="$project_root/.atlas-workspace"
  log "Installing Claude Code workspace context -> $claude_workspace"
  copy_workspace_bundle "$claude_workspace"
  copy_skill_pack "$project_root/.claude/skills/atlas-enterprise-ai-self-learning"
  write_project_launcher "$project_root" "Claude Code"
  log "Claude install complete. Claude Code will pick up AGENTS.md, ./.atlas-workspace/, and ./.claude/skills/."
}

install_codex() {
  project_root=$1
  [ -n "$project_root" ] || fail "Codex target requires --dest /path/to/project"
  ensure_safe_destination "$project_root"
  mkdir -p "$project_root"

  if [ -e "$project_root/AGENTS.md" ] && [ "$FORCE" -ne 1 ]; then
    fail "Refusing to overwrite $project_root/AGENTS.md. Move it, merge it manually, or rerun with --force."
  fi

  codex_workspace="$project_root/.atlas-workspace"
  log "Installing Codex CLI workspace context -> $codex_workspace"
  copy_workspace_bundle "$codex_workspace"
  write_project_launcher "$project_root" "Codex CLI"
  log "Codex install complete. Start Codex from $project_root so it discovers AGENTS.md."
}

install_qwen() {
  qwen_dest=${1:-"$HOME/.qwen/skills/atlas-enterprise-ai-self-learning"}
  ensure_safe_destination "$qwen_dest"
  log "Installing Qwen skill pack -> $qwen_dest"
  copy_skill_pack "$qwen_dest"
  log "Qwen install complete. Run qwen --list-skills to verify discovery."
}

install_hermes() {
  hermes_dest=${1:-"$HOME/.hermes/skills/openclaw-imports/openclaw-workspace-sowork"}
  ensure_safe_destination "$hermes_dest"
  log "Installing Hermes skill pack -> $hermes_dest"
  copy_skill_pack "$hermes_dest"
  log "Hermes install complete. Load the skill: openclaw-workspace-sowork"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target)
      [ $# -ge 2 ] || fail "--target requires a value"
      TARGET=$2
      shift 2
      ;;
    --dest)
      [ $# -ge 2 ] || fail "--dest requires a value"
      DEST=$2
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

[ -n "$TARGET" ] || {
  usage
  fail "--target is required"
}

command -v python3 >/dev/null 2>&1 || fail "python3 is required for path normalization"

case "$TARGET" in
  openclaw)
    install_openclaw "$DEST"
    ;;
  claude)
    install_claude "$DEST"
    ;;
  codex)
    install_codex "$DEST"
    ;;
  qwen)
    install_qwen "$DEST"
    ;;
  hermes)
    install_hermes "$DEST"
    ;;
  all)
    [ -n "$DEST" ] || fail "--target all requires --dest for the Claude/Codex project"
    install_openclaw
    install_claude "$DEST"
    log "Codex CLI support enabled through $DEST/AGENTS.md and $DEST/.atlas-workspace."
    install_qwen
    install_hermes
    ;;
  *)
    fail "Unsupported target: $TARGET"
    ;;
esac
