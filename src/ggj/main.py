import logging
import subprocess

import pygame as pg
from ggj import camera as cam
from ggj.ui import UserInterface
from ggj.keys import key_manager
from ggj.player import Player, GrapplingHook
from ggj.camera import camera
from ggj.game_object import GameObjectTracer
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

    user_interface = UserInterface(screen)
    object_group: pg.sprite.Group = pg.sprite.Group()
    player = Player()
    object_group.add(player)
    camera.follow(player)

    blocks = [SurfaceBlock(pg.Vector2(0, 500))]
    tracer = GameObjectTracer(player, blocks)

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
        tracer.update()
        object_group.update()
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
