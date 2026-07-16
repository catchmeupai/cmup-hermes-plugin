# cmup-hermes-plugin

A [Hermes Agents](https://github.com/NousResearch/hermes-agent) plugin that exposes the
**Catch Me Up** platform (catchmeupai.com) as native agent tools — Discord/Slack log archive,
AI daily/weekly summaries, keyword search, per-user messages + activity, popular messages, and
NotebookLM.

Each tool is a real, schema'd Hermes tool (not one generic "run a command" tool). Handlers shell
out to the [`catchmeup` CLI](https://github.com/catchmeupai/cmup-cli) in `--json` mode, so the
agent gets structured data. The toolset only appears when the CLI is installed **and**
authenticated.

## Install

```bash
# From the plugin directory:
./setup.sh
```

`setup.sh` installs the `catchmeup` CLI globally and runs the OAuth login (opens a browser,
sign in with Google) against catchmeupai.com. Then point Hermes at this plugin directory.

Manual equivalent:

```bash
npm install -g catchmeup          # or: npm i -g git+https://github.com/catchmeupai/cmup-cli.git
catchmeup auth login              # OAuth PKCE, opens a browser (defaults to catchmeupai.com)
catchmeup --json auth status      # → {"authenticated": true, ...}
```

## Tools (`catchmeup` toolset)

`catchmeup_auth_status`, `catchmeup_bots_list`, `catchmeup_channels_list`, `catchmeup_digest`,
`catchmeup_summaries_list`, `catchmeup_summaries_get`, `catchmeup_logs_get`, `catchmeup_search`,
`catchmeup_users_messages`, `catchmeup_users_activity`, `catchmeup_popular`,
`catchmeup_notebooklm_create`.

See [`skill/SKILL.md`](skill/SKILL.md) for the agent-facing reference (core model, workflows,
gotchas).

## How it works

```
Hermes ──register_tool──▶ tools/*.py ──run_cli──▶ `catchmeup --json <cmd>` ──HTTPS──▶ catchmeupai.com/api/v1
```

- `plugin.yaml` — manifest.
- `__init__.py` — `register(ctx)` entrypoint; registers each tool, gated by a `check_fn` that
  verifies `catchmeup --json auth status` reports `authenticated`.
- `runner.py` — `run_cli()` (subprocess → JSON envelope) + `build_flags()`.
- `tools/*.py` — one module per area; each exports `TOOLS = [(schema, handler), ...]`.

## Config

| Env | Default | Purpose |
|-----|---------|---------|
| `CATCHMEUP_CLI` | `catchmeup` | Path/name of the CLI binary. |

Auth is **OAuth 2.0 + PKCE**, the same flow the CLI uses; tokens live in
`~/.config/catchmeup/tokens.json` and auto-refresh.
