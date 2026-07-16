"""People tools: messages by author, activity ranking, popular messages."""

from __future__ import annotations

from ..runner import build_flags, run_cli


USERS_MESSAGES_SCHEMA = {
    "name": "catchmeup_users_messages",
    "description": "Find messages by a specific author (partial, case-insensitive name match). Use for 'what did X say'.",
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "author": {"type": "string", "description": "Author name (partial ok)."},
            "channel": {"type": "string"},
            "from": {"type": "string"},
            "to": {"type": "string"},
            "server_id": {"type": "string"},
            "page": {"type": "integer"},
            "page_size": {"type": "integer"},
        },
        "required": ["bot", "author"],
    },
}


def catchmeup_users_messages(args, **_):
    return run_cli(["users", "messages", *build_flags({
        "bot": args["bot"], "author": args["author"], "channel": args.get("channel"),
        "from": args.get("from"), "to": args.get("to"), "server-id": args.get("server_id"),
        "page": args.get("page"), "page-size": args.get("page_size"),
    })])


USERS_ACTIVITY_SCHEMA = {
    "name": "catchmeup_users_activity",
    "description": "Ranked message counts per author (who is most active), over an optional range/channel.",
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "channel": {"type": "string"},
            "from": {"type": "string"},
            "to": {"type": "string"},
            "server_id": {"type": "string"},
        },
        "required": ["bot"],
    },
}


def catchmeup_users_activity(args, **_):
    return run_cli(["users", "activity", *build_flags({
        "bot": args["bot"], "channel": args.get("channel"), "from": args.get("from"),
        "to": args.get("to"), "server-id": args.get("server_id"),
    })])


POPULAR_SCHEMA = {
    "name": "catchmeup_popular",
    "description": "Most-engaged messages (by reactions/replies) in a date range. Good for 'highlights / what got attention'.",
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string"},
            "from": {"type": "string", "description": "Start date YYYY-MM-DD."},
            "to": {"type": "string", "description": "End date YYYY-MM-DD."},
            "channel": {"type": "string"},
            "server_id": {"type": "string"},
            "limit": {"type": "integer", "description": "Max results (default 50)."},
        },
        "required": ["bot", "from", "to"],
    },
}


def catchmeup_popular(args, **_):
    return run_cli(["popular", *build_flags({
        "bot": args["bot"], "from": args["from"], "to": args["to"], "channel": args.get("channel"),
        "server-id": args.get("server_id"), "limit": args.get("limit"),
    })])


TOOLS = [
    (USERS_MESSAGES_SCHEMA, catchmeup_users_messages),
    (USERS_ACTIVITY_SCHEMA, catchmeup_users_activity),
    (POPULAR_SCHEMA, catchmeup_popular),
]
