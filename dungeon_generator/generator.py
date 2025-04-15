"""
Dungeon Generation Module

This module contains functions to procedurally generate grid-based dungeons.
"""
import random
from typing import List, Tuple, Set
from dataclasses import dataclass
from .enums import GenerationTag, Direction, DoorType, RoomType
from .dungeon import Dungeon
from .elements import WallSegment, Room, Path, Hallway, Door
from .utils import generate_room_walls_with_door_gaps, _ranges_overlap, offset_point_in_direction


@dataclass
class GenerationSettings:
    """
    Settings to control dungeon generation behavior.
    All values are adjustable from the GUI and affect generation.
    """
    min_room_size: int = 5
    max_room_size: int = 12
    max_depth: int = 5
    margin: int = 1
    seed: str = ""
    tags: Set[GenerationTag] = None

    def __init__(self, seed: str, tags: Set[GenerationTag], width: int, height: int):
        self.seed = seed
        self.tags = set(tags)
        self.width = width
        self.height = height

        self.room_min_size, self.room_max_size = GenerationTag.resolve_room_size(self.tags)
        self.max_depth = GenerationTag.resolve_max_depth(self.tags)

    def __post_init__(self):
        if self.tags:
            self.min_room_size, self.max_room_size = GenerationTag.resolve_room_size(self.tags)
            self.max_depth = GenerationTag.resolve_max_depth(self.tags)

    @classmethod
    def from_gui(
            cls,
            width: int,
            height: int,
            seed: str,
            tags: Set[GenerationTag]
    ) -> 'GenerationSettings':
        """Helper to create settings from GUI inputs."""
        settings = cls(seed=seed, tags=tags, width=width, height=height)
        return settings


def generate_dungeon(width: int, height: int, settings: GenerationSettings) -> Dungeon:
    """
    Procedurally generate a dungeon layout using a combination of algorithms.

    Args:
        width (int): The width of the dungeon grid.
        height (int): The height of the dungeon grid.
        settings (GenerationSettings): Configuration for how the dungeon should be generated.

    Returns:
        Dungeon: A fully generated dungeon object.
    """
    rng = random.Random(settings.seed)
    dungeon = Dungeon(width, height)

    # Step 1: Generate room layout
    rooms: List[Room] = _place_rooms(dungeon, settings, rng)

    # Step 2: Connect rooms with hallways
    hallways: List[Hallway] = _place_hallways(dungeon, rooms, settings, rng)

    # Step 2.1: Add an edge entrance if tag exists
    hallways.append(_connect_room_to_map_edge(dungeon, rooms, hallways, settings, rng))

    # Step 2.2 Ensure all rooms are connected somehow
    if not check_all_rooms_connected(rooms):
        print("Not all rooms are connected to the entrance, trying to fix it.")
        _place_missing_hallways(dungeon, rooms, hallways, settings, rng)

    # TODO: Step 3: Populate all Rooms with appropriate RoomTypes and DoorTypes

    # Step 4: Add doors
    dungeon.doors = _place_doors(dungeon, rooms, hallways, settings, rng)

    # Step 5: Add walls
    _place_walls(dungeon, rooms, hallways, dungeon.doors)

    return dungeon


def _place_rooms(dungeon: Dungeon, settings: GenerationSettings, rng: random.Random) -> List[Room]:
    """
    Randomly places non-overlapping rooms within the dungeon bounds.

    Returns:
        List[Room]: A list of successfully placed rooms.
    """
    placed_rooms: List[Room] = []

    for i in range(settings.max_depth * 10):
        w = rng.randint(settings.min_room_size, settings.max_room_size)
        h = rng.randint(settings.min_room_size, settings.max_room_size)
        x = rng.randint(settings.margin, dungeon.width - w - settings.margin)
        y = rng.randint(settings.margin, dungeon.height - h - settings.margin)
        new_room = Room(i ,x, y, x + w, y + h)

        if any(new_room.intersects_with_buffer(room) for room in placed_rooms):
            continue

        placed_rooms.append(new_room)
        dungeon.carve_room(new_room.x1, new_room.y1, new_room.x2, new_room.y2)

    return placed_rooms

