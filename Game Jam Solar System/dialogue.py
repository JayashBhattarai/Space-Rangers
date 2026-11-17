"""Pixel-wrapped dialogue with fitted text and consistent character reveal."""
import pygame

class DialogueBox:
    def __init__(self, x, y, width, height, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.font_size = font_size
        self.line_spacing = 4
        self.text = ''
        self.text_content = []
        self.rendered_text = []
        self.reveal_index = 0
        self.reveal_speed = 2
        self.pages = []
        self.current_text_index = 0
        self.page_wait = 0
        self.font = pygame.font.Font(None, font_size)

    def wrap_text(self, text, max_width):
        lines = []
        for paragraph in text.split('\n'):
            line = ''
            for word in paragraph.split():
                candidate = (line + ' ' + word).strip()
                if line and self.font.size(candidate)[0] > max_width:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        return lines

    def set_text(self, text):
        self.text = text
        self.pages = text if isinstance(text, list) else [text]
        self.current_text_index = 0
        self.set_current_text()

    def set_current_text(self):
        for size in range(self.font_size, 11, -1):
            self.font = pygame.font.Font(None, size)
            self.text_content = self.wrap_text(self.pages[self.current_text_index], self.rect.width - 24)
            if len(self.text_content) * (self.font.get_height() + self.line_spacing) <= self.rect.height - 20:
                break
        self.rendered_text = [self.font.render(line, True, 'white') for line in self.text_content]
        self.reveal_index = 0
        self.page_wait = 0

    def update(self):
        self.reveal_index += self.reveal_speed
        if self.is_finished() and self.current_text_index < len(self.pages) - 1:
            self.page_wait += 1
            if self.page_wait >= 120:
                self.current_text_index += 1
                self.set_current_text()

    def draw(self, surface):
        pygame.draw.rect(surface, 'black', self.rect)
        pygame.draw.rect(surface, 'white', self.rect, 2)
        remaining = self.reveal_index
        y = self.rect.y + 10
        old_clip = surface.get_clip()
        surface.set_clip(self.rect.inflate(-12, -12))
        for line in self.text_content:
            surface.blit(self.font.render(line[:max(0, remaining)], True, 'white'), (self.rect.x + 12, y))
            remaining -= len(line)
            y += self.font.get_height() + self.line_spacing
        surface.set_clip(old_clip)

    def is_finished(self):
        return self.reveal_index >= sum(map(len, self.text_content))
