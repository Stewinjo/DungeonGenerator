"""
Door Element

Defines the :class:`Door` dataclass used to represent doors in the dungeon structure.
Each door includes spatial coordinates, directional orientation, type, and open state.
It also provides functionality to convert a door into a wall segment for rendering and export.

This module is part of the dungeon element system used by Rosecrypt.
"""

from dataclasses import dataclass
from rosecrypt.enums import Direction
from rosecrypt.elements.wall_segment import WallSegment
from rosecrypt.generation.enums import DoorType

@dataclass
class Door:
    """
    Represents a dungeon door with a defined position, direction, type, and open/closed state.

    :param x1: The x-coordinate of the door.
    :type x1: int
    :param y1: The y-coordinate of the door.
    :type y1: int
    :param direction: The orientation of the door (vertical or horizontal).
    :type direction: Direction
    :param type: The type of the door (e.g., wood, metal).
    :type type: DoorType
    :param open: Whether the door is open or closed.
    :type open: bool
    """
    x1: int
    y1: int
    direction: Direction
    type: DoorType
    open: bool

    def door_to_wall(self) -> WallSegment:
        """
        Converts the door into a :class:`WallSegment` centered in the tile
        in the direction of the door. Used for rendering and collision.

        :return: A wall segment representing the door.
        :rtype: WallSegment
        """
        cx = self.x1 + 0.5
        cy = self.y1 + 0.5

        if self.direction in (Direction.UP, Direction.DOWN):
            x1, y1 = cx - 0.5, cy
            x2, y2 = cx + 0.5, cy
        else:
            x1, y1 = cx, cy - 0.5
            x2, y2 = cx, cy + 0.5

        return WallSegment(x1, y1, x2, y2, door=1, door_type=self.type)
