import logging
import subprocess

import pygame as pg
from ggj import camera as cam
from ggj.map.importer import surface_blocks
from ggj.ui import UserInterface
from ggj.keys import key_manager
from ggj.player import Player, GrapplingHook
from ggj.camera import camera
from ggj.game_object import GameObjectTracer, PhysicsBody
from ggj.world import SurfaceBlock


logging.basicConfig(
    filename="ggj.log",
    filemode="a",
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

    # only render the 1/4 of the surface blocks, prioritise LHS of map
    surface_block_vectors.sort(key=lambda b: b.x)
    surface_block_vectors = surface_block_vectors[: len(surface_block_vectors) // 4]

    blocks = [SurfaceBlock(v) for v in surface_block_vectors]

    user_interface = UserInterface(screen)
    object_group: pg.sprite.Group = pg.sprite.Group()

    player_init_pos = surface_block_vectors[0].copy()
    player_init_pos.y -= 1
    player = Player(player_init_pos)
    object_group.add(player)
    camera.follow(player)

    tracer = GameObjectTracer(player, blocks)

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
        pg.draw.rect(
            screen,
            (0, 125, 255),
            camera.get_screen_rect(
                pg.Rect(80, 80, 200, 200),
                zindex=2,
            ),
        )
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
                zindex=-1,
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
