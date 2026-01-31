import pygame as pg
from ggj.camera import camera
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject

PLAYER_SIZE = 50


class Player(pg.sprite.Sprite, GameObject):
    _world_rect: pg.Rect
    image: pg.Surface

    def __init__(self):
        super().__init__()

        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(pg.Color(255, 0, 0, 0))
        self.rect = self.image.get_rect()

        # contains the world position
        self._world_rect = pg.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)

        self._populate_rect()

    def _populate_rect(self):
        # contains the actual dimension on the screen
        self.rect = camera.get_screen_rect(self._world_rect)

    def update(self) -> None:
        if key_manager.is_key_down(key_map.player_down):
            self._world_rect.y += 10
        if key_manager.is_key_down(key_map.player_up):
            self._world_rect.y -= 10
        if key_manager.is_key_down(key_map.player_left):
            self._world_rect.x -= 10
        if key_manager.is_key_down(key_map.player_right):
            self._world_rect.x += 10

        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return self._world_rect
