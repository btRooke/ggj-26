import logging
import subprocess

import pygame as pg
from ggj import camera as cam

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

    done = False

    logger.info("starting main loop")
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        screen.fill((255, 0, 255))
        pg.draw.rect(
            screen, (255, 0, 0), cam.world_to_screen_rect(pg.Rect(200, 200, 50, 50))
        )
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()

if __name__ == "__main__":
    main()
