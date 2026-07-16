#!/usr/bin/env bash
# Set up the Catch Me Up Hermes plugin: install the `catchmeup` CLI and authenticate.
set -euo pipefail

if ! command -v catchmeup >/dev/null 2>&1; then
  echo "Installing the catchmeup CLI..."
  npm install -g catchmeup 2>/dev/null \
    || npm install -g "git+https://github.com/catchmeupai/cmup-cli.git"
fi
echo "catchmeup CLI: $(command -v catchmeup)"

# OAuth PKCE login (opens a browser) against catchmeupai.com. Skips if already authenticated.
if catchmeup --json auth status 2>/dev/null | grep -q '"authenticated": true'; then
  echo "Already authenticated."
else
  echo "Logging in to Catch Me Up (opens a browser)..."
  catchmeup auth login
fi

echo "Done. The catchmeup tools will appear in Hermes once authenticated."
