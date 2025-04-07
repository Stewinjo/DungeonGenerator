from dataclasses import dataclass, asdict
from enum import Enum, auto
from typing import Tuple, Optional

class DoorType(Enum):
    GLASS = auto()
    METAL = auto()
    STONE = auto()
    WOOD = auto()

@dataclass
class WallSegment:
    x1: int
    y1: int
    x2: int
    y2: int
    door: int = 0  # 0: no door, 1: door, 2: locked, etc.
    door_type: Optional[DoorType] = None  # None unless it's a door
    ds: int = 0    # door state (0=open, 1=closed)
    move: int = 1
    sense: int = 1
    sound: int = 0
    light: int = 0

    def to_foundry_dict(self):
        return {
            "c": [self.x1, self.y1, self.x2, self.y2],
            "door": self.door,
            "ds": self.ds,
            "move": self.move,
            "sense": self.sense,
            "sound": self.sound,
            "light": self.light,
            "flags": {}
        }

    def to_pixel_coords(self, scale: int) -> Tuple[int, int, int, int]:
        return self.x1 * scale, self.y1 * scale, self.x2 * scale, self.y2 * scale

@dataclass
class Light:
    x: int
    y: int
    dim: int = 30
    bright: int = 10
    color: Optional[str] = "#ffffff"

    def to_foundry_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "config": {
                "dim": self.dim,
                "bright": self.bright,
                "color": self.color
            }
        }


@dataclass
class Note:
    x: int
    y: int
    text: str
    icon: str = "icons/svg/book.svg"
    icon_size: int = 40

    def to_foundry_dict(self):
        return {
            "entryId": None,
            "icon": self.icon,
            "iconSize": self.icon_size,
            "iconTint": None,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "flags": {}
        }


@dataclass
class Tile:
    x: int
    y: int
    width: int
    height: int
    img: str

    def to_foundry_dict(self):
        return {
            "img": self.img,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }
