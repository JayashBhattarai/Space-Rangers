import pygame
import random
import time

class Mars:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.semi_transparent_black = (0, 0, 0, 128)

        # Set up display
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Volcano Climbing')

        # Load images
        self.player_img = pygame.image.load('ufo.png')
        self.rock_img = pygame.image.load('rock.png')
        self.background = pygame.image.load('mars.jpg')

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
        pygame.mixer.music.load('marsbgm.mp3')
        pygame.mixer.music.play(-1)  # Play music indefinitely

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

        while self.running:
            self.screen.fill(self.black)
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_SPACE and not self.player_jump:
                            self.player_jump = True
                            self.player_y_velocity = -self.jump_speed
                    if self.paused:
                        if event.key == pygame.K_r:  # Resume game
                            self.paused = False
                        elif event.key == pygame.K_n:  # Restart game
                            self.reset_game()
                        elif event.key == pygame.K_q:  # Quit game
                            self.running = False

            if not self.paused:
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

                        if rock[1] > self.screen_height:
                            self.rocks.remove(rock)
                        else:
                            self.screen.blit(self.rock_img, (rock[0], rock[1]))

                    self.screen.blit(self.player_img, (self.player_x, self.player_y))

                if self.game_over:
                    self.show_text('GAME OVER', self.screen_width // 2 - 150, self.screen_height // 2 - 50)
                    self.show_text('Press R to Restart', self.screen_width // 2 - 150, self.screen_height // 2 + 50,
                                   font_size=36)

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        self.reset_game()

                if self.level_complete:
                    self.show_text('CONGRATULATIONS', self.screen_width // 2 - 250, self.screen_height // 2 - 50)
                    self.show_text('Level Complete!', self.screen_width // 2 - 150, self.screen_height // 2 + 50,
                                   font_size=36)

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
