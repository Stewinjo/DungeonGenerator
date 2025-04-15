"""
Dungeon Rendering Module

This module provides functions to render dungeon layouts into images.
"""

import random
import math
from noise import pnoise2
from PIL import Image, ImageDraw
from .enums import AgingLevel
from .dungeon import Dungeon
from .style import DungeonStyle
from .elements import WallSegment, Door

TILE_SIZE = 100
WALL_THICKNESS = 5
GRID_DOT_SIZE = 2
BORDER = 2
FRAME_SIZE = TILE_SIZE // 8
BRICK_MIN_WIDTH = FRAME_SIZE * 2 + 10
BRICK_MAX_WIDTH = BRICK_MIN_WIDTH + 20
BRICK_MIN_HEIGHT = FRAME_SIZE * 2 + 10
BRICK_MAX_HEIGHT = BRICK_MIN_HEIGHT + 20


def draw_floor_tiles(draw: ImageDraw.ImageDraw, dungeon: Dungeon, style: DungeonStyle):
    """
    Draws the dungeon's floor tiles and a thin black grid around walkable tiles.
    """

    for y in range(dungeon.height):
        for x in range(dungeon.width):
            if dungeon.grid[y][x] != 1:
                continue

            x1 = x * TILE_SIZE
            y1 = y * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE

            # Draw floor tile
            draw.rectangle([x1, y1, x2, y2], fill=style.floor_color.get_hex_l())

            # Define wall edge segments around the tile
            wall_edges = {
                'top':    ((x, y), (x + 1, y)),
                'bottom': ((x, y + 1), (x + 1, y + 1)),
                'left':   ((x, y), (x, y + 1)),
                'right':  ((x + 1, y), (x + 1, y + 1)),
            }

            # For each edge, check if there's a wall segment at that exact spot
            for side, (start, end) in wall_edges.items():
                if side == 'top':
                    draw.line([(x1, y1), (x2, y1)], fill=style.ink_color.get_hex_l(), width=1)
                elif side == 'bottom':
                    draw.line([(x1, y2), (x2, y2)], fill=style.ink_color.get_hex_l(), width=1)
                elif side == 'left':
                    draw.line([(x1, y1), (x1, y2)], fill=style.ink_color.get_hex_l(), width=1)
                elif side == 'right':
                    draw.line([(x2, y1), (x2, y2)], fill=style.ink_color.get_hex_l(), width=1)


def draw_door(draw: ImageDraw.ImageDraw, door: Door, style: DungeonStyle):
    """
    Draws a door segment with colored door and frame, including ink outline.
    """

    wall_segment: WallSegment = door.door_to_wall()
    x1, y1, x2, y2 = wall_segment.to_pixel_coords(TILE_SIZE)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    door_type = wall_segment.door_type
    door_color = style.door_colors.get(door_type, style.wood_color)
    frame_color = style.frame_colors.get(door_type, style.stone_color)

    half = TILE_SIZE // 2
    frame_offset = FRAME_SIZE - BORDER

    if dy > dx:
        # Vertical door
        door_box = [center_x - WALL_THICKNESS / 2, center_y - half,
                    center_x + WALL_THICKNESS / 2, center_y + half]
        draw.rectangle(door_box, fill=door_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER)

        draw.rectangle(
            [center_x - FRAME_SIZE, center_y - half + frame_offset - FRAME_SIZE,
             center_x + FRAME_SIZE, center_y - half + frame_offset + FRAME_SIZE],
            fill=frame_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER
        )
        draw.rectangle(
            [center_x - FRAME_SIZE, center_y + half - frame_offset - FRAME_SIZE,
             center_x + FRAME_SIZE, center_y + half - frame_offset + FRAME_SIZE],
            fill=frame_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER
        )

    elif dx > dy:
        # Horizontal door
        door_box = [center_x - half, center_y - WALL_THICKNESS / 2,
                    center_x + half, center_y + WALL_THICKNESS / 2]
        draw.rectangle(door_box, fill=door_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER)

        draw.rectangle(
            [center_x - half + frame_offset - FRAME_SIZE, center_y - FRAME_SIZE,
             center_x - half + frame_offset + FRAME_SIZE, center_y + FRAME_SIZE],
            fill=frame_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER
        )
        draw.rectangle(
            [center_x + half - frame_offset - FRAME_SIZE, center_y - FRAME_SIZE,
             center_x + half - frame_offset + FRAME_SIZE, center_y + FRAME_SIZE],
            fill=frame_color.get_hex_l(), outline=style.ink_color.get_hex_l(), width=BORDER
        )

    else:
        # Fallback: draw cross
        draw.line(
            [(center_x - half, center_y - half), (center_x + half, center_y + half)],
            fill=door_color.get_hex_l(), width=2
        )
        draw.line(
            [(center_x - half, center_y + half), (center_x + half, center_y - half)],
            fill=door_color.get_hex_l(), width=2
        )

