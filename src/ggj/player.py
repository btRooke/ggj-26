import enum
import pygame as pg
import pygame.transform
from typing import cast

from ggj.camera import camera, screen_to_world_vector2
from ggj.assets import SPRITE_SHEET_PATH, GRAPPLE_PATH, WALKING_PATH
from ggj.constants import FPS
from ggj.keys import key_manager, key_map
from ggj.game_object import GameObject, PhysicsBody, PointMass, Drawable
from ggj.world import SURFACE_BLOCK_SIZE, SurfaceBlock
from ggj.collision import collision_object_manager
from ggj.telegraph import telegraph_placer
import logging

logger = logging.getLogger(__name__)

PLAYER_MAX_SPEED = 20
PLAYER_MASS = 10

SPRING_CONSTANT = 0.1

SPRITE_HEIGHT = 42
SPRITE_WIDTH = 42
SPRITE_SCALE = 4

SPRITE_WALKING_BOB_PX = 8
SPRITE_WALKING_FREQUENCY = (
    7  # frequency of change of sprite, not whole animation unfortunately
)
WALKING_ANIMATION_X_SPEED = 1.5

JUMP_FORCE = pg.Vector2(0, -400)

WALKING_FORCE_MULTIPLIER = 20

FRICTION_MULTIPLIER = 0.25
AIR_RESIST_MULTIPLIER = 0.75
WALKING_SPRITE_COUNT = 2


class FacingDirection(enum.Enum):
    RIGHT = 1
    LEFT = 2


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
        rect = sprite.get_rect()
        rect.x = i
        sprite.blit(sheet, dest=(0, 0), area=rect)

        # scale and append
        sprites.append(pygame.transform.scale_by(sprite, SPRITE_SCALE))

    # push the second walking sprite down a bit
    sprites[1].scroll(dy=SPRITE_WALKING_BOB_PX)
    return sprites


