import unittest
from PIL import Image
from dungeon_generator.generator import generate_basic_dungeon
from dungeon_generator.renderer import render_dungeon

class TestDungeonRenderer(unittest.TestCase):
    def test_dimensions(self):
        dungeon = generate_basic_dungeon(20, 20)
        image = render_dungeon(dungeon)
        self.assertIsInstance(image, Image.Image)
