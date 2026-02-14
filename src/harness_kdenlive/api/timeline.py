from typing import List, Optional, Tuple
from uuid import uuid4

from lxml import etree
from lxml.etree import _Element as Element

from harness_kdenlive.core.models import Clip, ClipMove, Track
from harness_kdenlive.core.xml_engine import KdenliveProject


class TimelineAPI:
    def __init__(self, project: KdenliveProject):
        self.project = project

    def get_clips(
        self, track_id: Optional[str] = None, time_range: Optional[Tuple[int, int]] = None
    ) -> List[Clip]:
        clips = self.project.get_clips_on_timeline(track_id=track_id)
        if not time_range:
            return clips
        start, end = time_range
        return [c for c in clips if c.timeline_start >= start and c.timeline_end <= end]

    def get_tracks(self) -> List[Track]:
        return self.project.get_tracks()

    def get_timeline_duration(self) -> int:
        clips = self.project.get_clips_on_timeline()
        return max([c.timeline_end for c in clips], default=0) + 1

    def add_clip(
        self,
        clip_id: str,
        track_id: str,
        position: int,
        in_point: str = "0",
        out_point: Optional[str] = None,
        allow_overlap: bool = False,
    ) -> str:
        playlist = self._get_playlist(track_id)
        if not self.project.get_producers(id_filter=clip_id):
            raise ValueError(f"Producer '{clip_id}' not found")
        new_entry = etree.Element("entry", producer=clip_id, **{"in": in_point})
        if out_point is not None:
            new_entry.set("out", out_point)
        clip_ref = f"hclip_{uuid4().hex}"
        ref_prop = etree.SubElement(new_entry, "property", name="harness:clip-ref")
        ref_prop.text = clip_ref
        self._insert_entry_at_position(playlist, new_entry, position, allow_overlap=allow_overlap)
        return clip_ref

    def remove_clip(self, clip_ref: str, close_gap: bool = False) -> bool:
        clip = self._resolve_clip(clip_ref)
        if clip is None or clip.element is None:
            return False
        playlist = self._get_playlist(clip.track_id)
        entry = clip.element
        idx = list(playlist).index(entry)
        duration = self.project._entry_duration(entry)
        playlist.remove(entry)
        if not close_gap and duration > 0:
            playlist.insert(idx, etree.Element("blank", length=str(duration)))
        self._normalize_playlist(playlist)
        return True

    def move_clip(
        self, clip_ref: str, new_track: str, new_position: int, allow_overlap: bool = False
    ) -> bool:
        clip = self._resolve_clip(clip_ref)
        if clip is None or clip.element is None:
            raise ValueError(f"Clip '{clip_ref}' not found")
        source_playlist = self._get_playlist(clip.track_id)
        entry = clip.element
        source_idx = list(source_playlist).index(entry)
        duration = self.project._entry_duration(entry)
        source_playlist.remove(entry)
        source_playlist.insert(source_idx, etree.Element("blank", length=str(duration)))
        self._normalize_playlist(source_playlist)
        target_playlist = self._get_playlist(new_track)
        self._insert_entry_at_position(target_playlist, entry, new_position, allow_overlap=allow_overlap)
        return True

    def trim_clip(
        self, clip_ref: str, new_in: Optional[str] = None, new_out: Optional[str] = None
    ) -> bool:
        clip = self._resolve_clip(clip_ref)
        if clip is None or clip.element is None:
            return False
        if new_in is not None:
            clip.element.set("in", new_in)
        if new_out is not None:
            clip.element.set("out", new_out)
        return True

    def batch_move_clips(self, moves: List[ClipMove]) -> int:
        moved = 0
        for move in moves:
            if self.move_clip(move.clip_ref, move.to_track, move.to_position):
                moved += 1
        return moved

    def _resolve_clip(self, clip_ref: str) -> Optional[Clip]:
        clips = self.project.get_clips_on_timeline()
        by_instance = next((c for c in clips if c.instance_id == clip_ref), None)
        if by_instance is not None:
            return by_instance
        return next((c for c in clips if c.producer_id == clip_ref), None)

    def _get_playlist(self, track_id: str) -> Element:
        playlist = self.project.root.find(f'.//playlist[@id="{track_id}"]')
        if playlist is None:
            raise ValueError(f"Track '{track_id}' not found")
        return playlist

    def _insert_entry_at_position(
        self, playlist: Element, entry: Element, position: int, allow_overlap: bool
    ) -> None:
        if position < 0:
            raise ValueError("position must be >= 0")
        cursor = 0
        for idx, node in enumerate(list(playlist)):
            if node.tag == "blank":
                blank_len = int(node.get("length", "0"))
                if position < cursor + blank_len:
                    before = position - cursor
                    after = blank_len - before
                    playlist.remove(node)
                    insert_at = idx
                    if before > 0:
                        playlist.insert(insert_at, etree.Element("blank", length=str(before)))
                        insert_at += 1
                    playlist.insert(insert_at, entry)
                    insert_at += 1
                    if after > 0:
                        playlist.insert(insert_at, etree.Element("blank", length=str(after)))
                    self._normalize_playlist(playlist)
                    return
                if position == cursor:
                    playlist.insert(idx, entry)
                    self._normalize_playlist(playlist)
                    return
                cursor += blank_len
                continue

            if node.tag != "entry":
                continue
            duration = self.project._entry_duration(node)
            if position == cursor:
                playlist.insert(idx, entry)
                self._normalize_playlist(playlist)
                return
            if cursor < position < cursor + duration and not allow_overlap:
                raise ValueError(
                    f"position {position} overlaps clip on track '{playlist.get('id')}'"
                )
            cursor += duration

        if position > cursor:
            playlist.append(etree.Element("blank", length=str(position - cursor)))
        playlist.append(entry)
        self._normalize_playlist(playlist)

    @staticmethod
    def _normalize_playlist(playlist: Element) -> None:
        for node in list(playlist):
            if node.tag == "blank" and int(node.get("length", "0")) <= 0:
                playlist.remove(node)
        nodes = list(playlist)
        i = 0
        while i < len(nodes) - 1:
            first = nodes[i]
            second = nodes[i + 1]
            if first.tag == "blank" and second.tag == "blank":
                merged = int(first.get("length", "0")) + int(second.get("length", "0"))
                first.set("length", str(merged))
                playlist.remove(second)
                nodes.pop(i + 1)
                continue
            i += 1
