import random
from functools import lru_cache

import pygame

from ggj.assets import FLOOR_SPRIES_PATH
from ggj.game_object import GameObject, PointMass
from ggj.camera import camera
import pygame as pg
import logging

SURFACE_BLOCK_SIZE = (48, 48)
COLOR = pg.Color(255, 125, 0)

WALL_MASS = 1000

logger = logging.getLogger(__name__)
FLOOR_BLOCK_SIZE = 22


@lru_cache
def load_surface_block_images() -> list[pg.Surface]:
    sheet = pg.image.load(FLOOR_SPRIES_PATH).convert_alpha()

    if (
        sheet.get_height() % FLOOR_BLOCK_SIZE != 0
        or sheet.get_width() != FLOOR_BLOCK_SIZE
    ):
        raise ValueError(f"Sprite sheet has wrong dims, {sheet.get_rect()}")

    sprites = []

    for i in range(0, sheet.get_height(), FLOOR_BLOCK_SIZE):
        # create blank surface for sprite
        sprite = pygame.surface.Surface((FLOOR_BLOCK_SIZE, FLOOR_BLOCK_SIZE))

        # blit the correct part to it
        rect = sprite.get_rect()
        rect.y = i
        sprite.blit(sheet, dest=(0, 0), area=rect)

        # scale and append
        sprites.append(pygame.transform.scale_by(sprite, FLOOR_BLOCK_SIZE))

    return [pygame.transform.scale(s, SURFACE_BLOCK_SIZE) for s in sprites]


def map_to_world_coords(v: pg.Vector2) -> pg.Vector2:
    """Convert a coordinate on the map (in map units) to the world."""
    return pg.Vector2(v.x * SURFACE_BLOCK_SIZE[0], v.y * SURFACE_BLOCK_SIZE[1])


class SurfaceBlock(pg.sprite.Sprite, GameObject):
    _point_mass: PointMass

    def __init__(self, position: pg.Vector2):
        super().__init__()

        self.image = random.choice(load_surface_block_images())
        self._point_mass = PointMass(position, WALL_MASS)

        self._populate_rect()

    def _populate_rect(self):
        self.rect = camera.get_screen_rect(self.world_rect)

    def update(self) -> None:
        self._populate_rect()

    @property
    def world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x * SURFACE_BLOCK_SIZE[0]
            - (SURFACE_BLOCK_SIZE[0] / 2),
            self._point_mass.position.y * SURFACE_BLOCK_SIZE[1]
            - (SURFACE_BLOCK_SIZE[1] / 2),
            *SURFACE_BLOCK_SIZE,
        )
