"""
Dungeon Enums Module

This module defines core enumerations used throughout the procedural dungeon generator.

Includes:
- :class:`Direction` for expressing cardinal directions on a 2D grid and moving between tiles.
- Utilities for directional logic such as moving a cell and retrieving the opposite direction.

These enums are used for spatial reasoning, wall and hallway placement, and pathfinding logic.
"""


from enum import Enum
from typing import Tuple, List, Set, Any

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

class Tag(Enum):
    """
    Base class for generation and rendering tags.

    Attributes:
        category (str): Descriptive grouping of the tag (e.g., Size, Density).
        data (Any): Any associated metadata, such as a tuple or numeric value.
    """

    def __new__(cls, category: str, data: Any):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)
        obj.category = category
        obj.data = data
        return obj

    def __str__(self):
        return self.name

    @classmethod
    def toggle_tag(
        cls,
        active_tags: Set['Tag'],
        new_tag: 'Tag'
    ) -> Set['Tag']:
        """
        Adds or removes a tag from the set, respecting exclusivity rules.

        Args:
            active_tags: The current set of tags.
            new_tag: The tag to toggle.

        Returns:
            Updated tag set.
        """
        updated = set(active_tags)
        if new_tag in updated:
            updated.remove(new_tag)
        else:
            for group in cls.mutually_exclusive_groups():
                if new_tag in group:
                    updated -= group
            updated.add(new_tag)
        return updated

    @staticmethod
    def mutually_exclusive_groups() -> List[Set['Tag']]:
        """
        Define tag groups that are mutually exclusive.

        Subclasses should override this.

        Returns:
            A list of mutually exclusive tag sets.
        """
        return []

    @classmethod
    def get_tag_by_category(cls, tags: Set['Tag'], category: str) -> 'Tag':
        """
        Returns the tag from a set that matches the given category, or None.

        Args:
            tags: The tag set to search.
            category: The category to look for.

        Returns:
            The matching tag or None.
        """
        return next((tag for tag in tags if tag.category == category), None)

    @classmethod
    def make_full_set(cls) -> Set['Tag']:
        """
        Returns a default set of tags, selecting the first tag from each mutually exclusive group.

        Can be overridden for more specific behavior (e.g., random choice or fixed tag defaults).

        Returns:
            Set[Tag]: A set containing one tag from each mutually exclusive group.
        """
        full_set = set()
        for group in cls.mutually_exclusive_groups():
            tag = next(iter(group))  # Pick the first one deterministically
            full_set.add(tag)
        return full_set
