"""
Dungeon Grid Model

This module defines the core `Dungeon` class, which represents a tile-based dungeon layout,
including walls, lights, notes, and decorative tiles. The grid is stored as a 2D array where
1 represents walkable floor and 0 represents solid or void tiles.

The dungeon is designed to support rendering, export, and dynamic procedural generation.
"""

from typing import List
from .elements import WallSegment, Light, Note, Tile, Door

# pylint: disable=too-many-instance-attributes
class Dungeon:
    """
    A class representing the structure and content of a dungeon.

    Attributes:
        name (str): Name of this dungeon.
        width (int): Width of the dungeon grid.
        height (int): Height of the dungeon grid.
        grid (List[List[int]]): 2D grid of integers where 1 = floor, 0 = wall/void.
        walls (List[WallSegment]): List of wall segments in the dungeon.
        lights (List[Light]): List of light sources in the dungeon.
        notes (List[Note]): List of informational notes or markers.
        tiles (List[Tile]): List of additional decorative tiles or overlays.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the Dungeon object with a given grid width and height.

        Args:
            width (int): Number of tiles horizontally.
            height (int): Number of tiles vertically.
        """

        self.width = width
        self.height = height
        self.name = "Dungeon"

        # Grid: 2D array where 1 = walkable (floor), 0 = solid (wall/void)
        self.grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]

        # Dungeon elements
        self.walls: List[WallSegment] = []
        self.doors: List[Door] = []
        self.lights: List[Light] = []
        self.notes: List[Note] = []
        self.tiles: List[Tile] = []

    def carve_room(self, x1, y1, x2, y2):
        """
        Mark a rectangular region of the dungeon as walkable floor tiles (1s in the grid).

        Args:
            x1 (int): Left boundary of the room (inclusive).
            y1 (int): Top boundary of the room (inclusive).
            x2 (int): Right boundary of the room (exclusive).
            y2 (int): Bottom boundary of the room (exclusive).
        """

        for y in range(y1, y2):
            for x in range(x1, x2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = 1

    def carve_tile(self, x: int, y: int):
        """
        Carve a single tile, marking it as walkable (1) if within bounds.

        Args:
            x (int): X-coordinate of the tile.
            y (int): Y-coordinate of the tile.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 1

    def carve_line(self, x1: int, y1: int, x2: int, y2: int):
        """
        Carves a straight horizontal or vertical path between two points.

        Args:
            x1 (int): Starting X coordinate.
            y1 (int): Starting Y coordinate.
            x2 (int): Ending X coordinate.
            y2 (int): Ending Y coordinate.
        """
        if x1 == x2:
            # Vertical line
            start, end = sorted([y1, y2])
            for y in range(start, end + 1):
                self.carve_tile(x1, y)
        elif y1 == y2:
            # Horizontal line
            start, end = sorted([x1, x2])
            for x in range(start, end + 1):
                self.carve_tile(x, y1)
        else:
            raise ValueError("Only horizontal or vertical lines are supported")