def _place_walls(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], doors: List[Door]):
    """
    Places walls around all floor tiles, skipping where neighboring floors exist.
    """
    floor_coords = set()
    for y, row in enumerate(dungeon.grid):
        for x, val in enumerate(row):
            if val == 1:
                floor_coords.add((x, y))

    for x, y in floor_coords:
        # Check each direction
        neighbors = {
            "top": (x, y - 1),
            "bottom": (x, y + 1),
            "left": (x - 1, y),
            "right": (x + 1, y),
        }

        if neighbors["top"] not in floor_coords:
            dungeon.walls.append(WallSegment(x, y, x + 1, y))
        if neighbors["bottom"] not in floor_coords:
            dungeon.walls.append(WallSegment(x, y + 1, x + 1, y + 1))
        if neighbors["left"] not in floor_coords:
            dungeon.walls.append(WallSegment(x, y, x, y + 1))
        if neighbors["right"] not in floor_coords:
            dungeon.walls.append(WallSegment(x + 1, y, x + 1, y + 1))


def _place_hallways(dungeon: Dungeon, rooms: List[Room], settings: GenerationSettings, rng: random.Random) -> List[Hallway]:
    print('--- Starting to connect rooms ---')
    hallways: List[Hallway] = []
    connected = set()
    remaining = set(range(len(rooms)))
    current: int = remaining.pop()
    connected.add(current)

    while remaining:
        nearest = None
        nearest_dist = float("inf")
        current_center = rooms[current].center()

        for i in remaining:
            dist = _manhattan_distance(current_center, rooms[i].center())
            if dist < nearest_dist:
                nearest: int = i
                nearest_dist = dist

        r1, r2 = rooms[current], rooms[nearest]
        success = False

        # Try to connect rooms that are adjacent
        hallway: Hallway | None = _connect_adjacent_rooms(dungeon, r1, r2, rng)
        if hallway:
            print(f'Connecting rooms -> adjacent: {r1} to {r2}')
            success = True
        else:
            # Try to connect rooms that are not adjacent
            hallway = connect_rooms(dungeon, rooms, hallways, r1, r2, settings, rng)
            if hallway:
                print(f'Connecting rooms -> nearest: {r1} to {r2}')
                success = True
            else:
                print(f'Warning: Could not connect next room: {r1} to {r2}')
                # Try connecting to any already connected room instead

                for alt in sorted(connected, key=lambda i: _manhattan_distance(rooms[nearest].center(), rooms[i].center())):
                    alt_room = rooms[alt]

                    # Try to connect rooms that are adjacent
                    hallway = _connect_adjacent_rooms(dungeon, rooms[nearest], alt_room, rng)
                    if hallway:
                        print(f'Connecting rooms -> adjacent: {rooms[nearest]} to {alt_room}')
                        success = True
                        break
                    else:
                        # Try to connect rooms that are not adjacent
                        hallway = connect_rooms(dungeon, rooms, hallways, r1, alt_room, settings, rng)
                        if hallway:
                            print(f'Connecting rooms -> alternative: {r1} to {alt_room}')
                            success = True
                            break
                else:
                    # Still no success
                    print(f'Final failure: Could not connect room {r1} to any other')
                    remaining.remove(nearest)
                    current = nearest
                    continue

        if success:
            hallways.append(hallway)
            connected.add(nearest)
            remaining.remove(nearest)
            current = nearest
            continue

    print('--- Finished connecting rooms ---')
    return hallways

def _place_missing_hallways(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], settings: GenerationSettings, rng: random.Random)-> bool:
    # List of ids of all rooms connected to the entrance
    connected_ids: List[int]

    # Populate connected_ids
    for room in rooms:
            if room.room_type == RoomType.ENTRANCE:
                connected_ids = room.get_connected_room_ids_by_extension(rooms)
                break

    # Get a list of all rooms not connected
    disconnected_rooms = [room for room in rooms if room.id not in connected_ids]

    for room in disconnected_rooms:
        # Find closest room in the main connected component
        closest_connected = None
        shortest_dist = float("inf")

        for other in rooms:
            if other.id in connected_ids:
                dist = _manhattan_distance(room.center(), other.center())
                if dist < shortest_dist:
                    closest_connected = other
                    shortest_dist = dist

        if closest_connected:

            hallway = _connect_adjacent_rooms(dungeon, room, closest_connected, rng)
            if not hallway:
                hallway = connect_rooms(dungeon, rooms, hallways, room, closest_connected, settings, rng)

            if hallway:
                hallways.append(hallway)
                room.add_connection(closest_connected)
                if check_all_rooms_connected(rooms):
                    print("Connected all missing sections to the entrance!")
                    return True
                connected_ids.update(room.get_connected_room_ids_by_extension(rooms))

    # TODO: Implement additional fallback logic

    print("Could not connect all sections/rooms to the entrance!")
    return False


