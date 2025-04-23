"""
Rendering Tag Enumeration

This module defines the RenderingTag enum, which controls visual styles and
weathering effects applied during dungeon rendering. Tags influence the
appearance of aging, such as crack density or texture wear.
"""

from enum import Enum
from typing import Set, List, Optional

class RenderingTag(Enum):
    """
    Enum representing rendering options that control visual aging effects.

    Each tag has an associated category and metadata. Only one tag per category
    can be active at a time due to mutual exclusivity.

    Attributes:
        category (str): The category this tag belongs to (e.g., "Aging").
        data (tuple): Metadata describing crack frequency and branch density.
    """
    def __new__(cls, category: str, data):
        """
        Creates a new RenderingTag instance with a unique value and attached metadata.

        :param category: The category of the tag.
        :type category: str
        :param data: Associated tag data (e.g., aging intensity).
        :type data: any
        :return: A new RenderingTag instance.
        :rtype: RenderingTag
        """
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)  # <- ensure unique int value
        obj.category = category
        obj.data = data
        return obj

    def __str__(self):
        """
        Returns the name of the tag as its string representation.

        :return: Name of the tag.
        :rtype: str
        """
        return self.name

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
    def get_tag_by_category(tags: Set['RenderingTag'], category: str) -> Optional['RenderingTag']:
        """
        Retrieves the tag belonging to the given category from a set of tags.

        :param tags: The set of tags to search.
        :type tags: Set[RenderingTag]
        :param category: The category to search for.
        :type category: str
        :return: The matching tag, or None if not found.
        :rtype: Optional[RenderingTag]
        """
        for tag in tags:
            if tag.category == category:
                return tag
        return None

    @classmethod
    def toggle_tag(
        cls,
        active_tags: Set['RenderingTag'],
        new_tag: 'RenderingTag'
        ) -> Set['RenderingTag']:
        """
        Toggles the presence of a tag in the active set, enforcing mutual exclusivity.

        If the new tag is already present, it is removed. Otherwise, it replaces
        any existing tags from the same mutually exclusive group.

        :param active_tags: Currently selected tags.
        :type active_tags: Set[RenderingTag]
        :param new_tag: Tag to toggle.
        :type new_tag: RenderingTag
        :return: Updated set of tags.
        :rtype: Set[RenderingTag]
        """

        updated = set(active_tags)
        if new_tag in updated:
            updated.remove(new_tag)
        else:
            for group in cls.mutually_exclusive_groups():
                if new_tag in group:
                    updated -= group
            updated.add(new_tag)
        return updated

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
