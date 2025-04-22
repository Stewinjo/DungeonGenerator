"""
Dungeon Enums Module

This module defines core enumerations used throughout the procedural dungeon generator.

Includes:
- :class:`Direction` for expressing cardinal directions on a 2D grid and moving between tiles.
- Utilities for directional logic such as moving a cell and retrieving the opposite direction.

These enums are used for spatial reasoning, wall and hallway placement, and pathfinding logic.
"""


from enum import Enum
from typing import Tuple

class Direction(Enum):
    """
    Cardinal directions used for grid-based navigation.

    This enum defines the four main directions on a 2D grid:
    up, down, left, and right. It also provides utilities
    to move coordinates in a direction or get the opposite direction.

    Members:
        UP (str): Represents upward movement ("up").
        DOWN (str): Represents downward movement ("down").
        LEFT (str): Represents leftward movement ("left").
        RIGHT (str): Represents rightward movement ("right").
    """
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    @staticmethod
    def move_cell_in_direction(
        cell: Tuple[int, int],
        direction:'Direction',
        steps: int = 1
        ) -> int | int:
        """
        Returns a new cell coordinate by moving a given cell in a specified direction.

        :param cell: The (x, y) coordinate to move from.
        :type cell: Tuple[int, int]
        :param direction: The direction to move in.
        :type direction: Direction
        :param steps: Number of steps to move in the given direction (default is 1).
        :type steps: int
        :return: A new (x, y) coordinate after movement.
        :rtype: Tuple[int, int]
        """
        match direction:
            case Direction.UP:
                return cell[0], cell[1] - steps
            case Direction.DOWN:
                return cell[0], cell[1] + steps
            case Direction.LEFT:
                return cell[0] - steps, cell[1]
            case Direction.RIGHT:
                return cell[0] + steps, cell[1]

    def get_opposite(self) -> 'Direction':
        """
        Returns the opposite direction of the current Direction.

        :return: The opposite cardinal direction.
        :rtype: Direction
        """
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]
