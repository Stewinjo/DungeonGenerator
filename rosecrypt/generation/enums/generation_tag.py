import random
from enum import Enum, auto
from typing import Set, List

class GenerationTag(Enum):
    """
    Enum representing tags that can be used to influence the dungeon generation process.
    These tags affect aspects such as room size, layout density, and corridor behavior.
    """

    def __new__(cls, category: str, data):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)  # <- ensure unique int value
        obj.category = category
        obj.data = data
        return obj

    def __str__(self):
        return self.name

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
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
        if GenerationTag.SMALL_ROOMS in tags:
            return GenerationTag.SMALL_ROOMS.data
        if GenerationTag.LARGE_ROOMS in tags:
            return GenerationTag.LARGE_ROOMS.data
        return GenerationTag.MEDIUM_ROOMS.data

    @staticmethod
    def resolve_max_depth(tags: Set['GenerationTag']) -> int:
        if GenerationTag.SPARSE in tags:
            return GenerationTag.SPARSE.data
        if GenerationTag.DENSE in tags:
            return GenerationTag.DENSE.data
        return GenerationTag.MEDIUM.data

    @staticmethod
    def mutually_exclusive_groups() -> List[Set['GenerationTag']]:
        """
        Returns a list of sets, each containing tags that are mutually exclusive.
        """

        return [
            {GenerationTag.SMALL_ROOMS, GenerationTag.MEDIUM_ROOMS, GenerationTag.LARGE_ROOMS},
            {GenerationTag.DENSE, GenerationTag.SPARSE, GenerationTag.MEDIUM},
            {
                GenerationTag.ENTRANCE_EAST, GenerationTag.ENTRANCE_NORTH, GenerationTag.ENTRANCE_SOUTH,
                GenerationTag.ENTRANCE_WEST, GenerationTag.STAIRS
            },
            {
                GenerationTag.ANY, GenerationTag.ARCTIC, GenerationTag.COASTAL, GenerationTag.DESERT,
                GenerationTag.FOREST, GenerationTag.GRASSLAND, GenerationTag.HILL, GenerationTag.MOUNTAIN,
                GenerationTag.SWAMP, GenerationTag.UNDERDARK, GenerationTag.UNDERWATER, GenerationTag.URBAN,
                GenerationTag.BANDIT, GenerationTag.NECROMANCER, GenerationTag.KOBOLD, GenerationTag.GOBLIN,
                GenerationTag.GNOLL
            },
            {
                GenerationTag.STRAIGHT, GenerationTag.MAZE
            }
        ]

    @classmethod
    def toggle_tag(cls, active_tags: Set['GenerationTag'], new_tag: 'GenerationTag') -> Set['GenerationTag']:
        """
        Toggles a tag in the active set. If the tag is being added, any mutually exclusive
        tags are removed first. If it's already active, it is removed.

        Args:
            active_tags: Current set of selected tags.
            new_tag: The tag being toggled.

        Returns:
            Updated set of active tags.
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
    def make_full_set() -> Set['GenerationTag']:
        return {
            GenerationTag.MEDIUM_ROOMS, # Default to medium rooms
            GenerationTag.MEDIUM, # Default to normal room density
            random.choice(list(GenerationTag.mutually_exclusive_groups()[3])), # Select random entrance option
            random.choice(list(GenerationTag.mutually_exclusive_groups()[4])), # Select random theme
            GenerationTag.STRAIGHT # Default to straight hallways
        }
