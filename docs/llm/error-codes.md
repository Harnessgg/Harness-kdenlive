# Error Codes

## Process exit codes

- `0`: success
- `1`: general/internal failure
- `2`: file not found
- `3`: validation failed
- `4`: invalid input
- `5`: bridge unavailable

## Retry guidance

- Retry only when `error.code == "BRIDGE_UNAVAILABLE"`.
- Recommended retry backoff: `0.5s`, `1s`, `2s` (max 3 retries).
- Before retrying mutating commands, run `harness-kdenlive bridge status`.

## JSON error object

```json
{
  "ok": false,
  "protocolVersion": "1.0",
  "command": "add-clip",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Track 'playlist99' not found",
    "retryable": false
  }
}
```
