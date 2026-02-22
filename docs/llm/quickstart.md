# LLM Quickstart

## 1) Start bridge

```bash
harnessgg-kdenlive bridge start
```

## 2) Verify bridge health/stability

```bash
harnessgg-kdenlive bridge status
harnessgg-kdenlive capabilities
harnessgg-kdenlive bridge verify --iterations 25
harnessgg-kdenlive bridge soak --iterations 100 --duration-seconds 5
```

## 3) Inspect and validate project

```bash
harnessgg-kdenlive inspect project.kdenlive
harnessgg-kdenlive validate project.kdenlive
```

## 4) Create/import/edit timeline

```bash
harnessgg-kdenlive create-project edited.kdenlive --title "Agent Edit" --overwrite
harnessgg-kdenlive import-asset edited.kdenlive C:\path\to\clip.mp4 --producer-id clip1
harnessgg-kdenlive add-text edited.kdenlive "Opening Title" --duration-frames 75 --track-id playlist0 --position 0
harnessgg-kdenlive stitch-clips edited.kdenlive playlist0 clip1 clip1 --position 75 --gap 10
```

## 5) Confirm changes

```bash
harnessgg-kdenlive inspect edited.kdenlive
harnessgg-kdenlive validate edited.kdenlive --no-check-files
harnessgg-kdenlive plan-edit edited.kdenlive timeline.add_clip --params-json "{\"clip_id\":\"clip1\",\"track_id\":\"playlist0\",\"position\":120}"
harnessgg-kdenlive render-project edited.kdenlive output.mp4
harnessgg-kdenlive render-status <job_id>
```

