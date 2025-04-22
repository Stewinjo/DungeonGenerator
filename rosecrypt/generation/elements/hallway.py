"""
Hallway Element

Defines the `Hallway` dataclass, which represents a collection of connected path segments.
Hallways are used to form corridor-like connections between rooms in dungeon layouts.
"""

from typing import List
from dataclasses import dataclass
from rosecrypt.generation.elements.path import Path

@dataclass
class Hallway:
    """
    A hallway is composed of one or more straight, connected Path segments.

    :param segments: List of path segments forming the hallway.
    :type segments: List[Path]
    """
    segments: List[Path]

    def is_one_cell_hallway(self) -> bool:
        """
        Determines whether this hallway consists of only a single one-tile path.

        :return: True if hallway is a single-tile segment.
        :rtype: bool
        """
        return len(self.segments) == 1 and self.segments[0].is_one_cell_path()
