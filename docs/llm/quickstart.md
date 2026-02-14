# LLM Quickstart

## 1) Start bridge

```bash
harness-kdenlive bridge start
```

## 2) Verify bridge health/stability

```bash
harness-kdenlive bridge status
harness-kdenlive bridge verify --iterations 25
harness-kdenlive bridge soak --iterations 100 --duration-seconds 5
```

## 3) Inspect and validate project

```bash
harness-kdenlive inspect project.kdenlive
harness-kdenlive validate project.kdenlive
```

## 4) Create/import/edit timeline

```bash
harness-kdenlive create-project edited.kdenlive --title "Agent Edit" --overwrite
harness-kdenlive import-asset edited.kdenlive C:\path\to\clip.mp4 --producer-id clip1
harness-kdenlive add-text edited.kdenlive "Opening Title" --duration-frames 75 --track-id playlist0 --position 0
harness-kdenlive stitch-clips edited.kdenlive playlist0 clip1 clip1 --position 75 --gap 10
```

## 5) Confirm changes

```bash
harness-kdenlive inspect edited.kdenlive
harness-kdenlive validate edited.kdenlive --no-check-files
harness-kdenlive plan-edit edited.kdenlive timeline.add_clip --params-json "{\"clip_id\":\"clip1\",\"track_id\":\"playlist0\",\"position\":120}"
harness-kdenlive render-project edited.kdenlive output.mp4
harness-kdenlive render-status <job_id>
```
