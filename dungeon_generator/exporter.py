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
    Exports a Foundry VTT scene JSON using provided dungeon data.

    Parameters:
    - scene_name: Name of the scene
    - background_image_path: Path to the background PNG
    - width, height: Dimensions of the scene canvas
    - grid_size: Pixel size of one grid square
    - walls, lights, notes, tiles, sounds: Lists of respective objects
    - output_path: File to write the exported scene JSON
    """

    if not os.path.exists(background_image_path):
        print("[i] No image found, generating one...")
        render_dungeon(Dungeon, output_path=background_image_path)

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
