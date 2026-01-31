import logging
import threading
from threading import Thread

import pygame.sprite

from .message_box import MessageBox

logger = logging.getLogger(__name__)


class UserInterface(pygame.sprite.Group):
    def __init__(self, parent: pygame.surface.Surface):
        super().__init__()

        self.parent = parent

        self.stopped = threading.Event()

        self.message_box = MessageBox()
        self.message_box.add(self)
        self.message_box.rect.x = (
            parent.get_rect().width - self.message_box.rect.width - 10
        )
        self.message_box.rect.y = (
            parent.get_rect().height - self.message_box.rect.height - 10
        )

        # thread to periodically add some messages to the box

        self.message_adding_thread = Thread(target=self.message_adding_loop)
        self.message_adding_thread.start()

    def message_adding_loop(self):
        logger.info("started msg adding thread")
        i = 0
        while not self.stopped.wait(1):
            i += 1
            self.message_box.add_message(
                f"{i}ello from the girlfriend how is it going whatever is going on"
            )

        logger.info("stopped msg adding thread")

    def shutdown(self):
        self.stopped.set()
        self.message_adding_thread.join()
