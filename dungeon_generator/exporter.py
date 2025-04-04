import json
import base64
from PIL import Image
from io import BytesIO

def export_to_uvtt(dungeon, image_path, output_path):
    uvtt_data = {
        "format": 0.1,
        "resolution": {
            "map_origin": {"x": 0, "y": 0},
            "map_size": {"x": dungeon.shape[1], "y": dungeon.shape[0]},
            "pixels_per_grid": 100
        },
        "line_of_sight": [],  # Populate with wall data
        "lights": [],         # Populate with light sources if any
        "image": ""           # Base64 encoded image
    }

    # Encode the map image
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        uvtt_data["image"] = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Write to output file
    with open(output_path, 'w') as f:
        json.dump(uvtt_data, f, indent=4)
