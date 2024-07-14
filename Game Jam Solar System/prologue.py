import pygame
from pygame import mixer


class TextBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.rendered_text = []
        self.text_content = []
        self.reveal_index = 0
        self.line_spacing = 5
        self.font = pygame.font.Font(None, 32)

    def set_text(self, text):
        self.text = text
        self.rendered_text = []
        self.text_content = []
        wrapped_text = self.wrap_text(text, self.rect.width - 20)
        for line in wrapped_text:
            self.rendered_text.append(self.font.render(line, True, (255, 255, 255)))
            self.text_content.append(line)
        self.reveal_index = 0

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        wrapped_lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "
        wrapped_lines.append(current_line.strip())
        return wrapped_lines

    def update(self):
        self.reveal_index += 1

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3)

        y = self.rect.top + 10
        for i, (line, content) in enumerate(zip(self.rendered_text, self.text_content)):
            x = self.rect.left + 10
            if i * len(content) < self.reveal_index:
                surface.blit(line, (x, y))
                y += line.get_height() + self.line_spacing

    def is_finished(self):
        return self.reveal_index >= sum(len(line) for line in self.text_content)


class Prologue:
    def __init__(self):
        pygame.init()

        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Prologue")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (169, 169, 169)

        self.text_box = TextBox(50, 600, 1100, 150)

        # Load background image
        self.background = pygame.image.load("src/prologue.png")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        mixer.music.load('src/prologue.mp3')
        mixer.music.play(-1)

        # Set the full story text
        self.full_story = [
            "In a certain quiet village, John lived a simple life. He had always been fascinated by the night sky, often spending hours stargazing."
            " One evening, while exploring a nearby forest, he stumbled upon a radiant gem emitting a golden light."
            " Intrigued, he picked it up and felt a strange warmth envelop his hand. The gem spoke to him, introducing itself as the Leo gem.",

            "A few days later, chaos erupted on Earth as alien ships descended from the sky. The aliens declared that they had conquered the entire solar system."
            " Panic spread like wildfire, and John felt a strange connection to the Leo gem in his pocket.",

            "That night, as John held the gem, it spoke again. 'The aliens have taken over because the shield machine protecting the solar system, located in the Sun, has been deactivated. "
            "The gems that power it were scattered across the eight planets. You, John, must find them to reactivate the shield and save our worlds.'",

            "Realizing the weight of his mission, John felt a surge of determination. With the Leo gem as his guide, he embarked on an extraordinary journey across the solar system. "
            "He would travel from planet to planet, facing unimaginable challenges, and seek out the remaining gems to restore the shield machine in the Sun.",

            "The fate of the solar system rested on his shoulders."
        ]
        self.current_part = 0
        self.text_box.set_text(self.full_story[self.current_part])
        self.show_end_options = False
        self.end_options = ["Reread (R)", "Main Menu (M)"]
        self.selected_end_option = 0

    def draw_end_options(self):
        # Draw the end options menu
        mixer.music.stop()
        self.screen.fill((0, 0, 0))
        menu_x = self.WIDTH // 2
        menu_y = self.HEIGHT // 2
        for i, option in enumerate(self.end_options):
            color = self.WHITE if i == self.selected_end_option else self.WHITE
            rendered_option = self.text_box.font.render(option, True, color)
            option_rect = rendered_option.get_rect(center=(menu_x, menu_y + i * 40))
            self.screen.blit(rendered_option, option_rect)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.show_end_options:
                        if event.key == pygame.K_r:
                            # Reread the story
                            mixer.music.load('src/prologue.mp3')
                            mixer.music.play(-1)
                            self.current_part = 0
                            self.text_box.set_text(self.full_story[self.current_part])
                            self.show_end_options = False
                        elif event.key == pygame.K_m:
                            # Go to the main menu (you can implement this as needed)
                            print("Go to the main menu")
                            return "main_menu"
                    else:
                        if event.key == pygame.K_RETURN:
                            # Advance to the next part of the story
                            if self.text_box.is_finished():
                                self.current_part += 1
                                if self.current_part < len(self.full_story):
                                    self.text_box.set_text(self.full_story[self.current_part])
                                else:
                                    self.show_end_options = True

            self.screen.blit(self.background, (0, 0))

            if self.show_end_options:
                self.draw_end_options()
            else:
                self.text_box.update()
                self.text_box.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Prologue()
    game.run()
