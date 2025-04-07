from dungeon_generator.elements import WallSegment
from typing import List, Tuple, Set


def generate_room_walls_with_door_gaps(
    x1: int, y1: int, x2: int, y2: int,
    door_coords: Set[Tuple[int, int]]
) -> List[WallSegment]:
    """
    Builds a perimeter of wall segments for a rectangular room, skipping
    segments where doors intersect (by cell edge midpoint).

    x1, y1: top-left corner (inclusive)
    x2, y2: bottom-right corner (exclusive)
    door_coords: set of (x, y) grid points where a door is centered
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
