"""
Dungeon Exporting Module

This module provides the :class:`DungeonExporter`, responsible for exporting
generated dungeons to external formats such as Foundry VTT scene files.

The export includes map images and structured JSON content to enable use
within virtual tabletops. Wall, door, and padding metadata are formatted
specifically for Foundry's expected scene schema.
"""

import json
import os
from typing import List, Tuple

from rosecrypt.dungeon import Dungeon
from rosecrypt.elements.wall_segment import WallSegment
from rosecrypt.elements.door import Door
from rosecrypt.logger import setup_logger
from rosecrypt.rendering.dungeon_renderer import DungeonRenderer
from rosecrypt.exporting.exporter_settings import ExporterSettings

log = setup_logger(__name__, category="Exporting")

#pylint: disable=too-few-public-methods
class DungeonExporter:
    """
    Exports a dungeon object into Foundry VTT-compatible formats.

    :param dungeon: The dungeon to export.
    :type dungeon: Dungeon
    :param exporter_settings: Settings for export configuration, including rendering options.
    :type exporter_settings: ExporterSettings
    """

    def __init__(self, dungeon: Dungeon, exporter_settings: ExporterSettings):
        self.dungeon = dungeon
        self.exporter_settings = exporter_settings

    def _calculate_offset(self, grid_size: int, padding_percent: float) -> Tuple[int, int]:
        """
        Calculates a pixel offset used for applying padding around the dungeon grid.

        :param grid_size: The size of a single grid tile in pixels.
        :type grid_size: int
        :param padding_percent: The padding percentage (relative to grid dimensions).
        :type padding_percent: float

        :return: Tuple of (x_offset, y_offset) in pixels.
        :rtype: Tuple[int, int]
        """
        offset_pixels = int(
            padding_percent * grid_size * max(self.dungeon.width, self.dungeon.height)
            )
        return offset_pixels, offset_pixels

    @staticmethod
    def _walls_to_foundry_format(
        walls: List[WallSegment],
        grid_size: int,
        offset: Tuple[int, int]
        ) -> List[dict]:
        """
        Converts a list of wall segments to Foundry-compatible wall dictionaries.

        :param walls: List of wall segments to convert.
        :type walls: List[WallSegment]
        :param grid_size: Size of one tile in pixels.
        :type grid_size: int
        :param offset: Tuple representing x and y pixel offsets for padding.
        :type offset: Tuple[int, int]

        :return: List of wall objects formatted for Foundry VTT scene JSON.
        :rtype: List[dict]
        """
        ox, oy = offset
        foundry_walls = [
            {
                "c": [
                    w.x1 * grid_size + ox,
                    w.y1 * grid_size + oy,
                    w.x2 * grid_size + ox,
                    w.y2 * grid_size + oy,
                ],
                "door": w.door,
                "ds": w.ds,
                "move": w.move,
                "sense": w.sense,
                "sound": w.sound,
                "light": w.light,
                "flags": {}
            }
            for w in walls
        ]

        # Add dummy wall at (0, 0) to anchor Foundry's origin
        dummy_wall = {
            "c": [ox, oy, ox, oy + int(grid_size * 0.1)],
            "door": 0,
            "ds": 0,
            "move": 0,
            "sense": 0,
            "sound": 0,
            "light": 0,
            "flags": {}
        }
        foundry_walls.insert(0, dummy_wall)

        return foundry_walls

    @staticmethod
    def _doors_to_foundry_format(
        doors: List[Door],
        grid_size: int,
        offset: Tuple[int, int]
        ) -> List[dict]:
        """
        Converts a list of Door objects into Foundry wall-format entries by turning
        them into short wall segments.

        :param doors: List of Door elements from the dungeon.
        :type doors: List[Door]
        :param grid_size: Pixel size of each tile.
        :type grid_size: int
        :param offset: Tuple of pixel offset (x, y).
        :type offset: Tuple[int, int]

        :return: List of Foundry-compatible wall entries representing doors.
        :rtype: List[dict]
        """
        return DungeonExporter._walls_to_foundry_format(
            [ d.door_to_wall() for d in doors],
            grid_size, offset
            )


    # @staticmethod
    # def _notes_to_foundry_format(notes: List[Note], grid_size: int) -> List[dict]:
    #     return [
    #         {
    #             "x": n.x * grid_size,
    #             "y": n.y * grid_size,
    #             "iconSize": 40,
    #             "iconTint": None,
    #             "text": n.text,
    #             "fontFamily": "Signika",
    #             "fontSize": 48,
    #             "textColor": "#FFFFFF",
    #             "flags": {},
    #         }
    #         for n in notes
    #     ]

    # @staticmethod
    # def _lights_to_foundry_format(lights: List[Light], grid_size: int) -> List[dict]:
    #     return [
    #         {
    #             "x": l.x * grid_size,
    #             "y": l.y * grid_size,
    #             "rotation": 0,
    #             "dim": l.dim_radius * grid_size,
    #             "bright": l.bright_radius * grid_size,
    #             "angle": 360,
    #             "color": l.color,
    #             "alpha": 0.25,
    #             "flags": {},
    #         }
    #         for l in lights
    #     ]

    # @staticmethod
    # def _tiles_to_foundry_format(tiles: List[Tile], grid_size: int) -> List[dict]:
    #     return [
    #         {
    #             "img": t.image_path,
    #             "x": t.x * grid_size,
    #             "y": t.y * grid_size,
    #             "width": t.width * grid_size,
    #             "height": t.height * grid_size,
    #             "z": 100,
    #             "rotation": 0,
    #             "hidden": False,
    #             "locked": False,
    #             "flags": {},
    #         }
    #         for t in tiles
    #     ]

    # @staticmethod
    # def _sounds_to_foundry_format(sounds: List[Sound], grid_size: int) -> List[dict]:
    #     return [
    #         {
    #             "x": s.x * grid_size,
    #             "y": s.y * grid_size,
    #             "radius": s.radius * grid_size,
    #             "path": s.audio_path,
    #             "flags": {},
    #         }
    #         for s in sounds
    #     ]

    def export_to_foundry_scene(self, folder: str) -> List[str]:
        """
        Exports the dungeon to a Foundry VTT-compatible scene.

        The export includes:
            - Rendered dungeon image (PNG)
            - Scene JSON with metadata, wall/door geometry, and Foundry-specific flags

        :param folder: Output directory for the exported scene files.
        :type folder: str
        """
        os.makedirs(folder, exist_ok=True)

        image_path = os.path.join(folder, f"{self.dungeon.name.lower()}.png")
        renderer = DungeonRenderer(self.dungeon, self.exporter_settings.rendering_settings)
        image = renderer.render_dungeon()
        image.save(image_path)

        grid_size = self.exporter_settings.rendering_settings.TILE_SIZE

        offset = self._calculate_offset(grid_size, self.exporter_settings.foundry_padding)
        walls = self._walls_to_foundry_format(self.dungeon.walls, grid_size, offset)
        doors = self._doors_to_foundry_format(self.dungeon.doors, grid_size, offset)
        # notes = _notes_to_foundry_format(self.dungeon.notes, grid_size)
        # lights = _lights_to_foundry_format(self.dungeon.lights, grid_size)
        # tiles = _tiles_to_foundry_format(self.dungeon.tiles, grid_size)
        # sounds = _sounds_to_foundry_format(self.dungeon.sounds, grid_size)

        scene = {
            "name": self.dungeon.name,
            "navigation": True,
            "navOrder": 0,
            "navName": "Unknown Dungeon",
              "background": {
                "src": f"{self.dungeon.name}.png",
                "anchorX": 0,
                "anchorY": 0,
                "offsetX": 0,
                "offsetY": 0,
                "fit": "fill",
                "scaleX": 1,
                "scaleY": 1,
                "rotation": 0,
                "tint": "#ffffff",
                "alphaThreshold": 0
            },
            "foreground": None,
            "foregroundElevation": 20,
            "thumb": None,
            "width": self.dungeon.width * grid_size,
            "height": self.dungeon.height * grid_size,
            "padding": self.exporter_settings.foundry_padding,
            "initial": {
                "x": 3767,
                "y": 3086,
                "scale": 0.3162075235608918
            },
            "backgroundColor": "#999999",
            "grid": {
                "type": 1,
                "size": grid_size,
                "style": "solidLines",
                "thickness": 1,
                "color": "#000000",
                "alpha": 0,
                "distance": 5,
                "units": "ft"
            },
            "tokenVision": True,
            "fog": {
                "exploration": True,
                "overlay": None,
                "colors": {
                "explored": None,
                "unexplored": None
                },
                "reset": 0
            },
              "environment": {
                "darknessLevel": 0.35,
                "darknessLock": False,
                "globalLight": {
                    "enabled": False,
                    "alpha": 0.5,
                    "bright": False,
                    "color": None,
                    "coloration": 1,
                    "luminosity": 0,
                    "saturation": 0,
                    "contrast": 0,
                    "shadows": 0,
                    "darkness": {
                        "min": 0,
                        "max": 0
                    }
                },
                "cycle": True,
                "base": {
                    "hue": 0,
                    "intensity": 0,
                    "luminosity": 0,
                    "saturation": 0,
                    "shadows": 0
                },
                "dark": {
                    "hue": 0.7138888888888889,
                    "intensity": 0,
                    "luminosity": -0.25,
                    "saturation": 0,
                    "shadows": 0
                }
            },
            "drawings": [],
            "tokens": [],
            "lights": [],
            "notes": [],
            "sounds": [],
            "regions": [],
            "templates": [],
            "tiles": [],
            "walls": walls + doors,
            "playlist": None,
            "playlistSound": None,
            "journal": None,
            "journalEntryPage": None,
            "weather": "",
            "folder": None,
            "flags": {},
        }

        json_path = os.path.join(folder, f"{self.dungeon.name.lower()}_scene.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(scene, f, indent=2)

        log.info("Foundry scene exported to %s", json_path)
        log.info("Foundry image exported to %s", image_path)

        return [image_path, json_path]
