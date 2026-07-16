#!/usr/bin/env bash
#
# Catch Me Up — Hermes Agents plugin installer.
#
# Does three things:
#   1. Installs the `catchmeup` CLI (npm global; from npm, falling back to the cmup-cli repo).
#   2. Auto-detects the Hermes install + config dir and copies this plugin into plugins/
#      (and skill/SKILL.md into skills/catchmeup/). Skips gracefully if Hermes isn't found.
#   3. Runs the OAuth login (browser) against catchmeupai.com.
#
# Overrides (env or flag):
#   HERMES_HOME / --hermes-home DIR   Hermes config dir (contains plugins/ and skills/)
#   HERMES_BIN  / --hermes-bin PATH   Path to the hermes binary
#   CATCHMEUP_CLI                     Name/path of the catchmeup CLI (default: catchmeup)
#   --skip-cli                        Don't (re)install the CLI
#   --skip-login                      Don't run auth login
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="catchmeup"
CLI="${CATCHMEUP_CLI:-catchmeup}"
CLI_REPO="https://github.com/catchmeupai/cmup-cli.git"
HERMES_BIN="${HERMES_BIN:-}"
HERMES_HOME_ARG="${HERMES_HOME:-}"
SKIP_CLI=0; SKIP_LOGIN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hermes-bin)  HERMES_BIN="$2"; shift 2 ;;
    --hermes-home) HERMES_HOME_ARG="$2"; shift 2 ;;
    --skip-cli)    SKIP_CLI=1; shift ;;
    --skip-login)  SKIP_LOGIN=1; shift ;;
    -h|--help)     sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

