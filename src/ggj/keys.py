import logging
import pygame as pg
from typing import Optional

logger = logging.getLogger(__name__)


class KeyManager:
    # Holds keys that are currently in the down state
    key_down: set[int]
    is_quit: bool
    _mouse_down_pos: Optional[tuple[int, int]]

    def __init__(self) -> None:
        self.key_down = set()
        self.is_quit = False
        self._mouse_down_pos = None

    def update(self) -> None:
        self.is_quit = False

        for event in pg.event.get():
            # nothing to do if key event has not been fired
            if event.type == pg.QUIT:
                self.is_quit = True
            elif event.type == pg.KEYDOWN:
                logger.debug(f"adding key {event.key} to 'down' set")
                self.key_down.add(event.key)
            elif event.type == pg.KEYUP:
                logger.debug(f"removing key {event.key} from 'down' set")
                self.key_down.discard(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                logger.debug(f"mouse down at pos {pg.mouse.get_pos()}")
                self._mouse_down_pos = pg.mouse.get_pos()
            elif event.type == pg.MOUSEMOTION and self._mouse_down_pos is not None:
                logger.debug(f"mouse move with down at pos {pg.mouse.get_pos()}")
                self._mouse_down_pos = pg.mouse.get_pos()
            elif event.type == pg.MOUSEBUTTONUP:
                logger.debug(f"mouse up at pos {pg.mouse.get_pos()}")
                self._mouse_down_pos = None

    def is_key_down(self, key: int) -> bool:
        """Checks if the key is in the set of keys that are down"""
        return key in self.key_down

    def quit(self) -> bool:
        return self.is_quit

    def get_mouse_down_pos(self) -> Optional[tuple[int, int]]:
        return self._mouse_down_pos


key_manager = KeyManager()


class KeyMaps:
    _player_left: int
    _player_right: int
    _player_up: int
    _player_down: int
    _player_jump: int

    def __init__(self):
        self._player_left = pg.K_a
        self._player_right = pg.K_d
        self._player_up = pg.K_w
        self._player_down = pg.K_s
        self._player_jump = pg.K_SPACE

    @property
    def player_left(self):
        return self._player_left

    @property
    def player_right(self):
        return self._player_right

    @property
    def player_up(self):
        return self._player_up

    @property
    def player_down(self):
        return self._player_down

    @property
    def player_jump(self):
        return self._player_jump


key_map = KeyMaps()
