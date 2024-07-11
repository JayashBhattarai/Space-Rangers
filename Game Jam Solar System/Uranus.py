import pygame
import random
import math

class Uranus:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Balloon Pop Game")

        # Colors
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GRAY = (169, 169, 169)
        self.BLACK = (0, 0, 0)

        # Font
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

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

        # Pause menu variables
        self.menu_font = pygame.font.Font(None, 48)
        self.menu_text_color = (255, 255, 255)
        self.menu_background_color = (0, 0, 0, 180)  # Translucent black
        self.menu_options = ["Resume (ESC)", "Restart (R)", "Quit (Q)"]
        self.menu_option_positions = [(self.WIDTH // 2 - 100, self.HEIGHT // 2 - 50 + 50 * i) for i in range(3)]
        self.selected_option = 0

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
        self.balloons = [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.RED, self) for _ in range(5)]
        self.balloons += [self.Balloon(random.randint(50, self.WIDTH - 50), random.randint(50, self.HEIGHT - 50), self.GRAY, self) for _ in range(10)]
        self.arrow = None
        self.player_score = 0

    def draw_pause_menu(self):
        # Draw translucent background
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.menu_background_color)
        self.screen.blit(overlay, (0, 0))

        # Draw menu options
        for idx, option in enumerate(self.menu_options):
            text_surface = self.menu_font.render(option, True, self.menu_text_color)
            self.screen.blit(text_surface, self.menu_option_positions[idx])

            # Highlight selected option
            if idx == self.selected_option:
                pygame.draw.rect(self.screen, self.WHITE, (*self.menu_option_positions[idx], text_surface.get_width(), text_surface.get_height()), 3)

    def handle_pause_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif keys[pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif keys[pygame.K_RETURN]:
            if self.selected_option == 0:  # Resume
                self.paused = False
            elif self.selected_option == 1:  # Restart
                self.reset_game()
            elif self.selected_option == 2:  # Quit
                pygame.quit()
                quit()

    def main(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            self.screen.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.game_over and not self.congratulations:
                        self.paused = not self.paused

                    if event.key == pygame.K_r and (self.game_over or self.congratulations):
                        self.reset_game()

                    if event.key == pygame.K_q and (self.game_over or self.congratulations):
                        pygame.quit()
                        quit()

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.arrow is None and not self.congratulations:
                    x, y = event.pos
                    self.arrow = self.Arrow(self.bow_x, self.bow_y, x, y, self.BLACK)

            if not self.paused:
                # Game logic
                for balloon in self.balloons:
                    balloon.move()
                    balloon.draw(self.screen)

                if self.arrow:
                    self.arrow.move()
                    self.arrow.draw(self.screen)

                    balloon = self.check_collision(self.arrow)
                    if balloon:
                        if balloon.color == self.RED:
                            self.balloons.remove(balloon)
                            self.arrow = None
                            self.player_score += 1
                            if self.player_score == 5:
                                self.congratulations = True
                                self.paused = True  # Automatically pause on congratulations
                                self.show_congratulations()
                        else:
                            self.game_over = True
                            self.paused = True  # Automatically pause on game over
                            self.show_game_over()
                            self.arrow = None
                    elif self.arrow.y < 0 or self.arrow.x < 0 or self.arrow.x > self.WIDTH:
                        self.game_over = True
                        self.paused = True  # Automatically pause on game over
                        self.show_game_over()
                        self.arrow = None

                if self.game_over:
                    self.show_game_over()

                if self.congratulations:
                    self.show_congratulations()

                # Draw bow and aiming line
                if self.arrow is None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    angle = math.atan2(mouse_y - self.bow_y, mouse_x - self.bow_x)
                    end_x = self.bow_x + self.bow_length * math.cos(angle)
                    end_y = self.bow_y + self.bow_length * math.sin(angle)
                    pygame.draw.line(self.screen, self.BLACK, (self.bow_x, self.bow_y), (end_x, end_y), 5)

            else:
                self.draw_pause_menu()
                self.handle_pause_input()

            # Draw score
            score_text = self.small_font.render(f"Score: {self.player_score}/5", True, self.BLACK)
            self.screen.blit(score_text, (20, 20))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Uranus()
    game.main()
