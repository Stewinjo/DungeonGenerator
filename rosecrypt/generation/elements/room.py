"""
Room Element

Defines the `Room` dataclass representing rectangular room structures in the dungeon grid.
Rooms contain metadata such as type and connectivity to other rooms,
and offer geometric utility methods.
"""

from typing import Set, List, Tuple
from dataclasses import dataclass, field
from rosecrypt.enums import Direction
from rosecrypt.generation.enums import RoomType

@dataclass()
class Room:
    """
    A rectangular region representing a room in the dungeon.

    :param id: Unique room identifier.
    :param x1: Top-left x-coordinate.
    :param y1: Top-left y-coordinate.
    :param x2: Bottom-right x-coordinate.
    :param y2: Bottom-right y-coordinate.
    :param room_type: Optional room type classification.
    :param connections: Set of connected room IDs.
    """
    id: int
    x1: int
    y1: int
    x2: int
    y2: int
    room_type: RoomType = None
    connections: Set[int] = field(default_factory=set)

    def __post_init__(self):
        # Initialize connections with its own id
        self.connections.add(self.id)
        self.room_type = None

    def intersects(self, other: 'Room') -> bool:
        """
        Determines if this room intersects another.

        :param other: The room to test intersection with.
        :type other: Room
        :return: True if the rooms overlap.
        :rtype: bool
        """
        return not (
            self.x2 <= other.x1 or self.x1 >= other.x2 or self.y2 <= other.y1 or self.y1 >= other.y2
            )

    def add_connection(self, other: 'Room'):
        """
        Adds a two-way connection between this room and another.

        :param other: Room to connect.
        :type other: Room
        """
        self.connections.add(other.id)
        other.connections.add(self.id)

    def get_connected_room_ids_by_extension(self, all_rooms: List['Room']) -> Set[int]:
        """
        Performs a breadth-first search to get all rooms connected to this one.

        :param all_rooms: Full list of rooms.
        :type all_rooms: List[Room]
        :return: All reachable room IDs.
        :rtype: Set[int]
        """
        visited = set()
        queue = [self]
        room_lookup = {room.id: room for room in all_rooms}

        while queue:
            current = queue.pop(0)
            if current.id in visited:
                continue
            visited.add(current.id)
            for conn_id in current.connections:
                if conn_id not in visited and conn_id in room_lookup:
                    queue.append(room_lookup[conn_id])

        return visited

    def contains_point(self, point: Tuple[int, int], margin: int = 0) -> bool:
        """
        Checks whether a point lies within this room (optionally with margin).

        :param point: Tuple (x, y) to check.
        :type point: Tuple[int, int]
        :param margin: Expansion distance in tiles.
        :type margin: int
        :return: True if the point lies within the room (with margin).
        :rtype: bool
        """
        x, y = point
        #pylint: disable=line-too-long
        return (self.x1 - margin <= x < self.x2 + margin) and (self.y1 - margin <= y < self.y2 + margin)

    def intersects_with_buffer(self, other: 'Room', buffer: int = 1) -> bool:
        """
        Determines if this room intersects another when expanded.

        :param other: Room to test intersection with.
        :type other: Room
        :param buffer: Buffer tiles to apply to this room before testing.
        :type buffer: int
        :return: True if expanded room intersects other.
        :rtype: bool
        """
        expanded = Room(
            self.id, self.x1 - buffer,
            self.y1 - buffer,
            self.x2 + buffer,
            self.y2 + buffer
            )
        return expanded.intersects(other)

    def center(self) -> Tuple[int, int]:
        """
        Returns the center point of this room.

        :return: Center (x, y) coordinates.
        :rtype: Tuple[int, int]
        """
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def edges(self) -> List[Tuple[int, int]]:
        """
        Returns all edge tiles of this room (outer perimeter).

        :return: List of (x, y) coordinates.
        :rtype: List[Tuple[int, int]]
        """
        edge_points = []
        for x in range(self.x1, self.x2):
            edge_points.append((x, self.y1))
            edge_points.append((x, self.y2 - 1))
        for y in range(self.y1 + 1, self.y2 - 1):
            edge_points.append((self.x1, y))
            edge_points.append((self.x2 - 1, y))

        return edge_points

    def edge_in_direction(self, direction: Direction) -> List[Tuple[int, int]]:
        """
        Returns all edge tiles in a specific direction.

        :param direction: Direction to check.
        :type direction: Direction
        :return: List of edge tiles.
        :rtype: List[Tuple[int, int]]
        """
        if direction == Direction.LEFT:
            return [(self.x1, y) for y in range(self.y1, self.y2)]
        if direction == Direction.RIGHT:
            return [(self.x2 - 1, y) for y in range(self.y1, self.y2)]
        if direction == Direction.UP:
            return [(x, self.y1) for x in range(self.x1, self.x2)]
        if direction == Direction.DOWN:
            return [(x, self.y2 - 1) for x in range(self.x1, self.x2)]
        return []

    def edges_excluding_direction(self, direction: Direction) -> List[Tuple[int, int]]:
        """
        Returns all edge tiles of the room, excluding those in the given direction.

        :param direction: Direction to exclude.
        :type direction: Direction
        :return: Filtered list of edge tiles.
        :rtype: List[Tuple[int, int]]
        """
        excluded = set(self.edge_in_direction(direction))
        return [edge for edge in self.edges() if edge not in excluded]

    def edges_including_direction(self, direction: Direction) -> List[Tuple[int, int]]:
        """
        Returns edge tiles specifically in the provided direction.

        :param direction: Direction to include.
        :type direction: Direction
        :return: List of edge tiles.
        :rtype: List[Tuple[int, int]]
        """
        return self.edge_in_direction(direction)
