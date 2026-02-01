from ggj.game_object import GameObject
from ggj.camera import camera

from typing import Mapping, Optional


class GameObjectTracer:
    """
    Tracks the positions between a single object and a set of objects.
    For example, you might want to track collisions between the player
    and walls in the world.

    NOTE: That candidates must be sorted by the tuple (row, col).
    """

    # todo(tbeatham): Refactor into checking between multiple and multiple objects?
    # split the screen into quadrants and check collisions between each object in
    # a quadrant?

    # candidates object is the object that the src might collide with.
    candidates: list[GameObject]

    def __init__(
        self,
        candidates: list[GameObject],
    ):
        self.candidates = candidates

    def get_collisions(self, src: GameObject) -> list[GameObject]:
        """
        Main update reactor.

        Args:
            src: The object to check for collisions.
        """
        collisions = []
        camera_rect = camera.get_world_rect()

        minimum = self._find_nearest_index_at_position((camera_rect.x, camera_rect.y))
        maximum = self._find_nearest_index_at_position(
            (camera_rect.right, camera_rect.bottom)
        )

        for candidate in self.candidates[minimum : maximum + 1]:
            if src.get_world_rect().colliderect(candidate.get_world_rect()):
                collisions.append(candidate)

        return collisions

    def _find_nearest_index_at_position(self, world_pos: tuple[int, int]) -> int:
        high = len(self.candidates)
        low = 0

        mid = low + ((high - low) // 2)
        while (high - low) > 1:
            candidate = self.candidates[mid]
            if candidate.get_world_rect().collidepoint(world_pos):
                return mid

            if world_pos < (candidate.get_world_rect().x, candidate.get_world_rect().y):
                high = mid
            else:
                low = mid + 1

            mid = low + ((high - low) // 2)

        return mid


class CollisionObjects:
    """
    Global list of all objects that a player/object could collide aginst.
    """

    objects: dict[type, GameObjectTracer]

    def __init__(self):
        self.objects = {}

    def get(self, t: type) -> Optional[GameObjectTracer]:
        return self.objects.get(t)

    def register(self, t: type, tracer: GameObjectTracer) -> None:
        self.objects[t] = tracer


collision_object_manager = CollisionObjects()
