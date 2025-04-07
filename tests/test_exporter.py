import unittest
import os
from dungeon_generator.generator import generate_basic_dungeon
from dungeon_generator.exporter import export_to_foundry_scene
from dungeon_generator.renderer import render_dungeon

class TestDungeonExporter(unittest.TestCase):
    def test_export_to_foundry(self):
        dungeon = generate_basic_dungeon(20, 20)
        render_dungeon(dungeon)

        # File paths
        folder = "./"
        img_path = os.path.join(folder, "dungeon.png")
        json_path = os.path.join(folder, "dungeon.scene.json")

        # Save image
        render_dungeon(dungeon).save(img_path)

        # Export scene JSON
        from dungeon_generator.renderer import TILE_SIZE
        walls = [w.to_foundry_dict() for w in dungeon.walls]
        lights = [l.to_foundry_dict() for l in dungeon.lights]
        notes = [n.to_foundry_dict() for n in dungeon.notes]
        tiles = [t.to_foundry_dict() for t in dungeon.tiles]

        export_to_foundry_scene(
            scene_name="Test Dungeon",
            background_image_path=os.path.basename(img_path),  # relative path
            width=dungeon.width * TILE_SIZE,
            height=dungeon.height * TILE_SIZE,
            grid_size=TILE_SIZE,
            walls=walls,
            lights=lights,
            notes=notes,
            tiles=tiles,
            output_path=json_path
        )

        # Assertions
        self.assertTrue(os.path.exists(img_path))
        self.assertTrue(os.path.exists(json_path))

        # Cleanup
        os.remove(img_path)
        os.remove(json_path)
