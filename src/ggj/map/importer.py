from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image

import pygame as pg
from pygame import Vector2

WORLD_PNG_PATH = Path(__file__).parent / "world.png"


@lru_cache
def world_rgb_array():
    """Load world RGB array."""
    im = Image.open(WORLD_PNG_PATH)

    assert im.format == "PNG"
    assert im.mode == "RGB"

    return np.asarray(im)


@lru_cache
def world_array():
    """Load world array, just 2D array of uint8s."""
    rgb_array = world_rgb_array()
    r_array = np.zeros(list(rgb_array.shape)[:2], dtype=np.uint8)

    i_max, j_max = r_array.shape

    for i in range(i_max):
        for j in range(j_max):
            r_array[i][j] = rgb_array[i][j][0]

    return r_array


class MapItems(NamedTuple):
    surface_blocks: list[pg.Vector2]
    mock_surface_blocks: list[pg.Vector2]
    location_markers: dict[str, list[Vector2]]


@lru_cache
def surface_blocks() -> MapItems:
    w_array = world_array()

    locations = {
        0xA0: "Limtoc crater",
        0xA1: "Stickney east",
        0xA2: "Stickney west",
        0xA3: "The monolith",
        0xA4: "The base",
    }

    rock_locations = []
    mock_rock_locations = []
    location_markers: dict[str, list[pg.Vector2]] = {k: [] for k in locations.values()}

    i_max, j_max = w_array.shape

    for i in range(i_max):
        for j in range(j_max):
            val = w_array[i][j]
            match val & 0xF0:
                case 0:
                    rock_locations.append(pg.Vector2(j, i))
                case 0xF0:
                    if val == 0xF0:  # TODO fix hack, change 0xF0 for mock block
                        mock_rock_locations.append(pg.Vector2(j, i))
                case 0xA0:
                    location_markers[locations[val]].append(pg.Vector2(j, i))

    return MapItems(rock_locations, mock_rock_locations, location_markers)
