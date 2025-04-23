"""
Enumeration of door types used in dungeon rendering and export.

Each type corresponds to a material with visual and mechanical
implications during rendering and gameplay export.
"""

from enum import Enum, auto

class DoorType(Enum):
    """
    Enum representing supported door materials.

    Values:
        GLASS: Transparent or decorative door, usually fragile.
        METAL: Reinforced or barred door, often used in secure areas.
        STONE: Heavy, immovable doors, typically ancient or arcane.
        WOOD: Default door type, moderately durable and common.
    """

    GLASS = auto()
    METAL = auto()
    STONE = auto()
    WOOD = auto()
