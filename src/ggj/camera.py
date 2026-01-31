import pygame as pg
from typing import Optional
import logging

from ggj import game_object

logger = logging.getLogger(__name__)

BASE_RESOLUTION = (1280, 720)


def world_to_screen_vector2(world_vector: pg.Vector2) -> pg.Vector2:
    size_multiplier_x = pg.display.get_window_size()[0] / BASE_RESOLUTION[0]
    size_multiplier_y = pg.display.get_window_size()[1] / BASE_RESOLUTION[1]

    return pg.Vector2(
        size_multiplier_x * world_vector.x, size_multiplier_y * world_vector.y
    )


def world_to_screen_rect(world_rect: pg.Rect) -> pg.Rect:
    size_multiplier_x = pg.display.get_window_size()[0] / BASE_RESOLUTION[0]
    size_multiplier_y = pg.display.get_window_size()[1] / BASE_RESOLUTION[1]
    return world_rect.scale_by(size_multiplier_x, size_multiplier_y)


# Viewport that the camera can collide with
CAMERA_COLLIDE_BOUNDS = (300, 300)


class Camera(game_object.GameObject):
    # Bounding box to follow the object being followed.
    # THis is defined in world coordinates.
    bounding_box: pg.Rect
    follow_object: Optional[game_object.GameObject]
    screen: Optional[pg.Surface]

    def __init__(self) -> None:
        self.bounding_box = pg.Rect(0, 0, *CAMERA_COLLIDE_BOUNDS)
        self.screen = None

    def set_screen(self, screen: pg.Surface) -> None:
        self.screen = screen

    def get_relative(self, position: pg.Vector2) -> pg.Vector2:
        """Draw an object relative to the camera's position"""
        return position - self.bounding_box.center

    def get_screen_rect(self, rect: pg.Rect) -> pg.Rect:
        relative_cam = self.get_relative(pg.Vector2(rect.x, rect.y))
        screen_rect = world_to_screen_rect(
            pg.Rect((relative_cam.x, relative_cam.y, rect.width, rect.height))
        )
        # center of the camera represents the center of the screen.
        assert self.screen
        width, height = self.screen.get_size()
        screen_rect.center = (
            screen_rect.center[0] + round(width / 2.0),
            screen_rect.center[1] + round(height / 2.0),
        )
        return screen_rect

    def get_world_rect(self) -> pg.Rect:
        return self.bounding_box

    def follow(self, obj: game_object.GameObject):
        self.follow_object = obj
        self.bounding_box.center = obj.get_world_rect().center

    def update(self):
        if not self.follow_object:
            return

        follow_rect = self.follow_object.get_world_rect()

        # Ensure the follower's center is always at the center.
        if not self.bounding_box.collidepoint(pg.Vector2(*follow_rect.center)):
            if follow_rect.center[0] > self.bounding_box.right:
                self.bounding_box.right = follow_rect.center[0]
            elif follow_rect.center[0] < self.bounding_box.left:
                self.bounding_box.left = follow_rect.center[0]

            if follow_rect.center[1] > self.bounding_box.bottom:
                self.bounding_box.bottom = follow_rect.center[1]
            elif follow_rect.center[1] < self.bounding_box.top:
                self.bounding_box.top = follow_rect.center[1]


camera = Camera()
