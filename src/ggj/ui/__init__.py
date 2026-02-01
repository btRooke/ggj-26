import logging
import threading
from threading import Thread

import pygame.sprite

from .message_box import MessageBox

logger = logging.getLogger(__name__)

UI_PADDING_PX = 10


class UserInterface(pygame.sprite.Group):
    def __init__(self, parent: pygame.surface.Surface):
        super().__init__()

        self.parent = parent

        self.stopped = threading.Event()

        self.message_box = MessageBox()

        self.message_box.add(self)
        self.refresh_message_box_location()

        # thread to periodically add some messages to the box

        self.message_adding_thread = Thread(target=self.message_adding_loop)
        self.message_adding_thread.start()

    def refresh_message_box_location(self):
        self.message_box.rect.x = (
            self.parent.get_rect().width - self.message_box.rect.width - UI_PADDING_PX
        )
        self.message_box.rect.y = UI_PADDING_PX

    def message_adding_loop(self):
        logger.info("started msg adding thread")
        i = 0
        while not self.stopped.wait(1):
            i += 1
            self.message_box.add_message(
                f"{i}ello from the girlfriend how is it going whatever is going on"
            )

        logger.info("stopped msg adding thread")

    def draw(self, *args, **kwargs):
        self.refresh_message_box_location()
        super().draw(*args, **kwargs)

    def shutdown(self):
        self.stopped.set()
        self.message_adding_thread.join()
