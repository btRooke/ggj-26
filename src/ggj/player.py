import pygame as pg
import pygame.transform
from typing import cast

from ggj.assets import SPRITE_SHEET_PATH
from ggj.camera import camera, screen_to_world_vector2
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PhysicsBody, PointMass, Drawable
from ggj.world import SurfaceBlock
from ggj.collision import collision_object_manager

import logging

logger = logging.getLogger(__name__)

PLAYER_MAX_SPEED = 20
PLAYER_MASS = 10

SPRING_CONSTANT = 0.1

PLAYER_COLLISION_BUFFER = 20

SPRITE_HEIGHT = 42
SPRITE_WIDTH = 42
SPRITE_SCALE = 4

JUMP_FORCE = pg.Vector2(0, -400)

WALKING_FORCE_MULTIPLIER = 20

FRICTION_MULTIPLIER = 2
AIR_RESIST_MULTIPLIER = 0.25


def _load_sprite_sheet() -> list[pg.Surface]:
    sheet = pg.image.load(SPRITE_SHEET_PATH).convert_alpha()

    if sheet.get_width() % SPRITE_WIDTH != 0 or sheet.get_height() != SPRITE_HEIGHT:
        raise ValueError(f"Sprite sheet has wrong dims, {sheet.get_rect()}")

    sprites = []
    # sprites.append(sheet)

    for i in range(0, sheet.get_width(), SPRITE_WIDTH):
        # create blank surface for sprite
        sprite = pygame.surface.Surface((SPRITE_HEIGHT, SPRITE_WIDTH), pygame.SRCALPHA)

        # blit the correct part to it
        pygame.transform.chop(
            sheet, pygame.rect.Rect(i, 0, SPRITE_WIDTH, SPRITE_HEIGHT)
        )
        rect = sprite.get_rect()
        rect.x = i
        sprite.blit(sheet, dest=(0, 0), area=rect)

        # scale and append
        sprites.append(pygame.transform.scale_by(sprite, SPRITE_SCALE))

    return sprites


class Player(pg.sprite.Sprite, GameObject, PhysicsBody):
    _point_mass: PointMass
    image: pg.Surface

    def __init__(self, start_pos: pg.Vector2):
        super().__init__()

        self.sprites = _load_sprite_sheet()
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self._point_mass = PointMass(
            start_pos,
            PLAYER_MASS,
        )
        self._populate_rect()

    def _populate_rect(self):
        # contains the actual dimension on the screen
        self.rect = camera.get_screen_rect(self.get_world_rect())

    def _can_walk_right(self, surfaces: list[GameObject]) -> bool:
        player_world_bounds = self.get_world_rect()
        for surface in surfaces:
            other_world_bounds = surface.get_world_rect()

            if other_world_bounds.clipline(
                (player_world_bounds.centerx, player_world_bounds.centery),
                (player_world_bounds.right, player_world_bounds.centery),
            ):
                return False

        return True

    def _can_walk_left(self, surfaces: list[GameObject]) -> bool:
        player_world_bounds = self.get_world_rect()
        for surface in surfaces:
            other_world_bounds = surface.get_world_rect()

            if other_world_bounds.clipline(
                (player_world_bounds.centerx, player_world_bounds.centery),
                (player_world_bounds.left, player_world_bounds.centery),
            ):
                return False
        return True

    def update(self) -> None:
        walking_force = pg.Vector2(0, 0)

        # check for collisions against surfaces
        surface_tracer = collision_object_manager.get(SurfaceBlock)
        collide_surfaces = []
        if surface_tracer is not None:
            collide_surfaces = surface_tracer.get_collisions(self)

        if (
            (
                self._point_mass.velocity.x >= 0
                or abs(self._point_mass.velocity.x) < PLAYER_MAX_SPEED
            )
            and self._can_walk_left(collide_surfaces)
        ) and key_manager.is_key_down(key_map.player_left):
            walking_force += pg.Vector2(-1, 0)

        if (
            (
                self._point_mass.velocity.x <= 0
                or abs(self._point_mass.velocity.x) < PLAYER_MAX_SPEED
            )
            and self._can_walk_right(collide_surfaces)
        ) and key_manager.is_key_down(key_map.player_right):
            walking_force += pg.Vector2(1, 0)

        air_resist_force = (
            pg.Vector2(-self._point_mass.velocity.x, 0) * AIR_RESIST_MULTIPLIER
        )
        self._point_mass.add_force(air_resist_force)
        self._point_mass.add_force(WALKING_FORCE_MULTIPLIER * walking_force)

        if (mouse_down_pos := key_manager.get_mouse_down_pos()) is not None:
            world_pos_mouse = screen_to_world_vector2(pg.Vector2(*mouse_down_pos))
            distance = world_pos_mouse - self._point_mass.position
            spring_force = SPRING_CONSTANT * distance
            logger.debug(f"spring applying force {spring_force} distance {distance}")
            self._point_mass.add_force(spring_force)

        self._point_mass.apply_gravity()

        # check for collisions against surfaces
        for surface in collide_surfaces:
            self._on_collide_surface(cast(SurfaceBlock, surface))

        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (self.image.get_width() / 2),
            self._point_mass.position.y - (self.image.get_height() / 2),
            self.image.get_width(),
            self.image.get_height(),
        )

    def _is_player_jumping(self) -> bool:
        return key_manager.is_key_down(key_map.player_jump)

    def _is_grappling_hook(self) -> bool:
        return key_manager.get_mouse_down_pos() is not None

    def _is_player_walking(self) -> bool:
        return key_manager.is_key_down(key_map.player_left) or key_manager.is_key_down(
            key_map.player_right
        )

    def _player_movement_action(self) -> bool:
        return key_manager.get_mouse_down_pos() is not None or key_manager.is_key_down(
            key_map.player_jump
        )

    def _on_collide_surface(self, surface: SurfaceBlock) -> None:
        player_world_bounds = self.get_world_rect()
        other_world_bounds = surface.get_world_rect()
        if other_world_bounds.clipline(
            (player_world_bounds.centerx, player_world_bounds.y),
            (player_world_bounds.centerx, player_world_bounds.bottom),
        ):
            if self._player_movement_action():
                if self._is_player_jumping():
                    logging.debug(self._point_mass._accumulative_force)
                    self._point_mass.add_force(JUMP_FORCE)
                    logging.debug("player performed jump")
                self._point_mass.position.y -= PLAYER_COLLISION_BUFFER
            else:
                self._point_mass.add_force(
                    pg.Vector2(0, -self._point_mass.get_force().y)
                )
            self._point_mass.position.y = other_world_bounds.top - (
                player_world_bounds.height / 2
            )

        if other_world_bounds.clipline(
            (player_world_bounds.left, player_world_bounds.centery),
            (player_world_bounds.right, player_world_bounds.centery),
        ):
            friction_force = (
                pg.Vector2(-self._point_mass.velocity.x, 0) * FRICTION_MULTIPLIER
            )
            self._point_mass.add_force(friction_force)

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
        pg.draw.line(
            screen,
            (255, 0, 0),
            (start_coords.x, start_coords.y),
            mouse_pos,
        )
