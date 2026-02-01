import logging
import subprocess
from typing import cast

import pygame as pg
import pygame.mixer_music

from ggj import camera as cam
from ggj.assets import THEME_PATH
from ggj.background import apply_star_tiles, apply_mars
from ggj.constants import FPS
from ggj.map.importer import surface_blocks
from ggj.telegraph import TeleGraph, telegraph_placer
from ggj.ui import UserInterface
from ggj.keys import key_manager
from ggj.player import GrapplingHook, Player
from ggj.camera import camera
from ggj.game_object import GameObject, PhysicsBody
from ggj.collision import GameObjectTracer, collision_object_manager
from ggj.world import SurfaceBlock, map_to_world_coords

logging.basicConfig(
    filename="ggj.log",
    filemode="w",
    format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


def check_types() -> None:
    subprocess.run(["mypy", "-p", "ggj"], check=True)


def main():
    check_types()
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(cam.BASE_RESOLUTION, pg.RESIZABLE)
    pg.display.set_caption("Stickney Lineman")

    done = False

    # theme

    music = pygame.mixer.Sound(THEME_PATH)
    music.play(loops=-1)

    # only render the 1/4 of the surface blocks

    surface_block_vectors = surface_blocks().surface_blocks
    surface_block_vectors.sort(key=lambda b: (b.x, b.y))
    surface_block_vectors = surface_block_vectors[: len(surface_block_vectors)]
    blocks = [SurfaceBlock(v) for v in surface_block_vectors]

    # user interface

    user_interface = UserInterface(screen, surface_blocks().location_markers)
    object_group: pg.sprite.Group = pg.sprite.Group()

    # player stuff

    player_init_pos = map_to_world_coords(pg.Vector2(750, 60))
    player = Player(player_init_pos)
    object_group.add(player)
    object_group.add(TeleGraph(player._point_mass.position.copy()))
    camera.follow(player)
    object_group.add(*telegraph_placer.poles)

    tracer = GameObjectTracer(cast(list[GameObject], blocks))
    collision_object_manager.register(SurfaceBlock, tracer)

    physics_bodies: list[PhysicsBody] = [player]

    object_group.add(*blocks)
    grapling_hook = GrapplingHook(player)
    logger.info("starting main loop")

    while not done:
        key_manager.update()

        if key_manager.quit():
            done = True
            continue

        screen.fill((255, 0, 255))
        apply_star_tiles(screen, camera, player)
        apply_mars(screen, camera, player)
        object_group.update()
        for body in physics_bodies:
            body.point_mass.integrate()
        object_group.draw(screen)
        pg.draw.rect(
            screen,
            (0, 0, 255),
            camera.get_screen_rect(
                pg.Rect(80, 80, 200, 200),
                zindex=2,
            ),
        )
        camera.update()
        grapling_hook.draw(screen)
        user_interface.draw(screen)
        user_interface.update(player.point_mass.position)
        pg.display.flip()
        clock.tick(FPS)

    user_interface.shutdown()
    pg.quit()


if __name__ == "__main__":
    main()
