import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

from harness_kdenlive.core.xml_engine import KdenliveProject


@dataclass
class ClipChange:
    change_type: str
    clip_ref: str
    producer_id: str
    track_id: str
    start: int
    end: int
    old_track_id: Optional[str] = None
    old_start: Optional[int] = None
    old_end: Optional[int] = None


@dataclass
class DiffSummary:
    source_path: str
    target_path: str
    timestamp: str
    added: List[ClipChange]
    removed: List[ClipChange]
    moved: List[ClipChange]
    trimmed: List[ClipChange]

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.moved) + len(self.trimmed)


class DiffEngine:
    def __init__(self, source: KdenliveProject, target: KdenliveProject):
        self.source = source
        self.target = target
        self._summary: Optional[DiffSummary] = None

    def compute_diff(self) -> DiffSummary:
        source_clips = self.source.get_clips_on_timeline()
        target_clips = self.target.get_clips_on_timeline()

        source_index: Dict[str, object] = {c.instance_id: c for c in source_clips}
        target_index: Dict[str, object] = {c.instance_id: c for c in target_clips}

        added: List[ClipChange] = []
        removed: List[ClipChange] = []
        moved: List[ClipChange] = []
        trimmed: List[ClipChange] = []

        for clip in target_clips:
            old = source_index.get(clip.instance_id)
            if old is None:
                added.append(
                    ClipChange(
                        change_type="added",
                        clip_ref=clip.instance_id,
                        producer_id=clip.producer_id,
                        track_id=clip.track_id,
                        start=clip.timeline_start,
                        end=clip.timeline_end,
                    )
                )
                continue
            if old.track_id != clip.track_id or old.timeline_start != clip.timeline_start:
                moved.append(
                    ClipChange(
                        change_type="moved",
                        clip_ref=clip.instance_id,
                        producer_id=clip.producer_id,
                        track_id=clip.track_id,
                        start=clip.timeline_start,
                        end=clip.timeline_end,
                        old_track_id=old.track_id,
                        old_start=old.timeline_start,
                        old_end=old.timeline_end,
                    )
                )
            elif old.in_point != clip.in_point or old.out_point != clip.out_point:
                trimmed.append(
                    ClipChange(
                        change_type="trimmed",
                        clip_ref=clip.instance_id,
                        producer_id=clip.producer_id,
                        track_id=clip.track_id,
                        start=clip.timeline_start,
                        end=clip.timeline_end,
                        old_start=old.timeline_start,
                        old_end=old.timeline_end,
                    )
                )

        for clip in source_clips:
            if clip.instance_id not in target_index:
                removed.append(
                    ClipChange(
                        change_type="removed",
                        clip_ref=clip.instance_id,
                        producer_id=clip.producer_id,
                        track_id=clip.track_id,
                        start=clip.timeline_start,
                        end=clip.timeline_end,
                    )
                )

        self._summary = DiffSummary(
            source_path=str(self.source.project_path),
            target_path=str(self.target.project_path),
            timestamp=datetime.utcnow().isoformat() + "Z",
            added=added,
            removed=removed,
            moved=moved,
            trimmed=trimmed,
        )
        return self._summary

    def to_dict(self, summary: Optional[DiffSummary] = None) -> Dict[str, object]:
        current = summary or self._summary or self.compute_diff()
        return {
            "source": current.source_path,
            "target": current.target_path,
            "timestamp": current.timestamp,
            "changes": {
                "added": [asdict(c) for c in current.added],
                "removed": [asdict(c) for c in current.removed],
                "moved": [asdict(c) for c in current.moved],
                "trimmed": [asdict(c) for c in current.trimmed],
            },
            "stats": {"total_changes": current.total_changes},
        }

    def to_json(self, summary: Optional[DiffSummary] = None) -> str:
        return json.dumps(self.to_dict(summary), indent=2)
