from ggj.game_object import GameObject, PointMass
from ggj.camera import camera
import pygame as pg
import logging

SURFACE_BLOCK_SIZE = (64, 64)
COLOR = pg.Color(255, 125, 0)

WALL_MASS = 1000

logger = logging.getLogger(__name__)


def map_to_world_coords(v: pg.Vector2) -> pg.Vector2:
    """Convert a coordinate on the map (in map units) to the world."""
    return pg.Vector2(v.x * SURFACE_BLOCK_SIZE[0], v.y * SURFACE_BLOCK_SIZE[1])


class SurfaceBlock(pg.sprite.Sprite, GameObject):
    _point_mass: PointMass

    def __init__(self, position: pg.Vector2):
        super().__init__()

        self.image = pg.Surface(SURFACE_BLOCK_SIZE)
        self.image.fill(COLOR)
        self._point_mass = PointMass(position, WALL_MASS)

        self._populate_rect()

    def _populate_rect(self):
        self.rect = camera.get_screen_rect(self.get_world_rect())

    def update(self) -> None:
        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x * SURFACE_BLOCK_SIZE[0]
            - (SURFACE_BLOCK_SIZE[0] / 2),
            self._point_mass.position.y * SURFACE_BLOCK_SIZE[1]
            - (SURFACE_BLOCK_SIZE[1] / 2),
            *SURFACE_BLOCK_SIZE,
        )
