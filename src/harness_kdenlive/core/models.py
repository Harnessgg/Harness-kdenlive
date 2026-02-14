from dataclasses import dataclass, field
from typing import Optional

from lxml.etree import _Element as Element


@dataclass
class Producer:
    id: str
    resource: Optional[str]
    in_point: str = "0"
    out_point: Optional[str] = None
    element: Optional[Element] = field(default=None, repr=False)


@dataclass
class Track:
    index: int
    producer_id: str
    is_audio: bool
    is_locked: bool = False
    name: Optional[str] = None
    element: Optional[Element] = field(default=None, repr=False)

    @property
    def track_type(self) -> str:
        return "audio" if self.is_audio else "video"


@dataclass
class Clip:
    instance_id: str
    producer_id: str
    track_id: str
    in_point: str = "0"
    out_point: Optional[str] = None
    timeline_start: int = 0
    timeline_end: int = 0
    element: Optional[Element] = field(default=None, repr=False)

    @property
    def duration(self) -> int:
        return self.timeline_end - self.timeline_start + 1


@dataclass
class ClipMove:
    clip_ref: str
    to_track: str
    to_position: int


@dataclass
class ValidationError:
    severity: str
    message: str
    element_type: Optional[str] = None
    element_id: Optional[str] = None
