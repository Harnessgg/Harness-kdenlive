# harness-kdenlive

Agent-first Python package for safe, scriptable edits to `.kdenlive` project files.

- JSON-first CLI for LLM/tooling use
- Bridge-first architecture (no direct CLI fallback)
- Position-aware timeline editing (`add`, `move`, `trim`, `remove`)
- Validation, diffing, and snapshot history

## Install

```bash
pip install harness-kdenlive
```

## Quick Start

```bash
harness-kdenlive bridge start
harness-kdenlive inspect project.kdenlive
harness-kdenlive validate project.kdenlive
harness-kdenlive add-clip project.kdenlive producer1 playlist0 120 --output edited.kdenlive
harness-kdenlive diff project.kdenlive edited.kdenlive
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
