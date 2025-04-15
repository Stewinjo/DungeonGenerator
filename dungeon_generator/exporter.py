"""
Dungeon Exporting Module

This module contains functions to export dungeon data to various formats.
"""

import json
import os
from typing import List, Dict, Tuple
from PIL import Image
from .renderer import render_dungeon, TILE_SIZE
from .dungeon import Dungeon
from .elements import WallSegment, Door

class DungeonExporter:
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon

    def _calculate_offset(self, grid_size: int, padding_percent: float) -> Tuple[int, int]:
        offset_pixels = int(padding_percent * grid_size * max(self.dungeon.width, self.dungeon.height))
        return offset_pixels, offset_pixels

    @staticmethod
    def _walls_to_foundry_format(walls: List[WallSegment], grid_size: int, offset: Tuple[int, int]) -> List[dict]:
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
    def _doors_to_foundry_format(doors: List[Door], grid_size: int, offset: Tuple[int, int]) -> List[dict]:
        return DungeonExporter._walls_to_foundry_format([ d.door_to_wall() for d in doors], grid_size, offset)

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

    def export_to_foundry_scene(
        self,
        folder: str,
        grid_size: int = TILE_SIZE,
    ):
        """
        Exports the dungeon to a FoundryVTT-compatible scene JSON file, along with a rendered background image.

        :param folder: Folder path to export JSON and image.
        :param grid_size: Grid size in pixels.
        """
        os.makedirs(folder, exist_ok=True)

        image_path = os.path.join(folder, f"{self.dungeon.name}.png")
        image = render_dungeon(self.dungeon)
        image.save(image_path)

        padding: float = 0.25

        offset = self._calculate_offset(grid_size, padding)
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
            "padding": padding,
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

        json_path = os.path.join(folder, f"{self.dungeon.name}_scene.json")
        with open(json_path, "w") as f:
            json.dump(scene, f, indent=2)

        print(f"[✓] Foundry scene exported to {json_path}")
