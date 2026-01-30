import pygame as pg

FPS = 60

def main():
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((512, 512), pg.RESIZABLE)

    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        screen.fill((255, 0, 255))
        pg.draw.rect(screen, (255, 0, 0), (200, 200, 50, 50))
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
