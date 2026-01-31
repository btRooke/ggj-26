from typing import Protocol
import pygame as pg


class GameObject(Protocol):
    def update(self) -> None: ...
    def get_world_rect(self) -> pg.Rect: ...
