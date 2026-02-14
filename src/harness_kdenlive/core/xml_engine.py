import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from lxml import etree
from lxml.etree import _Element as Element

from harness_kdenlive.core.models import Clip, Producer, Track


class KdenliveProject:
    """Load, inspect, and mutate .kdenlive (MLT XML) files."""

    NAMESPACES = {
        "kdenlive": "http://www.kdenlive.org/project",
        "xml": "http://www.w3.org/XML/1998/namespace",
    }

    def __init__(self, project_path: Union[str, Path]):
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project file not found: {project_path}")
        self.tree: etree._ElementTree
        self.root: Element
        self._generation: Optional[int] = None
        self._load_project()

    def _load_project(self) -> None:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        self.tree = etree.parse(str(self.project_path), parser)
        self.root = self.tree.getroot()
        if self.root.tag != "mlt":
            raise ValueError("Invalid project file: root element must be 'mlt'")

    def load_from_string(self, xml_content: str) -> None:
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        root = etree.fromstring(xml_content.encode("utf-8"), parser)
        if root.tag != "mlt":
            raise ValueError("Invalid project XML: root element must be 'mlt'")
        self.tree = etree.ElementTree(root)
        self.root = root
        self._generation = None

    @property
    def generation(self) -> int:
        if self._generation is None:
            value = self.get_property("kdenlive:docproperties.generation")
            self._generation = int(value) if value else 4
        return self._generation

    @property
    def version(self) -> Optional[str]:
        return self.get_property("kdenlive:docproperties.version")

    def get_property(self, name: str, parent: Optional[Element] = None) -> Optional[str]:
        search = parent if parent is not None else self.root
        node = search.find(f'.//property[@name="{name}"]')
        return node.text if node is not None else None

    def get_main_tractor(self) -> Optional[Element]:
        tractors = self.root.findall(".//tractor")
        if not tractors:
            return None
        for tractor in tractors:
            if tractor.get("id") == "timeline_preview":
                return tractor
        return tractors[-1]

    def get_playlists(self) -> List[Element]:
        return self.root.findall(".//playlist")

    def get_main_bin(self) -> Optional[Element]:
        return self.root.find('.//playlist[@id="main_bin"]')

    def get_tracks(self) -> List[Track]:
        tractor = self.get_main_tractor()
        if tractor is None:
            return []
        collected: List[Track] = []
        self._collect_tracks(tractor, collected)
        if collected:
            return collected
        tracks: List[Track] = []
        for idx, track_elem in enumerate(tractor.findall("track")):
            hide_attr = track_elem.get("hide")
            tracks.append(
                Track(
                    index=idx,
                    producer_id=track_elem.get("producer", ""),
                    is_audio=hide_attr == "video",
                    is_locked=False,
                    element=track_elem,
                )
            )
        return tracks

    def _collect_tracks(self, tractor: Element, tracks: List[Track]) -> None:
        for track_elem in tractor.findall("track"):
            producer_id = track_elem.get("producer")
            if not producer_id:
                continue
            playlist = self.root.find(f'.//playlist[@id="{producer_id}"]')
            if playlist is not None:
                hide_attr = track_elem.get("hide")
                tracks.append(
                    Track(
                        index=len(tracks),
                        producer_id=producer_id,
                        is_audio=hide_attr == "video",
                        is_locked=False,
                        element=track_elem,
                    )
                )
                continue
            sub_tractor = self.root.find(f'.//tractor[@id="{producer_id}"]')
            if sub_tractor is not None:
                self._collect_tracks(sub_tractor, tracks)

    def get_producers(self, id_filter: Optional[str] = None) -> List[Producer]:
        query = f'.//producer[@id="{id_filter}"]' if id_filter else ".//producer"
        producers: List[Producer] = []
        for elem in self.root.findall(query):
            producers.append(
                Producer(
                    id=elem.get("id", ""),
                    resource=self.get_property("resource", elem),
                    in_point=elem.get("in", "0"),
                    out_point=elem.get("out"),
                    element=elem,
                )
            )
        return producers

    def _collect_timeline_playlist_ids(self, tractor: Element, ids: List[str]) -> None:
        for track in tractor.findall("track"):
            producer_id = track.get("producer")
            if not producer_id:
                continue
            playlist = self.root.find(f'.//playlist[@id="{producer_id}"]')
            if playlist is not None:
                ids.append(producer_id)
                continue
            sub_tractor = self.root.find(f'.//tractor[@id="{producer_id}"]')
            if sub_tractor is not None:
                self._collect_timeline_playlist_ids(sub_tractor, ids)

    def get_clips_on_timeline(self, track_id: Optional[str] = None) -> List[Clip]:
        clips: List[Clip] = []
        if track_id:
            playlists = [self.root.find(f'.//playlist[@id="{track_id}"]')]
        else:
            tractor = self.get_main_tractor()
            if tractor is None:
                return []
            playlist_ids: List[str] = []
            self._collect_timeline_playlist_ids(tractor, playlist_ids)
            playlists = [self.root.find(f'.//playlist[@id="{pid}"]') for pid in playlist_ids]

        for playlist in playlists:
            if playlist is None:
                continue
            playlist_id = playlist.get("id", "")
            timeline_cursor = 0
            entry_count = 0
            for node in playlist:
                if node.tag == "blank":
                    timeline_cursor += int(node.get("length", "0"))
                    continue
                if node.tag != "entry":
                    continue
                in_point = node.get("in", "0")
                out_point = node.get("out")
                duration = self._entry_duration(node)
                clip_ref = self.get_property("harness:clip-ref", node)
                clip = Clip(
                    instance_id=clip_ref or f"{playlist_id}:{entry_count}",
                    producer_id=node.get("producer", ""),
                    track_id=playlist_id,
                    in_point=in_point,
                    out_point=out_point,
                    timeline_start=timeline_cursor,
                    timeline_end=timeline_cursor + duration - 1,
                    element=node,
                )
                clips.append(clip)
                timeline_cursor += duration
                entry_count += 1
        return clips

    @staticmethod
    def _entry_duration(entry: Element) -> int:
        in_point = int(entry.get("in", "0"))
        out_raw = entry.get("out")
        if out_raw is None:
            return 1
        out_point = int(out_raw)
        return max(1, out_point - in_point + 1)

    def get_project_info(self) -> Dict[str, Any]:
        properties: Dict[str, Optional[str]] = {}
        for prop in self.root.findall('.//property[@name]'):
            name = prop.get("name", "")
            if name.startswith("kdenlive:docproperties."):
                key = name.replace("kdenlive:docproperties.", "")
                properties[key] = prop.text
        return {
            "path": str(self.project_path),
            "generation": self.generation,
            "version": self.version,
            "num_producers": len(self.get_producers()),
            "num_tracks": len(self.get_tracks()),
            "num_clips": len(self.get_clips_on_timeline()),
            "properties": properties,
        }

    def save(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        target = Path(output_path) if output_path else self.project_path
        self.tree.write(
            str(target),
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=True,
        )
        return target

    def to_string(self) -> str:
        return etree.tostring(self.root, encoding="unicode", pretty_print=True)

    def clone(self) -> "KdenliveProject":
        cloned = KdenliveProject.__new__(KdenliveProject)
        cloned.project_path = self.project_path
        cloned.tree = copy.deepcopy(self.tree)
        cloned.root = cloned.tree.getroot()
        cloned._generation = self._generation
        return cloned
