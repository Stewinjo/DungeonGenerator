"""
Unit tests for dungeon generation and rendering.

This module tests the integration between dungeon generation and image rendering,
ensuring the output is a valid PIL image.
"""

import unittest
from PIL import Image
from dungeon_generator.generator import generate_basic_dungeon
from dungeon_generator.renderer import render_dungeon

class TestDungeonRenderer(unittest.TestCase):
    """Tests for verifying the dungeon renderer's output format."""

    def test_dimensions(self):
        """Ensure that rendering a generated dungeon returns a valid PIL Image."""

        dungeon = generate_basic_dungeon(20, 20)
        image = render_dungeon(dungeon)
        self.assertIsInstance(image, Image.Image)
