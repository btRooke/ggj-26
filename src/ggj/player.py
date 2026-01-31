import pygame as pg
from ggj.camera import camera, screen_to_world_vector2
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PointMass

import logging

logger = logging.getLogger(__name__)

PLAYER_SIZE = 50
PLAYER_MAX_SPEED = 5
PLAYER_MASS = 10

SPRING_CONSTANT = 0.001


class Player(pg.sprite.Sprite, GameObject):
    _world_rect: pg.Rect
    _point_mass: PointMass
    image: pg.Surface

    def __init__(self):
        super().__init__()

        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(pg.Color(255, 0, 0, 0))
        self.rect = self.image.get_rect()
        self._point_mass = PointMass(
            pg.Vector2(0, 0), PLAYER_MASS, clamp_speed=PLAYER_MAX_SPEED
        )
        self._populate_rect()

    def _populate_rect(self):
        # contains the actual dimension on the screen
        self.rect = camera.get_screen_rect(self.get_world_rect())

    def update(self) -> None:
        force_multiplier = 2
        net_force = pg.Vector2(0, 0)

        if key_manager.is_key_down(key_map.player_down):
            net_force += pg.Vector2(0, 1)
        if key_manager.is_key_down(key_map.player_up):
            net_force += pg.Vector2(0, -1)
        if key_manager.is_key_down(key_map.player_left):
            net_force += pg.Vector2(-1, 0)
        if key_manager.is_key_down(key_map.player_right):
            net_force += pg.Vector2(1, 0)

        if (mouse_down_pos := key_manager.get_mouse_down_pos()) is not None:
            world_pos_mouse = screen_to_world_vector2(pg.Vector2(mouse_down_pos))
            distance = world_pos_mouse - self._point_mass.position
            spring_force = SPRING_CONSTANT * distance
            logger.debug(f"applying force {spring_force}")
            self._point_mass.add_force(spring_force)

        self._point_mass.add_force(force_multiplier * net_force)
        self._point_mass.integrate()

        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x,
            self._point_mass.position.y,
            PLAYER_SIZE,
            PLAYER_SIZE,
        )
