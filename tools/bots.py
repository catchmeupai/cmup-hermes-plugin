"""Discovery tools: bots, channels, and the fast weekly digest."""

from __future__ import annotations

from ..runner import build_flags, run_cli


BOTS_LIST_SCHEMA = {
    "name": "catchmeup_bots_list",
    "description": (
        "List all bots the user can access (owned + shared), each with id, name, status, and "
        "connected Discord/Slack servers. EVERY other tool needs a bot id from here — call "
        "this first."
    ),
    "parameters": {"type": "object", "properties": {}},
}


def catchmeup_bots_list(args, **_):
    return run_cli(["bots", "list"])


CHANNELS_LIST_SCHEMA = {
    "name": "catchmeup_channels_list",
    "description": (
        "List a bot's channels with message counts and last-activity dates. Use it to discover "
        "the exact channel names before calling logs/summaries."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string", "description": "Bot id (from catchmeup_bots_list)."},
            "server_id": {"type": "string", "description": "Optional: restrict to one server/guild id."},
        },
        "required": ["bot"],
    },
}


def catchmeup_channels_list(args, **_):
    return run_cli(["channels", "list", *build_flags({"bot": args["bot"], "server-id": args.get("server_id")})])


DIGEST_SCHEMA = {
    "name": "catchmeup_digest",
    "description": (
        "7-day activity digest for a bot — the fastest high-level overview across all channels "
        "(cached). Best first call for 'what happened this week / catch me up'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bot": {"type": "string", "description": "Bot id."},
            "discord_links": {"type": "boolean", "description": "Render #channel refs as clickable Discord links."},
        },
        "required": ["bot"],
    },
}


def catchmeup_digest(args, **_):
    return run_cli(["digest", *build_flags({"bot": args["bot"], "discord-links": args.get("discord_links")})])


TOOLS = [
    (BOTS_LIST_SCHEMA, catchmeup_bots_list),
    (CHANNELS_LIST_SCHEMA, catchmeup_channels_list),
    (DIGEST_SCHEMA, catchmeup_digest),
]
