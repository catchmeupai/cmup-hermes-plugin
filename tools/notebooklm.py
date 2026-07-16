"""NotebookLM tool: turn a date range of logs into a NotebookLM notebook."""

from __future__ import annotations

from ..runner import build_flags, run_cli


NOTEBOOK_CREATE_SCHEMA = {
    "name": "catchmeup_notebooklm_create",
    "description": (
        "Create a NotebookLM notebook from a bot's logs over a date range (optionally with an "
        "audio overview). Blocks until ready and returns the notebook web URL. SLOW — can take "
        "a minute or more; only call when the user explicitly wants a notebook."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "from": {"type": "string", "description": "Start date YYYY-MM-DD."},
            "to": {"type": "string", "description": "End date YYYY-MM-DD."},
            "server_id": {"type": "string"},
            "audio": {"type": "boolean", "description": "Also generate an audio overview (podcast)."},
        },
        "required": ["bot", "from", "to"],
    },
}


def catchmeup_notebooklm_create(args, **_):
    return run_cli(["notebooklm", "create", *build_flags({
        "bot": args["bot"], "from": args["from"], "to": args["to"],
        "server-id": args.get("server_id"), "audio": args.get("audio"),
    })], timeout=300)


TOOLS = [(NOTEBOOK_CREATE_SCHEMA, catchmeup_notebooklm_create)]
