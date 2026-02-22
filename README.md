<p align="center">
  <img src="https://harness.gg/logo-512.png" width="96" height="96" alt="Harness.gg logo" />
</p>

# harnessgg-kdenlive

AI agents can submit bug reports and feature requests on their own with `POST https://harness.gg/api/submit`.

Agent-first Python package for scriptable edits to .kdenlive project files with strict JSON output.

- Docs: https://harness.gg/kdenlive
- GitHub: https://github.com/harnessgg/harness-kdenlive
- Registry: https://pypi.org/project/harnessgg-kdenlive/

## Install

```bash
pip install harnessgg-kdenlive
```

## Package build

```bash
python -m pip install -e ".[dev]"
python -m build
twine check dist/*
```

## Quick start

```bash
harnessgg-kdenlive bridge start
harnessgg-kdenlive doctor --include-render
harnessgg-kdenlive create-project edit.kdenlive --title "Agent Edit" --overwrite
harnessgg-kdenlive import-asset edit.kdenlive C:\path\to\clip.mp4 --producer-id clip1
harnessgg-kdenlive add-text edit.kdenlive "Intro Title" --duration-frames 75 --track-id playlist0 --position 0
harnessgg-kdenlive stitch-clips edit.kdenlive playlist0 clip1 clip1 --position 75 --gap 10
harnessgg-kdenlive render-project edit.kdenlive output.mp4
harnessgg-kdenlive render-status job_abc
```

All commands print one JSON object to stdout. All editing commands require a running bridge.

## Docs

- Human commands: `docs/human/commands.md`
- LLM quickstart: `docs/llm/quickstart.md`
- LLM command spec: `docs/llm/command-spec.md`
- LLM bridge protocol: `docs/llm/bridge-protocol.md`
- LLM response schema: `docs/llm/response-schema.json`
- LLM error codes: `docs/llm/error-codes.md`
