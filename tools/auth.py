"""Auth tool. login/logout are interactive and intentionally not exposed."""

from __future__ import annotations

from ..runner import run_cli


AUTH_STATUS_SCHEMA = {
    "name": "catchmeup_auth_status",
    "description": (
        "Check whether the local catchmeup CLI is authenticated to Catch Me Up "
        "(catchmeupai.com). Returns {authenticated, expired, server, scope}. Call this "
        "first if other catchmeup tools report an auth error."
    ),
    "parameters": {"type": "object", "properties": {}},
}


def catchmeup_auth_status(args, **_):
    return run_cli(["auth", "status"])


TOOLS = [(AUTH_STATUS_SCHEMA, catchmeup_auth_status)]
