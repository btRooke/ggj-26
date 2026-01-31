from functools import lru_cache

import pygame
import pygame as pg

from ggj.assets import STARS_BACKGROUND_PATH
from ggj.camera import Camera
from ggj.player import Player


@lru_cache
def load_star_image():
    return pg.image.load(STARS_BACKGROUND_PATH).convert()


def apply_star_tiles(
    screen: pygame.surface.Surface, camera: Camera, player: Player
) -> None:
    # TODO fix. This is a really bad function but works for now. The proper fix is to shrink parallax things.

    star_image = load_star_image()
    base_rect = star_image.get_rect()

    # roughly estimate what tile we need start  at, just x for now, 0.5 as tiles move half speed when zindex=3
    rough_tile_x = int(player.point_mass.position.x / star_image.get_width() * 0.5)

    # 2xs as tiles are squished together by parallax so compensate
    current_rect = star_image.get_rect()
    for x in range(-3, 3):  # render 3 tiles around player
        current_rect.x = base_rect.x + star_image.get_width() * (x + rough_tile_x) * 2
        for y in range(-3, 3):
            current_rect.y = base_rect.y + star_image.get_height() * y * 2
            screen.blit(
                star_image,
                camera.get_screen_rect(
                    current_rect,
                    zindex=3,
                ),
            )
