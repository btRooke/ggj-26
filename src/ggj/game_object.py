from __future__ import annotations
from typing import Protocol
import pygame as pg
from pygame.math import Vector2
import logging

GRAVITY = pg.Vector2(0, 10)

logger = logging.getLogger(__name__)


class PointMass:
    """
    Represents a point mass that we can apply physics to
    """

    position: pg.Vector2
    _velocity: pg.Vector2
    _accumulative_force: pg.Vector2
    _mass: float
    _rigid_multiplier: pg.Vector2

    def __init__(self, position: pg.Vector2, mass: float):
        self.position = position
        self._mass = mass
        self._accumulative_force = pg.Vector2(0, 0)
        self._velocity = pg.Vector2(0, 0)
        self._rigid_multiplier = pg.Vector2(1, 1)

    def add_force(self, force: pg.Vector2):
        self._accumulative_force += force

    def apply_gravity(self):
        self._accumulative_force += GRAVITY

    def get_force(self) -> pg.Vector2:
        return self._accumulative_force

    def integrate(self):
        # logger.debug(f"applying force {self._accumulative_force}")
        self._accumulative_force = (
            self._accumulative_force.elementwise() * self._rigid_multiplier
        )
        acceleration = self._accumulative_force / self._mass
        self._velocity += acceleration

        self.position += self._velocity
        self._accumulative_force = pg.Vector2(0, 0)

    def reset_velocty(self):
        self._velocity = pg.Vector2()

    @property
    def velocity(self) -> Vector2:
        return self._velocity

    def make_rigid_y(self, rigid_y=True):
        self._rigid_multiplier.y = 0 if rigid_y else 1
        self._velocity.y = 0


class GameObject(Protocol):
    @property
    def world_rect(self) -> pg.Rect: ...


class PhysicsBody(Protocol):
    @property
    def point_mass(self) -> PointMass: ...


class Drawable(Protocol):
    """
    Represents something in the world
    that requires a draw. This is different
    from a sprite as it may not necessarily be an
    image.
    """

    def draw(self, screen: pg.Surface) -> None: ...
