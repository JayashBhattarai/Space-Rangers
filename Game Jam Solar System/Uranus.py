import pygame
import random
import math
import textwrap
import time
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
        wrapped_text = textwrap.wrap(text, width=self.rect.width // 10)
        for line in wrapped_text:
            self.rendered_text.append(self.font.render(line, True, (255, 255, 255)))
            self.text_content.append(line)
        self.reveal_index = 0

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


class Uranus:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Balloon Pop Game")

        # Load background image
        self.background = pygame.image.load('uranus.jpg')

        # Load pop sound
        self.pop_sound = pygame.mixer.Sound('pop.mp3')

        # Load background music
        pygame.mixer.music.load('uranusbgm.mp3')
        pygame.mixer.music.play(-1)  # Play the music in a loop

        # Colors
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GRAY = (169, 169, 169)
        self.BLACK = (0, 0, 0)

        # Font
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 48)

        # Initialize game variables
        self.game_over = False
        self.congratulations = False
        self.paused = False
        self.balloons = [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.RED, self) for _ in range(5)]
        self.balloons += [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.GRAY, self) for _ in range(10)]
        self.arrow = None
        self.player_score = 0

        # Bow variables
        self.bow_x, self.bow_y = self.WIDTH // 2, self.HEIGHT - 50
        self.bow_length = 50

        # Pause menu options
        self.menu_options = ["Resume (ESC)", "Restart (R)", "Quit (Q)"]
        self.selected_option = 0

        # Text box and game state
        self.text_box = TextBox(50, 600, 1100, 150)
        self.game_state = "intro"
        self.intro_text = "Welcome to Uranus! Your mission is to pop the RED balloons! Don't miss a single shot!"
        self.victory_text = "Congratulations! You've successfully popped all the balloons! Obtained the Sagittarius gem"
        self.defeat_text = "Mission failed. Stay calm and aim. Try again!"

    class Balloon:
        def __init__(self, x, y, color, parent):
            self.x = x
            self.y = y
            self.color = color
            self.radius = 30
            self.speed = random.uniform(1, 3)
            self.direction = random.uniform(0, 2 * math.pi)
            self.parent = parent

        def move(self):
            self.x += self.speed * math.cos(self.direction)
            self.y += self.speed * math.sin(self.direction)

            if self.x < 0 or self.x > self.parent.WIDTH:
                self.direction = math.pi - self.direction
            if self.y < 0 or self.y > self.parent.HEIGHT:
                self.direction = -self.direction

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    class Arrow:
        def __init__(self, x, y, target_x, target_y, color):
            self.x = x
            self.y = y
            self.target_x = target_x
            self.target_y = target_y
            self.color = color
            self.speed = 10
            angle = math.atan2(target_y - y, target_x - x)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed

        def move(self):
            self.x += self.dx
            self.y += self.dy

        def draw(self, screen):
            points = [
                (self.x, self.y),
                (self.x - 20, self.y - 10),
                (self.x - 20, self.y + 10),
            ]
            pygame.draw.polygon(screen, self.color, points)

    def check_collision(self, arrow):
        for balloon in self.balloons:
            distance = math.hypot(balloon.x - arrow.x, balloon.y - arrow.y)
            if distance < balloon.radius:
                return balloon
        return None

    def display_message(self, message, sub_message=None):
        text = self.font.render(message, True, self.BLACK)
        self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - text.get_height() // 2))
        if sub_message:
            sub_text = self.small_font.render(sub_message, True, self.BLACK)
            self.screen.blit(sub_text, (self.WIDTH // 2 - sub_text.get_width() // 2, self.HEIGHT // 2 - sub_text.get_height() // 2 + 100))

    def show_game_over(self):
        self.display_message("Game Over!", "Press R to retry or Q to quit")

    def show_congratulations(self):
        self.display_message("Congratulations!", "Press R to retry or Q to quit")

    def reset_game(self):
        self.game_over = False
        self.congratulations = False
        self.paused = False
        self.balloons = [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.RED, self) for _ in range(5)]
        self.balloons += [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.GRAY, self) for _ in range(10)]
        self.arrow = None
        self.player_score = 0
        self.game_state = "playing"

    def draw_pause_menu(self):
        # Draw translucent background
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Translucent black
        self.screen.blit(overlay, (0, 0))

        # Draw menu options
        for idx, option in enumerate(self.menu_options):
            text_surface = self.menu_font.render(option, True, self.WHITE)
            x, y = self.WIDTH // 2 - text_surface.get_width() // 2, self.HEIGHT // 2 - 50 + idx * 50
            self.screen.blit(text_surface, (x, y))

            # Highlight selected option
            if idx == self.selected_option:
                pygame.draw.rect(self.screen, self.WHITE, (x - 10, y - 10, text_surface.get_width() + 20, text_surface.get_height() + 20), 3)

    def handle_game_over(self, is_victory):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Translucent black

        waiting = True
        while waiting:
            self.screen.blit(self.background, (0, 0))
            # self.screen.blit(overlay, (0, 0))

            if is_victory:
                self.display_message("Congratulations!")
            else:
                self.display_message("Game Over!")

            self.text_box.update()
            self.text_box.draw(self.screen)

            if self.text_box.is_finished():
                self.display_message("", "Press R to restart or Q to quit")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        return "restart"
                    elif event.key == pygame.K_q:
                        pygame.mixer.music.stop()
                        return "main_menu"

            self.clock.tick(60)

    def main(self):
        running = True
        self.clock = pygame.time.Clock()
        self.text_box.set_text(self.intro_text)

        while running:
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "intro" and self.text_box.is_finished():
                        self.game_state = "playing"
                    elif self.game_state == "playing":
                        if event.key == pygame.K_ESCAPE:
                            if self.paused:
                                if self.selected_option == 0:
                                    self.paused = False  # Resume
                                elif self.selected_option == 1:
                                    self.reset_game()  # Restart
                                elif self.selected_option == 2:
                                    pygame.mixer.music.stop()  # Quit
                                    return "main_menu"
                            else:
                                self.paused = not self.paused
                        elif self.paused:
                            if event.key == pygame.K_DOWN:
                                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                            elif event.key == pygame.K_UP:
                                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                            elif event.key == pygame.K_RETURN:
                                if self.selected_option == 0:  # Resume
                                    self.paused = False
                                elif self.selected_option == 1:  # Restart
                                    self.reset_game()
                                elif self.selected_option == 2:  # Quit
                                    pygame.mixer.music.stop()
                                    return "main_menu"
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing" and not self.paused and self.arrow is None:
                    x, y = event.pos
                    self.arrow = self.Arrow(self.bow_x, self.bow_y, x, y, self.RED)

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)
                if self.text_box.is_finished():
                    self.display_message("", "Press any key to start")
            elif self.game_state == "playing":
                if not self.paused:
                    # Move and draw balloons
                    for balloon in self.balloons:
                        balloon.move()
                        balloon.draw(self.screen)

                    # Move and draw arrow
                    if self.arrow:
                        self.arrow.move()
                        self.arrow.draw(self.screen)

                        # Check for collisions
                        balloon = self.check_collision(self.arrow)
                        if balloon:
                            if balloon.color == self.RED:
                                self.pop_sound.play()
                                self.balloons.remove(balloon)
                                self.arrow = None
                                self.player_score += 1
                                if self.player_score == 5:
                                    self.game_state = "victory"
                                    self.text_box.set_text(self.victory_text)
                            else:
                                self.game_state = "defeat"
                                self.text_box.set_text(self.defeat_text)
                                self.arrow = None
                        elif self.arrow.y < 0 or self.arrow.x < 0 or self.arrow.x > self.WIDTH:
                            self.game_state = "defeat"
                            self.text_box.set_text(self.defeat_text)
                            self.arrow = None

                    # Draw bow and aiming line
                    if self.arrow is None:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        angle = math.atan2(mouse_y - self.bow_y, mouse_x - self.bow_x)
                        end_x = self.bow_x + self.bow_length * math.cos(angle)
                        end_y = self.bow_y + self.bow_length * math.sin(angle)
                        pygame.draw.line(self.screen, self.RED, (self.bow_x, self.bow_y), (end_x, end_y), 5)

                    # Draw score
                    score_text = self.small_font.render(f"Score: {self.player_score}/5", True, self.WHITE)
                    self.screen.blit(score_text, (20, 20))
                else:
                    self.draw_pause_menu()
            elif self.game_state == "victory" or self.game_state == "defeat":
                result = self.handle_game_over(self.game_state == "victory")
                if result == "restart":
                    self.game_state = "playing"
                elif result == "main_menu":
                    return "main_menu"
                elif result == "quit":
                    running = False

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return "main_menu"


if __name__ == "__main__":
    game = Uranus()
    game.main()
