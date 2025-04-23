"""
This module defines the RoomType enumeration used in dungeon generation.

RoomType represents the functional role of a room within the dungeon layout.
It can be used to mark special-purpose rooms like entrances, boss chambers, treasure vaults, etc.
"""

from enum import Enum, auto

class RoomType(Enum):
    """
    Enum representing different types of rooms in a dungeon.

    Attributes:
        ENTRANCE: Marks the room as a dungeon entrance. Used for placement and routing logic.
    """

    ENTRANCE = auto()
