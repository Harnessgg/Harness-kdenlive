import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from harness_kdenlive import __version__
from harness_kdenlive.bridge.client import BridgeClient, BridgeClientError
from harness_kdenlive.bridge.protocol import ERROR_CODES, PROTOCOL_VERSION
from harness_kdenlive.bridge.server import run_bridge_server

app = typer.Typer(add_completion=False, help="Bridge-first CLI for Kdenlive editing")
bridge_app = typer.Typer(add_completion=False, help="Bridge lifecycle and verification")
app.add_typer(bridge_app, name="bridge")


def _print(payload: Dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, indent=2))


def _ok(command: str, data: Dict[str, Any]) -> None:
    _print({"ok": True, "protocolVersion": PROTOCOL_VERSION, "command": command, "data": data})


def _fail(command: str, code: str, message: str, retryable: bool = False) -> None:
    _print(
        {
            "ok": False,
            "protocolVersion": PROTOCOL_VERSION,
            "command": command,
            "error": {"code": code, "message": message, "retryable": retryable},
        }
    )
    raise SystemExit(ERROR_CODES.get(code, 1))


def _bridge_client() -> BridgeClient:
    return BridgeClient()


def _call_bridge(
    command: str,
    method: str,
    params: Dict[str, Any],
    timeout_seconds: float = 30,
) -> Dict[str, Any]:
    client = _bridge_client()
    try:
        return client.call(method, params, timeout_seconds=timeout_seconds)
    except BridgeClientError as exc:
        _fail(command, exc.code, exc.message, retryable=exc.code == "BRIDGE_UNAVAILABLE")
    except Exception as exc:
        _fail(command, "ERROR", str(exc))
    raise RuntimeError("unreachable")


def _bridge_state_dir() -> Path:
    root = Path(os.getenv("LOCALAPPDATA", Path.home()))
    state_dir = root / "harness-kdenlive"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def _bridge_pid_file() -> Path:
    return _bridge_state_dir() / "bridge.pid"


@bridge_app.command("serve")
def bridge_serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(41739, "--port"),
) -> None:
    run_bridge_server(host, port)


