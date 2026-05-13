from ggj.game_object import Drawable, GameObject, PointMass
import pygame as pg
import logging
from ggj.camera import camera, screen_to_world_vector2
import heapq
from ggj.collision import collision_object_manager
from ggj.world import SurfaceBlock

logger = logging.getLogger(__name__)

TELEGRAPH_DIMS = (10, 300)
POLE_COLOUR = (211, 211, 211)
WIRE_COLOUR = (255, 0, 0)

# maximum distance between any two poles in the game.
MAX_POLES_DISTANCE = 800


class TeleGraph(pg.sprite.Sprite, GameObject):
    _point_mass: PointMass

    def __init__(self, position: pg.Vector2):
        pg.sprite.Sprite.__init__(self)
        self._point_mass = PointMass(position, 20)
        self.image = pg.Surface(TELEGRAPH_DIMS)
        self.image.fill(POLE_COLOUR)

    def _populate_rect(self):
        self.rect = camera.get_screen_rect(self.world_rect)

    def update(self) -> None:
        self._populate_rect()

    @property
    def world_rect(self) -> pg.Rect:
        return pg.Rect(
            self._point_mass.position.x - (TELEGRAPH_DIMS[0] / 2),
            self._point_mass.position.y - (TELEGRAPH_DIMS[1] / 2),
            *TELEGRAPH_DIMS,
        )

    def __lt__(self, other):
        # order by displacement from the origin.
        return (self._point_mass.position.x, self._point_mass.position.y).__lt__(
            (other._point_mass.position.x, other._point_mass.position.y)
        )


class TeleGraphPolePlacer:
    # heap of all poles in poles in the game
    _poles: list[TeleGraph]
    _unused_poles: list[TeleGraph]

    def __init__(self):
        self._poles = []
        self._unused_poles = [
            TeleGraph(pg.Vector2(10000000, 1000000)) for _ in range(100)
        ]

    def add(self, position: pg.Vector2):
        """Add a telegraph at the mouse position.

        Args:
            position: position of the mouse on the screen.
        """
        # maintain poles by position for comparison
        world_pos = screen_to_world_vector2(position)
        logger.debug(
            f"adding telegraph at screen pos: {position}, world pos: {world_pos}"
        )
        pole = self._unused_poles.pop()
        prev_pos = pole._point_mass.position

        # temporarily modify the display of the pole to check for collision
        pole._point_mass.position = world_pos
        pole.rect.x = round(position.x)
        pole.rect.y = round(position.y)

        # order the holes in a heap so that we can find the "nearest" pole
        heapq.heappush(self._poles, pole)

        blocks = collision_object_manager.get(SurfaceBlock)
        assert blocks
        if len(collisions := pg.sprite.spritecollide(pole, blocks, False)) == 0:
            pole._point_mass.position = prev_pos
        else:
            # modify the position of the pole
            pole._point_mass.position.x = collisions[0].world_rect.centerx
            pole._point_mass.position.y = collisions[0].world_rect.top - (
                pole.world_rect.height / 2
            )

    @property
    def poles(self) -> pg.sprite.Group:
        """Returns all poles in the game (both used and un-used)."""
        return pg.sprite.Group(*(self._poles + self._unused_poles))

    @property
    def placed_poles(self) -> pg.sprite.Group:
        """Return only Telegraph Poles that have been placed."""
        return pg.sprite.Group(*self._poles)

    @property
    def visible_poles(self) -> list[TeleGraph]:
        """Return only Telegraph Poles that are currently visible in the game."""
        camera_bounds = camera.world_rect

        # also include any poles that we might need to
        # draw the wires between on the screen.
        camera_bounds.width += 2 * MAX_POLES_DISTANCE
        camera_bounds.height += 2 * MAX_POLES_DISTANCE
        camera_bounds.x -= MAX_POLES_DISTANCE
        camera_bounds.y -= MAX_POLES_DISTANCE

        # a better would be to ensure that the list is
        # always sorted and do a search between the bounds.
        visible_poles = []
        for pole in self._poles:
            if pole.world_rect.colliderect(camera_bounds):
                visible_poles.append(pole)

        return visible_poles


telegraph_placer = TeleGraphPolePlacer()


class TelegraphWireManager(Drawable):
    """Manages all wires betelegraph_wire_manageren Telegraph Poles in the game."""

    def _draw_wire(
        self, screen: pg.Surface, pole_1: TeleGraph, pole_2: TeleGraph
    ) -> None:
        """Draw a wire between two poles."""
        # draw a line between the two Poles
        point_1_pos = pole_1._point_mass.position.copy()
        point_1_pos.y -= TELEGRAPH_DIMS[1] / 2
        point_2_pos = pole_2._point_mass.position.copy()
        point_2_pos.y -= TELEGRAPH_DIMS[1] / 2

        pg.draw.line(
            screen,
            WIRE_COLOUR,
            camera.get_screen_vector2(point_1_pos),
            camera.get_screen_vector2(point_2_pos),
        )

    def draw(self, screen: pg.Surface) -> None:
        """Draw all wires between poles."""

        visible_poles = telegraph_placer.visible_poles

        logger.debug(f"visible poles length: {len(visible_poles)}")

        for i in range(len(visible_poles)):
            poles_left: list[tuple[float, TeleGraph]] = []
            poles_right: list[tuple[float, TeleGraph]] = []
            pole_1 = visible_poles[i]
            for j in range(len(visible_poles)):
                pole_2 = visible_poles[j]

                if (
                    pole_1._point_mass.position - pole_2._point_mass.position
                ).magnitude() < MAX_POLES_DISTANCE:
                    distance = (pole_1._point_mass.position - pole_2._point_mass.position).magnitude()
                    if pole_2._point_mass.position.x < pole_1._point_mass.position.x:
                        heapq.heappush(poles_left, (distance, pole_2))
                    else:
                        heapq.heappush(poles_right, (distance, pole_2))

            if len(poles_left):
                self._draw_wire(screen, pole_1, poles_left[0][1])

            if len(poles_right):
                self._draw_wire(screen, pole_1, poles_right[0][1])




telegraph_wire_manager = TelegraphWireManager()
