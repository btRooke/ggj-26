import logging
import subprocess

import pygame as pg
from ggj import camera as cam
from ggj.ui import UserInterface
from ggj.keys import key_manager
from ggj.player import Player
from ggj.camera import camera

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

    user_interface = UserInterface()
    player_group: pg.sprite.Group = pg.sprite.Group()
    player = Player()
    player_group.add(player)
    camera.follow(player)

    logger.info("starting main loop")

    while not done:
        key_manager.update()

        if key_manager.quit():
            done = True
            continue

        screen.fill((255, 0, 255))
        player_group.update()
        pg.draw.rect(
            screen,
            (0, 255, 0),
            camera.get_screen_rect(camera.get_world_rect()),
        )
        pg.draw.rect(
            screen,
            (0, 0, 255),
            camera.get_screen_rect(pg.Rect(20, 20, 20, 20)),
        )
        camera.update()
        player_group.draw(screen)
        user_interface.draw(screen)
        pg.display.flip()
        clock.tick(FPS)

    user_interface.shutdown()
    pg.quit()


if __name__ == "__main__":
    main()
