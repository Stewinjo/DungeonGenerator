"""
Dungeon Style Module

Defines the DungeonStyle class, which centralizes all visual styling information
used during dungeon rendering. This includes colors for floors, walls, doors, and
materials like wood, stone, metal, and glass. It also provides mappings from
DoorType enums to their associated fill and frame colors.

This style configuration ensures consistent rendering aesthetics across all visual
components of the dungeon.
"""

from dataclasses import dataclass, field
from colour import Color
from rosecrypt.generation.enums.door_type import DoorType

#pylint: disable=too-many-instance-attributes
@dataclass
class DungeonStyle:
    """
    A configuration class that defines the visual style of the dungeon rendering.

    This class contains color definitions for various dungeon elements such as floor,
    walls, doors, and water. It also sets up color mappings used during rendering
    to style doors and their frames based on their type.

    Attributes:
        paper_color (Color): The background color for areas outside the dungeon.
        ink_color (Color): The primary color for outlines, text, and decorative elements.
        water_color (Color): The fill color for water areas (not currently used).
        wood_color (Color): The color used for wooden doors and accents.
        stone_color (Color): The base color for walls and stone doors.
        glass_color (Color): The color used for glass doors.
        metal_color (Color): The color used for metallic doors.
        floor_color (Color): The color of walkable dungeon tiles.
        wall_color (Color): The default wall color, set to stone_color.
        door_colors (dict): Maps DoorType to their visual fill color.
        frame_colors (dict): Maps DoorType to the color of their frame.
    """

    # Materials
    paper_color: Color = field(
        default_factory=lambda: Color("#E5E2CF")
        )   # Background (non-tile area)
    ink_color: Color = field(
        default_factory=lambda: Color("#2C241D")
        )     # Reserved for text/labels
    water_color: Color = field(
        default_factory=lambda: Color("#5B9698")
        )   # Reserved for water tiles
    wood_color: Color = field(
        default_factory=lambda: Color("#A37143")
        )    # Medium warm wood tone
    stone_color: Color = field(
        default_factory=lambda: Color("#BFBEB6")
        )   # Wall segments
    glass_color: Color = field(
        default_factory=lambda: Color("#A87C5F")
        )   # Warm brown (glass door)
    metal_color: Color = field(
        default_factory=lambda: Color("#888A8C")
        )   # Cold steel gray

    # General theme
    floor_color: Color = field(default_factory=lambda: Color("#D9D5C3"))
    wall_color: Color = field(init=False)

    # Color mappings (initialized in __post_init__)
    door_colors: dict = field(init=False)
    frame_colors: dict = field(init=False)

    def __post_init__(self):
        """
        Initializes derived attributes after the dataclass is constructed.

        Sets the wall color to match the stone color, and defines the color
        mappings for door fills and frames based on the DoorType enum.
        """

        # Use the stone_color for walls by default
        self.wall_color = self.stone_color

        self.door_colors = {
            DoorType.GLASS: self.glass_color,
            DoorType.WOOD: self.wood_color,
            DoorType.METAL: self.metal_color,
            DoorType.STONE: self.stone_color,
        }

        self.frame_colors = {
            DoorType.GLASS: self.stone_color,
            DoorType.WOOD: self.wood_color,
            DoorType.METAL: self.stone_color,
            DoorType.STONE: self.stone_color,
        }