class Player(pg.sprite.Sprite, GameObject, PhysicsBody):
    _point_mass: PointMass
    image: pg.Surface

    def __init__(self, start_pos: pg.Vector2):
        super().__init__()

        self._animation_ticks_count = 0

        # sound fx

        self.grapple_sound = pygame.mixer.Sound(GRAPPLE_PATH)
        self.grapple_sound.set_volume(0.1)
        self.walking_sound = pygame.mixer.Sound(WALKING_PATH)
        self.walking_sound.set_volume(0.06)

        # sprite and animation stuff, first load sheet and generate left and right sprites

        all_sprites = _load_sprite_sheet()
        self._right_walking_sprites = all_sprites[:WALKING_SPRITE_COUNT]
        self._left_walking_sprites = [
            pygame.transform.flip(s, flip_x=True, flip_y=False)
            for s in self._right_walking_sprites
        ]
        self._walking_sprites = self._right_walking_sprites
        self._direction = FacingDirection.RIGHT
        self.grappling_sprite = all_sprites[WALKING_SPRITE_COUNT]
        self._current_walking_sprite_index = 0

        self.image = self._walking_sprites[self._current_walking_sprite_index]

        # other stuff

        self.rect = self.image.get_rect()
        self._point_mass = PointMass(
            start_pos,
            PLAYER_MASS,
        )
        self._populate_rect()

    def _populate_rect(self):
        screen_rect = camera.get_screen_rect(self.get_world_rect())
        self.rect.bottom = screen_rect.bottom
        self.rect.centerx = screen_rect.centerx

    def _place_telegraph(self) -> None:
        assert (right_pos := key_manager.get_right_up_pos()) is not None
        position = screen_to_world_vector2(pg.Vector2(*right_pos))
        telegraph_placer.add(position)

    def _handle_animations(self):
        """Must be called every tick."""
        self._animation_ticks_count += 1

        # set correct sprite sheet

        match self._direction:
            case FacingDirection.LEFT:
                self._walking_sprites = self._left_walking_sprites
            case FacingDirection.RIGHT:
                self._walking_sprites = self._right_walking_sprites
            case default:
                raise ValueError(f"unknown direction {default}")

        # animations

        if self._is_moving():
            self.walking_sound.play(loops=-1)
            if (
                self._animation_ticks_count % (int(FPS * SPRITE_WALKING_FREQUENCY**-1))
                == 0
            ):
                self._current_walking_sprite_index = (
                    self._current_walking_sprite_index + 1
                ) % WALKING_SPRITE_COUNT
                self.image = self._walking_sprites[self._current_walking_sprite_index]

        elif self._is_grappling_hook():
            self.image = self.grappling_sprite
        else:
            self.walking_sound.stop()
            self.image = self._walking_sprites[self._current_walking_sprite_index]

    def update(self) -> None:
        self._handle_animations()
        walking_force = pg.Vector2(0, 0)

        # check for collisions against surfaces
        surfaces = collision_object_manager.get(SurfaceBlock)
        collide_surfaces = []
        if surfaces is not None:
            collide_surfaces = pg.sprite.spritecollide(self, surfaces, False)
        if (
            self._point_mass.velocity.x >= 0
            or abs(self._point_mass.velocity.x) < PLAYER_MAX_SPEED
        ) and key_manager.is_key_down(key_map.player_left):
            walking_force += pg.Vector2(-1, 0)
            self._direction = FacingDirection.LEFT

        if (
            self._point_mass.velocity.x <= 0
            or abs(self._point_mass.velocity.x) < PLAYER_MAX_SPEED
        ) and key_manager.is_key_down(key_map.player_right):
            walking_force += pg.Vector2(1, 0)
            self._direction = FacingDirection.RIGHT

        air_resist_force = -self._point_mass.velocity * AIR_RESIST_MULTIPLIER
        self._point_mass.add_force(air_resist_force)
        self._point_mass.add_force(WALKING_FORCE_MULTIPLIER * walking_force)

        if (mouse_down_pos := key_manager.get_mouse_down_pos()) is not None:
            self.grapple_sound.play()
            world_pos_mouse = screen_to_world_vector2(pg.Vector2(*mouse_down_pos))
            distance = world_pos_mouse - self._point_mass.position
            spring_force = SPRING_CONSTANT * distance
            logger.debug(f"spring applying force {spring_force} distance {distance}")
            self._point_mass.add_force(spring_force)

        self._point_mass.apply_gravity()

        for surface in collide_surfaces:
            self._on_collide_surface(cast(SurfaceBlock, surface))

        if key_manager.get_right_up_pos() is not None:
            self._place_telegraph()

        self._populate_rect()

    def get_world_rect(self) -> pg.Rect:
        return pg.Rect(
            round(self._point_mass.position.x - (SURFACE_BLOCK_SIZE[0] / 2)),
            round(self._point_mass.position.y - (SURFACE_BLOCK_SIZE[0] / 2)),
            *SURFACE_BLOCK_SIZE,
        )

    def _is_moving(self):
        return abs(self._point_mass.velocity.x) > WALKING_ANIMATION_X_SPEED

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

        # check for collision above the player
        if other_world_bounds.clipline(
            (player_world_bounds.centerx, player_world_bounds.centery),
            (player_world_bounds.centerx, player_world_bounds.top),
        ):
            self._point_mass.velocity.y = 0
            self._point_mass.position.y = other_world_bounds.bottom + (
                SURFACE_BLOCK_SIZE[1] / 2
            )
            # only apply if the force is going down, if we are jumping we want to
            # remove away from the object.
            if self._point_mass.get_force().y < 0:
                self._point_mass.add_force(
                    pg.Vector2(0, -self._point_mass.get_force().y)
                )

        # check for collision below the player
        if other_world_bounds.clipline(
            (player_world_bounds.centerx, player_world_bounds.centery),
            (player_world_bounds.centerx, player_world_bounds.bottom),
        ):
            if self._is_player_jumping():
                logging.debug(self._point_mass._accumulative_force)
                self._point_mass.add_force(JUMP_FORCE)

            self._point_mass.velocity.y = 0
            self._point_mass.position.y = other_world_bounds.top - (
                SURFACE_BLOCK_SIZE[1] / 2
            )
            # only apply if the force is going down, if we are jumping we want to
            # remove away from the object.
            if self._point_mass.get_force().y > 0:
                self._point_mass.add_force(
                    pg.Vector2(0, -self._point_mass.get_force().y)
                )
            friction_force = (
                pg.Vector2(-self._point_mass.velocity.x, 0) * FRICTION_MULTIPLIER
            )
            self._point_mass.add_force(friction_force)
            logger.debug(f"accumulative force: {self._point_mass._accumulative_force}")
        # we are to the right of the surface.
        if other_world_bounds.clipline(
            (player_world_bounds.left, player_world_bounds.centery),
            (player_world_bounds.centerx, player_world_bounds.centery),
        ):
            self._point_mass.velocity.x = 0
            # only apply the force if the force is going into this object
            if self._point_mass.get_force().x < 0:
                self._point_mass.add_force(
                    pg.Vector2(-self._point_mass.get_force().x, 0)
                )

        # we are to the left of the object
        if other_world_bounds.clipline(
            (player_world_bounds.right, player_world_bounds.centery),
            (player_world_bounds.centerx, player_world_bounds.centery),
        ):
            self._point_mass.velocity.x = 0
            if self._point_mass.get_force().x > 0:
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
        pg.draw.line(
            screen,
            (255, 0, 0),
            (start_coords.x, start_coords.y),
            mouse_pos,
        )
