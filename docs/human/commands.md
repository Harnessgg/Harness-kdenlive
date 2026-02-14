# Commands

`harness-kdenlive` is bridge-only. Start the bridge first.

```bash
harness-kdenlive bridge start
harness-kdenlive bridge status
```

## Core Commands

```bash
harness-kdenlive actions
harness-kdenlive doctor [--report-on-failure/--no-report-on-failure] [--include-render/--no-include-render] [--report-url <url>]
harness-kdenlive plan-edit <project.kdenlive> <action> [--params-json <json>]
harness-kdenlive undo <project.kdenlive> [--snapshot-id <id>]
harness-kdenlive redo <project.kdenlive>
harness-kdenlive recalc-bounds <project.kdenlive> [--output out.kdenlive]
harness-kdenlive create-project <output.kdenlive> [--title <name>] [--width 1920] [--height 1080] [--fps 30] [--overwrite]
harness-kdenlive clone-project <source.kdenlive> <target.kdenlive> [--overwrite]
harness-kdenlive inspect <project.kdenlive>
harness-kdenlive validate <project.kdenlive> [--check-files/--no-check-files]
harness-kdenlive diff <source.kdenlive> <target.kdenlive>
harness-kdenlive import-asset <project.kdenlive> <media-path> [--producer-id <id>] [--output out.kdenlive] [--dry-run]
harness-kdenlive add-text <project.kdenlive> <text> [--duration-frames 90] [--track-id <id>] [--position 0] [--font "DejaVu Sans"] [--size 64] [--color "#ffffff"] [--output out.kdenlive] [--dry-run]
harness-kdenlive update-text <project.kdenlive> <producer_id> [--text <text>] [--font <font>] [--size <n>] [--color <hex>] [--duration-frames <n>] [--output out.kdenlive]
harness-kdenlive set-effect-keyframes <project> <clip_ref> <effect_id> <parameter> <keyframes-json> [--output out.kdenlive]
harness-kdenlive add-clip <project> <clip_id> <track_id> <position> [--in-point 0] [--out-point 49] [--output out.kdenlive] [--dry-run]
harness-kdenlive move-clip <project> <clip_ref> <track_id> <position> [--output out.kdenlive] [--dry-run]
harness-kdenlive trim-clip <project> <clip_ref> [--in-point 0] [--out-point 49] [--output out.kdenlive] [--dry-run]
harness-kdenlive remove-clip <project> <clip_ref> [--close-gap] [--output out.kdenlive] [--dry-run]
harness-kdenlive split-clip <project> <clip_ref> <position> [--output out.kdenlive] [--dry-run]
harness-kdenlive ripple-delete <project> <clip_ref> [--output out.kdenlive] [--dry-run]
harness-kdenlive insert-gap <project> <track_id> <position> <length> [--output out.kdenlive] [--dry-run]
harness-kdenlive remove-all-gaps <project> <track_id> [--output out.kdenlive] [--dry-run]
harness-kdenlive stitch-clips <project> <track_id> <clip_id...> [--position <frame>] [--gap 0] [--duration-frames <n>] [--output out.kdenlive] [--dry-run]
harness-kdenlive time-remap <project> <clip_ref> <speed> [--output out.kdenlive]
harness-kdenlive transform-clip <project> <clip_ref> [--geometry <str>] [--rotate <float>] [--scale <float>] [--opacity <float>] [--keyframes-json <json>] [--output out.kdenlive]
harness-kdenlive list-effects <project> <clip_ref>
harness-kdenlive apply-effect <project> <clip_ref> <service> [--effect-id <id>] [--properties-json <json>] [--output out.kdenlive]
harness-kdenlive update-effect <project> <clip_ref> <effect_id> <properties-json> [--output out.kdenlive]
harness-kdenlive remove-effect <project> <clip_ref> <effect_id> [--output out.kdenlive]
harness-kdenlive list-transitions <project>
harness-kdenlive apply-transition <project> [--in-frame 0] [--out-frame 0] [--service mix] [--transition-id <id>] [--properties-json <json>] [--output out.kdenlive]
harness-kdenlive remove-transition <project> <transition_id> [--output out.kdenlive]
harness-kdenlive apply-wipe <project> [--in-frame 0] [--out-frame 0] [--preset circle|clock|barn|iris|linear] [--transition-id <id>] [--softness <float>] [--invert] [--output out.kdenlive]
harness-kdenlive add-music-bed <project> <media> [--track-id playlist1] [--position 0] [--duration-frames <n>] [--producer-id <id>] [--output out.kdenlive]
harness-kdenlive duck-audio <project> <track_id> [--duck-gain 0.3] [--output out.kdenlive]
harness-kdenlive audio-fade <project> <clip_ref> [--fade-type in|out] [--frames 24] [--output out.kdenlive]
harness-kdenlive grade-clip <project> <clip_ref> [--lift <float>] [--gamma <float>] [--gain <float>] [--saturation <float>] [--temperature <float>] [--lut-path <path>] [--output out.kdenlive]
harness-kdenlive add-track <project> [--track-type video|audio] [--name <name>] [--index <n>] [--track-id <id>] [--output out.kdenlive]
harness-kdenlive remove-track <project> <track_id> [--force] [--output out.kdenlive]
harness-kdenlive reorder-track <project> <track_id> <index> [--output out.kdenlive]
harness-kdenlive snapshot <project> <description>
harness-kdenlive render-clip <source.mp4> <output.mp4> <duration_seconds> [--start-seconds 0] [--preset-name h264|hevc|prores]
harness-kdenlive render-project <project.kdenlive> <output.mp4> [--start-seconds <float>] [--duration-seconds <float>] [--zone-in <frame>] [--zone-out <frame>] [--preset-name h264|hevc|prores]
harness-kdenlive render-status <job_id>
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
harness-kdenlive bridge soak [--iterations 100] [--duration-seconds 5] [--action system.health]
```

Returns non-zero when stability criteria fail.
