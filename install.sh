#!/bin/sh
set -e

REPO="koreal6803/finlab-ai"
SKILL_SRC="skills/finlab"

# --- Colors ---
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
BOLD="\033[1m"
RESET="\033[0m"

info()  { printf "${CYAN}%s${RESET}\n" "$1"; }
ok()    { printf "${GREEN}%s${RESET}\n" "$1"; }
warn()  { printf "${YELLOW}%s${RESET}\n" "$1"; }
err()   { printf "${RED}%s${RESET}\n" "$1" >&2; }

finish() {
  echo ""
  ok "Done! FinLab AI skill installed for: $TARGETS"
  echo ""
  echo "  Start any CLI and try: /finlab"
  echo ""
}

# --- Detect all installed CLIs ---
TARGETS=""
command -v claude  >/dev/null 2>&1 && TARGETS="$TARGETS claude-code"
command -v codex   >/dev/null 2>&1 && TARGETS="$TARGETS codex"
command -v cursor  >/dev/null 2>&1 && TARGETS="$TARGETS cursor"
command -v windsurf >/dev/null 2>&1 && TARGETS="$TARGETS windsurf"
command -v gemini  >/dev/null 2>&1 && TARGETS="$TARGETS gemini-cli"
TARGETS=${TARGETS# }

skill_dir() {
  case "$1" in
    claude-code) echo "$HOME/.claude/skills/finlab" ;;
    codex)       echo "$HOME/.codex/skills/finlab" ;;
    cursor)      echo "$HOME/.cursor/skills/finlab" ;;
    windsurf)    echo "$HOME/.windsurf/skills/finlab" ;;
    gemini-cli)  echo "$HOME/.gemini/skills/finlab" ;;
  esac
}

# --- Main ---
printf "\n${BOLD}  FinLab AI Installer${RESET}\n"
printf "  ────────────────────\n\n"

if [ -z "$TARGETS" ]; then
  err "No supported AI CLI found."
  echo ""
  echo "  Please install one of:"
  echo "    - Claude Code:  npm install -g @anthropic-ai/claude-code"
  echo "    - Codex CLI:    npm install -g @openai/codex"
  echo "    - Cursor:       https://www.cursor.com/"
  echo "    - Windsurf:     https://windsurf.com/"
  echo "    - Gemini CLI:   npm install -g @google/gemini-cli"
  echo ""
  exit 1
fi

info "Detected: $TARGETS"

# Install uv if missing (needed to run Python code)
if ! command -v uv >/dev/null 2>&1; then
  info "Installing uv (Python package manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  if command -v uv >/dev/null 2>&1; then
    ok "uv installed successfully."
  else
    warn "uv installation failed. You can install it later: https://docs.astral.sh/uv/"
  fi
else
  info "uv: already installed."
fi

# Try npx first (installs for ALL detected agents at once)
if command -v npx >/dev/null 2>&1; then
  info "Installing via npx for: $TARGETS"
  AGENT_FLAGS=$(printf ' -a %s' $TARGETS)
  if npx skills add "$REPO" $AGENT_FLAGS -y 2>/dev/null; then
    finish
    exit 0
  fi
  warn "npx method failed, falling back to git clone..."
fi

# Fallback: git clone (install for all detected CLIs)
if ! command -v git >/dev/null 2>&1; then
  err "git is not installed. Please install git or Node.js and try again."
  exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 "https://github.com/$REPO.git" "$TMP/finlab-ai" 2>/dev/null

for t in $TARGETS; do
  DEST=$(skill_dir "$t")
  info "Installing for $t -> $DEST"
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -r "$TMP/finlab-ai/$SKILL_SRC" "$DEST"
done

finish
