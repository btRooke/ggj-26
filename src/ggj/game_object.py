from typing import Protocol
import pygame as pg
from pygame.math import Vector2
from typing import cast


class PointMass:
    """
    Represents a point mass that we can apploy physics to
    """

    _position: pg.Vector2
    _velocity: pg.Vector2
    _accumulative_force: pg.Vector2
    _mass: float
    # todo(tbeatham): drag instead?
    _max_speed: float

    def __init__(self, position: pg.Vector2):
        self._position = position
        # todo(tbeatham) paarameterise this as part of the point mass
        self._mass = 10.0
        self._accumulative_force = pg.Vector2(0, 0)
        self._velocity = pg.Vector2(0, 0)
        self._position = pg.Vector2(0, 0)
        self._max_speed = float("inf")

    def add_force(self, force: pg.Vector2):
        self._accumulative_force += force

    def integrate(self):
        acceleration = self._accumulative_force / self._mass

        prev_velocity = self._velocity.copy()
        self._velocity += acceleration

        # clamp the velocity if at max speed
        if self._max_speed != float("inf") and self._velocity.magnitude() > abs(
            self._max_speed
        ):
            self._velocity = prev_velocity

        self._position += self._velocity
        self._accumulative_force = pg.Vector2(0, 0)

    @property
    def position(self) -> Vector2:
        return self._position

    @property
    def velocity(self) -> Vector2:
        return self._velocity

    def clamp_speed(self, speed: float):
        self._max_speed = speed


class GameObject(Protocol):
    def update(self) -> None: ...
    def get_world_rect(self) -> pg.Rect: ...
