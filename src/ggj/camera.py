import pygame as pg
from typing import Optional, cast
import logging

from ggj import game_object

logger = logging.getLogger(__name__)

BASE_RESOLUTION = (1280, 720)


def world_to_screen_vector2(world_vector: pg.Vector2) -> pg.Vector2:
    return world_vector


def world_to_screen_rect(world_rect: pg.Rect) -> pg.Rect:
    return world_rect


# Viewport that the camera can collide with
CAMERA_COLLIDE_BOUNDS = (300, 300)


PARALLAX_LAYERS: dict[int, pg.Vector2] = {
    -1: pg.Vector2(2, 2),
    0: pg.Vector2(1.5, 1.5),
    1: pg.Vector2(1, 1),
    2: pg.Vector2(0.75, 0.75),
    3: pg.Vector2(0.5, 0.5),
    4: pg.Vector2(0.2, 0.2),
}


class Camera(game_object.GameObject):
    # Bounding box to follow the object being followed.
    # This is defined in world coordinates.
    player_box: pg.Rect
    follow_object: Optional[game_object.GameObject]

    def __init__(self) -> None:
        self.player_box = pg.Rect(0, 0, *CAMERA_COLLIDE_BOUNDS)

    def _get_relative(self, position: pg.Vector3) -> pg.Vector2:
        """
        Get object coordinates relative to the camera's position

        Args:
            position: The (x,y,z) coordinates of the character to get relative.
                to the camera.
        """
        # zindex 1 should be at index 1 in the
        if position.z not in PARALLAX_LAYERS:
            raise ValueError(f"parallax index {position.z} is not supported")

        pos_vec2 = pg.Vector2(position.x, position.y) - self.player_box.center
        return pos_vec2.elementwise() * PARALLAX_LAYERS[cast(int, position.z)]

    def get_screen_rect(self, rect: pg.Rect, zindex=1) -> pg.Rect:
        """
        Used to draw a rect in the game to the screen. The rect this
        is returned is a position on the game screen.

        Args:
            rect: The rectangle in world coordinates.
            zindex: The zindex in which the object exists. Lower values means
                an object is closer to the screen. Higher values means an
                object is further away.
        """
        relative_cam = self._get_relative(pg.Vector3(rect.x, rect.y, zindex))
        screen_rect = world_to_screen_rect(
            pg.Rect((relative_cam.x, relative_cam.y, rect.width, rect.height))
        )
        # center of the camera represents the center of the screen.
        window = pg.display.Info()
        width, height = (window.current_w, window.current_h)
        screen_rect.center = (
            screen_rect.center[0] + round(width / 2.0),
            screen_rect.center[1] + round(height / 2.0),
        )
        return screen_rect

    def get_world_rect(self) -> pg.Rect:
        window = pg.display.Info()
        return screen_to_world_rect(pg.Rect(0, 0, window.current_w, window.current_h))

    def follow(self, obj: game_object.GameObject):
        self.follow_object = obj
        self.player_box.center = obj.get_world_rect().center

    def update(self):
        if not self.follow_object:
            return

        follow_rect = self.follow_object.get_world_rect()

        # Ensure the follower's center is always at the center.
        if not self.player_box.collidepoint(pg.Vector2(*follow_rect.center)):
            if follow_rect.center[0] > self.player_box.right:
                self.player_box.right = follow_rect.center[0]
            elif follow_rect.center[0] < self.player_box.left:
                self.player_box.left = follow_rect.center[0]

            if follow_rect.center[1] > self.player_box.bottom:
                self.player_box.bottom = follow_rect.center[1]
            elif follow_rect.center[1] < self.player_box.top:
                self.player_box.top = follow_rect.center[1]

    def get_view_port(self) -> pg.Rect:
        window = pg.display.Info()
        top_left = self.player_box.centerx - (window.current_w / 2)
        top_right = self.player_box.centery - (window.current_h / 2)
        return pg.Rect(top_left, top_right, window.current_w, window.current_h)

    def on_collide(self, other: game_object.GameObject) -> None:
        pass


camera = Camera()


def screen_to_world_vector2(screen_vector: pg.Vector2) -> pg.Vector2:
    camera_port = camera.get_view_port()

    return pg.Vector2(
        camera_port.x + screen_vector.x,
        camera_port.y + screen_vector.y,
    )


def screen_to_world_rect(screen_rect: pg.Rect) -> pg.Rect:
    pos = screen_to_world_vector2(pg.Vector2(screen_rect.x, screen_rect.y))
    dims = screen_to_world_vector2(pg.Vector2(screen_rect.width, screen_rect.height))
    return pg.Rect(*pos, *dims)