info() { printf '  %s\n' "$*"; }
ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[33m!\033[0m %s\n' "$*"; }

# Install the CLI from the public repo by packing a tarball and installing that.
# (`npm i -g git+url` is unreliable for this package — it can omit the built dist/.)
install_cli_from_repo() {
  local d tgz rc
  d="$(mktemp -d)"
  git clone --depth 1 "$CLI_REPO" "$d/cmup-cli" >/dev/null 2>&1 || { rm -rf "$d"; return 1; }
  tgz="$(cd "$d/cmup-cli" && npm pack 2>/dev/null | tail -1)" || { rm -rf "$d"; return 1; }
  npm install -g "$d/cmup-cli/$tgz"; rc=$?
  rm -rf "$d"; return $rc
}

# ---------- 1. Node ----------
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required (for the catchmeup CLI). Install Node 18+ and re-run." >&2
  echo "  macOS: brew install node   |   nvm: nvm install 20 && nvm use 20" >&2
  exit 1
fi

# ---------- 2. Install the CLI ----------
if [[ "$SKIP_CLI" == 0 ]]; then
  if command -v "$CLI" >/dev/null 2>&1; then
    ok "catchmeup CLI already installed: $(command -v "$CLI")"
  else
    info "Installing the catchmeup CLI (npm registry, else from the public repo)..."
    npm install -g catchmeup >/dev/null 2>&1 || install_cli_from_repo
    if command -v "$CLI" >/dev/null 2>&1; then
      ok "catchmeup CLI: $(command -v "$CLI")"
    else
      warn "catchmeup installed but not on PATH. Add your npm global bin (\`npm bin -g\`) to PATH,"
      warn "then re-run. Note: install with the SAME node/npm that Hermes uses (e.g. Homebrew node)."
    fi
  fi
fi

# ---------- 3. Locate Hermes ----------
find_hermes() {
  local c
  for c in "$HERMES_BIN" "$(command -v hermes 2>/dev/null || true)" \
           "$HOME/.local/bin/hermes" "$HOME/.hermes/hermes-agent/venv/bin/hermes" \
           "$HOME/.hermes/venv/bin/hermes" "/opt/hermes/venv/bin/hermes" \
           "/opt/hermes/bin/hermes" "/usr/local/bin/hermes"; do
    [[ -n "$c" && -x "$c" ]] && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}

# Where does the hermes-agent package live? (pip show → Location) — used to walk up to HERMES_HOME.
hermes_source_dir() {
  local bin="$1" py
  py="$(dirname "$bin")/python"; [[ -x "$py" ]] || py="python3"
  "$py" -m pip show hermes-agent 2>/dev/null | awk -F': ' '/^Location:/ {print $2}'
}

detect_hermes_home() {
  [[ -n "$HERMES_HOME_ARG" ]] && { printf '%s\n' "$HERMES_HOME_ARG"; return; }
  local starts=() fallback="" start dir
  [[ -n "${HERMES_BIN_PATH:-}"   ]] && starts+=("$(dirname "$HERMES_BIN_PATH")")
  [[ -n "${HERMES_SOURCE_DIR:-}" ]] && starts+=("$HERMES_SOURCE_DIR")
  for start in "${starts[@]}"; do
    dir="$start"
    for _ in 1 2 3 4 5 6; do
      [[ -f "$dir/config.yaml" ]] && { printf '%s\n' "$dir"; return; }
      if [[ -z "$fallback" && -d "$dir/plugins" && -d "$dir/skills" \
            && ! -f "$dir/pyproject.toml" && ! -f "$dir/setup.py" ]]; then
        fallback="$dir"
      fi
      [[ "$dir" == "/" || "$dir" == "$HOME" ]] && break
      dir="$(dirname "$dir")"
    done
  done
  [[ -n "$fallback" ]] && { printf '%s\n' "$fallback"; return; }
  for c in "$HOME/.hermes" "/opt/hermes"; do [[ -d "$c" ]] && { printf '%s\n' "$c"; return; }; done
  printf '%s\n' "$HOME/.hermes"
}

HERMES_CONFIG_DIR=""
if HERMES_BIN_PATH="$(find_hermes)"; then
  ok "Found hermes: $HERMES_BIN_PATH"
  HERMES_SOURCE_DIR="$(hermes_source_dir "$HERMES_BIN_PATH" || true)"
  HERMES_CONFIG_DIR="$(detect_hermes_home)"
  if [[ -f "$HERMES_CONFIG_DIR/config.yaml" ]]; then
    info "Hermes config dir: $HERMES_CONFIG_DIR (has config.yaml)"
  else
    info "Hermes config dir (guessed): $HERMES_CONFIG_DIR"
  fi
else
  warn "hermes binary not found — installing the CLI + logging in only."
  warn "Re-run with --hermes-home <dir> to install the plugin, or set HERMES_HOME."
fi

# ---------- 4. Install plugin + skill ----------
if [[ -n "$HERMES_CONFIG_DIR" ]]; then
  PLUGIN_DIR="$HERMES_CONFIG_DIR/plugins/$PLUGIN_NAME"
  mkdir -p "$(dirname "$PLUGIN_DIR")"; rm -rf "$PLUGIN_DIR"; mkdir -p "$PLUGIN_DIR"
  for item in plugin.yaml __init__.py runner.py tools README.md; do
    [[ -e "$SCRIPT_DIR/$item" ]] && cp -r "$SCRIPT_DIR/$item" "$PLUGIN_DIR/"
  done
  ok "Plugin installed → $PLUGIN_DIR"
  if [[ -f "$SCRIPT_DIR/skill/SKILL.md" ]]; then
    SKILL_DIR="$HERMES_CONFIG_DIR/skills/$PLUGIN_NAME"
    mkdir -p "$SKILL_DIR"; cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_DIR/SKILL.md"
    ok "Skill installed → $SKILL_DIR/SKILL.md"
  fi
fi

# ---------- 5. Authenticate ----------
if [[ "$SKIP_LOGIN" == 0 ]]; then
  if "$CLI" --json auth status 2>/dev/null | grep -q '"authenticated": true'; then
    ok "Already authenticated to Catch Me Up."
  else
    info "Logging in to Catch Me Up (opens a browser)..."
    "$CLI" auth login || warn "Login not completed — run '$CLI auth login' later."
  fi
fi

echo
ok "Setup complete. The 'catchmeup' toolset will appear in Hermes once you're authenticated."
[[ -n "$HERMES_CONFIG_DIR" ]] && info "Restart Hermes if it was already running so it loads the plugin."