def draw_wall_block_ring(draw: ImageDraw.ImageDraw, wall: WallSegment, style: DungeonStyle, seed: int = 0):
    """
    Draws a series of overlapping rectangular bricks along a wall to simulate rough stonework.
    """

    x1, y1, x2, y2 = wall.to_pixel_coords(TILE_SIZE)

    dx = x2 - x1
    dy = y2 - y1
    length = int(math.hypot(dx, dy))
    dist_covered = 0
    rng = random.Random(seed + int(x1 + y1 + x2 + y2))

    while dist_covered < length:
        width = rng.randint(BRICK_MIN_WIDTH, BRICK_MAX_WIDTH)
        height = rng.randint(BRICK_MIN_HEIGHT, BRICK_MAX_HEIGHT)

        t = dist_covered / length
        cx = x1 + dx * t
        cy = y1 + dy * t

        bx1 = cx - width / 2
        by1 = cy - height / 2
        bx2 = cx + width / 2
        by2 = cy + height / 2

        draw.rectangle([bx1, by1, bx2, by2], fill=style.stone_color.get_hex_l())
        draw.rectangle([bx1, by1, bx2, by2], outline=style.ink_color.get_hex_l(), width=BORDER)

        dist_covered += width * 0.6  # ensures overlap even for smallest bricks

def draw_wall_segment(draw: ImageDraw.ImageDraw, wall: WallSegment, style: DungeonStyle):
    """
    Draws a basic straight wall segment using a thick ink line.
    """

    x1, y1, x2, y2 = wall.to_pixel_coords(TILE_SIZE)
    draw.line([x1, y1, x2, y2], fill=style.ink_color.get_hex_l(), width=WALL_THICKNESS)

def draw_pebbles(draw: ImageDraw.ImageDraw, dungeon: Dungeon, style: DungeonStyle, seed: int = 0):
    """
    Draws randomly placed pebbles or irregular stones on walkable floor tiles using Perlin noise.
    """

    scale = 0.9
    threshold = 0.4
    rng = random.Random(seed)

    for y in range(dungeon.height):
        for x in range(dungeon.width):
            if dungeon.grid[y][x] != 1:
                continue

            n = pnoise2(x * scale, y * scale, octaves=1)
            if n > threshold:
                x1 = x * TILE_SIZE
                y1 = y * TILE_SIZE

                pebble_count = rng.randint(1, 3)
                for _ in range(pebble_count):
                    px = x1 + rng.randint(10, TILE_SIZE - 10)
                    py = y1 + rng.randint(10, TILE_SIZE - 10)
                    r = rng.randint(3, 6)

                    if r > 4:
                        # Irregular shape for larger stone
                        points = []
                        for angle in range(0, 360, 15):
                            rad = math.radians(angle)
                            perturb = rng.uniform(-1.5, 1.5)
                            rr = r + perturb
                            sx = px + rr * math.cos(rad)
                            sy = py + rr * math.sin(rad)
                            points.append((sx, sy))
                        draw.polygon(points, fill=style.ink_color.get_hex_l())
                    else:
                        # Simple round pebble
                        draw.ellipse([px - r, py - r, px + r, py + r], fill=style.ink_color.get_hex_l())

