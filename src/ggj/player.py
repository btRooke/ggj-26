import pygame as pg
import pygame.transform

from ggj.assets import SPRITE_SHEET_PATH
from ggj.camera import camera, screen_to_world_vector2
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PhysicsBody, PointMass, Drawable
from ggj.world import SurfaceBlock

import logging

logger = logging.getLogger(__name__)

PLAYER_MAX_SPEED = 20
PLAYER_MASS = 10

SPRING_CONSTANT = 0.1
SURFACE_IMPULSE = 300

PLAYER_COLLISION_BUFFER = 2

SPRITE_HEIGHT = 42
SPRITE_WIDTH = 42
SPRITE_SCALE = 4


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
        # logger.debug(f"result force {self._point_mass._accumulative_force}")
        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (self.image.get_width() / 2),
            self._point_mass.position.y - (self.image.get_height() / 2),
            self.image.get_width(),
            self.image.get_height(),
        )

    def _player_movement_action(self) -> bool:
        return key_manager.get_mouse_down_pos() is not None

    def on_collide(self, other: GameObject) -> None:
        player_world_bounds = self.get_world_rect()

        if isinstance(other, SurfaceBlock):
            other_world_bounds = other.get_world_rect()

            if other_world_bounds.clipline(
                (player_world_bounds.centerx, player_world_bounds.y),
                (player_world_bounds.centerx, player_world_bounds.bottom),
            ):
                self._point_mass.position.y = other_world_bounds.top - (
                    self.image.get_height() / 2
                )
                if player_world_bounds.centery < other_world_bounds.centery:
                    if (
                        not self._player_movement_action()
                        and self._point_mass.get_force().y > 0
                    ):
                        self._point_mass.reset_velocty()
                        self._point_mass.add_force(
                            pg.Vector2(0, -self._point_mass.get_force().y)
                        )
                else:
                    impulse = SURFACE_IMPULSE * -self._point_mass.get_force()
                    self._point_mass.add_force(impulse)
                    self._point_mass.reset_velocty()
                    self._point_mass.position.y = (
                        other_world_bounds.bottom + PLAYER_COLLISION_BUFFER
                    ) + (self.image.get_height() / 2)

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
