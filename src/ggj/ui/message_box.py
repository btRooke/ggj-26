import pygame


class MessageBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.Font(pygame.font.match_font("monospace"), size=17)

        # sprites must have image + rect attributes

        self.image = pygame.Surface([500, 150])
        self.image.fill("black")

        self.rect = self.image.get_rect()

        # padding can be modified to whatever

        self.padding = self.image.get_rect().width * 0.025
        self.text_width = self.rect.width - self.padding * 2

        # list of messages to display, these will be wrapped

        self.messages = []

    def _line_width(self, message: list[str]) -> int:
        return self.font.size("".join(message))[0]

    def add_message(self, message: str) -> None:
        """Add a message to be displayed in the box."""
        self.messages.append(message)
        self._re_render_messages()

    def max_lines(self) -> int:
        return (
            int(self.image.get_rect().height - 2 * self.padding)
        ) // self.font.get_height()

    def _re_render_messages(self) -> None:
        # clear box

        self.image.fill("black")

        # create line groups for last few relevant messages

        line_groups = [
            self._create_line_group(m) for m in self.messages[-self.max_lines() :]
        ]
        line_groups.reverse()

        # start rendering

        next_msg_y = self.padding
        lines_rendered = 0

        for group in line_groups:
            # stop if will exceed box size

            if lines_rendered + len(group) > self.max_lines():
                break

            # otherwise do it

            for line in group:
                rendered_line = self.font.render(line, True, "white")
                self.image.blit(rendered_line, (self.padding, next_msg_y))
                next_msg_y += self.font.get_height()

            lines_rendered += len(group)

    def _create_line_group(self, message: str) -> list[str]:
        """Split a string message into a group of lines that will fit into the box when rendered."""

        line_group = []
        characters = list(message)
        characters.reverse()

        while characters:
            line_chars: list[str] = []

            while (
                characters
                and self._line_width(line_chars + [characters[-1]]) < self.text_width
            ):
                line_chars.append(characters.pop())

            line_group.append("".join(line_chars))

        return line_group
