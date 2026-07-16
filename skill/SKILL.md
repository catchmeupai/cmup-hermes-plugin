# Catch Me Up — Hermes toolset reference

The `catchmeup` toolset gives the agent read access to a team's **Discord/Slack message
history** on the Catch Me Up platform (catchmeupai.com): raw logs, AI-generated daily/weekly
summaries, keyword search, per-user messages and activity, and popular messages.

All tools shell out to the local `catchmeup` CLI (`--json` mode) and return a structured
envelope: `{"ok": true, "data": ...}` on success, `{"error": "..."}` on failure. The toolset
is only visible when the CLI is installed **and** the user is logged in (OAuth to
catchmeupai.com); if a tool returns an auth error, call `catchmeup_auth_status`.

## Core model

- A **bot** is one archival deployment. It has one or more **servers** (Discord guilds / Slack
  workspaces), each with **channels**. Almost every tool needs a **bot id** — get it from
  `catchmeup_bots_list` first, and reuse it.
- **Summaries** are the cheap, high-signal source. Prefer them over raw logs for "what was
  discussed / what happened." Two granularities: `daily` and `weekly`.
- **Raw logs** (`catchmeup_logs_get`, `catchmeup_search`, `catchmeup_users_messages`) are for
  verbatim quotes, attribution, exact timing, and anything a summary flattened away.

## Tools

| Tool | Use it for |
|------|-----------|
| `catchmeup_auth_status` | Confirm login before/after an auth error. |
| `catchmeup_bots_list` | Discover bots + their servers. **Call first** — everything needs a bot id. |
| `catchmeup_channels_list` | Discover exact channel names + activity for a bot. |
| `catchmeup_digest` | Fastest 7-day overview across all channels (cached). Best first answer to "catch me up." |
| `catchmeup_summaries_list` | Daily/weekly summaries with content over a range — the workhorse for "what was discussed." |
| `catchmeup_summaries_get` | One specific summary (channel + date). |
| `catchmeup_logs_get` | Raw messages from one channel (paginated) — verbatim quotes/attribution. |
| `catchmeup_search` | Keyword search across a bot's channels — find *where* a topic/person came up. |
| `catchmeup_users_messages` | Messages by a specific author — "what did X say." |
| `catchmeup_users_activity` | Ranked message counts — "who's most active." |
| `catchmeup_popular` | Most-engaged messages (reactions/replies) in a range — "highlights." |

## Typical workflows

- **"Catch me up on <bot>":** `catchmeup_bots_list` → `catchmeup_digest`. Drill into a channel
  with `catchmeup_summaries_list` (filter `channels`) or `catchmeup_logs_get` if the user wants
  detail/quotes.
- **"What was discussed in #X last week":** `catchmeup_summaries_list` with `channels: ["X"]`
  and `from`/`to`. Fall back to `catchmeup_logs_get` for exact wording.
- **"What did <person> say about <topic>":** `catchmeup_users_messages` (author) and/or
  `catchmeup_search` (topic), then quote from the raw results.
- **"Who's most active / highlights":** `catchmeup_users_activity` / `catchmeup_popular`.

## Gotchas

- **Always pass a `bot` id** to bot-scoped tools; get it from `catchmeup_bots_list`.
- **Dates are `YYYY-MM-DD`.** `weekly` summaries key on the week-start date.
- **Prefer summaries first**, then raw logs — raw pulls can be large; narrow with `from`/`to`
  and `page_size`.
- **Summaries can lag** for the current day (they're generated on a schedule); if today looks
  empty, fetch raw logs for today rather than concluding "nothing happened."
