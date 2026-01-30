import logging
import subprocess

import pygame as pg
from ggj import camera as cam
from ggj.ui import UserInterface
from ggj.keys import key_manager, key_map

logging.basicConfig(
    filename="ggj.log",
    filemode="a",
    format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

FPS = 60


def get_move_vector() -> pg.Vector2:
    move_camera = pg.Vector2()
    key_manager.update()

    if key_manager.is_key_down(key_map.player_up):
        move_camera += pg.Vector2(0, -10)
    if key_manager.is_key_down(key_map.player_down):
        move_camera += pg.Vector2(0, 10)
    if key_manager.is_key_down(key_map.player_left):
        move_camera += pg.Vector2(-10, 0)
    if key_manager.is_key_down(key_map.player_right):
        move_camera += pg.Vector2(10, 0)

    return move_camera


def check_types() -> None:
    subprocess.run(["mypy", "-p", "ggj"], check=True)


def main():
    check_types()
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(cam.BASE_RESOLUTION, pg.RESIZABLE)

    done = False

    camera = cam.Camera()
    user_interface = UserInterface()
    logger.info("starting main loop")

    while not done:
        key_manager.update()

        if key_manager.quit():
            done = True
            continue

        screen.fill((255, 0, 255))
        camera.move(get_move_vector())

        pg.draw.rect(
            screen, (255, 0, 0), camera.get_screen_coords(pg.Rect((200, 200, 50, 50)))
        )
        user_interface.draw(screen)
        pg.display.flip()
        clock.tick(FPS)

    user_interface.shutdown()
    pg.quit()


if __name__ == "__main__":
    main()
