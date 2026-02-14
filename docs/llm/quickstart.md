# LLM Quickstart

## 1) Start bridge

```bash
harness-kdenlive bridge start
```

## 2) Verify bridge health/stability

```bash
harness-kdenlive bridge status
harness-kdenlive bridge verify --iterations 25
```

## 3) Inspect and validate project

```bash
harness-kdenlive inspect project.kdenlive
harness-kdenlive validate project.kdenlive
```

## 4) Edit timeline

```bash
harness-kdenlive add-clip project.kdenlive producer1 playlist0 100 --out-point 49 --output edited.kdenlive
harness-kdenlive move-clip edited.kdenlive hclip_xxx playlist1 200 --output edited2.kdenlive
```

## 5) Confirm changes

```bash
harness-kdenlive diff project.kdenlive edited2.kdenlive
```
