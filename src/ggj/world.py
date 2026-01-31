from ggj.game_object import GameObject, PointMass
from ggj.camera import camera
import pygame as pg
import logging

SURFACE_BLOCK_SIZE = (1, 1)
COLOR = pg.Color(255, 125, 0)

WALL_MASS = 1000

logger = logging.getLogger(__name__)


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
            self._point_mass.position.x - (SURFACE_BLOCK_SIZE[0] / 2),
            self._point_mass.position.y - (SURFACE_BLOCK_SIZE[1] / 2),
            *SURFACE_BLOCK_SIZE,
        )

    def on_collide(self, other: GameObject) -> None:
        pass
