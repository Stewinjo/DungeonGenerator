"""
Light Element

Defines the :class:`Light` dataclass representing a light source in the dungeon.
Lights include position, brightness levels, and optional color tint for VTT export.
"""
from typing import Optional
from dataclasses import dataclass

@dataclass
class Light:
    """
    Represents a light source to be placed on the dungeon map.

    :param x: The x-coordinate of the light source.
    :type x: int
    :param y: The y-coordinate of the light source.
    :type y: int
    :param dim: Radius of dim light emitted (default is 30).
    :type dim: int
    :param bright: Radius of bright light emitted (default is 10).
    :type bright: int
    :param color: Optional hex color of the light (e.g., "#ffffff").
    :type color: Optional[str]
    """
    x: int
    y: int
    dim: int = 30
    bright: int = 10
    color: Optional[str] = "#ffffff"
