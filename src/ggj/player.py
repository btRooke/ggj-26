import pygame as pg
from ggj.camera import camera, screen_to_world_vector2
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PointMass, Drawable
from ggj.world import SurfaceBlock

import logging

logger = logging.getLogger(__name__)

PLAYER_SIZE = 50
PLAYER_MAX_SPEED = 25
PLAYER_MASS = 10

SPRING_CONSTANT = 0.001


class Player(pg.sprite.Sprite, GameObject):
    _point_mass: PointMass
    image: pg.Surface
    apply_gravity: bool

    def __init__(self):
        super().__init__()

        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(pg.Color(255, 0, 0, 0))
        self.rect = self.image.get_rect()
        self._point_mass = PointMass(
            pg.Vector2(0, 0), PLAYER_MASS, clamp_speed=PLAYER_MAX_SPEED
        )
        self._populate_rect()
        self.apply_gravity = True

    def _populate_rect(self):
        # contains the actual dimension on the screen
        self.rect = camera.get_screen_rect(self.get_world_rect())

    def update(self) -> None:
        force_multiplier = 2
        net_force = pg.Vector2(0, 0)

        if key_manager.is_key_down(key_map.player_down):
            net_force += pg.Vector2(0, 1)
        if key_manager.is_key_down(key_map.player_up):
            net_force += pg.Vector2(0, -1)
        if key_manager.is_key_down(key_map.player_left):
            net_force += pg.Vector2(-1, 0)
        if key_manager.is_key_down(key_map.player_right):
            net_force += pg.Vector2(1, 0)

        if (mouse_down_pos := key_manager.get_mouse_down_pos()) is not None:
            world_pos_mouse = screen_to_world_vector2(pg.Vector2(mouse_down_pos))
            distance = world_pos_mouse - self._point_mass.position
            spring_force = SPRING_CONSTANT * distance
            logger.debug(f"applying force {spring_force}")
            self._point_mass.add_force(spring_force)

        if self.apply_gravity:
            self._point_mass.apply_gravity()
        self._point_mass.add_force(force_multiplier * net_force)
        self._point_mass.integrate()

        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (PLAYER_SIZE / 2),
            self._point_mass.position.y - (PLAYER_SIZE / 2),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

    def on_collide(self, other: GameObject) -> None:
        if isinstance(other, SurfaceBlock):
            player_rect = self.get_world_rect()
            other_rect = other.get_world_rect()

            logging.debug("collide with surface")
            self.apply_gravity = False

            if player_rect.clipline(other_rect.topleft, other_rect.topright):
                # equal and opposite reaction
                self._point_mass.add_force(
                    pg.Vector2(-self._point_mass.get_force().y, 0)
                )
                self._point_mass.reset_velocty()
                logging.debug("collide top")


class GrapplingHook(Drawable):
    player: Player

    def __init__(self, player: Player) -> None:
        self.player = player

    def draw(self, screen: pg.Surface) -> None:
        if (mouse_pos := key_manager.get_mouse_down_pos()) is None:
            return

        player_world_rect = self.player.get_world_rect()

        start_coords = camera.get_screen_rect(pg.Rect(*player_world_rect.center, 0, 0))
        mouse_pos_world = screen_to_world_vector2(pg.Vector2(*mouse_pos))
        end_coords = camera.get_screen_rect(
            pg.Rect(mouse_pos_world.x, mouse_pos_world.y, 0, 0)
        )
        pg.draw.line(
            screen,
            (255, 0, 0),
            (start_coords.x, start_coords.y),
            (end_coords.x, end_coords.y),
        )
