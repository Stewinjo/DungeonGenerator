"""
Unit tests for the dungeon generation process.

This module tests that dungeons generated using the procedural generator
have correct dimensions and conform to basic structural expectations.
"""

import unittest
import uuid

from rosecrypt.logger import setup_logger
from rosecrypt.generation.dungeon_generator import DungeonGenerator, GenerationSettings
from rosecrypt.generation.enums.generation_tag import GenerationTag

log = setup_logger(__name__, category="Generation")

class TestDungeonGenerator(unittest.TestCase):
    """
    Test case for verifying procedural dungeon generation.

    Ensures the generator produces a dungeon with correct grid dimensions
    and basic integrity using default generation tags and a fixed seed.
    """

    def test_dimensions(self):
        """
        Tests that the generated dungeon has a grid matching the specified dimensions.

        Ensures the width and height of the dungeon match the provided input values.
        """

        width, height = 100, 100
        seed = uuid.uuid4().hex[:8]
        log.info(
            "Trying to generate dungeon with seed %s (%s, %s)",
            seed,
            width,
            height
            )

        settings = GenerationSettings.from_gui(
            width=width,
            height=height,
            seed=seed,
            tags=GenerationTag.make_full_set()
        )

        dungeon = DungeonGenerator(settings).generate_dungeon(width, height)

        self.assertEqual(len(dungeon.grid), height)
        self.assertEqual(len(dungeon.grid[0]), width)
