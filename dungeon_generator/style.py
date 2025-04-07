from dataclasses import dataclass, field
from colour import Color
from dungeon_generator.elements import DoorType

@dataclass
class DungeonStyle:
    # Materials
    paper_color: Color = field(default_factory=lambda: Color("#E5E2CF"))   # Background (non-tile area)
    ink_color: Color = field(default_factory=lambda: Color("#2C241D"))     # Reserved for text/labels
    water_color: Color = field(default_factory=lambda: Color("#5B9698"))   # Reserved for water tiles
    wood_color: Color = field(default_factory=lambda: Color("#A37143"))    # Medium warm wood tone
    stone_color: Color = field(default_factory=lambda: Color("#BFBEB6"))   # Wall segments
    glass_color: Color = field(default_factory=lambda: Color("#A87C5F"))   # Warm brown (glass door)
    metal_color: Color = field(default_factory=lambda: Color("#888A8C"))   # Cold steel gray

    # General theme
    floor_color: Color = field(default_factory=lambda: Color("#D9D5C3"))
    wall_color: Color = field(init=False)

    # Color mappings (initialized in __post_init__)
    door_colors: dict = field(init=False)
    frame_colors: dict = field(init=False)

    def __post_init__(self):
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
