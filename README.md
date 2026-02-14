# harness-kdenlive

Agent-first Python package for safe, scriptable edits to `.kdenlive` project files.

- JSON-first CLI for LLM/tooling use
- Bridge-first architecture (no direct CLI fallback)
- Position-aware timeline editing (`add`, `move`, `trim`, `remove`)
- Validation, diffing, and snapshot history

## Install

```bash
pip install harnessgg-kdenlive
```

## Quick Start

```bash
harness-kdenlive bridge start
harness-kdenlive doctor --include-render
harness-kdenlive create-project edit.kdenlive --title "Agent Edit" --overwrite
harness-kdenlive import-asset edit.kdenlive C:\path\to\clip.mp4 --producer-id clip1
harness-kdenlive add-text edit.kdenlive "Intro Title" --duration-frames 75 --track-id playlist0 --position 0
harness-kdenlive stitch-clips edit.kdenlive playlist0 clip1 clip1 --position 75 --gap 10
harness-kdenlive inspect project.kdenlive
harness-kdenlive validate project.kdenlive
harness-kdenlive add-clip project.kdenlive producer1 playlist0 120 --output edited.kdenlive
harness-kdenlive diff project.kdenlive edited.kdenlive
harness-kdenlive render-project edited.kdenlive output.mp4
harness-kdenlive list-effects edited.kdenlive producer1
harness-kdenlive apply-effect edited.kdenlive producer1 brightness --effect-id fx1 --properties-json "{\"gain\":\"0.5\"}"
harness-kdenlive list-transitions edited.kdenlive
harness-kdenlive bridge soak --iterations 100 --duration-seconds 5
harness-kdenlive bridge verify --iterations 25
```

All commands print one JSON object to stdout.
All editing commands require a running bridge.

## Python API

```python
from harness_kdenlive import KdenliveProject, TransactionManager
from harness_kdenlive.api import TimelineAPI

project = KdenliveProject("project.kdenlive")
timeline = TimelineAPI(project)
txn = TransactionManager(project)

with txn.transaction("Add intro clip"):
    timeline.add_clip("producer1", "playlist0", position=0, in_point="0", out_point="49")

project.save("edited.kdenlive")
```

## Docs

- Human commands: `docs/human/commands.md`
- LLM quickstart: `docs/llm/quickstart.md`
- LLM command spec: `docs/llm/command-spec.md`
- LLM bridge protocol: `docs/llm/bridge-protocol.md`
- LLM response schema: `docs/llm/response-schema.json`
- LLM error codes: `docs/llm/error-codes.md`

## Publishing

```bash
python -m pip install -e ".[dev]"
python -m build
twine check dist/*
```

GitHub Actions workflow for trusted publishing is in `.github/workflows/publish.yml`.
