# Command Spec (LLM)

## Global rules

1. CLI commands emit exactly one JSON object to stdout.
2. Commands are bridge-only except `version`. If bridge is unavailable, bridge-backed calls fail with `BRIDGE_UNAVAILABLE`.
3. Start bridge with `harness-kdenlive bridge start`.
4. Mutating commands perform bridge health preflight (`system.health`) before edit/render calls.

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
- `harness-kdenlive bridge soak [--iterations <int>] [--duration-seconds <float>] [--action <method>]`

## Editing commands

- `harness-kdenlive actions`
- `harness-kdenlive doctor [--report-on-failure/--no-report-on-failure] [--include-render/--no-include-render] [--report-url <url>]`
- `harness-kdenlive create-project <output> [--title <str>] [--width <int>] [--height <int>] [--fps <float>] [--overwrite]`
- `harness-kdenlive clone-project <source> <target> [--overwrite]`
- `harness-kdenlive plan-edit <project> <action> [--params-json <json>]`
- `harness-kdenlive undo <project> [--snapshot-id <id>]`
- `harness-kdenlive redo <project>`
- `harness-kdenlive recalc-bounds <project> [--output <path>]`
- `harness-kdenlive inspect <project>`
- `harness-kdenlive validate <project> [--check-files/--no-check-files]`
- `harness-kdenlive diff <source> <target>`
- `harness-kdenlive import-asset <project> <media> [--producer-id <str>] [--output <path>] [--dry-run]`
- `harness-kdenlive add-text <project> <text> [--duration-frames <int>] [--track-id <str>] [--position <int>] [--font <str>] [--size <int>] [--color <hex>] [--output <path>] [--dry-run]`
- `harness-kdenlive update-text <project> <producer_id> [--text <str>] [--font <str>] [--size <int>] [--color <hex>] [--duration-frames <int>] [--output <path>]`
- `harness-kdenlive set-effect-keyframes <project> <clip_ref> <effect_id> <parameter> <keyframes-json> [--output <path>]`
- `harness-kdenlive add-clip <project> <clip_id> <track_id> <position> [--in-point <int>] [--out-point <int>] [--output <path>] [--dry-run]`
- `harness-kdenlive move-clip <project> <clip_ref> <track_id> <position> [--output <path>] [--dry-run]`
- `harness-kdenlive trim-clip <project> <clip_ref> [--in-point <int>] [--out-point <int>] [--output <path>] [--dry-run]`
- `harness-kdenlive remove-clip <project> <clip_ref> [--close-gap] [--output <path>] [--dry-run]`
- `harness-kdenlive split-clip <project> <clip_ref> <position> [--output <path>] [--dry-run]`
- `harness-kdenlive ripple-delete <project> <clip_ref> [--output <path>] [--dry-run]`
- `harness-kdenlive insert-gap <project> <track_id> <position> <length> [--output <path>] [--dry-run]`
- `harness-kdenlive remove-all-gaps <project> <track_id> [--output <path>] [--dry-run]`
- `harness-kdenlive stitch-clips <project> <track_id> <clip_id...> [--position <int>] [--gap <int>] [--duration-frames <int>] [--output <path>] [--dry-run]`
- `harness-kdenlive time-remap <project> <clip_ref> <speed> [--output <path>]`
- `harness-kdenlive transform-clip <project> <clip_ref> [--geometry <str>] [--rotate <float>] [--scale <float>] [--opacity <float>] [--keyframes-json <json>] [--output <path>]`
- `harness-kdenlive list-effects <project> <clip_ref>`
- `harness-kdenlive apply-effect <project> <clip_ref> <service> [--effect-id <id>] [--properties-json <json>] [--output <path>]`
- `harness-kdenlive update-effect <project> <clip_ref> <effect_id> <properties-json> [--output <path>]`
- `harness-kdenlive remove-effect <project> <clip_ref> <effect_id> [--output <path>]`
- `harness-kdenlive list-transitions <project>`
- `harness-kdenlive apply-transition <project> [--in-frame <int>] [--out-frame <int>] [--service <str>] [--transition-id <id>] [--properties-json <json>] [--output <path>]`
- `harness-kdenlive remove-transition <project> <transition_id> [--output <path>]`
- `harness-kdenlive apply-wipe <project> [--in-frame <int>] [--out-frame <int>] [--preset <name>] [--transition-id <id>] [--softness <float>] [--invert] [--output <path>]`
- `harness-kdenlive add-music-bed <project> <media> [--track-id <id>] [--position <int>] [--duration-frames <int>] [--producer-id <id>] [--output <path>]`
- `harness-kdenlive duck-audio <project> <track_id> [--duck-gain <float>] [--output <path>]`
- `harness-kdenlive audio-fade <project> <clip_ref> [--fade-type in|out] [--frames <int>] [--output <path>]`
- `harness-kdenlive grade-clip <project> <clip_ref> [--lift <float>] [--gamma <float>] [--gain <float>] [--saturation <float>] [--temperature <float>] [--lut-path <path>] [--output <path>]`
- `harness-kdenlive add-track <project> [--track-type video|audio] [--name <str>] [--index <int>] [--track-id <str>] [--output <path>]`
- `harness-kdenlive remove-track <project> <track_id> [--force] [--output <path>]`
- `harness-kdenlive reorder-track <project> <track_id> <index> [--output <path>]`
- `harness-kdenlive snapshot <project> <description>`
- `harness-kdenlive render-clip <source.mp4> <output.mp4> <duration_seconds> [--start-seconds <float>] [--preset-name h264|hevc|prores]`
- `harness-kdenlive render-project <project.kdenlive> <output.mp4> [--start-seconds <float>] [--duration-seconds <float>] [--zone-in <int>] [--zone-out <int>] [--preset-name h264|hevc|prores]`
- `harness-kdenlive render-status <job_id>`
- `harness-kdenlive version`

## Timeouts and Retry Guidance

- Default bridge call timeout: `30s`.
- Health and readiness calls: `5s`.
- Doctor: `180s`.
- Render calls: `600s`.
- Bridge soak timeout: `duration-seconds + 5` (minimum `10s`).
- Retry policy for transient bridge errors:
  - Retry only for `BRIDGE_UNAVAILABLE`.
  - Recommended backoff: `0.5s`, `1s`, `2s` (max 3 retries).
  - Re-run `harness-kdenlive bridge status` before retrying mutating commands.
