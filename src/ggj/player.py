import pygame as pg
from ggj.camera import camera, screen_to_world_vector2
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PhysicsBody, PointMass, Drawable
from ggj.world import SurfaceBlock

import logging

logger = logging.getLogger(__name__)

PLAYER_SIZE = 50
PLAYER_MAX_SPEED = 20
PLAYER_MASS = 10

SPRING_CONSTANT = 0.1
SURFACE_IMPULSE = 2000

PLAYER_COLLISION_BUFFER = 20


class Player(pg.sprite.Sprite, GameObject, PhysicsBody):
    _point_mass: PointMass
    image: pg.Surface

    def __init__(self, start_pos: pg.Vector2):
        super().__init__()

        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(pg.Color(255, 0, 0, 0))
        self.rect = self.image.get_rect()
        self._point_mass = PointMass(
            start_pos, PLAYER_MASS, clamp_speed=PLAYER_MAX_SPEED
        )
        self._populate_rect()

    def _populate_rect(self):
        # contains the actual dimension on the screen
        self.rect = camera.get_screen_rect(self.get_world_rect())

    def update(self) -> None:
        force_multiplier = 40
        net_force = pg.Vector2(0, 0)

        if key_manager.is_key_down(key_map.player_down):
            net_force += pg.Vector2(0, 1)
        if key_manager.is_key_down(key_map.player_up):
            net_force += pg.Vector2(0, -1)
        if key_manager.is_key_down(key_map.player_left):
            net_force += pg.Vector2(-1, 0)
        if key_manager.is_key_down(key_map.player_right):
            net_force += pg.Vector2(1, 0)
        self._point_mass.add_force(force_multiplier * net_force)

        if (mouse_down_pos := key_manager.get_mouse_down_pos()) is not None:
            world_pos_mouse = screen_to_world_vector2(pg.Vector2(mouse_down_pos))
            distance = world_pos_mouse - self._point_mass.position
            spring_force = SPRING_CONSTANT * distance
            logger.debug(f"spring applying force {spring_force} distance {distance}")
            self._point_mass.add_force(spring_force)

        self._point_mass.apply_gravity()
        logger.debug(f"result force {self._point_mass._accumulative_force}")
        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (PLAYER_SIZE / 2),
            self._point_mass.position.y - (PLAYER_SIZE / 2),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

    def _player_movement_action(self) -> bool:
        return key_manager.get_mouse_down_pos() is not None

    def on_collide(self, other: GameObject) -> None:
        player_world_bounds = self.get_world_rect()

        if isinstance(other, SurfaceBlock):
            logging.debug("collide with surface")

            other_world_bounds = other.get_world_rect()

            if other_world_bounds.clipline(
                (player_world_bounds.centerx, player_world_bounds.y),
                (player_world_bounds.centerx, player_world_bounds.bottom),
            ):
                # if play performing an action free the player so that it can move
                self._point_mass.position.y = (
                    other_world_bounds.y - PLAYER_COLLISION_BUFFER
                )
                if not self._player_movement_action():
                    self._point_mass.reset_velocty()
                    self._point_mass.add_force(
                        pg.Vector2(0, -self._point_mass.get_force().y)
                    )
            if other_world_bounds.clipline(
                (player_world_bounds.left, player_world_bounds.centery),
                (player_world_bounds.right, player_world_bounds.centery),
            ):
                if (
                    self._point_mass.get_force().x > 0
                    and player_world_bounds.centerx < other_world_bounds.centerx
                ):
                    self._point_mass.reset_velocty()
                    self._point_mass.add_force(
                        pg.Vector2(-self._point_mass.get_force().x, 0)
                    )
                elif (
                    self._point_mass.get_force().x < 0
                    and player_world_bounds.centerx > other_world_bounds.centerx
                ):
                    if key_manager.get_mouse_down_pos() is None:
                        self._point_mass.reset_velocty()
                        self._point_mass.add_force(
                            pg.Vector2(-self._point_mass.get_force().x, 0)
                        )

    @property
    def point_mass(self) -> PointMass:
        return self._point_mass


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
