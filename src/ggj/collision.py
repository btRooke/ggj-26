from ggj.game_object import GameObject
from ggj.camera import camera


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

    # src object is the object moving around in the world.
    src: GameObject
    # candidates object is the object that the src might collide with.
    candidates: list[GameObject]

    def __init__(
        self,
        src: GameObject,
        candidates: list[GameObject],
    ):
        """
        pos_to_index maps a position in the world to an instance in the
        objects.
        """
        self.src = src
        self.candidates = candidates

    def update(self):
        """
        Main update reactor. Checks whether objects overlap or not.
        """
        # todo(tbeatham): keep track of what objects are on the screen.
        camera_rect = camera.get_world_rect()

        minimum = self._find_nearest_index_at_position((camera_rect.x, camera_rect.y))
        maximum = self._find_nearest_index_at_position(
            (camera_rect.right, camera_rect.bottom)
        )

        for candidate in self.candidates[minimum : maximum + 1]:
            if self.src.get_world_rect().colliderect(candidate.get_world_rect()):
                self.src.on_collide(candidate)
                candidate.on_collide(self.src)

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