def _connect_adjacent_rooms(dungeon: Dungeon, r1: Room, r2: Room, rng: random.Random) -> Hallway | None:
    """
    Connects two rooms that are 1 or 2 cells apart by creating a connecting hallway tile or short path.
    """
    path: Path = None

    # Horizontal alignment (left-right)
    if _ranges_overlap(r1.y1, r1.y2, r2.y1, r2.y2):
        y_start = max(r1.y1, r2.y1)
        y_end = min(r1.y2, r2.y2)
        y = rng.randint(y_start, y_end - 1)

        # Room A is to the left of B
        if r1.x2 + 1 == r2.x1:
            path = Path(r1.x2, y, r1.x2, y)
        elif r1.x2 + 2 == r2.x1:
            path = Path(r1.x2, y, r1.x2 + 1, y)

        # Room A is to the right of B
        if r2.x2 + 1 == r1.x1:
            path = Path(r2.x2, y, r2.x2, y)
        elif r2.x2 + 2 == r1.x1:
            path = Path(r2.x2, y, r2.x2 + 1, y)

    # Vertical alignment (above-below)
    elif _ranges_overlap(r1.x1, r1.x2, r2.x1, r2.x2):
        x_start = max(r1.x1, r2.x1)
        x_end = min(r1.x2, r2.x2)
        x = rng.randint(x_start, x_end - 1)

        # Room A is above B
        if r1.y2 + 1 == r2.y1:
            path = Path(x, r1.y2, x, r1.y2)
        elif r1.y2 + 2 == r2.y1:
            path = Path(x, r1.y2, x, r1.y2 + 1)

        # Room A is below B
        if r2.y2 + 1 == r1.y1:
            path = Path(x, r2.y2, x, r2.y2)
        elif r2.y2 + 2 == r1.y1:
            path = Path(x, r2.y2, x, r2.y2 + 1)

    if path:
        if path.x1 == path.x2 and path.y1 == path.y2:
            dungeon.carve_tile(path.x1, path.y1)
        else:
            dungeon.carve_line(path.x1, path.y1, path.x2, path.y2)

        r1.add_connection(r2)
        return Hallway([path])

    return None

def _connect_tiles(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], a: Tuple[int, int], b: Tuple[int, int], direction_a: Direction, direction_b: Direction, rng: random.Random) -> Hallway | None:
    ax, ay = a
    bx, by = b

    # Carve Straight line
    if ax == bx or ay == by:
        path = Path(ax, ay, bx, by)
        if can_connect(dungeon, path, rooms, hallways, 1):
            dungeon.carve_line(ax, ay, bx, by)
            print(f"Connecing rooms -> straight line: {path}")
            return Hallway([path])
        return None

    success: bool = False

    # Carve 1 tile path in direction to begin with
    hallway = Hallway([Path(ax, ay, ax, ay)])
    hallway.segments.append(Path(bx, by, bx, by))

    # Calculate new starting cells:
    ax2, ay2 = Direction.move_cell_in_direction(a, direction_a)
    bx2, by2 = Direction.move_cell_in_direction(b, direction_b)

    # Connect the ends of both starting path
    if ax2 == bx2 or ay2 == by2:
        # If they already alinge in one axis just connect them
        path = Path(ax2, ay2, bx2, by2)
        if can_connect(dungeon, path, rooms, hallways, 1):
            success = True
            hallway.segments.append(path)
            print(f"Connecing rooms -> secondary straight line: {hallway.segments}")
    else:
        # Connect both points by using an L shape

        # Define first path for vertical movement first
        path_1 = Path(ax2, ay2, ax2, by2)

        # Paths starting at cell a and moving against its direction are never valid
        # Check if vertical first works if not always try horizontal otherwise do it randomly
        if bool(rng.getrandbits(1)) or path_1.get_direction() == direction_a.get_opposite():
            # Define paths for horizontal movement first
            path_1 = Path(ax2, ay2, bx2, ay2)
            path_2 = Path(bx2, by2, bx2, (ay2 - 1) if ay2 > by2 else (ay2 + 1))
        else:
            # Define second path for vertical movement first
            path_2 = Path(bx2, by2, (ax2 - 1) if ax2 > bx2 else (ax2 + 1), by2)

        if can_connect(dungeon, path_1, rooms, hallways, 1) and can_connect(dungeon, path_2, rooms, hallways, 1):
            success = True
            hallway.segments.append(path_1)
            hallway.segments.append(path_2)
            print(f"Connecing rooms -> L-shape: {hallway.segments}")

    if success:
        # Only start carving after we confirmed success for the whole thing
        for p in hallway.segments:
            if not p.is_one_cell_path():
                dungeon.carve_line(p.x1, p.y1, p.x2, p.y2)
            else:
                dungeon.carve_tile(p.x1, p.y1)
        return hallway
    else:
        return None

