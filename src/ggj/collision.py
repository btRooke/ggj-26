from typing import Optional
import pygame as pg
from pygame.time import wait


class CollisionObjects:
    """Contains a mapping between a type and a group of collidable sprites"""

    # contains a mapping between the type that is in the group
    # and a group that the player can collide with.
    objects: dict[type, pg.sprite.Group]

    def __init__(self):
        self.objects = {}

    def get(self, t: type) -> Optional[pg.sprite.Group]:
        return self.objects.get(t)

    def register(self, t: type, sprite_group: pg.sprite.Group) -> None:
        self.objects[t] = sprite_group


collision_object_manager = CollisionObjects()


def point_collide_group(
    point: pg.Vector2, group: pg.sprite.Group
) -> list[pg.sprite.Sprite]:
    """Utility method for checking if a single point collides a group"""

    class DummySprite(pg.sprite.Sprite):
        """DummySprite that we can use to check for a collision"""

        MOUSE_SIZE = (4, 4)

        def __init__(self, *_: pg.sprite.Group):
            super().__init__()
            self.image = pg.Surface(DummySprite.MOUSE_SIZE)
            self.rect = pg.Rect(
                point.x,
                point.y - DummySprite.MOUSE_SIZE[1] / 2,
                *DummySprite.MOUSE_SIZE,
            )

    return pg.sprite.spritecollide(DummySprite(), group, False)
