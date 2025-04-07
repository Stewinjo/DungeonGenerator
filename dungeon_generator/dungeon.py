from typing import List
from .elements import WallSegment, Light, Note, Tile


class Dungeon:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Grid: 2D array where 1 = walkable (floor), 0 = solid (wall/void)
        self.grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]

        # Dungeon elements
        self.walls: List[WallSegment] = []
        self.lights: List[Light] = []
        self.notes: List[Note] = []
        self.tiles: List[Tile] = []

    def carve_room(self, x1, y1, x2, y2):
        """Utility to mark a rectangular area as walkable floor."""
        for y in range(y1, y2):
            for x in range(x1, x2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = 1
