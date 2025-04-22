"""
Dungeon Rendering Module

This module provides functionality to convert a generated dungeon layout into
a visually styled image using configurable rendering parameters, including
lighting, materials, aging effects, and more.
"""

import random
import math
from noise import pnoise2
from PIL import Image, ImageDraw
from rosecrypt.dungeon import Dungeon
from rosecrypt.logger import setup_logger
from rosecrypt.elements.door import Door
from rosecrypt.elements.wall_segment import WallSegment
from rosecrypt.rendering.enums.rendering_tag import RenderingTag
from rosecrypt.rendering.rendering_settings import RenderingSettings

log = setup_logger(__name__, category="Rendering")

class DungeonRenderer():
    """
    Renders a Dungeon instance to a styled image using configurable rendering settings.

    :param dungeon: The dungeon object to render.
    :type dungeon: Dungeon
    :param settings: The visual rendering settings to use.
    :type settings: RenderingSettings
    """

    def __init__(self, dungeon: Dungeon, settings: RenderingSettings):
        self.dungeon = dungeon
        self.rng: random.Random = random.Random(settings.seed)
        self.settings = settings

        width_px = self.dungeon.width * settings.TILE_SIZE
        height_px = self.dungeon.height * settings.TILE_SIZE
        self.image = Image.new(
            "RGB",
            (width_px, height_px),
            color=settings.style.paper_color.get_hex_l()
            )
        self.draw = ImageDraw.Draw(self.image)

    def render_dungeon(self):
        """
        Renders the dungeon as a complete image with all visual layers.

        Drawing includes:
        - Background floor tiles
        - Bricks and outlines for walls
        - Pebbles and cracks for weathering
        - Doors with appropriate frame and material

        :return: The rendered dungeon image.
        :rtype: PIL.Image
        """

        # Draw cosmetic stone-blocks/bricks and separetes WallSegments
        log.info("Drawing pretty walls...")
        for wall in self.dungeon.walls:
            self._draw_wall_block_ring(wall)
        log.info("Finshed drawing %s pretty walls.", len(self.dungeon.walls))

        # Draw simple wall outlines
        log.info("Drawing simple walls...")
        for wall in self.dungeon.walls:
            self._draw_wall_segment(wall)
        log.info("Finshed drawing %s simple walls.", len(self.dungeon.walls))

        # Draw floor and its cosmetics
        log.info("Drawing floor...")
        self._draw_floor_tiles()
        log.info("Finished drawing floor.")

        log.info("Drawing pebbles...")
        self._draw_pebbles()
        log.info("Finished pebbles floor.")

        log.info("Drawing cracks...")
        self._draw_cracks(RenderingTag.get_tag_by_category(self.settings.tags, 'Aging'))
        log.info("Finished cracks floor.")

        # Draw doors
        log.info("Drawing doors...")
        for door in self.dungeon.doors:
            self._draw_door(door)
        log.info("Finished drawing %s doors.", len(self.dungeon.doors))

        return self.image

    def _draw_floor_tiles(self):
        """
        Draws floor tiles on walkable areas with a grid and outline effect.

        Applies the floor color and ink borders to all walkable tiles
        in the dungeon's grid.
        """

        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if self.dungeon.grid[y][x] != 1:
                    continue

                x1 = x * self.settings.TILE_SIZE
                y1 = y * self.settings.TILE_SIZE
                x2 = x1 + self.settings.TILE_SIZE
                y2 = y1 + self.settings.TILE_SIZE

                # Draw floor tile
                self.draw.rectangle(
                    [x1, y1, x2, y2],
                    fill=self.settings.style.floor_color.get_hex_l()
                    )

                # Define wall edge segments around the tile
                wall_edges = {
                    'top':    ((x, y), (x + 1, y)),
                    'bottom': ((x, y + 1), (x + 1, y + 1)),
                    'left':   ((x, y), (x, y + 1)),
                    'right':  ((x + 1, y), (x + 1, y + 1)),
                }

                # For each edge, check if there's a wall segment at that exact spot
                #pylint: disable=unused-variable
                for side, (start, end) in wall_edges.items():
                    if side == 'top':
                        self.draw.line(
                            [(x1, y1), (x2, y1)],
                            fill=self.settings.style.ink_color.get_hex_l(),
                            width=1
                            )
                    elif side == 'bottom':
                        self.draw.line(
                            [(x1, y2), (x2, y2)],
                            fill=self.settings.style.ink_color.get_hex_l(),
                            width=1
                            )
                    elif side == 'left':
                        self.draw.line(
                            [(x1, y1), (x1, y2)],
                            fill=self.settings.style.ink_color.get_hex_l(),
                            width=1
                            )
                    elif side == 'right':
                        self.draw.line(
                            [(x2, y1), (x2, y2)],
                            fill=self.settings.style.ink_color.get_hex_l(),
                            width=1
                            )


    def _draw_door(self, door: Door):
        """
        Draws a visual representation of a door, including color and frame.

        :param door: The door object to draw.
        :type door: Door
        """

        wall_segment: WallSegment = door.door_to_wall()
        x1, y1, x2, y2 = wall_segment.to_pixel_coords(self.settings.TILE_SIZE)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        door_type = door.type
        door_color = self.settings.style.door_colors.get(door_type, self.settings.style.wood_color)
        frame_color = self.settings.style.frame_colors.get(
            door_type,
            self.settings.style.stone_color
            )

        half = self.settings.TILE_SIZE // 2
        frame_offset = self.settings.FRAME_SIZE - self.settings.BORDER

        if dy > dx:
            # Vertical door
            log.debug("Drawing vertical %s door at (%s, %s)", door.type, door.x1, door.y1)
            door_box = [center_x - self.settings.WALL_THICKNESS / 2, center_y - half,
                        center_x + self.settings.WALL_THICKNESS / 2, center_y + half]
            self.draw.rectangle(
                door_box,
                fill=door_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
                )

            self.draw.rectangle(
                [
                    center_x - self.settings.FRAME_SIZE,
                    center_y - half + frame_offset - self.settings.FRAME_SIZE,
                    center_x + self.settings.FRAME_SIZE,
                    center_y - half + frame_offset + self.settings.FRAME_SIZE
                    ],
                fill=frame_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
            )
            self.draw.rectangle(
                [
                    center_x - self.settings.FRAME_SIZE,
                    center_y + half - frame_offset - self.settings.FRAME_SIZE,
                    center_x + self.settings.FRAME_SIZE,
                    center_y + half - frame_offset + self.settings.FRAME_SIZE
                    ],
                fill=frame_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
            )

        elif dx > dy:
            # Horizontal door
            log.debug("Drawing horizontal %s door at (%s, %s)", door.type, door.x1, door.y1)
            door_box = [center_x - half, center_y - self.settings.WALL_THICKNESS / 2,
                        center_x + half, center_y + self.settings.WALL_THICKNESS / 2]
            self.draw.rectangle(
                door_box,
                fill=door_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
                )

            self.draw.rectangle(
                [
                    center_x - half + frame_offset - self.settings.FRAME_SIZE,
                    center_y - self.settings.FRAME_SIZE,
                    center_x - half + frame_offset + self.settings.FRAME_SIZE,
                    center_y + self.settings.FRAME_SIZE
                    ],
                fill=frame_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
            )
            self.draw.rectangle(
                [
                    center_x + half - frame_offset - self.settings.FRAME_SIZE,
                    center_y - self.settings.FRAME_SIZE,
                    center_x + half - frame_offset + self.settings.FRAME_SIZE,
                    center_y + self.settings.FRAME_SIZE
                    ],
                fill=frame_color.get_hex_l(),
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
            )

        else:
            # Fallback: draw cross
            log.warning(
                "Could not identify door direction, drawing %s coss at (%s, %s)",
                door.type,
                door.x1, door.y1
                )
            self.draw.line(
                [(center_x - half, center_y - half), (center_x + half, center_y + half)],
                fill=door_color.get_hex_l(), width=2
            )
            self.draw.line(
                [(center_x - half, center_y + half), (center_x + half, center_y - half)],
                fill=door_color.get_hex_l(), width=2
            )

    def _draw_wall_block_ring(self, wall: WallSegment):
        """
        Draws a ring of overlapping bricks to simulate rough stonework for a wall.

        :param wall: Wall segment to decorate with stone blocks.
        :type wall: WallSegment
        """

        x1, y1, x2, y2 = wall.to_pixel_coords(self.settings.TILE_SIZE)

        dx = x2 - x1
        dy = y2 - y1
        length = int(math.hypot(dx, dy))
        dist_covered = 0

        while dist_covered < length:
            width = self.rng.randint(
                self.settings.BRICK_MIN_WIDTH,
                self.settings.BRICK_MAX_WIDTH
                )
            height = self.rng.randint(
                self.settings.BRICK_MIN_HEIGHT,
                self.settings.BRICK_MAX_HEIGHT
                )

            t = dist_covered / length
            cx = x1 + dx * t
            cy = y1 + dy * t

            bx1 = cx - width / 2
            by1 = cy - height / 2
            bx2 = cx + width / 2
            by2 = cy + height / 2

            self.draw.rectangle(
                [bx1, by1, bx2, by2],
                fill=self.settings.style.stone_color.get_hex_l()
                )
            self.draw.rectangle(
                [bx1, by1, bx2, by2],
                outline=self.settings.style.ink_color.get_hex_l(),
                width=self.settings.BORDER
                )

            dist_covered += width * 0.6  # ensures overlap even for smallest bricks

    def _draw_wall_segment(self, wall: WallSegment):
        """
        Draws a basic wall line using ink color and thickness from settings.

        :param wall: The wall segment to render as a line.
        :type wall: WallSegment
        """

        x1, y1, x2, y2 = wall.to_pixel_coords(self.settings.TILE_SIZE)
        self.draw.line(
            [x1, y1, x2, y2],
            fill=self.settings.style.ink_color.get_hex_l(),
            width=self.settings.WALL_THICKNESS
            )

    def _draw_pebbles(self):
        """
        Randomly draws scattered pebbles on floor tiles using Perlin noise.

        Simulates small stones and irregular fragments to make the floor look aged
        and natural. Uses ellipse and polygon drawing depending on size.
        """

        scale = 0.9
        threshold = 0.4

        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if self.dungeon.grid[y][x] != 1:
                    continue

                n = pnoise2(x * scale, y * scale, octaves=1)
                if n > threshold:
                    x1 = x * self.settings.TILE_SIZE
                    y1 = y * self.settings.TILE_SIZE

                    pebble_count = self.rng.randint(1, 3)
                    for _ in range(pebble_count):
                        px = x1 + self.rng.randint(10, self.settings.TILE_SIZE - 10)
                        py = y1 + self.rng.randint(10, self.settings.TILE_SIZE - 10)
                        r = self.rng.randint(3, 6)

                        if r > 4:
                            # Irregular shape for larger stone
                            points = []
                            for angle in range(0, 360, 15):
                                rad = math.radians(angle)
                                perturb = self.rng.uniform(-1.5, 1.5)
                                rr = r + perturb
                                sx = px + rr * math.cos(rad)
                                sy = py + rr * math.sin(rad)
                                points.append((sx, sy))
                            self.draw.polygon(
                                points,
                                fill=self.settings.style.ink_color.get_hex_l()
                                )
                        else:
                            # Simple round pebble
                            self.draw.ellipse(
                                [px - r, py - r, px + r, py + r],
                                fill=self.settings.style.ink_color.get_hex_l()
                                )

    def _draw_cracks(self, aging_level: RenderingTag = RenderingTag.OLD):
        """
        Draws cracks extending outward from walls based on the given aging level.

        Applies a primary crack and possibly a branching secondary crack using
        probabilistic rules.

        :param aging_level: The aging intensity tag, controls crack density.
        :type aging_level: RenderingTag
        """

        crack_chance, branch_chance = aging_level.data

        for wall in self.dungeon.walls:
            x1, y1, x2, y2 = wall.to_pixel_coords(self.settings.TILE_SIZE)
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
            floor_x = int(offset_x // self.settings.TILE_SIZE)
            floor_y = int(offset_y // self.settings.TILE_SIZE)

            #pylint: disable=line-too-long
            if not (0 <= floor_x < self.dungeon.width and 0 <= floor_y < self.dungeon.height) or self.dungeon.grid[floor_y][floor_x] != 1:
                perp_x *= -1
                perp_y *= -1
                offset_x = mx + perp_x * 2
                offset_y = my + perp_y * 2
                floor_x = int(offset_x // self.settings.TILE_SIZE)
                floor_y = int(offset_y // self.settings.TILE_SIZE)

            if not (0 <= floor_x < self.dungeon.width and 0 <= floor_y < self.dungeon.height):
                continue

            if self.dungeon.grid[floor_y][floor_x] != 1:
                continue

            if self.rng.random() < crack_chance:
                start_x = mx + perp_x
                start_y = my + perp_y
                dir_angle = math.atan2(perp_y, perp_x)
                points = [(start_x, start_y)]

                for _ in range(self.rng.randint(3, 6)):
                    last_x, last_y = points[-1]
                    length = self.rng.randint(5, 15)
                    angle = dir_angle + self.rng.uniform(-0.5, 0.5)
                    next_x = last_x + math.cos(angle) * length
                    next_y = last_y + math.sin(angle) * length
                    points.append((next_x, next_y))

                self.draw.line(points, fill=self.settings.style.ink_color.get_hex_l(), width=1)

                if self.rng.random() < branch_chance:
                    bx, by = points[self.rng.randint(1, len(points) - 2)]
                    branch_angle = dir_angle + math.pi / 2 + self.rng.uniform(-0.5, 0.5)
                    blen = self.rng.randint(5, 12)
                    bx2 = bx + math.cos(branch_angle) * blen
                    by2 = by + math.sin(branch_angle) * blen
                    self.draw.line([(bx, by), (bx2, by2)], fill=self.settings.style.ink_color.get_hex_l(), width=1)
