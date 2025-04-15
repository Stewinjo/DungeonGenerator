import unittest
import os
import uuid
from dungeon_generator.generator import generate_dungeon, GenerationSettings
from dungeon_generator.enums import GenerationTag
from dungeon_generator.exporter import DungeonExporter
from dungeon_generator.renderer import TILE_SIZE

class TestDungeonExporter(unittest.TestCase):
    """
    Test exporting a dungeon to Foundry VTT format using DungeonExporter.
    """

    def test_export_to_foundry(self):
        """
        Generate a dungeon and test exporting the scene and image files.
        """
        # Setup export folder
        export_folder = "./.test_export"
        os.makedirs(export_folder, exist_ok=True)

        # Generate dungeon with dummy settings
        width = 20
        height = 20
        seed = uuid.uuid4().hex[:8]
        tags = GenerationTag.make_full_set()
        settings = GenerationSettings.from_gui(width, height, seed, tags)
        dungeon = generate_dungeon(width, height, settings)
        dungeon.name = "TestDungeon"

        # Export using DungeonExporter
        exporter = DungeonExporter(dungeon)
        exporter.export_to_foundry_scene(export_folder)

        # Check outputs
        image_path = os.path.join(export_folder, "TestDungeon.png")
        json_path = os.path.join(export_folder, "TestDungeon_scene.json")

        self.assertTrue(os.path.exists(image_path), f"Missing dungeon image: {image_path}")
        self.assertTrue(os.path.exists(json_path), f"Missing dungeon scene JSON: {json_path}")

        # Cleanup
        os.remove(image_path)
        os.remove(json_path)
        os.rmdir(export_folder)
