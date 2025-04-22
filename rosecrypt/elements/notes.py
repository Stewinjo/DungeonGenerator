"""
Note Element

Defines the :class:`Note` dataclass used to represent annotation markers on the dungeon grid.
These notes are exportable to Foundry VTT and can display tooltips or icons in-game.
"""

from dataclasses import dataclass


@dataclass
class Note:
    """
    Represents a note or annotation to be displayed in the dungeon.

    :param x: The x-coordinate of the note.
    :type x: int
    :param y: The y-coordinate of the note.
    :type y: int
    :param text: The tooltip text or annotation content.
    :type text: str
    :param icon: The icon path used for this note (default is "icons/svg/book.svg").
    :type icon: str
    :param icon_size: The icon's display size in pixels (default is 40).
    :type icon_size: int
    """
    x: int
    y: int
    text: str
    icon: str = "icons/svg/book.svg"
    icon_size: int = 40
