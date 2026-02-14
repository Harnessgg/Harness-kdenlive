import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from harness_kdenlive import __version__
from harness_kdenlive.api.timeline import TimelineAPI
from harness_kdenlive.core.diff_engine import DiffEngine
from harness_kdenlive.core.transaction import TransactionManager
from harness_kdenlive.core.validator import ProjectValidator
from harness_kdenlive.core.xml_engine import KdenliveProject


class BridgeOperationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


ACTION_METHODS = [
    "system.health",
    "system.version",
    "system.actions",
    "project.inspect",
    "project.validate",
    "project.diff",
    "project.snapshot",
    "timeline.add_clip",
    "timeline.move_clip",
    "timeline.trim_clip",
    "timeline.remove_clip",
    "render.clip",
]


def _load(path: str) -> KdenliveProject:
    try:
        return KdenliveProject(path)
    except FileNotFoundError as exc:
        raise BridgeOperationError("NOT_FOUND", str(exc)) from exc


def _save(project: KdenliveProject, output: Optional[str]) -> str:
    target = Path(output) if output else None
    return str(project.save(target))


def _resolve_bin(name: str) -> Path:
    env_key = f"HARNESS_KDENLIVE_{name.upper()}_PATH"
    from_env = os.getenv(env_key)
    if from_env:
        p = Path(from_env)
        if p.exists():
            return p
    default_root = Path(r"C:\Program Files\kdenlive\bin")
    default = default_root / f"{name}.exe"
    if default.exists():
        return default
    raise BridgeOperationError("NOT_FOUND", f"Kdenlive binary not found: {name}. Set {env_key}.")


def _render_clip(params: Dict[str, Any]) -> Dict[str, Any]:
    source = Path(params["source"])
    output = Path(params["output"])
    if not source.exists():
        raise BridgeOperationError("NOT_FOUND", f"Source not found: {source}")
    start_seconds = float(params.get("start_seconds", 0))
    duration_seconds = float(params["duration_seconds"])
    if duration_seconds <= 0:
        raise BridgeOperationError("INVALID_INPUT", "duration_seconds must be > 0")
    in_frame = int(round(start_seconds * 30))
    out_frame = in_frame + int(round(duration_seconds * 30)) - 1
    melt = _resolve_bin("melt")
    ffprobe = _resolve_bin("ffprobe")

    cmd = [
        str(melt),
        str(source),
        f"in={in_frame}",
        f"out={out_frame}",
        "-consumer",
        f"avformat:{output}",
        f"vcodec={params.get('vcodec', 'libx264')}",
        f"acodec={params.get('acodec', 'aac')}",
        f"ab={params.get('audio_bitrate', '192k')}",
        f"crf={params.get('crf', '18')}",
        f"preset={params.get('preset', 'fast')}",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode != 0:
        message = (process.stderr or process.stdout or "render failed").strip()
        raise BridgeOperationError("ERROR", message)
    if not output.exists():
        raise BridgeOperationError("ERROR", f"Render failed, output missing: {output}")

    probe = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        raise BridgeOperationError("ERROR", f"Render created invalid output: {output}")
    try:
        rendered_duration = float(probe.stdout.strip())
    except ValueError as exc:
        raise BridgeOperationError("ERROR", "Could not parse rendered duration") from exc

    return {
        "source": str(source),
        "output": str(output),
        "durationSeconds": rendered_duration,
        "targetDurationSeconds": duration_seconds,
    }


def execute(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if method == "system.health":
        return {"status": "ok", "version": __version__}
    if method == "system.version":
        return {"version": __version__}
    if method == "system.actions":
        return {"actions": ACTION_METHODS}
    if method == "project.inspect":
        loaded = _load(params["project"])
        clips = loaded.get_clips_on_timeline()
        return {
            "path": str(params["project"]),
            "generation": loaded.generation,
            "version": loaded.version,
            "statistics": {
                "tracks": len(loaded.get_tracks()),
                "producers": len(loaded.get_producers()),
                "clips": len(clips),
                "durationFrames": max([c.timeline_end for c in clips], default=-1) + 1,
            },
        }
    if method == "project.validate":
        loaded = _load(params["project"])
        validator = ProjectValidator(loaded)
        check_files = bool(params.get("check_files", True))
        issues = validator.validate_all(check_files=check_files)
        errors = [e for e in issues if e.severity == "error"]
        warnings = [e for e in issues if e.severity == "warning"]
        return {
            "path": str(params["project"]),
            "isValid": len(errors) == 0,
            "errorCount": len(errors),
            "warningCount": len(warnings),
            "errors": [e.__dict__ for e in errors],
            "warnings": [e.__dict__ for e in warnings],
        }
    if method == "project.diff":
        source = _load(params["source"])
        target = _load(params["target"])
        return DiffEngine(source, target).to_dict()
    if method == "project.snapshot":
        loaded = _load(params["project"])
        snap = TransactionManager(loaded).create_snapshot(params["description"])
        return {"snapshotId": snap}
    if method == "timeline.add_clip":
        loaded = _load(params["project"])
        timeline = TimelineAPI(loaded)
        clip_ref = timeline.add_clip(
            clip_id=params["clip_id"],
            track_id=params["track_id"],
            position=int(params["position"]),
            in_point=str(params.get("in_point", "0")),
            out_point=params.get("out_point"),
        )
        saved = _save(loaded, params.get("output"))
        return {"clipRef": clip_ref, "savedTo": saved}
    if method == "timeline.move_clip":
        loaded = _load(params["project"])
        timeline = TimelineAPI(loaded)
        ok = timeline.move_clip(
            clip_ref=params["clip_ref"],
            new_track=params["track_id"],
            new_position=int(params["position"]),
        )
        if not ok:
            raise BridgeOperationError("INVALID_INPUT", f"Clip not found: {params['clip_ref']}")
        saved = _save(loaded, params.get("output"))
        return {"clipRef": params["clip_ref"], "savedTo": saved}
    if method == "timeline.trim_clip":
        loaded = _load(params["project"])
        timeline = TimelineAPI(loaded)
        ok = timeline.trim_clip(
            clip_ref=params["clip_ref"],
            new_in=params.get("in_point"),
            new_out=params.get("out_point"),
        )
        if not ok:
            raise BridgeOperationError("INVALID_INPUT", f"Clip not found: {params['clip_ref']}")
        saved = _save(loaded, params.get("output"))
        return {"clipRef": params["clip_ref"], "savedTo": saved}
    if method == "timeline.remove_clip":
        loaded = _load(params["project"])
        timeline = TimelineAPI(loaded)
        ok = timeline.remove_clip(
            clip_ref=params["clip_ref"],
            close_gap=bool(params.get("close_gap", False)),
        )
        if not ok:
            raise BridgeOperationError("INVALID_INPUT", f"Clip not found: {params['clip_ref']}")
        saved = _save(loaded, params.get("output"))
        return {"clipRef": params["clip_ref"], "savedTo": saved}
    if method == "render.clip":
        return _render_clip(params)
    raise BridgeOperationError("INVALID_INPUT", f"Unknown method: {method}")

