"""Raw-log tools: fetch a channel's messages, and keyword search across channels."""

from __future__ import annotations

from ..runner import build_flags, run_cli


LOGS_GET_SCHEMA = {
    "name": "catchmeup_logs_get",
    "description": (
        "Raw messages from ONE channel, oldest-first, paginated. Use for verbatim quotes and "
        "attribution when a summary isn't enough. Always narrow with from/to when you can."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "channel": {"type": "string", "description": "Channel name (from catchmeup_channels_list)."},
            "from": {"type": "string", "description": "Start date YYYY-MM-DD."},
            "to": {"type": "string", "description": "End date YYYY-MM-DD."},
            "server_id": {"type": "string"},
            "page": {"type": "integer", "description": "Page number (default 1)."},
            "page_size": {"type": "integer", "description": "Messages per page (default 100)."},
        },
        "required": ["bot", "channel"],
    },
}


def catchmeup_logs_get(args, **_):
    return run_cli(["logs", "get", *build_flags({
        "bot": args["bot"], "channel": args["channel"], "from": args.get("from"), "to": args.get("to"),
        "server-id": args.get("server_id"), "page": args.get("page"), "page-size": args.get("page_size"),
    })])


SEARCH_SCHEMA = {
    "name": "catchmeup_search",
    "description": (
        "Keyword search across all of a bot's channels. Returns matching messages with channel, "
        "author, date, and content. Best for finding WHERE a topic/term/person was discussed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "query": {"type": "string", "description": "Search term / keyword."},
            "channel": {"type": "string", "description": "Optional: limit to one channel."},
            "server_id": {"type": "string"},
            "page": {"type": "integer"},
            "page_size": {"type": "integer"},
        },
        "required": ["bot", "query"],
    },
}


def catchmeup_search(args, **_):
    return run_cli(["search", str(args["query"]), *build_flags({
        "bot": args["bot"], "channel": args.get("channel"), "server-id": args.get("server_id"),
        "page": args.get("page"), "page-size": args.get("page_size"),
    })])


TOOLS = [(LOGS_GET_SCHEMA, catchmeup_logs_get), (SEARCH_SCHEMA, catchmeup_search)]
