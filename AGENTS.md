# AGENTS

## Mission
Enable coding agents to use Kdenlive capabilities end-to-end for real video editing workflows (timeline edits + render/export), reliably and programmatically.

## Operating Model
- `harness-kdenlive` is bridge-first.
- Agent commands must be deterministic, machine-readable JSON.
- Command names should map to explicit action methods (`system.*`, `project.*`, `timeline.*`, `render.*`).
- Bridge runs locally only (`127.0.0.1`) and must expose health + stability checks.

## Agent Contract
- Always call `bridge status` before editing.
- Use `actions` to discover supported actions.
- Validate projects before destructive edits.
- Prefer action methods over ad-hoc shell commands.
- Return structured errors with actionable codes.

## Required Capabilities (Target)
1. Project lifecycle: create/open/save/clone/snapshot.
2. Timeline editing: add/move/trim/split/ripple/insert-gap/remove-gap.
3. Asset management: import media, bin folders, metadata lookup.
4. Effects/transitions: list/apply/update/remove.
5. Track controls: add/remove/reorder/mute/lock/show-hide.
6. Render/export: clip and project render presets + status/progress.
7. Verification: bridge health, latency, soak tests, schema checks.

## Quality Bar
- Every command has tests (unit + bridge integration).
- No hidden fallback path for primary actions.
- Non-zero exit codes must match documented error semantics.
- Documentation stays synchronized with actual CLI behavior.

