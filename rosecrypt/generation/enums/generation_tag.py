"""
Tags used to control and influence procedural dungeon generation.

GenerationTags are modular switches applied to customize the behavior,
layout, style, and content of generated dungeons. These include room
sizes, density, themes, entry point behavior, and corridor style.
"""

import random
from enum import auto
from typing import Set, List
from rosecrypt.enums import Tag

class GenerationTag(Tag):
    """
    Enum representing tags that modify dungeon generation behavior.

    Attributes:
        category (str): Descriptive category of the tag (e.g., Room Size, Themes).
        data (Any): Optional data associated with the tag (e.g., size tuple or numeric value).
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """
        Overrides the default behavior for auto-assigned enum values.

        This method ensures each enum value receives a unique, sequential integer
        regardless of category or data structure. The value is simply set to the
        number of already defined members (i.e., `count`), ensuring predictable ordering.

        Args:
            name (str): The name of the enum member.
            start (Any): The initial value (unused here).
            count (int): The number of previously defined members.
            last_values (List[Any]): A list of previous values.

        Returns:
            int: A unique integer value for the enum member.
        """
        return count  # Ensure safe int values for all auto() fields

    # Room sizes
    SMALL_ROOMS = ("Room Size", (4, 6))
    MEDIUM_ROOMS = ("Room Size", (6, 10))
    LARGE_ROOMS = ("Room Size", (10, 16))

    # Room amounts
    DENSE = ("Room Distribution", 7)
    MEDIUM = ("Room Distribution", 5)
    SPARSE = ("Room Distribution", 3)

    # Entrance options
    ENTRANCE_NORTH = ("Entrances", auto())
    ENTRANCE_SOUTH = ("Entrances", auto())
    ENTRANCE_WEST = ("Entrances", auto())
    ENTRANCE_EAST = ("Entrances", auto())
    STAIRS = ("Entrances", auto())

    # Themes
    ANY = ("Themes", auto())
    ARCTIC = ("Themes", auto())
    COASTAL = ("Themes", auto())
    DESERT = ("Themes", auto())
    FOREST = ("Themes", auto())
    GRASSLAND = ("Themes", auto())
    HILL = ("Themes", auto())
    MOUNTAIN = ("Themes", auto())
    SWAMP = ("Themes", auto())
    UNDERDARK = ("Themes", auto())
    UNDERWATER = ("Themes", auto())
    URBAN = ("Themes", auto())
    BANDIT = ("Themes", auto())
    NECROMANCER = ("Themes", auto())
    KOBOLD = ("Themes", auto())
    GOBLIN = ("Themes", auto())
    GNOLL = ("Themes", auto())

    # Hallway options
    STRAIGHT = ("Hallways", auto())
    MAZE = ("Hallways", auto())

    @staticmethod
    def resolve_room_size(tags: Set['GenerationTag']) -> tuple[int, int]:
        """
        Determines the room size range based on active tags.

        Args:
            tags (Set[GenerationTag]): Active generation tags.

        Returns:
            tuple[int, int]: A (min, max) tuple defining room dimensions.
        """
        if GenerationTag.SMALL_ROOMS in tags:
            return GenerationTag.SMALL_ROOMS.data
        if GenerationTag.LARGE_ROOMS in tags:
            return GenerationTag.LARGE_ROOMS.data
        return GenerationTag.MEDIUM_ROOMS.data

    @staticmethod
    def resolve_max_depth(tags: Set['GenerationTag']) -> int:
        """
        Resolves how many room placement passes (depth) to attempt based on density tags.

        Args:
            tags (Set[GenerationTag]): Active generation tags.

        Returns:
            int: Number of attempts or depth used during room placement.
        """
        if GenerationTag.SPARSE in tags:
            return GenerationTag.SPARSE.data
        if GenerationTag.DENSE in tags:
            return GenerationTag.DENSE.data
        return GenerationTag.MEDIUM.data

    @staticmethod
    def mutually_exclusive_groups() -> List[Set['GenerationTag']]:
        """
        Defines sets of tags that cannot be combined. Used for validation and UI toggles.

        Returns:
            List[Set[GenerationTag]]: List of sets, each set containing mutually exclusive tags.
        """

        return [
            {GenerationTag.SMALL_ROOMS, GenerationTag.MEDIUM_ROOMS, GenerationTag.LARGE_ROOMS},
            {GenerationTag.DENSE, GenerationTag.SPARSE, GenerationTag.MEDIUM},
            {
                GenerationTag.ENTRANCE_EAST, GenerationTag.ENTRANCE_NORTH,
                GenerationTag.ENTRANCE_SOUTH, GenerationTag.ENTRANCE_WEST,
                GenerationTag.STAIRS
            },
            {
                GenerationTag.ANY, GenerationTag.ARCTIC, GenerationTag.COASTAL,
                GenerationTag.DESERT, GenerationTag.FOREST, GenerationTag.GRASSLAND,
                GenerationTag.HILL, GenerationTag.MOUNTAIN, GenerationTag.SWAMP,
                GenerationTag.UNDERDARK, GenerationTag.UNDERWATER, GenerationTag.URBAN,
                GenerationTag.BANDIT, GenerationTag.NECROMANCER, GenerationTag.KOBOLD,
                GenerationTag.GOBLIN, GenerationTag.GNOLL
            },
            {
                GenerationTag.STRAIGHT, GenerationTag.MAZE
            }
        ]

    @staticmethod
    def make_full_set() -> Set['GenerationTag']:
        """
        Returns a default set of generation tags, including one tag from each exclusive group.

        Returns:
            Set[GenerationTag]: Default tag set for medium-sized, medium-density dungeons.
        """
        return {
            GenerationTag.MEDIUM_ROOMS, # Default to medium rooms
            GenerationTag.MEDIUM, # Default to normal room density
            random.choice(
                list(GenerationTag.mutually_exclusive_groups()[3])
                ), # Select random entrance option
            random.choice(
                list(GenerationTag.mutually_exclusive_groups()[4])
                ), # Select random theme
            GenerationTag.STRAIGHT # Default to straight hallways
        }
