import pygame


class MessageBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.Font(pygame.font.match_font("monospace"), size=17)

        # sprites must have image + rect attributes

        self.image = pygame.Surface([500, 150])
        # self.image.set_alpha(255 // 2)
        self.image.fill("black")

        self.rect = self.image.get_rect()

        self.padding = self.image.get_rect().width * 0.025

        self.messages = []

    def line_width(self, message: list[str]) -> int:
        return self.font.size("".join(message))[0]

    def add_message(self, message: str) -> None:
        self.messages.append(message)
        self.render_all_messages()

    def render_all_messages(self) -> None:
        width = self.image.get_rect().width - self.padding * 2

        max_lines = (
            int(self.image.get_rect().height - 2 * self.padding)
        ) // self.font.get_height()

        self.image.fill("black")

        next_msg_y = self.padding

        line_groups = []

        for message in self.messages[-max_lines:]:
            line_groups.append(self.create_line_group(message, width))

        line_groups.reverse()

        lines_rendered = 0

        for group in line_groups:
            if lines_rendered + len(group) > max_lines:
                break

            for line in group:
                rendered_line = self.font.render(line, True, "white")
                self.image.blit(rendered_line, (self.padding, next_msg_y))
                next_msg_y += self.font.get_height()

            lines_rendered += len(group)

    def create_line_group(self, message, width) -> list[str]:
        line_group = []
        characters = list(message)
        characters.reverse()
        while characters:
            line_chars: list[str] = []

            while characters and self.line_width(line_chars + [characters[-1]]) < width:
                line_chars.append(characters.pop())

            line_group.append("".join(line_chars))
        return line_group
