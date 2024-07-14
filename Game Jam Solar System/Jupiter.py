import pygame
import random
from pygame import mixer
import textwrap


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


class Jupiter:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Balance the Stones")

        # Load background image
        try:
            self.background = pygame.image.load('src/Jupiterbackground.jpg')
            self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        except pygame.error as e:
            print(f"Unable to load background image: {e}")
            self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.background.fill((0, 0, 0))  # Fill with black if image fails to load

        # Load and play background music
        try:
            mixer.music.load('src/Jupiter.mp3')
            mixer.music.play(-1)
        except pygame.error as e:
            print(f"Unable to load music file: {e}")

        self.text_box = TextBox(50, 600, 1100, 150)
        self.game_state = "intro"
        self.intro_text = "Welcome to Jupiter! John, your mission is to use the scale to find out the correct weights of the stones."
        self.victory_text = "Congratulations! You've successfully completed the Jupiter stage! Obtained the Libra gem"
        self.defeat_text = "Mission failed. John, is maths too hard for you? Try again!"

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (169, 169, 169)
        self.GOLD = (255, 215, 0)
        self.SILVER = (192, 192, 192)
        self.COPPER = (184, 115, 51)
        self.PINK = (238, 25, 91, 255)

        # Fonts
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

        # Fixed weights for the stones
        self.gold_weight = 7
        self.silver_weight = 4
        self.copper_weight = 5

        # Player's guess weights
        self.gold_guess = ""
        self.silver_guess = ""
        self.copper_guess = ""

        # Initialize stones
        self.stones = []
        for i in range(10):
            self.stones.append(self.Stone(100 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.GOLD, self.gold_weight))
            self.stones.append(self.Stone(200 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.SILVER, self.silver_weight))
            self.stones.append(self.Stone(300 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.COPPER, self.copper_weight))

        self.left_weight = 0
        self.right_weight = 0
        self.game_over = False
        self.entering_guesses = False
        self.paused = False
        self.current_stone = None
        self.correct = False

    class Stone:
        def __init__(self, x, y, color, weight):
            self.x = x
            self.y = y
            self.color = color
            self.weight = weight
            self.dragging = False
            self.side = None

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (self.x, self.y), 20)

        def is_mouse_on_stone(self, pos):
            return (self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2 < 20 ** 2

    def draw_scales(self, left_weight, right_weight):
        # Calculate the tilt based on the weight difference
        weight_difference = right_weight - left_weight
        max_tilt = 50  # Maximum tilt in pixels
        tilt = max(-max_tilt, min(max_tilt, weight_difference * 5))  # Adjust the factor for more sensitivity

        left_scale_y = 400 - tilt
        right_scale_y = 400 + tilt

        # Base
        pygame.draw.rect(self.screen, self.PINK, (500, 500, 200, 20))

        # Left scale
        pygame.draw.rect(self.screen, self.PINK, (200, left_scale_y, 200, 20))
        pygame.draw.rect(self.screen, self.PINK, (300, left_scale_y - 100, 10, 100))

        # Right scale
        pygame.draw.rect(self.screen, self.PINK, (800, right_scale_y, 200, 20))
        pygame.draw.rect(self.screen, self.PINK, (900, right_scale_y - 100, 10, 100))

        # Center pillar
        pygame.draw.rect(self.screen, self.PINK, (590, 300, 20, 200))

        # Arms
        pygame.draw.line(self.screen, self.PINK, (600, left_scale_y + 10), (300, left_scale_y + 10), 5)
        pygame.draw.line(self.screen, self.PINK, (600, right_scale_y + 10), (900, right_scale_y + 10), 5)

        # Balance line
        pygame.draw.line(self.screen, self.BLACK, (600, left_scale_y + 10), (600, right_scale_y + 10), 2)

    def reset_game(self):
        self.left_weight = 0
        self.right_weight = 0
        self.game_over = False
        self.entering_guesses = False
        self.gold_guess = ""
        self.silver_guess = ""
        self.copper_guess = ""
        self.stones = []
        for i in range(10):
            self.stones.append(self.Stone(100 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.GOLD, self.gold_weight))
            self.stones.append(self.Stone(200 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.SILVER, self.silver_weight))
            self.stones.append(self.Stone(300 + random.randint(-20, 20), 700 + random.randint(-20, 20), self.COPPER, self.copper_weight))

    def pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("Paused", True, self.WHITE)
        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - 150))

        resume_text = self.small_font.render("Press 'R' to Resume", True, self.WHITE)
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, self.HEIGHT // 2 - 50))

        restart_text = self.small_font.render("Press 'N' to Restart", True, self.WHITE)
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2))

        quit_text = self.small_font.render("Press 'Q' to Quit", True, self.WHITE)
        self.screen.blit(quit_text, (self.WIDTH // 2 - quit_text.get_width() // 2, self.HEIGHT // 2 + 50))

    def main(self):
        running = True
        clock = pygame.time.Clock()

        self.text_box.set_text(self.intro_text)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif self.game_state == "intro" and event.key == pygame.K_RETURN:
                        if self.text_box.is_finished():
                            self.game_state = "playing"
                        else:
                            self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)
                    elif self.paused:
                        if event.key == pygame.K_r:
                            self.paused = False
                        elif event.key == pygame.K_n:
                            self.reset_game()
                            self.paused = False
                        elif event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"
                    elif self.game_state == "playing":
                        if event.key == pygame.K_RETURN:
                            if self.entering_guesses:
                                # Check if the guesses are correct
                                if (
                                        self.gold_guess.isdigit() and self.silver_guess.isdigit() and self.copper_guess.isdigit() and
                                        int(self.gold_guess) == self.gold_weight and int(
                                    self.silver_guess) == self.silver_weight and int(
                                    self.copper_guess) == self.copper_weight):
                                    self.game_over = True
                                    self.correct = True
                                    self.game_state = "victory"
                                    self.text_box.set_text(self.victory_text)
                                else:
                                    self.game_over = True
                                    self.correct = False
                                    self.game_state = "defeat"
                                    self.text_box.set_text(self.defeat_text)
                            else:
                                self.entering_guesses = True
                        elif event.key == pygame.K_BACKSPACE and self.entering_guesses:
                            if len(self.copper_guess) > 0:
                                self.copper_guess = self.copper_guess[:-1]
                            elif len(self.silver_guess) > 0:
                                self.silver_guess = self.silver_guess[:-1]
                            elif len(self.gold_guess) > 0:
                                self.gold_guess = self.gold_guess[:-1]
                        elif event.unicode.isdigit() and self.entering_guesses:
                            if len(self.gold_guess) == 0:
                                self.gold_guess += event.unicode
                            elif len(self.silver_guess) == 0:
                                self.silver_guess += event.unicode
                            elif len(self.copper_guess) == 0:
                                self.copper_guess += event.unicode
                        elif event.key == pygame.K_r and self.game_over:
                            # Restart the game
                            self.reset_game()
                            self.game_state = "intro"
                            self.text_box.set_text(self.intro_text)
                        elif event.key == pygame.K_q and self.game_over:
                            pygame.mixer.music.stop()
                            return "main_menu"
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing" and not self.game_over and not self.entering_guesses and not self.paused:
                    for stone in self.stones:
                        if stone.is_mouse_on_stone(event.pos):
                            stone.dragging = True
                            self.current_stone = stone
                            break
                elif event.type == pygame.MOUSEBUTTONUP and self.game_state == "playing" and not self.game_over and not self.entering_guesses and not self.paused:
                    if self.current_stone:
                        if self.current_stone.side == "left":
                            self.left_weight -= self.current_stone.weight
                        elif self.current_stone.side == "right":
                            self.right_weight -= self.current_stone.weight

                        if 200 <= self.current_stone.x <= 400 and 300 <= self.current_stone.y <= 500:
                            self.left_weight += self.current_stone.weight
                            self.current_stone.side = "left"
                        elif 800 <= self.current_stone.x <= 1000 and 300 <= self.current_stone.y <= 500:
                            self.right_weight += self.current_stone.weight
                            self.current_stone.side = "right"
                        else:
                            self.current_stone.side = None

                        self.current_stone.dragging = False
                        self.current_stone = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.current_stone and self.current_stone.dragging:
                        self.current_stone.x, self.current_stone.y = event.pos

            # Draw background first
            self.screen.blit(self.background, (0, 0))

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)
            elif self.paused:
                self.pause_menu()
            elif self.game_state == "playing":
                if not self.entering_guesses and not self.game_over:
                    pygame.draw.rect(self.screen, self.GOLD, (50, 650, 100, 100))
                    pygame.draw.rect(self.screen, self.SILVER, (150, 650, 100, 100))
                    pygame.draw.rect(self.screen, self.COPPER, (250, 650, 100, 100))

                    self.draw_scales(self.left_weight, self.right_weight)

                    for stone in self.stones:
                        stone.draw(self.screen)
                elif self.entering_guesses:
                    result_text = self.font.render("Guess the weights!", True, self.BLACK)
                    self.screen.blit(result_text, (self.WIDTH // 2 - result_text.get_width() // 2, 50))

                    gold_text = self.font.render(f"Gold: {self.gold_guess}", True, self.GOLD)
                    self.screen.blit(gold_text, (self.WIDTH // 2 - gold_text.get_width() // 2, 200))

                    silver_text = self.font.render(f"Silver: {self.silver_guess}", True, self.SILVER)
                    self.screen.blit(silver_text, (self.WIDTH // 2 - silver_text.get_width() // 2, 300))

                    copper_text = self.font.render(f"Copper: {self.copper_guess}", True, self.COPPER)
                    self.screen.blit(copper_text, (self.WIDTH // 2 - silver_text.get_width() // 2, 400))

                    if self.gold_guess and self.silver_guess and self.copper_guess:
                        submit_text = self.small_font.render("Press Enter to submit your guess", True, self.BLACK)
                        self.screen.blit(submit_text, (self.WIDTH // 2 - submit_text.get_width() // 2, 500))

            elif self.game_state in ["victory", "defeat"]:
                overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 180))
                self.screen.blit(overlay, (0, 0))

                if self.correct:
                    result_text = self.font.render("Congratulations!", True, self.GREEN)
                else:
                    result_text = self.font.render("Wrong guesses! Try again.", True, self.RED)

                self.screen.blit(result_text,(self.WIDTH // 2 - result_text.get_width() // 2, self.HEIGHT // 2 - 100))

                self.text_box.update()
                self.text_box.draw(self.screen)

                retry_text = self.small_font.render("Press 'R' to retry 'Q' to quit", True, self.GREEN)
                self.screen.blit(retry_text,(self.WIDTH // 2 - retry_text.get_width() // 2, self.HEIGHT // 2 + 150))

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = "intro"
                            self.text_box.set_text(self.intro_text)
                        elif event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"

            pygame.display.flip()

            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Jupiter()
    game.main()