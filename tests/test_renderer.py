import unittest
from PIL import Image
from dungeon_generator.generator import generate_dungeon, GenerationSettings
from dungeon_generator.renderer import render_dungeon
from dungeon_generator.enums import GenerationTag

class TestDungeonRenderer(unittest.TestCase):
    """Tests for verifying the dungeon renderer's output format."""

    def test_render_returns_pil_image(self):
        """Ensure that rendering a generated dungeon returns a valid PIL Image."""

        width, height = 20, 20
        settings = GenerationSettings.from_gui(
            width=width,
            height=height,
            seed="render-test",
            tags=GenerationTag.make_full_set()
        )

        dungeon = generate_dungeon(width, height, settings)
        image = render_dungeon(dungeon)

        self.assertIsInstance(image, Image.Image)
