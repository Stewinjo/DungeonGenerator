"""
Dungeon Generation Settings

This module defines the GenerationSettings dataclass used to control procedural
dungeon generation behavior. It stores map dimensions, seed, active generation tags,
and room constraints, all of which influence dungeon structure and complexity.
"""

from dataclasses import dataclass
from typing import Set
from rosecrypt.generation.enums.generation_tag import GenerationTag

@dataclass
class GenerationSettings:
    """
    Settings container for dungeon generation configuration.

    Attributes:
        seed (str): Seed used for random number generation.
        tags (Set[GenerationTag]): Set of active generation tags.
        width (int): Width of the dungeon map.
        height (int): Height of the dungeon map.
        min_room_size (int): Minimum room size (auto-derived from tags).
        max_room_size (int): Maximum room size (auto-derived from tags).
        max_depth (int): Maximum recursion depth for generation (auto-derived).
        margin (int): Margin around the edge of the map where rooms may not be placed.
    """
    min_room_size: int = 5
    max_room_size: int = 12
    max_depth: int = 5
    margin: int = 1

    def __init__(self, seed: str, tags: Set[GenerationTag], width: int, height: int):
        """
        Initializes generation settings and derives tag-based parameters.

        :param seed: The RNG seed string.
        :type seed: str
        :param tags: Set of generation behavior flags.
        :type tags: Set[GenerationTag]
        :param width: Dungeon width in tiles.
        :type width: int
        :param height: Dungeon height in tiles.
        :type height: int
        """
        self.seed = seed
        self.tags = set(tags)
        self.width = width
        self.height = height

        self.room_min_size, self.room_max_size = GenerationTag.resolve_room_size(self.tags)
        self.max_depth = GenerationTag.resolve_max_depth(self.tags)

    def __post_init__(self):
        """
        Post-initialization hook to update derived settings from tags.
        """
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
        """
        Constructs a GenerationSettings instance from GUI input parameters.

        :param width: Dungeon width in tiles.
        :type width: int
        :param height: Dungeon height in tiles.
        :type height: int
        :param seed: RNG seed for generation.
        :type seed: str
        :param tags: Set of generation tags selected in the GUI.
        :type tags: Set[GenerationTag]
        :return: A new GenerationSettings instance.
        :rtype: GenerationSettings
        """
        settings = cls(seed=seed, tags=tags, width=width, height=height)
        return settings
