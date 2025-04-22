from enum import Enum, auto

class DoorType(Enum):
    """
    Enumeration of supported door types.
    Used to determine door appearance and interaction behavior.
    """

    GLASS = auto()
    METAL = auto()
    STONE = auto()
    WOOD = auto()
