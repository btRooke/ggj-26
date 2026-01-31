from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

import pygame as pg

WORLD_PNG_PATH = Path(__file__).parent / "world.png"


@lru_cache
def world_rgb_array():
    im = Image.open(WORLD_PNG_PATH)

    print(im.format, im.size, im.mode)

    assert im.format == "PNG"
    assert im.mode == "RGB"

    return np.asarray(im)


@lru_cache
def world_array():
    rgb_array = world_rgb_array()
    r_array = np.zeros(list(rgb_array.shape)[:2], dtype=np.uint8)

    i_max, j_max = r_array.shape

    for i in range(i_max):
        for j in range(j_max):
            r_array[i][j] = rgb_array[i][j][0]

    return r_array


def surface_blocks() -> list[pg.Vector2]:
    w_array = world_array()

    rock_locations = []

    i_max, j_max = w_array.shape

    for i in range(i_max):
        for j in range(j_max):
            if w_array[i][j] == 0:
                rock_locations.append(pg.Vector2(j, i))

    return rock_locations
