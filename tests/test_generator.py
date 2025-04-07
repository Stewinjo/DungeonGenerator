"""
Unit tests for the dungeon generation logic.

This module verifies the structural integrity of the generated dungeon grid.
"""

import unittest
from dungeon_generator.generator import generate_basic_dungeon

class TestDungeonGenerator(unittest.TestCase):
    """Tests for validating the dungeon generation process."""

    def test_dimensions(self):
        """Ensure the generated dungeon grid has the correct width and height."""

        dungeon = generate_basic_dungeon(100, 100)
        self.assertEqual(len(dungeon.grid), 100)
        self.assertEqual(len(dungeon.grid[0]), 100)
