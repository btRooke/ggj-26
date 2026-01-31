import logging
import subprocess
from typing import cast

import pygame as pg
from ggj import camera as cam
from ggj.background import apply_star_tiles
from ggj.map.importer import surface_blocks
from ggj.ui import UserInterface
from ggj.keys import key_manager
from ggj.player import GrapplingHook, Player
from ggj.camera import camera
from ggj.game_object import GameObject, PhysicsBody
from ggj.collision import GameObjectTracer
from ggj.world import SurfaceBlock, map_to_world_coords

logging.basicConfig(
    filename="ggj.log",
    filemode="w",
    format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

FPS = 60


def check_types() -> None:
    subprocess.run(["mypy", "-p", "ggj"], check=True)


def main():
    check_types()
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(cam.BASE_RESOLUTION, pg.RESIZABLE)
    pg.display.set_caption("Stickney Lineman")

    done = False

    surface_block_vectors = surface_blocks()

    # only render the 1/4 of the surface blocks
    surface_block_vectors.sort(key=lambda b: (b.x, b.y))
    surface_block_vectors = surface_block_vectors[: len(surface_block_vectors)]

    blocks = [SurfaceBlock(v) for v in surface_block_vectors]

    user_interface = UserInterface(screen)
    object_group: pg.sprite.Group = pg.sprite.Group()

    player_init_pos = map_to_world_coords(pg.Vector2(0, 0))  # pg.Vector2(750, 60))
    player = Player(player_init_pos)
    object_group.add(player)
    camera.follow(player)

    tracer = GameObjectTracer(player, cast(list[GameObject], blocks))

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
        object_group.update()
        tracer.update()
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
        pg.display.flip()
        clock.tick(FPS)

    user_interface.shutdown()
    pg.quit()


if __name__ == "__main__":
    main()
