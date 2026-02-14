# Commands

`harness-kdenlive` is bridge-only. Start the bridge first.

```bash
harness-kdenlive bridge start
harness-kdenlive bridge status
```

## Core Commands

```bash
harness-kdenlive actions
harness-kdenlive inspect <project.kdenlive>
harness-kdenlive validate <project.kdenlive> [--check-files/--no-check-files]
harness-kdenlive diff <source.kdenlive> <target.kdenlive>
harness-kdenlive add-clip <project> <clip_id> <track_id> <position> [--in-point 0] [--out-point 49] [--output out.kdenlive]
harness-kdenlive move-clip <project> <clip_ref> <track_id> <position> [--output out.kdenlive]
harness-kdenlive trim-clip <project> <clip_ref> [--in-point 0] [--out-point 49] [--output out.kdenlive]
harness-kdenlive remove-clip <project> <clip_ref> [--close-gap] [--output out.kdenlive]
harness-kdenlive snapshot <project> <description>
harness-kdenlive render-clip <source.mp4> <output.mp4> <duration_seconds> [--start-seconds 0]
harness-kdenlive version
```

## Bridge Lifecycle

```bash
harness-kdenlive bridge start [--host 127.0.0.1] [--port 41739]
harness-kdenlive bridge serve [--host 127.0.0.1] [--port 41739]   # foreground
harness-kdenlive bridge status
harness-kdenlive bridge stop
```

## Bridge Verification

Use this to verify the bridge is stable and responsive.

```bash
harness-kdenlive bridge verify [--iterations 25] [--max-failures 0]
```

Returns non-zero when stability criteria fail.
