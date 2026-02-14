# Bridge Protocol

Transport: HTTP JSON-RPC style over localhost.

- Health endpoint: `GET /health`
- RPC endpoint: `POST /rpc`

Request:

```json
{
  "id": "inspect",
  "method": "inspect",
  "params": {
    "project": "C:/path/project.kdenlive"
  }
}
```

Success response:

```json
{
  "ok": true,
  "protocolVersion": "1.0",
  "id": "inspect",
  "result": {}
}
```

Error response:

```json
{
  "ok": false,
  "protocolVersion": "1.0",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Unknown method: xyz"
  }
}
```

Implemented methods:

- `system.health`
- `system.version`
- `system.actions`
- `system.doctor`
- `system.soak`
- `project.create`
- `project.clone`
- `project.plan_edit`
- `project.undo`
- `project.redo`
- `project.recalculate_timeline_bounds`
- `project.inspect`
- `project.validate`
- `project.diff`
- `project.snapshot`
- `asset.import`
- `asset.create_text`
- `asset.update_text`
- `effect.list`
- `effect.apply`
- `effect.update`
- `effect.remove`
- `effect.keyframes`
- `transition.list`
- `transition.apply`
- `transition.remove`
- `transition.wipe`
- `timeline.add_clip`
- `timeline.move_clip`
- `timeline.trim_clip`
- `timeline.remove_clip`
- `timeline.split_clip`
- `timeline.ripple_delete`
- `timeline.insert_gap`
- `timeline.remove_all_gaps`
- `timeline.stitch_clips`
- `timeline.time_remap`
- `timeline.transform`
- `audio.add_music`
- `audio.duck`
- `audio.fade`
- `color.grade`
- `track.add`
- `track.remove`
- `track.reorder`
- `render.clip`
- `render.project`
- `render.status`
