import pygame
import random


class Earth:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("2D Airplane Dodge")

        # Colors
        self.SKY_BLUE = (135, 206, 235)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (50, 50, 50)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)

        # Player
        self.player_width = 80
        self.player_height = 40
        self.player_x = self.WIDTH // 4
        self.player_y = self.HEIGHT // 2
        self.player_speed = 8
        self.player_jump = -15
        self.gravity = 1

        # Buildings
        self.building_width = 150
        self.building_min_height = 200
        self.building_max_height = 500
        self.buildings = []

        # Game variables
        self.scroll_speed = 5
        self.score = 0
        self.game_over = False
        self.paused = False

        # Create initial buildings
        self.create_buildings()

    # Create 2D airplane shape facing right
    def draw_airplane(self, surface, x, y):
        # Body
        pygame.draw.rect(surface, self.WHITE, (x, y + 10, self.player_width, 20))
        pygame.draw.polygon(surface, self.WHITE, [(x + self.player_width, y + 10), (x + self.player_width + 20, y + 20),
                                                  (x + self.player_width, y + 30)])
        pygame.draw.polygon(surface, self.WHITE, [(x, y + 10), (x - 20, y), (x, y + 20)])
        pygame.draw.polygon(surface, self.WHITE, [(x, y + 30), (x - 20, y + 40), (x, y + 50)])
        # Cockpit
        pygame.draw.rect(surface, self.RED, (x + 50, y + 10, 20, 20))

    # Create 2D building
    def draw_building(self, surface, x, y, width, height, color):
        # Front face
        pygame.draw.rect(surface, color, (x, y, width, height))
        # Windows
        for row in range(5, height, 40):
            for col in range(20, width, 80):
                pygame.draw.rect(surface, self.SKY_BLUE, (x + col, y + row, 40, 30))
                pygame.draw.rect(surface, self.DARK_GRAY, (x + col, y + row, 40, 30), 2)

    # Create initial buildings
    def create_buildings(self):
        self.buildings = []
        for i in range(6):  # Increased number of buildings
            height = random.randint(self.building_min_height, self.building_max_height)
            x = self.WIDTH + i * 300
            y = self.HEIGHT - height
            self.buildings.append({'x': x, 'y': y, 'height': height})

    # Draw the pause menu
    def draw_pause_menu(self):
        font = pygame.font.Font(None, 64)
        pause_text = font.render("Paused", True, self.DARK_GRAY)
        resume_text = font.render("Resume (Press R)", True, self.DARK_GRAY)
        restart_text = font.render("Restart (Press N)", True, self.DARK_GRAY)
        quit_text = font.render("Quit (Press Q)", True, self.DARK_GRAY)

        menu_width = 400
        menu_height = 300
        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, self.WHITE, (menu_x, menu_y, menu_width, menu_height))
        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, menu_y + 30))
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, menu_y + 100))
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, menu_y + 170))
        self.screen.blit(quit_text, (self.WIDTH // 2 - quit_text.get_width() // 2, menu_y + 240))

    # Main game loop
    def main(self):
        clock = pygame.time.Clock()
        running = True
        player_vel = 0
        victory = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused

            if not self.paused:
                if not self.game_over:
                    # Apply gravity
                    player_vel += self.gravity
                    self.player_y += player_vel

                    # Jump
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        player_vel = self.player_jump

                    # Move buildings
                    for building in self.buildings:
                        building['x'] -= self.scroll_speed

                    # Remove off-screen buildings and add new ones
                    if self.buildings[0]['x'] < -self.building_width:
                        self.buildings.pop(0)
                        height = random.randint(self.building_min_height, self.building_max_height)
                        x = self.buildings[-1]['x'] + 300
                        y = self.HEIGHT - height
                        self.buildings.append({'x': x, 'y': y, 'height': height})
                        self.score += 1

                    # Check for collision
                    for building in self.buildings:
                        if (self.player_x + self.player_width > building['x'] and
                                self.player_x < building['x'] + self.building_width and
                                self.player_y + self.player_height > building['y']):
                            self.game_over = True

                    # Check for hitting the ground or going too high
                    if self.player_y + self.player_height > self.HEIGHT or self.player_y < 0:
                        self.game_over = True

                    # Clear the screen
                    self.screen.fill(self.SKY_BLUE)

                    # Draw buildings
                    for building in self.buildings:
                        self.draw_building(self.screen, building['x'], building['y'],
                                           self.building_width, building['height'], self.GRAY)

                    # Draw player
                    self.draw_airplane(self.screen, self.player_x, self.player_y)

                    # Draw score
                    font = pygame.font.Font(None, 48)
                    score_text = font.render(f"Score: {self.score}", True, self.WHITE)
                    self.screen.blit(score_text, (20, 20))

                    # Check if score reaches 20 for victory condition
                    if self.score >= 20:
                        self.game_over = True
                        victory = True

                else:
                    # Game over or Victory screen
                    pygame.draw.rect(self.screen, self.WHITE,
                                     (self.WIDTH // 4, self.HEIGHT // 4, self.WIDTH // 2, self.HEIGHT // 2))
                    font = pygame.font.Font(None, 64)
                    if victory:
                        game_over_text = font.render("Congratulations!", True, self.GREEN)
                    else:
                        game_over_text = font.render("Game Over", True, self.RED)
                    self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2,
                                                      self.HEIGHT // 2 - game_over_text.get_height() // 2))

                    # Restart and Quit options
                    font = pygame.font.Font(None, 36)
                    restart_text = font.render("Press R to Restart", True, self.DARK_GRAY)
                    quit_text = font.render("Press Q to Quit", True, self.DARK_GRAY)
                    self.screen.blit(restart_text,
                                     (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 50))
                    self.screen.blit(quit_text, (self.WIDTH // 2 - quit_text.get_width() // 2, self.HEIGHT // 2 + 100))

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        self.game_over = False
                        self.score = 0
                        victory = False
                        self.player_y = self.HEIGHT // 2
                        player_vel = 0
                        self.create_buildings()
                    elif keys[pygame.K_q]:
                        running = False
            else:
                # Draw pause menu
                self.draw_pause_menu()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.paused = False
                elif keys[pygame.K_n]:
                    self.game_over = False
                    self.score = 0
                    victory = False
                    self.player_y = self.HEIGHT // 2
                    player_vel = 0
                    self.create_buildings()
                    self.paused = False
                elif keys[pygame.K_q]:
                    running = False

            # Update the display
            pygame.display.flip()

            # Control the game speed
            clock.tick(60)

        # Quit the game
        pygame.quit()


if __name__ == "__main__":
    game = Earth()
    game.main()
