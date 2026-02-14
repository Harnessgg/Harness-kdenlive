# Command Spec (LLM)

## Global rules

1. CLI commands emit exactly one JSON object to stdout.
2. Commands are bridge-only. If bridge is unavailable, calls fail with `BRIDGE_UNAVAILABLE`.
3. Start bridge with `harness-kdenlive bridge start`.

## Exit codes

- `0`: success
- `1`: internal error
- `2`: file not found
- `3`: validation failed
- `4`: invalid input
- `5`: bridge unavailable

## Bridge commands

- `harness-kdenlive bridge start [--host <ip>] [--port <int>]`
- `harness-kdenlive bridge serve [--host <ip>] [--port <int>]`
- `harness-kdenlive bridge status`
- `harness-kdenlive bridge stop`
- `harness-kdenlive bridge verify [--iterations <int>] [--max-failures <int>]`

## Editing commands

- `harness-kdenlive actions`
- `harness-kdenlive inspect <project>`
- `harness-kdenlive validate <project> [--check-files/--no-check-files]`
- `harness-kdenlive diff <source> <target>`
- `harness-kdenlive add-clip <project> <clip_id> <track_id> <position> [--in-point <int>] [--out-point <int>] [--output <path>]`
- `harness-kdenlive move-clip <project> <clip_ref> <track_id> <position> [--output <path>]`
- `harness-kdenlive trim-clip <project> <clip_ref> [--in-point <int>] [--out-point <int>] [--output <path>]`
- `harness-kdenlive remove-clip <project> <clip_ref> [--close-gap] [--output <path>]`
- `harness-kdenlive snapshot <project> <description>`
- `harness-kdenlive render-clip <source.mp4> <output.mp4> <duration_seconds> [--start-seconds <float>]`
- `harness-kdenlive version`