@bridge_app.command("start")
def bridge_start(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(41739, "--port"),
) -> None:
    pid_file = _bridge_pid_file()
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            _ok("bridge.start", {"status": "already-running", "pid": pid, "host": host, "port": port})
            return
        except Exception:
            pid_file.unlink(missing_ok=True)

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    process = subprocess.Popen(
        [sys.executable, "-m", "harness_kdenlive", "bridge", "serve", "--host", host, "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    pid_file.write_text(str(process.pid), encoding="utf-8")
    os.environ["HARNESS_KDENLIVE_BRIDGE_URL"] = f"http://{host}:{port}"

    for _ in range(30):
        time.sleep(0.1)
        try:
            status = BridgeClient(f"http://{host}:{port}").health()
            if status.get("ok"):
                _ok("bridge.start", {"status": "started", "pid": process.pid, "host": host, "port": port})
                return
        except BridgeClientError:
            continue
    _fail("bridge.start", "BRIDGE_UNAVAILABLE", "Bridge process started but health check failed")


@bridge_app.command("stop")
def bridge_stop() -> None:
    pid_file = _bridge_pid_file()
    if not pid_file.exists():
        _ok("bridge.stop", {"status": "not-running"})
        return
    pid = int(pid_file.read_text(encoding="utf-8").strip())
    try:
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink(missing_ok=True)
        _ok("bridge.stop", {"status": "stopped", "pid": pid})
    except Exception as exc:
        _fail("bridge.stop", "ERROR", str(exc))


@bridge_app.command("status")
def bridge_status() -> None:
    client = _bridge_client()
    try:
        health = client.health()
        _ok("bridge.status", {"running": True, "health": health, "url": client.url})
    except BridgeClientError as exc:
        _fail("bridge.status", exc.code, exc.message, retryable=True)


@bridge_app.command("verify")
def bridge_verify(
    iterations: int = typer.Option(25, "--iterations", min=1, max=500),
    max_failures: int = typer.Option(0, "--max-failures", min=0),
) -> None:
    client = _bridge_client()
    failures = 0
    latencies_ms = []
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            client.call("system.health", {})
        except BridgeClientError:
            failures += 1
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies_ms.append(round(elapsed_ms, 3))
        time.sleep(0.02)
    stable = failures <= max_failures
    data = {
        "stable": stable,
        "iterations": iterations,
        "failures": failures,
        "maxFailuresAllowed": max_failures,
        "latencyMs": {
            "min": min(latencies_ms),
            "max": max(latencies_ms),
            "avg": round(sum(latencies_ms) / len(latencies_ms), 3),
        },
    }
    if not stable:
        _ok("bridge.verify", data)
        raise SystemExit(ERROR_CODES["ERROR"])
    _ok("bridge.verify", data)


@app.command("actions")
def actions() -> None:
    _ok("actions", _call_bridge("actions", "system.actions", {}))


@app.command("inspect")
def inspect_project(project: Path) -> None:
    _ok("inspect", _call_bridge("inspect", "project.inspect", {"project": str(project)}))


@app.command("validate")
def validate_project(
    project: Path,
    check_files: bool = True,
) -> None:
    data = _call_bridge(
        "validate",
        "project.validate",
        {"project": str(project), "check_files": check_files},
    )
    _ok("validate", data)
    if not data.get("isValid", False):
        raise SystemExit(ERROR_CODES["VALIDATION_FAILED"])


@app.command("diff")
def diff_projects(source: Path, target: Path) -> None:
    _ok("diff", _call_bridge("diff", "project.diff", {"source": str(source), "target": str(target)}))


@app.command("add-clip")
def add_clip(
    project: Path,
    clip_id: str,
    track_id: str,
    position: int,
    in_point: str = "0",
    out_point: Optional[str] = None,
    output: Optional[Path] = None,
) -> None:
    _ok(
        "add-clip",
        _call_bridge(
            "add-clip",
            "timeline.add_clip",
            {
                "project": str(project),
                "clip_id": clip_id,
                "track_id": track_id,
                "position": position,
                "in_point": in_point,
                "out_point": out_point,
                "output": str(output) if output else None,
            },
        ),
    )


@app.command("move-clip")
def move_clip(
    project: Path,
    clip_ref: str,
    track_id: str,
    position: int,
    output: Optional[Path] = None,
) -> None:
    _ok(
        "move-clip",
        _call_bridge(
            "move-clip",
            "timeline.move_clip",
            {
                "project": str(project),
                "clip_ref": clip_ref,
                "track_id": track_id,
                "position": position,
                "output": str(output) if output else None,
            },
        ),
    )


@app.command("trim-clip")
def trim_clip(
    project: Path,
    clip_ref: str,
    in_point: Optional[str] = None,
    out_point: Optional[str] = None,
    output: Optional[Path] = None,
) -> None:
    _ok(
        "trim-clip",
        _call_bridge(
            "trim-clip",
            "timeline.trim_clip",
            {
                "project": str(project),
                "clip_ref": clip_ref,
                "in_point": in_point,
                "out_point": out_point,
                "output": str(output) if output else None,
            },
        ),
    )


@app.command("remove-clip")
def remove_clip(
    project: Path,
    clip_ref: str,
    close_gap: bool = False,
    output: Optional[Path] = None,
) -> None:
    _ok(
        "remove-clip",
        _call_bridge(
            "remove-clip",
            "timeline.remove_clip",
            {
                "project": str(project),
                "clip_ref": clip_ref,
                "close_gap": close_gap,
                "output": str(output) if output else None,
            },
        ),
    )


@app.command("snapshot")
def snapshot(project: Path, description: str) -> None:
    _ok(
        "snapshot",
        _call_bridge(
            "snapshot",
            "project.snapshot",
            {"project": str(project), "description": description},
        ),
    )


@app.command("version")
def version() -> None:
    _ok("version", _call_bridge("version", "system.version", {}))


@app.command("render-clip")
def render_clip(
    source: Path,
    output: Path,
    duration_seconds: float,
    start_seconds: float = 0.0,
) -> None:
    _ok(
        "render-clip",
        _call_bridge(
            "render-clip",
            "render.clip",
            {
                "source": str(source),
                "output": str(output),
                "duration_seconds": duration_seconds,
                "start_seconds": start_seconds,
            },
            timeout_seconds=600,
        ),
    )


def main() -> None:
    app()