def draw_cracks(draw: ImageDraw.ImageDraw, dungeon: Dungeon, style: DungeonStyle, seed: int = 0, aging: AgingLevel = AgingLevel.NORMAL):
    """
    Draws cracks that radiate from the edge of wall segments onto adjacent floor tiles,
    with aging level controlling the density.
    """

    rng = random.Random(seed + 1337)

    aging_map = {
        AgingLevel.FEW: 0.1,
        AgingLevel.NORMAL: 0.3,
        AgingLevel.MANY: 0.6
    }

    crack_chance = aging_map[aging]
    branch_chance = 0.4

    for wall in dungeon.walls:
        x1, y1, x2, y2 = wall.to_pixel_coords(TILE_SIZE)
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        dx = x2 - x1
        dy = y2 - y1
        norm = math.hypot(dx, dy)
        if norm == 0:
            continue
        dx /= norm
        dy /= norm

        perp_x, perp_y = -dy, dx

        offset_x = mx + perp_x * 2
        offset_y = my + perp_y * 2
        floor_x = int(offset_x // TILE_SIZE)
        floor_y = int(offset_y // TILE_SIZE)

        if not (0 <= floor_x < dungeon.width and 0 <= floor_y < dungeon.height) or dungeon.grid[floor_y][floor_x] != 1:
            perp_x *= -1
            perp_y *= -1
            offset_x = mx + perp_x * 2
            offset_y = my + perp_y * 2
            floor_x = int(offset_x // TILE_SIZE)
            floor_y = int(offset_y // TILE_SIZE)

        if not (0 <= floor_x < dungeon.width and 0 <= floor_y < dungeon.height):
            continue

        if dungeon.grid[floor_y][floor_x] != 1:
            continue

        if rng.random() < crack_chance:
            start_x = mx + perp_x
            start_y = my + perp_y
            dir_angle = math.atan2(perp_y, perp_x)
            points = [(start_x, start_y)]

            for _ in range(rng.randint(3, 6)):
                last_x, last_y = points[-1]
                length = rng.randint(5, 15)
                angle = dir_angle + rng.uniform(-0.5, 0.5)
                next_x = last_x + math.cos(angle) * length
                next_y = last_y + math.sin(angle) * length
                points.append((next_x, next_y))

            draw.line(points, fill=style.ink_color.get_hex_l(), width=1)

            if rng.random() < branch_chance:
                bx, by = points[rng.randint(1, len(points) - 2)]
                branch_angle = dir_angle + math.pi / 2 + rng.uniform(-0.5, 0.5)
                blen = rng.randint(5, 12)
                bx2 = bx + math.cos(branch_angle) * blen
                by2 = by + math.sin(branch_angle) * blen
                draw.line([(bx, by), (bx2, by2)], fill=style.ink_color.get_hex_l(), width=1)

def render_dungeon(dungeon: Dungeon, style: DungeonStyle = DungeonStyle(), seed: int = 0, aging: AgingLevel = AgingLevel.NORMAL):
    """
    Render the given dungeon as an image using the specified style.

    Args:
        dungeon (Dungeon): The dungeon instance to render.
        style (DungeonStyle, optional): The style settings for rendering. Defaults to DungeonStyle().
        seed (int, optional): Seed for random number generation to ensure reproducibility. Defaults to 0.
        aging (AgingLevel, optional): Level of aging effects to apply. Defaults to AgingLevel.NORMAL.

    Returns:
        Image: A PIL Image object representing the rendered dungeon.
    """

    width_px = dungeon.width * TILE_SIZE
    height_px = dungeon.height * TILE_SIZE
    image = Image.new("RGB", (width_px, height_px), color=style.paper_color.get_hex_l())
    draw = ImageDraw.Draw(image)

    # Draw cosmetic stone-blocks/bricks and separetes WallSegments
    for wall in dungeon.walls:
        draw_wall_block_ring(draw, wall, style)

    # Draw simple wall outlines
    for wall in dungeon.walls:
        draw_wall_segment(draw, wall, style)

    # Draw floor and its cosmetics
    draw_floor_tiles(draw, dungeon, style)
    draw_pebbles(draw, dungeon, style, seed)
    draw_cracks(draw, dungeon, style, seed, aging)

    # Draw doors
    for door in dungeon.doors:
        draw_door(draw, door, style)

    return image
