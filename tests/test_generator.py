import unittest
from dungeon_generator.generator import generate_dungeon, GenerationSettings
from dungeon_generator.enums import GenerationTag

class TestDungeonGenerator(unittest.TestCase):
    """Tests for validating the dungeon generation process."""

    def test_dimensions(self):
        """Ensure the generated dungeon grid has the correct width and height."""

        width = 100
        height = 100
        settings = GenerationSettings.from_gui(
            width=width,
            height=height,
            seed="testseed",
            tags=GenerationTag.make_full_set()
        )

        dungeon = generate_dungeon(width, height, settings)

        self.assertEqual(len(dungeon.grid), height)
        self.assertEqual(len(dungeon.grid[0]), width)
