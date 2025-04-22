"""
Unit tests for the dungeon rendering system.

This module verifies that the dungeon renderer produces valid image outputs
from generated dungeon structures using default rendering settings.
"""

import unittest
import uuid
from PIL import Image
from rosecrypt.generation.dungeon_generator import DungeonGenerator, GenerationSettings
from rosecrypt.generation.enums.generation_tag import GenerationTag
from rosecrypt.rendering.dungeon_renderer import DungeonRenderer
from rosecrypt.rendering.rendering_settings import RenderingSettings
from rosecrypt.rendering.enums.rendering_tag import RenderingTag

class TestDungeonRenderer(unittest.TestCase):
    """
    Test case for verifying the functionality of the dungeon renderer.

    Ensures that the renderer produces valid image outputs compatible with PIL.
    """

    def test_render_returns_pil_image(self):
        """
        Tests that rendering a dungeon returns a valid PIL Image instance.

        Verifies the output type after rendering a small dungeon with default settings.
        """

        width, height = 40, 40
        seed = uuid.uuid4().hex[:8]
        generation_tags = GenerationTag.make_full_set()
        generation_settings = GenerationSettings.from_gui(width, height, seed, generation_tags)
        dungeon = DungeonGenerator(generation_settings).generate_dungeon(width, height)
        dungeon.name = "RendererTestDungeon"

        rendering_tags= RenderingTag.make_full_set()
        render_settings= RenderingSettings(seed, rendering_tags)

        image = DungeonRenderer(dungeon, render_settings).render_dungeon()

        self.assertIsInstance(image, Image.Image)
