"""Catch Me Up Hermes Agents plugin.

Exposes the Catch Me Up CLI (`catchmeup`, catchmeupai.com) as agent tools grouped under the
`catchmeup` toolset — Discord/Slack log archive, AI daily/weekly summaries, keyword search,
per-user messages + activity, popular messages, and NotebookLM.

Each tool shells out to the `catchmeup` CLI in --json mode (see runner.py) and returns a
structured envelope. Tools are only visible when the CLI is installed AND authenticated.
See skill/SKILL.md for the deep reference (product model, workflows, gotchas).
"""

from __future__ import annotations

import json
import subprocess

from .runner import CLI, cli_available
from .tools import auth, bots, logs, notebooklm, summaries, users

_TOOL_MODULES = [auth, bots, logs, summaries, users, notebooklm]
_TOOLSET = "catchmeup"


def _authenticated() -> bool:
    """check_fn: tools are visible only when catchmeup is installed AND logged in."""
    if not cli_available():
        return False
    try:
        proc = subprocess.run(
            [CLI, "--json", "auth", "status"], capture_output=True, timeout=10, check=False
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    if proc.returncode != 0:
        return False
    try:
        return bool(json.loads(proc.stdout).get("authenticated"))
    except (json.JSONDecodeError, AttributeError):
        return False


def register(ctx) -> None:
    """Hermes entrypoint. Registers every tool from every module under the `catchmeup` toolset."""
    for module in _TOOL_MODULES:
        for schema, handler in module.TOOLS:
            ctx.register_tool(
                name=schema["name"],
                toolset=_TOOLSET,
                schema=schema,
                handler=lambda args, _h=handler, **kw: _h(args, **kw),
                check_fn=_authenticated,
                emoji="📨",
            )
