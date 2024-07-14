import pygame
import random
import time
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


class Mars:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.screen_width = 1200
        self.screen_height = 800

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.semi_transparent_black = (0, 0, 0, 128)

        # Set up display
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Volcano Climbing')

        # Load images
        self.player_img = pygame.image.load('src/ufo.png')
        self.rock_img = pygame.image.load('src/rock.png')
        self.background = pygame.image.load('src/mars.jpg')

        # Player settings
        self.player_width = 50
        self.player_height = 60
        self.player_x = self.screen_width // 2
        self.player_y = self.screen_height - self.player_height
        self.player_speed = 5
        self.player_jump = False
        self.jump_speed = 10
        self.gravity = 1

        # Rock settings
        self.rock_width = 50
        self.rock_height = 50
        self.rock_speed = 5  # Adjust rock falling speed here
        self.rock_interval = 2.0  # time in seconds between rocks
        self.last_rock_time = time.time()

        # Game variables
        self.player_y_velocity = 0
        self.running = True
        self.game_over = False
        self.level_complete = False
        self.score = 0
        self.target_score = 22000

        # Fonts
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

        # Rocks list
        self.rocks = []

        # Pause state
        self.paused = False

        # Initialize Pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load('src/marsbgm.mp3')
        pygame.mixer.music.play(-1)  # Play music indefinitely

        self.text_box = TextBox(50, 600, 1100, 150)
        self.game_state = "intro"
        self.intro_text = "Welcome to Mars! John, your mission is to climb the volcano while avoiding falling rocks. Reach a height of 22,000m to win!"
        self.victory_text = "Congratulations! You've successfully climbed the Martian volcano! Obtained the Cancer gem"
        self.defeat_text = "Mission failed. John, don't rush! Try again!"

    def show_text(self, text, x, y, font_size=74):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, self.white)
        self.screen.blit(text_surface, (x, y))

    def reset_game(self):
        self.player_x = self.screen_width // 2
        self.player_y = self.screen_height - self.player_height
        self.player_y_velocity = 0
        self.rocks = []
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.paused = False  # Reset pause state
        self.game_state = "intro"
        self.text_box.set_text(self.intro_text)

    def pause_menu(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.semi_transparent_black)
        self.screen.blit(overlay, (0, 0))

        self.show_text('PAUSED', self.screen_width // 2 - 150, self.screen_height // 2 - 50)
        self.show_text('Press R to Resume', self.screen_width // 2 - 150, self.screen_height // 2 + 50, font_size=36)
        self.show_text('Press N to Restart', self.screen_width // 2 - 150, self.screen_height // 2 + 100, font_size=36)
        self.show_text('Press Q to Quit', self.screen_width // 2 - 150, self.screen_height // 2 + 150, font_size=36)

    def main(self):
        clock = pygame.time.Clock()

        self.text_box.set_text(self.intro_text)

        while self.running:
            self.screen.fill(self.black)
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if self.game_state == "intro" and event.key == pygame.K_RETURN:
                        if self.text_box.is_finished():
                            self.game_state = "playing"
                        else:
                            self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)
                    elif not self.paused and self.game_state == "playing":
                        if event.key == pygame.K_SPACE and not self.player_jump:
                            self.player_jump = True
                            self.player_y_velocity = -self.jump_speed
                    if self.paused:
                        if event.key == pygame.K_r:  # Resume game
                            self.paused = False
                        elif event.key == pygame.K_n:  # Restart game
                            self.reset_game()
                        elif event.key == pygame.K_q:  # Quit game
                            pygame.mixer.music.stop()
                            return "main_menu"

            if not self.paused:
                if self.game_state == "intro":
                    self.text_box.update()
                    self.text_box.draw(self.screen)
                elif self.game_state == "playing":
                    if not self.game_over and not self.level_complete:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT] and self.player_x > 0:
                            self.player_x -= self.player_speed
                        if keys[pygame.K_RIGHT] and self.player_x < self.screen_width - self.player_width:
                            self.player_x += self.player_speed

                        if self.player_jump:
                            self.player_y += self.player_y_velocity
                            self.player_y_velocity += self.gravity
                            if self.player_y >= self.screen_height - self.player_height:
                                self.player_y = self.screen_height - self.player_height
                                self.player_jump = False

                        # Update score based on player movement
                        self.score += self.player_speed

                        # Check if player has reached target score
                        if self.score >= self.target_score:
                            self.level_complete = True
                            self.game_state = "victory"
                            self.text_box.set_text(self.victory_text)

                        # Spawn rocks at random intervals
                        if time.time() - self.last_rock_time > self.rock_interval:
                            rock_x = random.randint(0, self.screen_width - self.rock_width)
                            self.rocks.append([rock_x, 0])
                            self.last_rock_time = time.time()
                            self.rock_interval = random.uniform(1, 3)  # randomize the interval between rocks

                        # Update rocks and check for collisions
                        for rock in self.rocks[:]:
                            rock[1] += self.rock_speed
                            rock_rect = pygame.Rect(rock[0], rock[1], self.rock_width, self.rock_height)
                            player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)

                            # Check for collision with player
                            if rock_rect.colliderect(player_rect):
                                self.game_over = True
                                self.game_state = "defeat"
                                self.text_box.set_text(self.defeat_text)

                            if rock[1] > self.screen_height:
                                self.rocks.remove(rock)
                            else:
                                self.screen.blit(self.rock_img, (rock[0], rock[1]))

                    self.screen.blit(self.player_img, (self.player_x, self.player_y))

                elif self.game_state in ["victory", "defeat"]:
                    # Game over or Victory screen
                    overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                    overlay.fill(self.semi_transparent_black)
                    self.screen.blit(overlay, (0, 0))

                    font_large = pygame.font.Font(None, 74)
                    if self.game_state == "victory":
                        game_over_text = font_large.render("Congratulations!", True, self.white)
                    else:
                        game_over_text = font_large.render("Game Over", True, self.red)
                    self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2,
                                                      self.screen_height // 3 - game_over_text.get_height() // 2))

                    font_small = pygame.font.Font(None, 36)
                    restart_text = font_small.render("Press R to Restart", True, self.white)
                    quit_text = font_small.render("Press Q to Quit", True, self.white)
                    self.screen.blit(restart_text,
                                     (self.screen_width // 2 - restart_text.get_width() // 2,
                                      self.screen_height // 3 + game_over_text.get_height()))
                    self.screen.blit(quit_text,
                                     (self.screen_width // 2 - quit_text.get_width() // 2,
                                      self.screen_height // 3 + game_over_text.get_height() + restart_text.get_height() + 10))

                    self.text_box.update()
                    self.text_box.draw(self.screen)

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        self.reset_game()
                    elif keys[pygame.K_q]:
                        pygame.mixer.music.stop()
                        return "main_menu"

                # Display score
                self.show_text(f'Height: {self.score}m', 10, 10, font_size=36)
            else:
                self.pause_menu()

            pygame.display.update()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Mars()
    game.main()