def connect_rooms(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], r1: Room, r2: Room, settings: GenerationSettings, rng: random.Random) -> Hallway | None:
    # STRAIGHT or MAZE logic
    direction_r1: Direction
    direction_r2: Direction
    nearest_center: Tuple[int, int] = r2.center()
    if GenerationTag.MAZE in settings.tags:
        # Every edge except the opposite ones are valid
        furthest_distance: int = 0
        furthest_cell_r1: Tuple[int, int]
        furthest_direction_r1: Direction
        furthest_direction_r2: Direction
        for d in Direction:
            for cell_r1 in r1.edge_in_direction(d):
                distance = _manhattan_distance(cell_r1, nearest_center)
                if distance > furthest_distance:
                    furthest_direction_r1 = d
                    furthest_cell_r1 = cell_r1
                    furthest_distance = distance
            for cell_r2 in r2.edge_in_direction(d):
                distance = _manhattan_distance(furthest_cell_r1, cell_r2)
                if distance > furthest_distance:
                    furthest_direction_r2 = d
                    furthest_distance = distance
    else:
        # Only the closest edges are valid
        closest_distance: int = float("inf")
        nearest_cell_r1: Tuple[int, int]
        closest_direction_r1: Direction
        closest_direction_r2: Direction
        for d in Direction:
            for cell_r1 in r1.edge_in_direction(d):
                distance = _manhattan_distance(cell_r1, nearest_center)
                if distance < closest_distance:
                    closest_direction_r1 = d
                    nearest_cell_r1 = cell_r1
                    closest_distance = distance
            for cell_r2 in r2.edge_in_direction(d):
                distance = _manhattan_distance(nearest_cell_r1, cell_r2)
                if distance < closest_distance:
                    closest_direction_r2 = d
                    closest_distance = distance
        direction_r1 = closest_direction_r1
        direction_r2 = closest_direction_r2
    # Save tried edge combination so we can save on retries and calculations
    tried_edge_cells: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
    for _ in range(100):
        if GenerationTag.MAZE in settings.tags:
            directions = list(Direction)
            directions.remove(furthest_direction_r1)
            direction_r1 = rng.choice(directions)
            directions = list(Direction)
            directions.remove(furthest_direction_r2)
            direction_r2 = rng.choice(directions)
        # Get random valide tile after moving it away from the room
        edge_cell_r1: int
        edge_cell_r2: int
        for _ in range(100):
            # Find edges not yet tried
            edge_cell_r1 = rng.choice(r1.edge_in_direction(direction_r1))
            edge_cell_r2 = rng.choice(r2.edge_in_direction(direction_r2))
            key = (edge_cell_r1, edge_cell_r2)
            if key not in tried_edge_cells:
                # print(f'  Trying new edge cells "{key}"')
                tried_edge_cells.add(key)
                break
        else:
            # Break if the loop finished without finding new edges to try
            print('  Ran out of Edges to try!')
            break
        a = Direction.move_cell_in_direction(edge_cell_r1, direction_r1)
        b = Direction.move_cell_in_direction(edge_cell_r2, direction_r2)
        hallway = _connect_tiles(dungeon, rooms, hallways, a, b, direction_r1, direction_r2, rng)
        if hallway:
            r1.add_connection(r2)
            return hallway

    return None

def check_room_connected(room: Room, rooms: List[Room]) -> bool:
    filtered_rooms = rooms.copy()

    for r in filtered_rooms:
        if r.id in room.connections:
            filtered_rooms.remove(r)

    full_set = {room.id for room in filtered_rooms}

    return room.id in full_set

def check_all_rooms_connected(rooms: List[Room]) -> bool:
    full_set = {room.id for room in rooms}
    return rooms[0].get_connected_room_ids_by_extension(rooms) == full_set

