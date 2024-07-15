import pygame
from pygame import mixer
import ctypes


class TextBox:
    def __init__(self, x, y, width, height, font_size):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.rendered_text = []
        self.text_content = []
        self.reveal_index = 0
        self.line_spacing = 5
        self.font = pygame.font.Font(None, font_size)

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


class Epilogue:
    def __init__(self):
        pygame.init()

        # Get the screen size
        user32 = ctypes.windll.user32
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Epilogue")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (169, 169, 169)

        text_box_width = int(self.WIDTH * 0.9)
        text_box_height = int(self.HEIGHT * 0.2)
        text_box_x = (self.WIDTH - text_box_width) // 2
        text_box_y = int(self.HEIGHT * 0.75)
        font_size = int(self.HEIGHT * 0.045)  # Adjust font size based on screen height

        self.text_box = TextBox(text_box_x, text_box_y, text_box_width, text_box_height, font_size)

        # Load background image
        self.background = pygame.image.load("src/epilogue.png")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        mixer.music.load('src/epilogue.mp3')
        mixer.music.play(-1)

        # Set the full story text
        self.full_story = [
            "John stood on the surface of the Sun, the intense heat held back by the protective aura of the collected gems."
            " As the alien boss was defeated, the Leo gem whispered its final instructions."
            " Around him, the twelve gems formed a brilliant circle, their combined energy pulsing with life.",

            "With a heavy heart, John placed all the other gems into the slots of the shield machine. The gems began to glow brighter, their light merging into a blinding radiance. "
            " As the machine hummed to life, John felt the Leo gem vibrating in his pocket.",

            "'John,' the Leo gem spoke softly, 'You've done it. You've saved the solar system. "
            " Now, you must place me into the machine to complete the activation.'",

            "John hesitated, his heart aching at the thought of parting with his steadfast companion. "
            "'Leo, I don't want to lose you,' he admitted, his voice trembling.",

            "'You won't lose me, John,' Leo reassured him.",

            "'Our bond will always remain. This is my purpose, and your courage has made it possible. The peace of our worlds depends on this moment.'",

            "With tears in his eyes, John took a deep breath and placed the Leo gem into its slot.",

            "The machine roared to life, the gems' energy creating a magnificent shield that spread out across the solar system."
            " The alien ships, unable to penetrate the barrier, retreated in defeat.",

            "John watched as the shield enveloped the Sun, a beacon of hope and protection for all the planets. "
            "He felt a profound sense of loss as the Leo gem's voice faded, but also a deep pride in knowing he had fulfilled his mission.",

            "Returning to Earth, John looked up at the night sky, now peaceful and safe. The stars twinkled brightly, a testament to his journey and the bond he had formed with the Leo gem.",

            "Though emotional, he found solace in knowing that peace had returned to the solar system, and his friendship with Leo would forever shine in his heart."
        ]
        self.current_part = 0
        self.text_box.set_text(self.full_story[self.current_part])
        self.show_end_options = False
        self.end_options = ["Reread (R)", "Main Menu (M)"]
        self.selected_end_option = 0

    def draw_end_options(self):
        self.screen.fill(self.BLACK)
        menu_x = self.WIDTH // 2
        menu_y = self.HEIGHT // 2
        font_size = int(self.HEIGHT * 0.04)  # Adjust font size for end options
        font = pygame.font.Font(None, font_size)
        for i, option in enumerate(self.end_options):
            color = self.WHITE
            rendered_option = font.render(option, True, color)
            option_rect = rendered_option.get_rect(center=(menu_x, menu_y + i * (font_size + 10)))
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
                            mixer.music.load('src/epilogue.mp3')
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
    game = Epilogue()
    game.run()
