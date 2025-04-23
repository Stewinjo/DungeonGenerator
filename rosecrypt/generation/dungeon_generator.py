"""
Dungeon Generator

Implements the `DungeonGenerator` class, responsible for procedural generation
of dungeons on a grid. Combines multiple algorithms to generate rooms, hallways,
doors, and walls based on configuration provided via `GenerationSettings`.

Features:
- Room placement with configurable size and margin
- Hallway generation with fallback connectivity logic
- Optional entrance path from dungeon edge
- Door and wall placement based on room adjacency
- Maze-like and linear connection strategies via tags
"""

import random
from typing import List, Tuple, Set
from rosecrypt.dungeon import Dungeon
from rosecrypt.enums import Direction
from rosecrypt.logger import setup_logger
from rosecrypt.elements.wall_segment import WallSegment
from rosecrypt.elements.door import Door
from rosecrypt.generation.enums.door_type import DoorType
from rosecrypt.generation.generation_settings import GenerationSettings
from rosecrypt.generation.elements.hallway import Hallway
from rosecrypt.generation.elements.path import Path
from rosecrypt.generation.elements.room import Room
from rosecrypt.generation.enums.generation_tag import GenerationTag
from rosecrypt.generation.enums.room_type import RoomType

log = setup_logger(__name__, category="Generation")

