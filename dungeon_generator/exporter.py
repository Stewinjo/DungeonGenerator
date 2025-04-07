"""
Dungeon Exporting Module

This module contains functions to export dungeon data to various formats.
"""

import json
import os
from typing import List, Dict, Any
from .renderer import render_dungeon
from .dungeon import Dungeon


def export_to_foundry_scene(
    scene_name: str,
    background_image_path: str,
    width: int,
    height: int,
    grid_size: int,
    walls: List[Dict[str, Any]] = None,
    lights: List[Dict[str, Any]] = None,
    notes: List[Dict[str, Any]] = None,
    tiles: List[Dict[str, Any]] = None,
    sounds: List[Dict[str, Any]] = None,
    output_path: str = "foundry_scene.json"
):
    """
    Export the dungeon layout to a Foundry VTT scene JSON file.

    Args:
        scene_name (str): Name of the scene.
        background_image_path (str): Path to the background image file.
        width (int): Width of the scene in pixels.
        height (int): Height of the scene in pixels.
        grid_size (int): Size of the grid squares in pixels.
        walls (list): List of wall definitions.
        lights (list): List of light sources.
        notes (list): List of notes.
        tiles (list): List of tiles.
        output_path (str): Path to save the exported JSON file.
    """

    if not os.path.exists(background_image_path):
        print("[i] No image found, generating one...")
        render_dungeon(Dungeon)

    scene = {
        "name": scene_name,
        "navigation": True,
        "navOrder": 1,
        "navName": scene_name,
        "img": background_image_path,
        "width": width,
        "height": height,
        "grid": grid_size,
        "gridType": 0,
        "gridDistance": 5,
        "gridUnits": "ft",
        "padding": 0.25,
        "initial": {"x": 0, "y": 0, "scale": 1.0},
        "fogExploration": True,
        "fogReset": False,
        "tokenVision": True,
        "globalLight": False,
        "globalLightThreshold": None,
        "walls": walls or [],
        "lighting": lights or [],
        "notes": notes or [],
        "tiles": tiles or [],
        "sounds": sounds or [],
        # tokens intentionally omitted
        "flags": {},
        "weather": "",
        "playlist": None,
        "playlistSound": None,
        "journal": None,
        "folder": None,
        "sorting": "m",
        "sort": 0,
        "ownership": {},
    }

    with open(output_path, "w") as f:
        json.dump(scene, f, indent=2)

    print(f"[✓] Foundry scene exported to {output_path}")
