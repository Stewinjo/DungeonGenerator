import unittest
from dungeon_generator.generator import generate_basic_dungeon

class TestDungeonGenerator(unittest.TestCase):
    def test_dimensions(self):
        dungeon = generate_basic_dungeon(100, 100)
        self.assertEqual(len(dungeon.grid), 100)
        self.assertEqual(len(dungeon.grid[0]), 100)
