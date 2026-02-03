from typing import Optional
import pygame as pg


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
