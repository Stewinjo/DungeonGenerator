"""
Generation Enums Package

Contains enums specific to dungeon generation behavior, such as room types,
door types, and generation tags. These enums define behavior and user-configurable
options for the generation system.
"""

from rosecrypt.generation.enums.generation_tag import GenerationTag
from rosecrypt.generation.enums.room_type import RoomType
from rosecrypt.generation.enums.door_type import DoorType

__all__ = ["GenerationTag", "RoomType", "DoorType"]
