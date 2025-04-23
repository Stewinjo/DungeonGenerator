"""
Rendering Tag Enumeration

This module defines the RenderingTag enum, which controls visual styles and
weathering effects applied during dungeon rendering. Tags influence the
appearance of aging, such as crack density or texture wear.
"""

from typing import Set, List
from rosecrypt.enums import Tag

class RenderingTag(Tag):
    """
    Enum representing rendering options that control visual aging effects.

    Each tag has an associated category and metadata. Only one tag per category
    can be active at a time due to mutual exclusivity.

    Attributes:
        category (str): The category this tag belongs to (e.g., "Aging").
        data (tuple): Metadata describing crack frequency and branch density.
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """
        Overrides the default behavior for auto-assigned enum values.

        This method ensures each enum value receives a unique, sequential integer
        regardless of category or data structure. The value is simply set to the
        number of already defined members (i.e., `count`), ensuring predictable ordering.

        Args:
            name (str): The name of the enum member.
            start (Any): The initial value (unused here).
            count (int): The number of previously defined members.
            last_values (List[Any]): A list of previous values.

        Returns:
            int: A unique integer value for the enum member.
        """
        return count  # Ensure safe int values for all auto() fields

    # Aging levels returning chance of cracks and chance of crack branches
    YOUNG = ("Aging", (0.1, 0.3))
    OLD = ("Aging", (0.2, 0.4))
    ANCIENT = ("Aging", (0.3, 0.5))

    @staticmethod
    def mutually_exclusive_groups() -> List[Set['RenderingTag']]:
        """
        Returns sets of tags that are mutually exclusive within their category.

        :return: A list of mutually exclusive tag groups.
        :rtype: List[Set[RenderingTag]]
        """

        return [
            {RenderingTag.YOUNG, RenderingTag.OLD, RenderingTag.ANCIENT}
        ]

    @staticmethod
    def make_full_set() -> Set['RenderingTag']:
        """
        Returns a default rendering tag set, used to initialize new scenes.

        :return: Default tag set.
        :rtype: Set[RenderingTag]
        """
        return {
            RenderingTag.OLD # Default to old/medium aging
        }
