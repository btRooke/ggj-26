import logging
import threading
from threading import Thread
from typing import cast

import pygame.sprite
import pygame as pg
from .message_box import MessageBox
from ..world import map_to_world_coords

logger = logging.getLogger(__name__)

UI_PADDING_PX = 10


def to_tuple(v: pg.Vector2) -> tuple[int, int]:
    return int(v.x), int(v.y)


class UserInterface(pygame.sprite.Group):
    def __init__(
        self,
        parent: pygame.surface.Surface,
        location_markers: dict[str, list[pg.Vector2]],
    ):
        super().__init__()

        self.parent = parent

        self.stopped = threading.Event()

        self.message_box = MessageBox()

        self.message_box.add(self)
        self.refresh_message_box_location()

        # location markers stuff

        self.location_markers: dict[str, list[tuple[int, int]]] = {
            k: [to_tuple(map_to_world_coords(v)) for v in vs]
            for k, vs in location_markers.items()
        }

        self.vec_to_location: dict[int, str] = dict()

        for k in self.location_markers.keys():
            for v in self.location_markers[k]:
                for i in range(-10, 10, 1):
                    self.vec_to_location[v[0] + i] = (
                        k  # TODO all the location names are copied a million times!!!
                    )

        # create set for easy lookup

        self.all_markers: set[int] = set()
        for vs in self.location_markers.values():
            for v in vs:
                for i in range(-10, 10, 1):
                    self.all_markers.add(v[0] + i)

    def update(self, player_pos: pg.Vector2):
        ppt = to_tuple(player_pos)
        if ppt[0] in self.all_markers:
            self.message_box.add_message(
                f"Location update - {self.vec_to_location[ppt[0]]}"
            )

    def refresh_message_box_location(self):
        self.message_box.rect.x = (
            self.parent.get_rect().width - self.message_box.rect.width - UI_PADDING_PX
        )
        self.message_box.rect.y = UI_PADDING_PX

    def draw(self, *args, **kwargs):
        self.refresh_message_box_location()
        super().draw(*args, **kwargs)

    def shutdown(self):
        self.stopped.set()