def can_connect(
        dungeon: Dungeon,
        path: Path,
        rooms: List[Room],
        hallways: List[Hallway],
        buffer: int = 0,
        rooms_to_ignore: List[Room] = [],
        ignore_bounds: bool = False
        ) -> bool:
    """
    Checks whether a path would intersect any room (with optional buffer) or any hallway segment.

    Args:
        path (Path): The proposed path to check.
        rooms (List[Room]): List of placed rooms.
        hallways (List[Hallway]): List of existing hallways.
        buffer (int): Optional expansion of room boundaries for collision checks.

    Returns:
        bool: True if the path is clear, False if it intersects any room or hallway.
    """
    # Check for collision with rooms (with buffer)
    for room in rooms:
        if room not in rooms_to_ignore:
            if path.path_intersects_room(room, buffer):
                # print(f'        Path "{path}" intersects Room "{room}"')
                return False

    # Check for collision with existing hallway segments
    for hall in hallways:
        for segment in hall.segments:
            if path.paths_intersect_path(segment):
                # print(f'        Path "{path}" intersects Hallway in segment "{segment}"')
                return False

    if not ignore_bounds:
        # Check that path endpoints are within the map borders.
        if not (1 <= path.x1 < dungeon.width - 1 and 1 <= path.x2 < dungeon.width - 1 and
            1 <= path.y1 < dungeon.height - 1 and 1 <= path.y2 < dungeon.height - 1):
            print(f'        Path "{path}" is out of map bounds (0,0) to ({dungeon.width}, {dungeon.height})')
            return False

    return True


def _connect_room_to_map_edge(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], settings: GenerationSettings,
                              rng: random.Random) -> Hallway | None:
    direction = rng.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])

    if GenerationTag.ENTRANCE_NORTH in settings.tags:
        direction = Direction.UP
    elif GenerationTag.ENTRANCE_SOUTH in settings.tags:
        direction = Direction.DOWN
    elif GenerationTag.ENTRANCE_WEST in settings.tags:
        direction = Direction.LEFT
    elif GenerationTag.ENTRANCE_EAST in settings.tags:
        direction = Direction.RIGHT
    elif GenerationTag.STAIRS in settings.tags:
        return None

    for room in rooms:

        if direction == Direction.UP:
            edge = rng.choice([(x, room.y1) for x in range(room.x1, room.x2)])
            candidate = Path(edge[0], edge[1] - 1, edge[0], 0)
        elif direction == Direction.DOWN:
            edge = rng.choice([(x, room.y2 - 1) for x in range(room.x1, room.x2)])
            candidate = Path(edge[0], edge[1] + 1, edge[0], dungeon.height - 1)
        elif direction == Direction.LEFT:
            edge = rng.choice([(room.x1, y) for y in range(room.y1, room.y2)])
            candidate = Path(edge[0] - 1, edge[1], 0, edge[1])
        else: # direction == Direction.RIGHT:
            edge = rng.choice([(room.x2 - 1, y) for y in range(room.y1, room.y2)])
            candidate = Path(edge[0] + 1, edge[1], dungeon.width - 1, edge[1])

        if can_connect(dungeon, candidate, rooms, hallways, 0, rooms_to_ignore=List[room], ignore_bounds=True):
            dungeon.carve_line(candidate.x1, candidate.y1, candidate.x2, candidate.y2)
            room.room_type = RoomType.ENTRANCE
            return Hallway([candidate])

    return None


def _manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _place_doors(dungeon: Dungeon, rooms: List[Room], hallways: List[Hallway], settings: GenerationSettings, rng: random.Random) -> List[Door]:
    """
    Places doors where the start or end of a hallway is adjacent to a room.
    Ensures no duplicate doors are placed.
    """
    doors: List[Door] = []
    door_positions: Set[Tuple[int, int]] = set()

    for hallway in hallways:
        endpoints: List[Path] = [hallway.segments[0]]
        if len(hallway.segments) > 1:
            endpoints.append(hallway.segments[1])

        for endpoint in endpoints:
            x, y = endpoint.x1, endpoint.y1
            for room in rooms:
                if room.contains_point((x, y), margin=1):
                    if (x, y) in door_positions:
                        continue

                    # Determine direction based on adjacency to room edge
                    if x == room.x1 - 1:
                        direction = Direction.RIGHT
                    elif x == room.x2:
                        direction = Direction.LEFT
                    elif y == room.y1 - 1:
                        direction = Direction.DOWN
                    elif y == room.y2:
                        direction = Direction.UP
                    else:
                        # Not on a known edge — skip
                        continue

                    doors.append(Door(x, y, direction, DoorType.WOOD, open=False))
                    door_positions.add((x, y))
                    break

    return doors
