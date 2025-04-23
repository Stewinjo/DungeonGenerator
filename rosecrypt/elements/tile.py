"""
Tile Element

Defines the :class:`Tile` dataclass used to represent background image tiles in the dungeon scene.
These tiles are placed on the canvas for visual decoration or structural guidance.
"""

from dataclasses import dataclass

@dataclass
class Tile:
    """
    Represents a background image tile used in the dungeon.

    :param x: The x-coordinate of the tile.
    :type x: int
    :param y: The y-coordinate of the tile.
    :type y: int
    :param width: The width of the tile in grid units.
    :type width: int
    :param height: The height of the tile in grid units.
    :type height: int
    :param img: The file path to the image used as the tile background.
    :type img: str
    """
    x: int
    y: int
    width: int
    height: int
    img: str
