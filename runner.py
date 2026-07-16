"""Subprocess helper for shelling out to the `catchmeup` CLI in --json mode.

Every tool handler returns a JSON-string envelope so callers always get a
predictable shape: {"ok": true, "data": ...} on success, {"error": ...} on failure.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

CLI = os.environ.get("CATCHMEUP_CLI", "catchmeup")


def cli_available() -> bool:
    return shutil.which(CLI) is not None


def run_cli(args: list[str], timeout: int = 120) -> str:
    """Exec `catchmeup --json <args>` and normalize the result to a JSON envelope."""
    if not cli_available():
        return json.dumps({
            "error": f"'{CLI}' CLI not found in PATH. Run setup.sh (installs the CLI and logs in)."
        })
    try:
        proc = subprocess.run(
            [CLI, "--json", *args], capture_output=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"catchmeup timed out after {timeout}s", "args": args})

    stdout = proc.stdout.decode("utf-8", "replace")
    stderr = proc.stderr.decode("utf-8", "replace")

    if proc.returncode == 0:
        try:
            return json.dumps({"ok": True, "data": json.loads(stdout)})
        except json.JSONDecodeError:
            return json.dumps({"ok": True, "data": stdout.strip()})

    err_msg = stderr.strip() or stdout.strip() or f"exit code {proc.returncode}"
    try:
        parsed = json.loads(stderr)
        if isinstance(parsed, dict) and "error" in parsed:
            err_msg = parsed["error"]
    except json.JSONDecodeError:
        pass
    return json.dumps({"error": err_msg, "exit_code": proc.returncode})


def build_flags(mapping: dict[str, Any]) -> list[str]:
    """Turn {flag: value} into ['--flag', 'value', ...].

    None / False are skipped. True becomes a bare '--flag' (boolean flags like --audio,
    --discord-links). Lists become repeated '--flag v --flag v' (the CLI's --channel).
    """
    out: list[str] = []
    for name, value in mapping.items():
        if value is None or value is False:
            continue
        if value is True:
            out.append(f"--{name}")
            continue
        if isinstance(value, list):
            for v in value:
                out.extend([f"--{name}", str(v)])
            continue
        out.extend([f"--{name}", str(value)])
    return out
