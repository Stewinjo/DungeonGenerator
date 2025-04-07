"""
Dungeon Elements

This module defines the individual structural and interactive components used
in a dungeon layout. These include wall segments, lights, notes, and image tiles.

Each element supports export to Foundry VTT-compatible dictionaries for JSON scene generation.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Optional

class DoorType(Enum):
    """
    Enumeration of supported door types.
    Used to determine door appearance and interaction behavior.
    """

    GLASS = auto()
    METAL = auto()
    STONE = auto()
    WOOD = auto()

@dataclass
class WallSegment:
    """
    Represents a wall segment, optionally functioning as a door with metadata for Foundry export.

    Attributes:
        x1, y1 (int): Starting coordinates.
        x2, y2 (int): Ending coordinates.
        door (int): 0 = no door, 1 = door, 2 = locked, etc.
        door_type (Optional[DoorType]): Type of door material, used for styling.
        ds (int): Door state (0=open, 1=closed).
        move, sense, sound, light (int): Foundry-specific wall properties.
    """

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
        """
        Returns a dictionary compatible with Foundry VTT's wall data format.
        """

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
        """
        Converts tile-based coordinates to pixel-based coordinates.

        Args:
            scale (int): Size of a tile in pixels.

        Returns:
            Tuple[int, int, int, int]: (x1, y1, x2, y2) in pixel units.
        """

        return self.x1 * scale, self.y1 * scale, self.x2 * scale, self.y2 * scale

@dataclass
class Light:
    """
    Represents a light source in the dungeon.

    Attributes:
        x, y (int): Position of the light in pixels.
        dim (int): Radius of dim light.
        bright (int): Radius of bright light.
        color (Optional[str]): Hex color code for the light.
    """

    x: int
    y: int
    dim: int = 30
    bright: int = 10
    color: Optional[str] = "#ffffff"

    def to_foundry_dict(self):
        """
        Returns a dictionary compatible with Foundry VTT's light source format.
        """

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
    """
    Represents a note or marker that can appear on the map.

    Attributes:
        x, y (int): Position in pixels.
        text (str): The text content of the note.
        icon (str): Path to the icon image.
        icon_size (int): Size of the icon in pixels.
    """

    x: int
    y: int
    text: str
    icon: str = "icons/svg/book.svg"
    icon_size: int = 40

    def to_foundry_dict(self):
        """
        Returns a dictionary compatible with Foundry VTT's note format.
        """

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
    """
    Represents a visual overlay tile such as an image asset on the dungeon map.

    Attributes:
        x, y (int): Top-left corner of the tile in pixels.
        width, height (int): Size of the tile in pixels.
        img (str): File path to the image used for the tile.
    """

    x: int
    y: int
    width: int
    height: int
    img: str

    def to_foundry_dict(self):
        """
        Returns a dictionary compatible with Foundry VTT's tile format.
        """

        return {
            "img": self.img,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }
