from functools import lru_cache

import pygame
import pygame as pg

from ggj.assets import STARS_BACKGROUND_PATH, MARS_PATH
from ggj.camera import Camera
from ggj.player import Player

init_mars_pos = None


@lru_cache
def load_star_image() -> pg.Surface:
    i = pg.image.load(STARS_BACKGROUND_PATH).convert()
    return pygame.transform.scale_by(i, 1.8)


@lru_cache
def load_mars_image() -> pg.Surface:
    i = pg.image.load(MARS_PATH).convert_alpha()
    i = pygame.transform.scale_by(i, 4)
    return i


def apply_mars(screen: pygame.surface.Surface, camera: Camera, player: Player):
    mars = load_mars_image()

    global init_mars_pos

    if init_mars_pos is None:
        mars_rect = mars.get_rect()
        mars_rect.x = int(player.point_mass.position.x - mars.get_width() / 2)
        mars_rect.y += int(mars.get_height() * 1.5)
        init_mars_pos = mars_rect

    screen.blit(
        mars,
        camera.get_screen_rect(
            init_mars_pos,
            zindex=2,
        ),
    )


def apply_star_tiles(
    screen: pygame.surface.Surface, camera: Camera, player: Player
) -> None:
    # TODO fix. This is a really bad function but works for now. The proper fix is to shrink parallax things.

    star_image = load_star_image()
    star_image.get_rect()
    base_rect = star_image.get_rect()

    # roughly estimate what tile we need start  at, just x for now, 0.5 as tiles move half speed when zindex=3
    rough_tile_x = int(player.point_mass.position.x / star_image.get_width() * 0.5)

    # 2xs as tiles are squished together by parallax so compensate
    current_rect = star_image.get_rect()
    for x in range(-8, 10):  # render some tiles around player
        current_rect.x = base_rect.x + star_image.get_width() * (x + rough_tile_x) * 2
        for y in range(-8, 10):
            current_rect.y = base_rect.y + star_image.get_height() * y * 2
            screen.blit(
                star_image,
                camera.get_screen_rect(
                    current_rect,
                    zindex=3,
                ),
            )
