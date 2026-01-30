import logging
import pygame as pg

logger = logging.getLogger(__name__)


class KeyManager:
    # Holds keys that are currently in the down state
    key_down: set[int]
    is_quit: bool

    def __init__(self) -> None:
        self.key_down = set()
        self.is_quit = False

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

    def is_key_down(self, key: int) -> bool:
        """Checks if the key is in the set of keys that are down"""
        return key in self.key_down

    def quit(self) -> bool:
        return self.is_quit


key_manager = KeyManager()
