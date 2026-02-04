from ggj import world
from ggj.game_object import GameObject, PointMass
import pygame as pg
import logging
from ggj.camera import camera, screen_to_world_vector2
import heapq
from ggj.collision import collision_object_manager
from ggj.world import SurfaceBlock

logger = logging.getLogger(__name__)

TELEGRAPH_DIMS = (10, 300)
COLOR = (211, 211, 211)


class TeleGraph(pg.sprite.Sprite, GameObject):
    _point_mass: PointMass

    def __init__(self, position: pg.Vector2):
        pg.sprite.Sprite.__init__(self)
        self._point_mass = PointMass(position, 20)
        self.image = pg.Surface(TELEGRAPH_DIMS)
        self.image.fill(COLOR)

    def _populate_rect(self):
        self.rect = camera.get_screen_rect(self.world_rect)

    def update(self) -> None:
        self._populate_rect()

    @property
    def world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (TELEGRAPH_DIMS[0] / 2),
            self._point_mass.position.y - (TELEGRAPH_DIMS[1] / 2),
            *TELEGRAPH_DIMS,
        )

    def __lt__(self, other):
        our_pos = (self._point_mass.position.x, self._point_mass.position.y)
        o_pos = (other._point_mass.position.x, other._point_mass.position.y)
        return our_pos.__lt__(o_pos)


class TeleGraphPolePlacer:
    _active_poles: list[TeleGraph]
    _sprite_group: pg.sprite.Group

    def __init__(self):
        self._poles = []
        self._sprite_group = pg.sprite.Group()
        self._unused_poles = [
            TeleGraph(pg.Vector2(10000000, 1000000)) for _ in range(100)
        ]

    def add(self, position: pg.Vector2):
        """Add a telegraph at the mouse position.

        Args:
            position: position of the mouse on the screen.
        """
        # maintain poles by position for comparison
        world_pos = screen_to_world_vector2(position)
        logger.debug(
            f"adding telegraph at screen pos: {position}, world pos: {world_pos}"
        )
        pole = self._unused_poles.pop()
        prev_pos = pole._point_mass.position

        # temporarily modify the display of the pole to check for collision
        pole._point_mass.position = world_pos
        pole.rect.x = round(position.x)
        pole.rect.y = round(position.y)
        heapq.heappush(self._poles, pole)

        blocks = collision_object_manager.get(SurfaceBlock)
        assert blocks
        if len(collisions := pg.sprite.spritecollide(pole, blocks, False)) == 0:
            pole._point_mass.position = prev_pos
        else:
            # modify the position of the pole
            pole._point_mass.position.x = collisions[0].world_rect.centerx
            pole._point_mass.position.y = collisions[0].world_rect.top - (
                pole.world_rect.height / 2
            )

    @property
    def poles(self):
        return self._poles + self._unused_poles


telegraph_placer = TeleGraphPolePlacer()
