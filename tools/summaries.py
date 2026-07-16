"""AI summary tools: bulk daily/weekly summaries, and a single summary."""

from __future__ import annotations

from ..runner import build_flags, run_cli


SUMMARIES_LIST_SCHEMA = {
    "name": "catchmeup_summaries_list",
    "description": (
        "AI-generated daily/weekly channel summaries WITH their content, grouped by date. The "
        "best source for 'what was discussed' over a range without reading raw logs. Filter by "
        "type (daily|weekly), channels, and from/to."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "type": {"type": "string", "enum": ["daily", "weekly"], "description": "Restrict to daily or weekly."},
            "channels": {"type": "array", "items": {"type": "string"}, "description": "Restrict to these channel names."},
            "from": {"type": "string", "description": "Start date YYYY-MM-DD."},
            "to": {"type": "string", "description": "End date YYYY-MM-DD."},
            "server_id": {"type": "string"},
            "page": {"type": "integer"},
            "page_size": {"type": "integer", "description": "Dates per page (default 7, max 31)."},
        },
        "required": ["bot"],
    },
}


def catchmeup_summaries_list(args, **_):
    return run_cli(["summaries", "list", *build_flags({
        "bot": args["bot"], "type": args.get("type"), "channel": args.get("channels"),
        "from": args.get("from"), "to": args.get("to"), "server-id": args.get("server_id"),
        "page": args.get("page"), "page-size": args.get("page_size"),
    })])


SUMMARIES_GET_SCHEMA = {
    "name": "catchmeup_summaries_get",
    "description": "One specific summary (daily or weekly) for a channel + date.",
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "type": {"type": "string", "enum": ["daily", "weekly"]},
            "channel": {"type": "string"},
            "date": {"type": "string", "description": "YYYY-MM-DD (week-start date for weekly)."},
            "server_id": {"type": "string"},
        },
        "required": ["bot", "type", "channel", "date"],
    },
}


def catchmeup_summaries_get(args, **_):
    return run_cli(["summaries", "get", *build_flags({
        "bot": args["bot"], "type": args["type"], "channel": args["channel"],
        "date": args["date"], "server-id": args.get("server_id"),
    })])


TOOLS = [(SUMMARIES_LIST_SCHEMA, catchmeup_summaries_list), (SUMMARIES_GET_SCHEMA, catchmeup_summaries_get)]
