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
        if position < 0:
            raise ValueError("position must be >= 0")
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
        if new_position < 0:
            raise ValueError("position must be >= 0")
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
        current_in = int(clip.element.get("in", "0"))
        current_out_raw = clip.element.get("out")
        current_out = int(current_out_raw) if current_out_raw is not None else current_in
        target_in = int(new_in) if new_in is not None else current_in
        target_out = int(new_out) if new_out is not None else current_out
        if target_in < 0 or target_out < 0:
            raise ValueError("in/out points must be >= 0")
        if target_out < target_in:
            raise ValueError("out point must be >= in point")
        if new_in is not None:
            clip.element.set("in", new_in)
        if new_out is not None:
            clip.element.set("out", new_out)
        return True

    def split_clip(self, clip_ref: str, position: int) -> str:
        if position < 0:
            raise ValueError("position must be >= 0")
        clip = self._resolve_clip(clip_ref)
        if clip is None or clip.element is None:
            raise ValueError(f"Clip '{clip_ref}' not found")
        if position <= clip.timeline_start or position > clip.timeline_end:
            raise ValueError(
                f"split position {position} must be within clip range [{clip.timeline_start + 1}, {clip.timeline_end}]"
            )
        playlist = self._get_playlist(clip.track_id)
        entry = clip.element
        split_offset = position - clip.timeline_start
        first_entry, second_entry = self._split_entry(entry, split_offset)
        for prop in list(second_entry.findall('./property[@name="harness:clip-ref"]')):
            second_entry.remove(prop)
        second_clip_ref = f"hclip_{uuid4().hex}"
        ref_prop = etree.SubElement(second_entry, "property", name="harness:clip-ref")
        ref_prop.text = second_clip_ref
        idx = list(playlist).index(entry)
        playlist.remove(entry)
        playlist.insert(idx, first_entry)
        playlist.insert(idx + 1, second_entry)
        self._normalize_playlist(playlist)
        return second_clip_ref

    def ripple_delete(self, clip_ref: str) -> bool:
        return self.remove_clip(clip_ref=clip_ref, close_gap=True)

    def insert_gap(self, track_id: str, position: int, length: int) -> bool:
        if position < 0:
            raise ValueError("position must be >= 0")
        if length <= 0:
            raise ValueError("length must be > 0")
        playlist = self._get_playlist(track_id)
        cursor = 0
        for idx, node in enumerate(list(playlist)):
            if node.tag == "blank":
                blank_len = int(node.get("length", "0"))
                if position < cursor + blank_len:
                    node.set("length", str(blank_len + length))
                    self._normalize_playlist(playlist)
                    return True
                if position == cursor:
                    playlist.insert(idx, etree.Element("blank", length=str(length)))
                    self._normalize_playlist(playlist)
                    return True
                cursor += blank_len
                continue

            if node.tag != "entry":
                continue
            duration = self.project._entry_duration(node)
            if position == cursor:
                playlist.insert(idx, etree.Element("blank", length=str(length)))
                self._normalize_playlist(playlist)
                return True
            if cursor < position < cursor + duration:
                split_offset = position - cursor
                first_entry, second_entry = self._split_entry(node, split_offset)
                playlist.remove(node)
                playlist.insert(idx, first_entry)
                playlist.insert(idx + 1, etree.Element("blank", length=str(length)))
                playlist.insert(idx + 2, second_entry)
                self._normalize_playlist(playlist)
                return True
            cursor += duration

        if position > cursor:
            playlist.append(etree.Element("blank", length=str(position - cursor)))
        playlist.append(etree.Element("blank", length=str(length)))
        self._normalize_playlist(playlist)
        return True

    def remove_all_gaps(self, track_id: str) -> int:
        playlist = self._get_playlist(track_id)
        removed = 0
        for node in list(playlist):
            if node.tag == "blank":
                removed += int(node.get("length", "0"))
                playlist.remove(node)
        self._normalize_playlist(playlist)
        return removed

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

    @staticmethod
    def _split_entry(entry: Element, offset_frames: int) -> Tuple[Element, Element]:
        duration = max(1, int(entry.get("out", entry.get("in", "0"))) - int(entry.get("in", "0")) + 1)
        if offset_frames <= 0 or offset_frames >= duration:
            raise ValueError("split point must produce two non-empty clips")
        start = int(entry.get("in", "0"))
        end_raw = entry.get("out")
        end = int(end_raw) if end_raw is not None else start
        first_end = start + offset_frames - 1
        second_start = first_end + 1
        first = etree.fromstring(etree.tostring(entry))
        second = etree.fromstring(etree.tostring(entry))
        first.set("in", str(start))
        first.set("out", str(first_end))
        second.set("in", str(second_start))
        second.set("out", str(end))
        return first, second
