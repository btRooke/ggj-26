import pygame as pg

BASE_RESOLUTION = (1280, 720)


def world_to_screen_rect(world_rect: pg.Rect) -> pg.Rect:
    size_multiplier_x = pg.display.get_window_size()[0] / BASE_RESOLUTION[0]
    size_multiplier_y = pg.display.get_window_size()[1] / BASE_RESOLUTION[1]

    return world_rect.scale_by(size_multiplier_x, size_multiplier_y)
