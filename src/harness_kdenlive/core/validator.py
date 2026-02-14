from pathlib import Path
from typing import List, Set

from harness_kdenlive.core.models import ValidationError
from harness_kdenlive.core.xml_engine import KdenliveProject


class ProjectValidator:
    def __init__(self, project: KdenliveProject):
        self.project = project
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_all(self, check_files: bool = True) -> List[ValidationError]:
        self.errors = []
        self.warnings = []
        self._validate_structure()
        self._validate_references()
        self._validate_timecodes()
        self._validate_generation()
        self._validate_timeline_overlaps()
        if check_files:
            self._validate_files()
        return self.errors + self.warnings

    def _error(self, message: str, element_type: str = "project", element_id: str = "") -> None:
        self.errors.append(
            ValidationError(
                severity="error",
                message=message,
                element_type=element_type,
                element_id=element_id or None,
            )
        )

    def _warning(self, message: str, element_type: str = "project", element_id: str = "") -> None:
        self.warnings.append(
            ValidationError(
                severity="warning",
                message=message,
                element_type=element_type,
                element_id=element_id or None,
            )
        )

    def _validate_structure(self) -> None:
        if self.project.root.tag != "mlt":
            self._error("Root element must be 'mlt'", "root")
        if self.project.get_main_tractor() is None:
            self._error("No timeline tractor found", "tractor")

    def _validate_references(self) -> None:
        producer_ids: Set[str] = {p.id for p in self.project.get_producers()}
        for clip in self.project.get_clips_on_timeline():
            if clip.producer_id not in producer_ids:
                self._error(
                    f"Clip references missing producer '{clip.producer_id}'",
                    "clip",
                    clip.producer_id,
                )

    def _validate_files(self) -> None:
        for producer in self.project.get_producers():
            if not producer.resource:
                continue
            if producer.resource in {"black", "colour", "color"}:
                continue
            if producer.resource.startswith(("http://", "https://", "file://", "#")):
                continue
            path = Path(producer.resource)
            if not path.is_absolute():
                path = self.project.project_path.parent / path
            if not path.exists():
                self._warning(
                    f"Media file not found: {producer.resource}",
                    "producer",
                    producer.id,
                )

    def _validate_timecodes(self) -> None:
        for clip in self.project.get_clips_on_timeline():
            try:
                in_point = int(clip.in_point)
                if clip.out_point is not None and int(clip.out_point) < in_point:
                    self._error(
                        f"Clip '{clip.instance_id}' has out < in",
                        "clip",
                        clip.instance_id,
                    )
            except ValueError:
                self._error(
                    f"Clip '{clip.instance_id}' has invalid in/out points",
                    "clip",
                    clip.instance_id,
                )

    def _validate_generation(self) -> None:
        if self.project.generation < 4:
            self._warning("Project generation is below 4", "project")
        if self.project.generation == 5 and self.project.get_main_bin() is None:
            self._warning("Generation 5 project missing main_bin playlist", "playlist")

    def _validate_timeline_overlaps(self) -> None:
        by_track = {}
        for clip in self.project.get_clips_on_timeline():
            by_track.setdefault(clip.track_id, []).append(clip)
        for track_id, clips in by_track.items():
            clips = sorted(clips, key=lambda c: c.timeline_start)
            for idx in range(1, len(clips)):
                prev = clips[idx - 1]
                curr = clips[idx]
                if curr.timeline_start <= prev.timeline_end:
                    self._error(
                        (
                            f"Track '{track_id}' has overlap between "
                            f"'{prev.instance_id}' and '{curr.instance_id}'"
                        ),
                        "track",
                        track_id,
                    )

    def check_file_references_exist(self) -> List[str]:
        missing: List[str] = []
        for warning in self.warnings:
            if warning.message.startswith("Media file not found: "):
                missing.append(warning.message.replace("Media file not found: ", ""))
        return missing
