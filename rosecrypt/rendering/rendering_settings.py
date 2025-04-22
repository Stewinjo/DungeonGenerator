"""
Rendering Settings Module

Defines configurable parameters used during dungeon rendering, including
tile size, wall thickness, frame dimensions, and visual tags for aging effects.
"""

from dataclasses import dataclass
from typing import Set
from rosecrypt.rendering.style import DungeonStyle
from rosecrypt.rendering.enums.rendering_tag import RenderingTag

@dataclass
class RenderingSettings:
    """
    Rendering configuration used to control visual output during dungeon rendering.

    Includes tunable constants for tile and wall dimensions, brick generation ranges,
    and styling preferences.

    :param seed: Seed string for consistent randomization.
    :type seed: str
    :param tags: A set of rendering tags that influence visual features like aging.
    :type tags: Set[RenderingTag]
    :param style: A DungeonStyle object specifying visual colors and materials.
    :type style: DungeonStyle
    """
    TILE_SIZE = 100
    WALL_THICKNESS = 5
    GRID_DOT_SIZE = 2
    BORDER = 2
    FRAME_SIZE = TILE_SIZE // 8
    BRICK_MIN_WIDTH = FRAME_SIZE * 2 + 10
    BRICK_MAX_WIDTH = BRICK_MIN_WIDTH + 20
    BRICK_MIN_HEIGHT = FRAME_SIZE * 2 + 10
    BRICK_MAX_HEIGHT = BRICK_MIN_HEIGHT + 20

    def __init__(self, seed: str, tags: Set[RenderingTag], style: DungeonStyle = DungeonStyle()):
        self.seed = seed
        self.tags = tags
        self.style = style

    @classmethod
    def from_gui(
            cls,
            seed: str,
            tags: Set[RenderingTag]
    ) -> 'RenderingTag':
        """
        Constructs a RenderingSettings object from GUI inputs.

        :param seed: The seed string used to initialize randomness.
        :type seed: str
        :param tags: A set of rendering tags selected in the GUI.
        :type tags: Set[RenderingTag]
        :return: A fully populated RenderingSettings instance.
        :rtype: RenderingSettings
        """
        settings = cls(seed=seed, tags=tags)
        return settings
