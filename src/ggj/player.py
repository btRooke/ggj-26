import pygame as pg
from ggj.camera import camera
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PointMass

PLAYER_SIZE = 50
MAX_SPEED = 5


class Player(pg.sprite.Sprite, GameObject):
    _world_rect: pg.Rect
    _point_mass: PointMass
    image: pg.Surface

    def __init__(self):
        super().__init__()

        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(pg.Color(255, 0, 0, 0))
        self.rect = self.image.get_rect()
        self._point_mass = PointMass(pg.Vector2(0, 0))
        self._point_mass.clamp_speed(MAX_SPEED)
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
