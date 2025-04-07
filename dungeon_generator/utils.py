"""
Utility Functions for Dungeon Wall Generation

This module provides helper functions used in dungeon generation, such as building
room perimeters with intelligent wall placement around door openings.
"""

from typing import List, Tuple, Set
from dungeon_generator.elements import WallSegment

def generate_room_walls_with_door_gaps(
    x1: int, y1: int, x2: int, y2: int,
    door_coords: Set[Tuple[int, int]]
) -> List[WallSegment]:
    """
    Generate wall segments for the perimeter of a rectangular room,
    skipping walls where doors are placed.

    This function creates a complete rectangular border using `WallSegment`s except where
    door coordinates are provided, in which case the wall segment is omitted.

    Args:
        x1 (int): Left X coordinate of the room (inclusive).
        y1 (int): Top Y coordinate of the room (inclusive).
        x2 (int): Right X coordinate of the room (exclusive).
        y2 (int): Bottom Y coordinate of the room (exclusive).
        door_coords (Set[Tuple[int, int]]): A set of (x, y) tile coordinates representing door positions.

    Returns:
        List[WallSegment]: A list of `WallSegment` instances forming the room's outer walls with gaps for doors.
    """
    walls = []

    # Horizontal top and bottom
    for x in range(x1, x2):
        if (x, y1) not in door_coords:
            walls.append(WallSegment(x, y1, x + 1, y1))  # top
        if (x, y2) not in door_coords:
            walls.append(WallSegment(x, y2, x + 1, y2))  # bottom

    # Vertical left and right
    for y in range(y1, y2):
        if (x1, y) not in door_coords:
            walls.append(WallSegment(x1, y, x1, y + 1))  # left
        if (x2, y) not in door_coords:
            walls.append(WallSegment(x2, y, x2, y + 1))  # right

    return walls
