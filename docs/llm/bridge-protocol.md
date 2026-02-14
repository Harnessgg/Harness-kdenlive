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
- `project.inspect`
- `project.validate`
- `project.diff`
- `project.snapshot`
- `timeline.add_clip`
- `timeline.move_clip`
- `timeline.trim_clip`
- `timeline.remove_clip`
- `render.clip`
