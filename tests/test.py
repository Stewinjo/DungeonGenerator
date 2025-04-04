import unittest
from dungeon_generator.generator import generate_dungeon
from dungeon_generator.exporter import export_to_uvtt
import os

class TestDungeonGenerator(unittest.TestCase):

    def test_generate_dungeon(self):
        dungeon = generate_dungeon(50, 50)
        self.assertEqual(dungeon.shape, (50, 50))
        # Add more assertions related to dungeon properties

    def test_export_to_uvtt(self):
        dungeon = generate_dungeon(50, 50)
        export_to_uvtt(dungeon, 'test_image.png', 'test_output.uvtt')
        self.assertTrue(os.path.exists('test_output.uvtt'))
        # Clean up
        os.remove('test_output.uvtt')

if __name__ == '__main__':
    unittest.main()
