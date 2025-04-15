"""
Dungeon Elements

This module defines the individual structural and interactive components used
in a dungeon layout. These include wall segments, lights, notes, and image tiles.

Each element supports export to Foundry VTT-compatible dictionaries for JSON scene generation.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Set
from .enums import DoorType, Direction, RoomType


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
    ds: int = 0  # door state (0=open, 1=closed)
    move: int = 1
    sense: int = 1
    sound: int = 0
    light: int = 0

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

@dataclass
class Door:
    """
    A door consists of its coordinates and type.
    """
    x1: int
    y1: int
    direction: Direction
    type: DoorType
    open: bool

    def door_to_wall(self) -> WallSegment:
        """
        Converts the door to a short wall segment centered in the cell in the correct direction.
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

@dataclass()
class Room:
    """
    Dataclass holding all the information of one room
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
        Checks whether two rooms intersect and return true if they do.

        Args:
            self (Room): This room.
            other (Room): The room to check against.

        Returns:
            bool: True if the rooms intersect.
        """
        return not (self.x2 <= other.x1 or self.x1 >= other.x2 or self.y2 <= other.y1 or self.y1 >= other.y2)

    def add_connection(self, other: 'Room'):
        self.connections.add(other.id)
        other.connections.add(self.id)

    def get_connected_room_ids_by_extension(self, all_rooms: List['Room']) -> Set[int]:
        """
        Given this room and a list of all rooms, returns the set of room IDs
        that are reachable through any chain of connections from this room.

        Args:
            self (Room): The room to start from.
            all_rooms (List[Room]): All rooms in the dungeon.

        Returns:
            Set[int]: A set of all connected room IDs (including the start room itself).
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
        x, y = point
        return (self.x1 - margin <= x < self.x2 + margin) and (self.y1 - margin <= y < self.y2 + margin)

    def intersects_with_buffer(self, other: 'Room', buffer: int = 1) -> bool:
        """Check if this room would intersect another if it was 1 cell larger on all sides."""
        expanded = Room(self.id, self.x1 - buffer, self.y1 - buffer, self.x2 + buffer, self.y2 + buffer)
        return expanded.intersects(other)

    def center(self) -> Tuple[int, int]:
        """Returns center point (rounded) of the room."""
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def edges(self) -> List[Tuple[int, int]]:
        """Returns all perimeter tiles of the room as (x, y) coordinates."""
        edge_points = []
        for x in range(self.x1, self.x2):
            edge_points.append((x, self.y1))
            edge_points.append((x, self.y2 - 1))
        for y in range(self.y1 + 1, self.y2 - 1):
            edge_points.append((self.x1, y))
            edge_points.append((self.x2 - 1, y))

        return edge_points

    def edge_in_direction(self, direction: Direction) -> List[Tuple[int, int]]:
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
        excluded = set(self.edge_in_direction(direction))
        return [edge for edge in self.edges() if edge not in excluded]

    def edges_including_direction(self, direction: Direction) -> List[Tuple[int, int]]:
        return self.edge_in_direction(direction)

@dataclass
class Path:
    """
    Dataclass holding all the information of one Path
    """
    x1: int
    y1: int
    x2: int
    y2: int

    def paths_intersect_path(self, other: 'Path') -> bool:
        """
        Returns True if this path intersects another path.
        """

        def on_segment(p: Tuple[int, int], q: Tuple[int, int], r: Tuple[int, int]) -> bool:
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
        elif o1 == 0 and on_segment(p1, p2, q1):
            return True
        elif o2 == 0 and on_segment(p1, q2, q1):
            return True
        elif o3 == 0 and on_segment(p2, p1, q2):
            return True
        elif o4 == 0 and on_segment(p2, q1, q2):
            return True

        return False

    def is_one_cell_path(self) -> bool:
        length = max(abs(self.x2 - self.x1), abs(self.y2 - self.y1))
        return length == 0

    def get_direction(self) -> Direction | None:
        if self.is_one_cell_path():
            return None
        if self.x1 == self.x2:
            if self.y1 > self.y2:
                return Direction.UP
            else:
                return Direction.DOWN
        else:
            if self.x1 > self.x2:
                return Direction.LEFT
            else:
                return Direction.RIGHT

    def get_line_points(self) -> List[Tuple[int, int]]:
        """
        Returns a list of all tile coordinates that this path segment covers.
        Assumes the path is axis-aligned (horizontal or vertical).
        """
        if self.is_one_cell_path():
            return [[self.x1, self.y1]]
        elif self.x1 == self.x2:
            # Vertical path
            return [(self.x1, y) for y in range(min(self.y1, self.y2), max(self.y1, self.y2) + 1)]
        elif self.y1 == self.y2:
            # Horizontal path
            return [(x, self.y1) for x in range(min(self.x1, self.x2), max(self.x1, self.x2) + 1)]
        else:
            raise ValueError(f"Path is not axis-aligned: {self}")

    def path_intersects_room(self, room: Room, buffer: int = 0) -> bool:
        """
        Returns True if a path passes through any tile within the expanded room's bounding box.
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


@dataclass
class Hallway:
    """
    A hallway consists of one or more connected straight Path segments.
    """
    segments: List[Path]

    def is_one_cell_hallway(self) -> bool:
        return len(self.segments) == 1 and self.segments[0].is_one_cell_path()
