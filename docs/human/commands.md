# Commands

`harnessgg-kdenlive` is bridge-only. Start the bridge first.

```bash
harnessgg-kdenlive bridge start
harnessgg-kdenlive bridge status
```

## Core Commands

```bash
harnessgg-kdenlive actions
harnessgg-kdenlive capabilities
harnessgg-kdenlive doctor [--report-on-failure/--no-report-on-failure] [--include-render/--no-include-render] [--report-url <url>]
harnessgg-kdenlive plan-edit <project.kdenlive> <action> [--params-json <json>]
harnessgg-kdenlive undo <project.kdenlive> [--snapshot-id <id>]
harnessgg-kdenlive redo <project.kdenlive>
harnessgg-kdenlive autosave <project.kdenlive> [--interval-seconds 60] [--enabled/--no-enabled]
harnessgg-kdenlive pack-project <project.kdenlive> <output-dir> [--media-dir-name media]
harnessgg-kdenlive recalc-bounds <project.kdenlive> [--output out.kdenlive]
harnessgg-kdenlive create-project <output.kdenlive> [--title <name>] [--width 1920] [--height 1080] [--fps 30] [--overwrite]
harnessgg-kdenlive clone-project <source.kdenlive> <target.kdenlive> [--overwrite]
harnessgg-kdenlive inspect <project.kdenlive>
harnessgg-kdenlive validate <project.kdenlive> [--check-files/--no-check-files]
harnessgg-kdenlive diff <source.kdenlive> <target.kdenlive>
harnessgg-kdenlive import-asset <project.kdenlive> <media-path> [--producer-id <id>] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive add-text <project.kdenlive> <text> [--duration-frames 90] [--track-id <id>] [--position 0] [--font "DejaVu Sans"] [--size 64] [--color "#ffffff"] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive update-text <project.kdenlive> <producer_id> [--text <text>] [--font <font>] [--size <n>] [--color <hex>] [--duration-frames <n>] [--output out.kdenlive]
harnessgg-kdenlive asset-metadata <project.kdenlive> <producer_id>
harnessgg-kdenlive replace-asset <project.kdenlive> <producer_id> <media-path> [--update-name/--no-update-name] [--output out.kdenlive]
harnessgg-kdenlive list-bin <project.kdenlive>
harnessgg-kdenlive create-bin-folder <project.kdenlive> <name> [--parent-id <id>] [--output out.kdenlive]
harnessgg-kdenlive move-asset-to-folder <project.kdenlive> <producer_id> <folder_id> [--output out.kdenlive]
harnessgg-kdenlive set-effect-keyframes <project> <clip_ref> <effect_id> <parameter> <keyframes-json> [--output out.kdenlive]
harnessgg-kdenlive add-clip <project> <clip_id> <track_id> <position> [--in-point 0] [--out-point 49] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive move-clip <project> <clip_ref> <track_id> <position> [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive trim-clip <project> <clip_ref> [--in-point 0] [--out-point 49] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive remove-clip <project> <clip_ref> [--close-gap] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive split-clip <project> <clip_ref> <position> [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive ripple-delete <project> <clip_ref> [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive insert-gap <project> <track_id> <position> <length> [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive remove-all-gaps <project> <track_id> [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive stitch-clips <project> <track_id> <clip_id...> [--position <frame>] [--gap 0] [--duration-frames <n>] [--output out.kdenlive] [--dry-run]
harnessgg-kdenlive list-clips <project> [--track-id <id>] [--producer-id <id>]
harnessgg-kdenlive resolve-clip <project> <selector> [--track-id <id>] [--at-frame <n>]
harnessgg-kdenlive select-zone <project> [--zone-in 0] [--zone-out 0] [--output out.kdenlive]
harnessgg-kdenlive detect-gaps <project> [--track-id <id>]
harnessgg-kdenlive time-remap <project> <clip_ref> <speed> [--output out.kdenlive]
harnessgg-kdenlive transform-clip <project> <clip_ref> [--geometry <str>] [--rotate <float>] [--scale <float>] [--opacity <float>] [--keyframes-json <json>] [--output out.kdenlive]
harnessgg-kdenlive nudge-clip <project> <clip_ref> <delta_frames> [--output out.kdenlive]
harnessgg-kdenlive slip-clip <project> <clip_ref> <delta_frames> [--output out.kdenlive]
harnessgg-kdenlive slide-clip <project> <clip_ref> <delta_frames> [--output out.kdenlive]
harnessgg-kdenlive ripple-insert <project> <track_id> <position> [--length <n>] [--clip-id <id>] [--in-point <n>] [--out-point <n>] [--output out.kdenlive]
harnessgg-kdenlive group-clips <project> <clip_ref...> [--group-id <id>] [--output out.kdenlive]
harnessgg-kdenlive ungroup-clips <project> <clip_ref...> [--output out.kdenlive]
harnessgg-kdenlive list-sequences <project>
harnessgg-kdenlive copy-sequence <project> <source_id> [--new-id <id>] [--output out.kdenlive]
harnessgg-kdenlive set-active-sequence <project> <sequence_id> [--output out.kdenlive]
harnessgg-kdenlive list-effects <project> <clip_ref>
harnessgg-kdenlive apply-effect <project> <clip_ref> <service> [--effect-id <id>] [--properties-json <json>] [--output out.kdenlive]
harnessgg-kdenlive update-effect <project> <clip_ref> <effect_id> <properties-json> [--output out.kdenlive]
harnessgg-kdenlive remove-effect <project> <clip_ref> <effect_id> [--output out.kdenlive]
harnessgg-kdenlive list-transitions <project>
harnessgg-kdenlive apply-transition <project> [--in-frame 0] [--out-frame 0] [--service mix] [--transition-id <id>] [--properties-json <json>] [--output out.kdenlive]
harnessgg-kdenlive remove-transition <project> <transition_id> [--output out.kdenlive]
harnessgg-kdenlive apply-wipe <project> [--in-frame 0] [--out-frame 0] [--preset circle|clock|barn|iris|linear] [--transition-id <id>] [--softness <float>] [--invert] [--output out.kdenlive]
harnessgg-kdenlive add-music-bed <project> <media> [--track-id playlist1] [--position 0] [--duration-frames <n>] [--producer-id <id>] [--output out.kdenlive]
harnessgg-kdenlive duck-audio <project> <track_id> [--duck-gain 0.3] [--output out.kdenlive]
harnessgg-kdenlive audio-fade <project> <clip_ref> [--fade-type in|out] [--frames 24] [--output out.kdenlive]
harnessgg-kdenlive normalize-audio <project> <clip_ref> [--target-db -14] [--output out.kdenlive]
harnessgg-kdenlive remove-silence <project> <clip_ref> [--threshold-db -35] [--min-duration-frames 6] [--output out.kdenlive]
harnessgg-kdenlive audio-pan <project> <clip_ref> <pan> [--output out.kdenlive]
harnessgg-kdenlive grade-clip <project> <clip_ref> [--lift <float>] [--gamma <float>] [--gain <float>] [--saturation <float>] [--temperature <float>] [--lut-path <path>] [--output out.kdenlive]
harnessgg-kdenlive add-track <project> [--track-type video|audio] [--name <name>] [--index <n>] [--track-id <id>] [--output out.kdenlive]
harnessgg-kdenlive remove-track <project> <track_id> [--force] [--output out.kdenlive]
harnessgg-kdenlive reorder-track <project> <track_id> <index> [--output out.kdenlive]
harnessgg-kdenlive resolve-track <project> <name-or-id>
harnessgg-kdenlive track-mute <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive track-unmute <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive track-lock <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive track-unlock <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive track-show <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive track-hide <project> <track_id> [--output out.kdenlive]
harnessgg-kdenlive snapshot <project> <description>
harnessgg-kdenlive render-clip <source.mp4> <output.mp4> <duration_seconds> [--start-seconds 0] [--preset-name h264|hevc|prores]
harnessgg-kdenlive render-project <project.kdenlive> <output.mp4> [--start-seconds <float>] [--duration-seconds <float>] [--zone-in <frame>] [--zone-out <frame>] [--preset-name h264|hevc|prores]
harnessgg-kdenlive render-status <job_id>
harnessgg-kdenlive render-latest [--type project|clip] [--status running|completed|failed|canceled]
harnessgg-kdenlive render-retry <job_id> [--output <path>]
harnessgg-kdenlive render-cancel <job_id>
harnessgg-kdenlive render-list-jobs
harnessgg-kdenlive render-wait <job_id> [--timeout-seconds 120] [--poll-interval-seconds 0.2]
harnessgg-kdenlive export-edl <project.kdenlive> <output.edl>
harnessgg-kdenlive export-xml <project.kdenlive> <output.xml>
harnessgg-kdenlive export-otio <project.kdenlive> <output.otio>
harnessgg-kdenlive batch <steps-json> [--stop-on-error/--no-stop-on-error]
harnessgg-kdenlive version
```

Notes:
- `add-text` automatically falls back to subtitle-sidecar mode when `qtext` is unavailable on the local MLT build.
- `render-project` automatically burns harness text overlays with `ffmpeg` when local MLT text producers are unavailable/unreliable.

## Bridge Lifecycle

```bash
harnessgg-kdenlive bridge start [--host 127.0.0.1] [--port 41739]
harnessgg-kdenlive bridge serve [--host 127.0.0.1] [--port 41739]   # foreground
harnessgg-kdenlive bridge status
harnessgg-kdenlive bridge stop
```

## Bridge Verification

Use this to verify the bridge is stable and responsive.

```bash
harnessgg-kdenlive bridge verify [--iterations 25] [--max-failures 0]
harnessgg-kdenlive bridge soak [--iterations 100] [--duration-seconds 5] [--action system.health]
```

Returns non-zero when stability criteria fail.

