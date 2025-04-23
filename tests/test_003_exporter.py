"""
Unit tests for the DungeonExporter class.

This test verifies that a procedurally generated dungeon can be successfully
exported to Foundry VTT's format, including both the scene JSON and image file.
"""

import unittest
import os
import uuid

from rosecrypt.logger import setup_logger
from rosecrypt.generation.dungeon_generator import DungeonGenerator, GenerationSettings
from rosecrypt.generation.enums.generation_tag import GenerationTag
from rosecrypt.exporting.dungeon_exporter import DungeonExporter, ExporterSettings
from rosecrypt.rendering.dungeon_renderer import RenderingSettings
from rosecrypt.rendering.enums.rendering_tag import RenderingTag

log = setup_logger(__name__, category="Exporting")

class TestDungeonExporter(unittest.TestCase):
    """
    Test case for validating the Foundry export functionality of a generated dungeon.

    Ensures that the DungeonExporter correctly outputs a PNG image and JSON scene file
    that meet Foundry VTT's expected structure and naming conventions.
    """

    def test_export_to_foundry(self):
        """
        Generates a dungeon, exports it using DungeonExporter, and verifies that
        both the PNG and JSON files are created.

        Cleans up all generated files after the test completes.
        """
        # Setup export folder
        export_folder = "./.test_export"
        os.makedirs(export_folder, exist_ok=True)

        # Generate dungeon with dummy settings
        width, height = 20, 20
        seed = uuid.uuid4().hex[:8]
        log.info(
            "Trying to export dungeon with seed %s (%s, %s)",
            seed,
            width,
            height
            )

        generation_tags = GenerationTag.make_full_set()
        generation_settings = GenerationSettings.from_gui(width, height, seed, generation_tags)
        dungeon = DungeonGenerator(generation_settings).generate_dungeon(width, height)
        dungeon.name = "ExporterTestDungeon"

        # Export using DungeonExporter
        rendering_tags= RenderingTag.make_full_set()
        render_settings= RenderingSettings(seed, rendering_tags)
        exporter = DungeonExporter(dungeon, ExporterSettings(render_settings))
        exporter.export_to_foundry_scene(export_folder)

        # Check outputs
        image_path = os.path.join(export_folder, f"{dungeon.name.lower()}.png")
        json_path = os.path.join(export_folder, f"{dungeon.name.lower()}_scene.json")

        self.assertTrue(os.path.exists(image_path), f"Missing dungeon image: {image_path}")
        self.assertTrue(os.path.exists(json_path), f"Missing dungeon scene JSON: {json_path}")

        # Cleanup
        os.remove(image_path)
        os.remove(json_path)
        os.rmdir(export_folder)
