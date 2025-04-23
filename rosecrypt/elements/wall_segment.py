"""
Wall Segment Element

Defines the :class:`WallSegment` dataclass used to represent solid barriers and doorways
between tiles, with optional Foundry VTT export metadata.
"""

from typing import Tuple, Optional
from dataclasses import dataclass
from rosecrypt.generation.enums import DoorType

# pylint: disable=too-many-instance-attributes
@dataclass
class WallSegment:
    """
    Represents a linear wall or door segment in the dungeon grid.

    :param x1: Starting x-coordinate.
    :type x1: int
    :param y1: Starting y-coordinate.
    :type y1: int
    :param x2: Ending x-coordinate.
    :type x2: int
    :param y2: Ending y-coordinate.
    :type y2: int
    :param door: Whether this segment represents a door (0 = wall, 1 = open door, 2 = locked, etc.).
    :type door: int
    :param door_type: Optional door type to determine styling/material.
    :type door_type: Optional[DoorType]
    :param ds: Door state (0 = open, 1 = closed).
    :type ds: int
    :param move: Foundry wall movement restriction.
    :type move: int
    :param sense: Foundry wall sensing restriction.
    :type sense: int
    :param sound: Foundry wall sound restriction.
    :type sound: int
    :param light: Foundry wall light restriction.
    :type light: int
    """

    x1: int
    y1: int
    x2: int
    y2: int
    door: int = 0  # 0: no door, 1: door, 2: locked, etc.
    door_type: Optional[DoorType] = None  # None unless it's a door
    ds: int = 0  # door state (0=open, 1=closed)
    move: int = 1
    sense: int = 1
    sound: int = 0
    light: int = 0

    def to_pixel_coords(self, scale: int) -> Tuple[int, int, int, int]:
        """
        Converts tile-based wall coordinates into pixel-space for rendering or export.

        :param scale: Pixel size of one grid unit.
        :type scale: int

        :return: A tuple of pixel coordinates (x1, y1, x2, y2).
        :rtype: Tuple[int, int, int, int]
        """
        return self.x1 * scale, self.y1 * scale, self.x2 * scale, self.y2 * scale
