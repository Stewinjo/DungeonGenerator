"""
Utility Functions for Dungeon Wall Generation

This module provides helper functions used in dungeon generation, such as building
room perimeters with intelligent wall placement around door openings.
"""

from typing import List, Tuple, Set
from .elements import WallSegment, Path, Room, Direction

def generate_room_walls_with_door_gaps(x1, y1, x2, y2, door_segments: Set[Tuple[float, float, float, float]]) -> List[WallSegment]:
    walls = []
    for x in range(x1, x2):
        top = WallSegment(x, y1, x + 1, y1)
        bottom = WallSegment(x, y2, x + 1, y2)
        if (top.x1, top.y1, top.x2, top.y2) not in door_segments:
            walls.append(top)
        if (bottom.x1, bottom.y1, bottom.x2, bottom.y2) not in door_segments:
            walls.append(bottom)
    for y in range(y1, y2):
        left = WallSegment(x1, y, x1, y + 1)
        right = WallSegment(x2, y, x2, y + 1)
        if (left.x1, left.y1, left.x2, left.y2) not in door_segments:
            walls.append(left)
        if (right.x1, right.y1, right.x2, right.y2) not in door_segments:
            walls.append(right)
    return walls

def _ranges_overlap(a1: int, a2: int, b1: int, b2: int) -> bool:
    """
    Returns True if the ranges [a1, a2) and [b1, b2) overlap.
    """
    return max(a1, b1) < min(a2, b2)

def offset_point_in_direction(point: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
    x, y = point
    if direction == Direction.UP:
        return (x, y - 1)
    elif direction == Direction.DOWN:
        return (x, y + 1)
    elif direction == Direction.LEFT:
        return (x - 1, y)
    elif direction == Direction.RIGHT:
        return (x + 1, y)
    return (x, y)
