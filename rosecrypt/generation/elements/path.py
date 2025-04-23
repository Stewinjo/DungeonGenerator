"""
Path Element

Provides the `Path` dataclass used to represent linear connections between two grid points.
Includes methods for collision detection, direction calculation, and spatial queries.
"""

from typing import Tuple, List
from dataclasses import dataclass
from rosecrypt.enums import Direction
from rosecrypt.generation.elements.room import Room

@dataclass
class Path:
    """
    A path segment that connects two points on the dungeon grid.

    :param x1: Starting x-coordinate.
    :param y1: Starting y-coordinate.
    :param x2: Ending x-coordinate.
    :param y2: Ending y-coordinate.
    """
    x1: int
    y1: int
    x2: int
    y2: int

    def paths_intersect_path(self, other: 'Path') -> bool:
        """
        Determines if this path intersects with another path.

        :param other: The path to compare against.
        :type other: Path
        :return: True if paths intersect.
        :rtype: bool
        """

        def on_segment(p: Tuple[int, int], q: Tuple[int, int], r: Tuple[int, int]) -> bool:
            #pylint: disable=line-too-long
            return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])

        def orientation(p: Tuple[int, int], q: Tuple[int, int], r: Tuple[int, int]) -> int:
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0
            return 1 if val > 0 else 2

        p1, q1 = (self.x1, self.y1), (self.x2, self.y2)
        p2, q2 = (other.x1, other.y1), (other.x2, other.y2)

        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and on_segment(p1, p2, q1):
            return True
        if o2 == 0 and on_segment(p1, q2, q1):
            return True
        if o3 == 0 and on_segment(p2, p1, q2):
            return True
        if o4 == 0 and on_segment(p2, q1, q2):
            return True

        return False

    def is_one_cell_path(self) -> bool:
        """
        Determines if the path spans a single cell (zero-length).

        :return: True if the path covers only one tile.
        :rtype: bool
        """
        length = max(abs(self.x2 - self.x1), abs(self.y2 - self.y1))
        return length == 0

    def get_direction(self) -> Direction | None:
        """
        Returns the cardinal direction of the path, if applicable.

        :return: The path's orientation, or None if it is a one-cell path.
        :rtype: Optional[Direction]
        """
        if self.is_one_cell_path():
            return None
        if self.x1 == self.x2:
            if self.y1 > self.y2:
                return Direction.UP
            return Direction.DOWN
        if self.x1 > self.x2:
            return Direction.LEFT
        return Direction.RIGHT

    def get_line_points(self) -> List[Tuple[int, int]]:
        """
        Returns a list of all (x, y) grid coordinates the path covers.

        :return: List of tile positions along the path.
        :rtype: List[Tuple[int, int]]
        :raises ValueError: If the path is not axis-aligned.
        """
        if self.is_one_cell_path():
            return [[self.x1, self.y1]]
        if self.x1 == self.x2:
            # Vertical path
            return [(self.x1, y) for y in range(min(self.y1, self.y2), max(self.y1, self.y2) + 1)]
        if self.y1 == self.y2:
            # Horizontal path
            return [(x, self.y1) for x in range(min(self.x1, self.x2), max(self.x1, self.x2) + 1)]
        raise ValueError(f"Path is not axis-aligned: {self}")

    def path_intersects_room(self, room: Room, buffer: int = 0) -> bool:
        """
        Checks whether this path intersects a room's bounds (optionally expanded).

        :param room: Room to test intersection against.
        :type room: Room
        :param buffer: Number of tiles to expand the room bounds by.
        :type buffer: int
        :return: True if the path intersects the room.
        :rtype: bool
        """
        # Expand the room
        x1 = room.x1 - buffer
        y1 = room.y1 - buffer
        x2 = room.x2 + buffer
        y2 = room.y2 + buffer

        # Determine the bounding box of the path
        px_min = min(self.x1, self.x2)
        px_max = max(self.x1, self.x2)
        py_min = min(self.y1, self.y2)
        py_max = max(self.y1, self.y2)

        # Check for overlap in X and Y ranges
        return not (px_max < x1 or px_min >= x2 or py_max < y1 or py_min >= y2)