#pylint: disable=too-few-public-methods
class DungeonGenerator:
    """
    Main generator class for producing procedural dungeons.

    This class orchestrates the dungeon generation process by creating rooms,
    connecting them with hallways, and populating additional structures such as
    walls and doors. The generation strategy adapts based on configured tags.

    :param settings: Configuration for how the dungeon should be generated.
    :type settings: GenerationSettings
    """

    def __init__(self, settings: GenerationSettings):
        """
        Initializes a DungeonGenerator instance.

        :param settings: Generation settings object containing all config parameters.
        :type settings: GenerationSettings
        """
        self.settings: GenerationSettings = settings
        self.rng: random.Random = random.Random(settings.seed)
        self.rooms: List[Room] = []
        self.hallways: List[Hallway] = []

    def generate_dungeon(self, width: int, height: int) -> Dungeon:
        """
        Procedurally generate a dungeon layout using a combination of algorithms.

        :param width: The width of the dungeon grid.
        :type width: int
        :param height: The height of the dungeon grid.
        :type height: int
        :return: A fully generated dungeon object.
        :rtype: Dungeon
        """
        dungeon = Dungeon(width, height)

        # Step 1: Generate room layout
        self._place_rooms(dungeon)

        # Step 2: Connect rooms with hallways
        self._place_hallways(dungeon)

        # Step 2.1: Add an edge entrance if tag exists
        self._connect_room_to_map_edge(dungeon)

        # Step 2.2 Ensure all rooms are connected somehow
        if not self.__check_all_rooms_connected():
            log.info("Not all rooms are connected to the entrance, trying to fix it.")
            self._place_missing_hallways(dungeon)

        # TODO: Step 3: Populate all Rooms with appropriate RoomTypes and DoorTypes

        # Step 4: Add doors
        self._place_doors(dungeon)

        # Step 5: Add walls
        self._place_walls(dungeon)

        return dungeon


    def _place_rooms(self, dungeon: Dungeon) -> bool:
        """
        Places randomly sized and positioned rooms in the dungeon grid.

        :param dungeon: The dungeon to populate with rooms.
        :type dungeon: Dungeon
        :return: True if at least one room was placed.
        :rtype: bool
        """

        log.info("Starting to place rooms...")
        placed_rooms: List[Room] = []

        for i in range(self.settings.max_depth * 10):
            w = self.rng.randint(self.settings.min_room_size, self.settings.max_room_size)
            h = self.rng.randint(self.settings.min_room_size, self.settings.max_room_size)
            x = self.rng.randint(self.settings.margin, dungeon.width - w - self.settings.margin)
            y = self.rng.randint(self.settings.margin, dungeon.height - h - self.settings.margin)
            new_room = Room(i ,x, y, x + w, y + h)

            if any(new_room.intersects_with_buffer(room) for room in placed_rooms):
                continue

            placed_rooms.append(new_room)
            dungeon.carve_room(new_room.x1, new_room.y1, new_room.x2, new_room.y2)

        if len(placed_rooms) > 0:
            self.rooms = placed_rooms
            log.info("Finished placing %s rooms.", len(placed_rooms))
            return True

        log.error("Could not place any rooms!")
        return False

    #pylint: disable=too-many-branches disable=too-many-statements
    def _place_hallways(self, dungeon: Dungeon) -> bool:
        """
        Connects rooms together using hallway segments.

        :param dungeon: The dungeon to add hallways to.
        :type dungeon: Dungeon
        :return: True if all rooms were successfully connected.
        :rtype: bool
        """
        log.info('Starting to connect rooms...')
        hallways: List[Hallway] = []
        connected = set()
        remaining = set(range(len(self.rooms)))
        current: int = remaining.pop()
        connected.add(current)

        failure: bool = False

        while remaining:
            nearest = None
            nearest_dist = float("inf")
            current_center = self.rooms[current].center()

            for i in remaining:
                dist = self.__manhattan_distance(current_center, self.rooms[i].center())
                if dist < nearest_dist:
                    nearest: int = i
                    nearest_dist = dist

            success = False

            # Try to connect rooms that are adjacent
            hallway: Hallway | None = self._connect_adjacent_rooms(
                dungeon,
                self.rooms[current],
                self.rooms[nearest]
                )
            if hallway:
                log.debug(
                    'Connecting rooms, adjacent: %s to %s.',
                    self.rooms[current],
                    self.rooms[nearest]
                    )
                success = True
            else:
                # Try to connect rooms that are not adjacent
                hallway = self._connect_rooms(dungeon, self.rooms[current], self.rooms[nearest])
                if hallway:
                    log.debug(
                        'Connecting rooms, nearest: %s to %s.',
                        self.rooms[current],
                        self.rooms[nearest]
                        )
                    success = True
                else:
                    log.info(
                        'Could not connect next room: %s to %s.',
                        self.rooms[current],
                        self.rooms[nearest]
                        )
                    # Try connecting to any already connected room instead

                    for alt in sorted(
                        connected,
                        key=lambda i: self.__manhattan_distance(
                            self.rooms[nearest].center(),
                            self.rooms[i].center()
                            )
                        ):

                        # Try to connect rooms that are adjacent
                        hallway = self._connect_adjacent_rooms(
                            dungeon,
                            self.rooms[nearest],
                            self.rooms[alt]
                            )
                        if hallway:
                            log.debug(
                                'Connecting rooms, adjacent: %s to %s.',
                                self.rooms[nearest],
                                self.rooms[alt]
                                )
                            success = True
                            break
                        # Try to connect rooms that are not adjacent
                        hallway = self._connect_rooms(dungeon, self.rooms[current], self.rooms[alt])
                        if hallway:
                            log.debug(
                                'Connecting rooms, alternative: %s to %s.',
                                self.rooms[current],
                                self.rooms[alt]
                                )
                            success = True
                            break
                    else:
                        # Still no success
                        log.warning('Could not connect room %s to any other.', self.rooms[current])
                        remaining.remove(nearest)
                        current = nearest
                        failure = True
                        continue

            if success:
                hallways.append(hallway)
                connected.add(nearest)
                remaining.remove(nearest)
                current = nearest
                continue

        log.info('Finished connecting rooms.')
        if not failure:
            self.hallways = hallways
            return True

        # Return False if at least one room could not be connected
        return False

    def _connect_room_to_map_edge(self, dungeon: Dungeon) -> bool:
        """
        Attempts to connect a room to the edge of the dungeon based on entrance tags.

        :param dungeon: The dungeon to modify.
        :type dungeon: Dungeon
        :return: True if connection was successful, False otherwise.
        :rtype: bool
        """
        direction = self.rng.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])

        if GenerationTag.ENTRANCE_NORTH in self.settings.tags:
            direction = Direction.UP
        elif GenerationTag.ENTRANCE_SOUTH in self.settings.tags:
            direction = Direction.DOWN
        elif GenerationTag.ENTRANCE_WEST in self.settings.tags:
            direction = Direction.LEFT
        elif GenerationTag.ENTRANCE_EAST in self.settings.tags:
            direction = Direction.RIGHT
        elif GenerationTag.STAIRS in self.settings.tags:
            return None

        for room in self.rooms:

            if direction == Direction.UP:
                edge = self.rng.choice([(x, room.y1) for x in range(room.x1, room.x2)])
                candidate = Path(edge[0], edge[1] - 1, edge[0], 0)
            elif direction == Direction.DOWN:
                edge = self.rng.choice([(x, room.y2 - 1) for x in range(room.x1, room.x2)])
                candidate = Path(edge[0], edge[1] + 1, edge[0], dungeon.height - 1)
            elif direction == Direction.LEFT:
                edge = self.rng.choice([(room.x1, y) for y in range(room.y1, room.y2)])
                candidate = Path(edge[0] - 1, edge[1], 0, edge[1])
            else: # direction == Direction.RIGHT:
                edge = self.rng.choice([(room.x2 - 1, y) for y in range(room.y1, room.y2)])
                candidate = Path(edge[0] + 1, edge[1], dungeon.width - 1, edge[1])

            if self.__can_connect(
                dungeon,
                candidate,
                0,
                rooms_to_ignore=List[room],
                ignore_bounds=True
                ):
                dungeon.carve_line(candidate.x1, candidate.y1, candidate.x2, candidate.y2)
                room.room_type = RoomType.ENTRANCE
                self.hallways.append(Hallway([candidate]))
                return True

        return False

    def _place_doors(self, dungeon: Dungeon):
        """
        Places doors where hallway endpoints are adjacent to rooms.

        :param dungeon: The dungeon to modify.
        :type dungeon: Dungeon
        """

        log.info("Starting to place doors...")

        doors: List[Door] = []
        door_positions: Set[Tuple[int, int]] = set()

        for hallway in self.hallways:
            endpoints: List[Path] = [hallway.segments[0]]
            if len(hallway.segments) > 1:
                endpoints.append(hallway.segments[1])

            for endpoint in endpoints:
                x, y = endpoint.x1, endpoint.y1
                for room in self.rooms:
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

        log.info("Finished placing %s doors.", len(doors))
        dungeon.doors = doors

    def _place_missing_hallways(self, dungeon: Dungeon)-> bool:
        """
        Ensures that all rooms are reachable by connecting unconnected ones.

        :param dungeon: The dungeon to connect.
        :type dungeon: Dungeon
        :return: True if full connectivity was achieved.
        :rtype: bool
        """

        # List of ids of all rooms connected to the entrance
        connected_ids: List[int]

        # Populate connected_ids
        for room in self.rooms:
            if room.room_type == RoomType.ENTRANCE:
                connected_ids = room.get_connected_room_ids_by_extension(self.rooms)
                break

        # Get a list of all rooms not connected
        disconnected_rooms = [room for room in self.rooms if room.id not in connected_ids]

        for room in disconnected_rooms:
            # Find closest room in the main connected component
            closest_connected = None
            shortest_dist = float("inf")

            for other in self.rooms:
                if other.id in connected_ids:
                    dist = self.__manhattan_distance(room.center(), other.center())
                    if dist < shortest_dist:
                        closest_connected = other
                        shortest_dist = dist

            if closest_connected:

                hallway = self._connect_adjacent_rooms(dungeon, room, closest_connected)
                if not hallway:
                    hallway = self._connect_rooms(dungeon, room, closest_connected)

                if hallway:
                    self.hallways.append(hallway)
                    room.add_connection(closest_connected)
                    if self.__check_all_rooms_connected():
                        log.info("Connected all missing sections to the entrance.")
                        return True
                    connected_ids.update(room.get_connected_room_ids_by_extension(self.rooms))

        # TODO: Implement additional fallback logic

        log.warning("Could not connect all sections/rooms to the entrance!")
        return False


    def _connect_adjacent_rooms(self, dungeon: Dungeon, r1: Room, r2: Room) -> Hallway | None:
        """
        Connects rooms that are next to each other with a short path.

        :param dungeon: The dungeon to modify.
        :type dungeon: Dungeon
        :param r1: First room.
        :type r1: Room
        :param r2: Second room.
        :type r2: Room
        :return: A hallway object if successful, else None.
        :rtype: Optional[Hallway]
        """
        path: Path = None

        # Horizontal alignment (left-right)
        if self.__ranges_overlap(r1.y1, r1.y2, r2.y1, r2.y2):
            y_start = max(r1.y1, r2.y1)
            y_end = min(r1.y2, r2.y2)
            y = self.rng.randint(y_start, y_end - 1)

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
        elif self.__ranges_overlap(r1.x1, r1.x2, r2.x1, r2.x2):
            x_start = max(r1.x1, r2.x1)
            x_end = min(r1.x2, r2.x2)
            x = self.rng.randint(x_start, x_end - 1)

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

    #pylint: disable=too-many-arguments disable=too-many-positional-arguments disable=too-many-locals
    def _connect_tiles(
            self,
            dungeon: Dungeon,
            a: Tuple[int, int],
            b: Tuple[int, int],
            direction_a: Direction,
            direction_b: Direction
            ) -> Hallway | None:
        """
        Attempts to connect two points on the grid with a hallway segment or L-shape.

        :param dungeon: The dungeon to modify.
        :type dungeon: Dungeon
        :param a: Start point.
        :type a: Tuple[int, int]
        :param b: End point.
        :type b: Tuple[int, int]
        :param direction_a: Exit direction from point a.
        :type direction_a: Direction
        :param direction_b: Exit direction from point b.
        :type direction_b: Direction
        :return: A hallway object if a valid path was found.
        :rtype: Optional[Hallway]
        """
        ax, ay = a
        bx, by = b

        # Carve Straight line
        if ax == bx or ay == by:
            path = Path(ax, ay, bx, by)
            if self.__can_connect(dungeon, path, 1):
                dungeon.carve_line(ax, ay, bx, by)
                log.debug("Connecing rooms, straight line: %s", path)
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
            if self.__can_connect(dungeon, path, 1):
                success = True
                hallway.segments.append(path)
                log.debug("Connecing rooms, secondary straight line: %s", hallway.segments)
        else:
            # Connect both points by using an L shape

            # Define first path for vertical movement first
            path_1 = Path(ax2, ay2, ax2, by2)

            # Paths starting at cell a and moving against its direction are never valid
            # Check if vertical first works if not always try horizontal otherwise do it randomly
            if bool(
                self.rng.getrandbits(1)
                ) or path_1.get_direction() == direction_a.get_opposite():
                # Define paths for horizontal movement first
                path_1 = Path(ax2, ay2, bx2, ay2)
                path_2 = Path(bx2, by2, bx2, (ay2 - 1) if ay2 > by2 else (ay2 + 1))
            else:
                # Define second path for vertical movement first
                path_2 = Path(bx2, by2, (ax2 - 1) if ax2 > bx2 else (ax2 + 1), by2)

            if self.__can_connect(dungeon, path_1, 1) and self.__can_connect(dungeon, path_2, 1):
                success = True
                hallway.segments.append(path_1)
                hallway.segments.append(path_2)
                log.debug("Connecing rooms, L-shape: %s", hallway.segments)

        if success:
            # Only start carving after we confirmed success for the whole thing
            for p in hallway.segments:
                if not p.is_one_cell_path():
                    dungeon.carve_line(p.x1, p.y1, p.x2, p.y2)
                else:
                    dungeon.carve_tile(p.x1, p.y1)
            return hallway
        return None

    def _connect_rooms(self, dungeon: Dungeon, r1: Room, r2: Room) -> Hallway | None:
        """
        Connects two rooms using straight or L-shaped hallways based on configured tags.

        :param dungeon: The dungeon to modify.
        :type dungeon: Dungeon
        :param r1: The first room to connect.
        :type r1: Room
        :param r2: The second room to connect.
        :type r2: Room
        :return: A Hallway object if connection was made.
        :rtype: Optional[Hallway]
        """

        # STRAIGHT or MAZE logic
        direction_r1: Direction
        direction_r2: Direction
        nearest_center: Tuple[int, int] = r2.center()
        if GenerationTag.MAZE in self.settings.tags:
            # Every edge except the opposite ones are valid
            furthest_distance: int = 0
            furthest_cell_r1: Tuple[int, int]
            furthest_direction_r1: Direction
            furthest_direction_r2: Direction
            for d in Direction:
                for cell_r1 in r1.edge_in_direction(d):
                    distance = self.__manhattan_distance(cell_r1, nearest_center)
                    if distance > furthest_distance:
                        furthest_direction_r1 = d
                        furthest_cell_r1 = cell_r1
                        furthest_distance = distance
                for cell_r2 in r2.edge_in_direction(d):
                    distance = self.__manhattan_distance(furthest_cell_r1, cell_r2)
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
                    distance = self.__manhattan_distance(cell_r1, nearest_center)
                    if distance < closest_distance:
                        closest_direction_r1 = d
                        nearest_cell_r1 = cell_r1
                        closest_distance = distance
                for cell_r2 in r2.edge_in_direction(d):
                    distance = self.__manhattan_distance(nearest_cell_r1, cell_r2)
                    if distance < closest_distance:
                        closest_direction_r2 = d
                        closest_distance = distance
            direction_r1 = closest_direction_r1
            direction_r2 = closest_direction_r2
        # Save tried edge combination so we can save on retries and calculations
        tried_edge_cells: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
        for _ in range(100):
            if GenerationTag.MAZE in self.settings.tags:
                directions = list(Direction)
                directions.remove(furthest_direction_r1)
                direction_r1 = self.rng.choice(directions)
                directions = list(Direction)
                directions.remove(furthest_direction_r2)
                direction_r2 = self.rng.choice(directions)
            # Get random valide tile after moving it away from the room
            edge_cell_r1: int
            edge_cell_r2: int
            for _ in range(100):
                # Find edges not yet tried
                edge_cell_r1 = self.rng.choice(r1.edge_in_direction(direction_r1))
                edge_cell_r2 = self.rng.choice(r2.edge_in_direction(direction_r2))
                key = (edge_cell_r1, edge_cell_r2)
                if key not in tried_edge_cells:
                    # print(f'  Trying new edge cells "{key}"')
                    tried_edge_cells.add(key)
                    break
            else:
                # Break if the loop finished without finding new edges to try
                log.warning('Ran out of Edges to try.')
                break
            a = Direction.move_cell_in_direction(edge_cell_r1, direction_r1)
            b = Direction.move_cell_in_direction(edge_cell_r2, direction_r2)
            hallway = self._connect_tiles(dungeon, a, b, direction_r1, direction_r2)
            if hallway:
                r1.add_connection(r2)
                return hallway

        return None

    # def __check_room_connected(room: Room, rooms: List[Room]) -> bool:
    #     filtered_rooms = rooms.copy()

    #     for r in filtered_rooms:
    #         if r.id in room.connections:
    #             filtered_rooms.remove(r)

    #     full_set = {room.id for room in filtered_rooms}

    #     return room.id in full_set

    def __check_all_rooms_connected(self) -> bool:
        """
        Verifies that all rooms belong to a single connected component.

        :return: True if all rooms are connected.
        :rtype: bool
        """
        full_set = {room.id for room in self.rooms}
        return self.rooms[0].get_connected_room_ids_by_extension(self.rooms) == full_set

    #pylint: disable=too-many-positional-arguments
    def __can_connect(
            self,
            dungeon: Dungeon,
            path: Path,
            buffer: int = 0,
            rooms_to_ignore: List[Room] = None,
            ignore_bounds: bool = False
            ) -> bool:
        """
        Determines if a path can be carved without intersecting rooms or other paths.

        :param dungeon: Dungeon instance.
        :type dungeon: Dungeon
        :param path: Path to test.
        :type path: Path
        :param buffer: Optional buffer around rooms.
        :type buffer: int
        :param rooms_to_ignore: Rooms that should not block the path.
        :type rooms_to_ignore: List[Room], optional
        :param ignore_bounds: If True, disables map boundary checks.
        :type ignore_bounds: bool
        :return: True if the path is valid.
        :rtype: bool
        """

        # Check for collision with rooms (with buffer)
        if not rooms_to_ignore:
            rooms_to_ignore = []

        for room in self.rooms:
            if room not in rooms_to_ignore:
                if path.path_intersects_room(room, buffer):
                    # print(f'        Path "{path}" intersects Room "{room}"')
                    return False

        # Check for collision with existing hallway segments
        for hall in self.hallways:
            for segment in hall.segments:
                if path.paths_intersect_path(segment):
                    # print(f'        Path "{path}" intersects Hallway in segment "{segment}"')
                    return False

        if not ignore_bounds:
            # Check that path endpoints are within the map borders.
            if not (1 <= path.x1 < dungeon.width - 1 and 1 <= path.x2 < dungeon.width - 1 and
                1 <= path.y1 < dungeon.height - 1 and 1 <= path.y2 < dungeon.height - 1):
                log.debug('Path "%s" is out of map bounds.', path)
                return False

        return True

    @staticmethod
    def _place_walls(dungeon: Dungeon):
        """
        Automatically adds walls to all exposed edges of carved tiles.

        :param dungeon: The dungeon to add walls to.
        :type dungeon: Dungeon
        """

        log.info("Starting to place walls...")

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

        log.info("Finished placing walls.")

    @staticmethod
    def __manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """
        Calculates Manhattan distance between two points.

        :param a: First coordinate.
        :type a: Tuple[int, int]
        :param b: Second coordinate.
        :type b: Tuple[int, int]
        :return: Manhattan distance between a and b.
        :rtype: int
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def __ranges_overlap(a1: int, a2: int, b1: int, b2: int) -> bool:
        """
        Returns True if the ranges [a1, a2) and [b1, b2) overlap.

        :param a1: Start of first range.
        :type a1: int
        :param a2: End of first range.
        :type a2: int
        :param b1: Start of second range.
        :type b1: int
        :param b2: End of second range.
        :type b2: int
        :return: True if ranges overlap.
        :rtype: bool
        """
        return max(a1, b1) < min(a2, b2)
