from .dungeon import Dungeon
from .elements import WallSegment, DoorType
from .utils import generate_room_walls_with_door_gaps


def generate_basic_dungeon(width: int, height: int, seed: str = "") -> Dungeon:
    dungeon = Dungeon(width, height)

    # Calculate room sizes
    room_width = (width - 2) // 3
    room_height = height - 2  # fill nearly full height
    margin = 1

    # Left room
    left_x1 = margin
    left_x2 = left_x1 + room_width
    y1 = margin
    y2 = y1 + room_height
    dungeon.carve_room(left_x1, y1, left_x2, y2)

    # Right room
    right_x2 = width - margin
    right_x1 = right_x2 - room_width
    dungeon.carve_room(right_x1, y1, right_x2, y2)

    # Connecting hallway
    hall_x1 = left_x2
    hall_x2 = right_x1
    hall_y = height // 2  # vertical center
    for x in range(hall_x1, hall_x2):
        dungeon.grid[hall_y][x] = 1  # carve horizontal hall

    # Doors
    left_door_coord = (left_x2, hall_y)
    right_door_coord = (right_x1, hall_y)
    door_coords = {left_door_coord, right_door_coord}

    # Doors where hall meets rooms
    dungeon.walls += [
        WallSegment(left_door_coord[0] + 0.5, left_door_coord[1],
                    left_door_coord[0] + 0.5, left_door_coord[1] + 1,
                    door=1, door_type=DoorType.WOOD),

        WallSegment(right_door_coord[0] - 0.5, right_door_coord[1],
                    right_door_coord[0] - 0.5, right_door_coord[1] + 1,
                    door=1, door_type=DoorType.METAL),
    ]

    # Walls above and below hallway
    for x in range(hall_x1, hall_x2):
        if (x, hall_y - 1) not in door_coords:
            dungeon.walls.append(WallSegment(x, hall_y, x + 1, hall_y))  # top edge

        if (x, hall_y + 1) not in door_coords:
            dungeon.walls.append(WallSegment(x, hall_y + 1, x + 1, hall_y + 1))  # bottom edge

    # Generate walls with door gaps
    dungeon.walls += generate_room_walls_with_door_gaps(left_x1, y1, left_x2, y2, door_coords)
    dungeon.walls += generate_room_walls_with_door_gaps(right_x1, y1, right_x2, y2, door_coords)

    return dungeon
