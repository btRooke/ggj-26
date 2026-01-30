import pygame as pg

BASE_RESOLUTION = (1280, 720)


def world_to_screen_rect(world_rect: pg.Rect) -> pg.Rect:
    size_multiplier_x = pg.display.get_window_size()[0] / BASE_RESOLUTION[0]
    size_multiplier_y = pg.display.get_window_size()[1] / BASE_RESOLUTION[1]

    return world_rect.scale_by(size_multiplier_x, size_multiplier_y)


class Camera:
    position: pg.Vector2

    def __init__(self) -> None:
        self.position = pg.math.Vector2(0, 0)

    def set_position(self, position: pg.Vector2) -> None:
        self.position = position

    def get_relative(self, position: pg.Vector2) -> pg.Vector2:
        """Draw an object relative to the camera's position"""
        return position - self.position

    def move(self, move: pg.Vector2) -> None:
        self.position += move

    def get_screen_coords(self, rect: pg.Rect) -> pg.Rect:
        rect_vector2 = pg.Vector2(rect.x, rect.y)
        relative_cam = self.get_relative(rect_vector2)
        return world_to_screen_rect(pg.Rect((*relative_cam, rect.width, rect.height)))
