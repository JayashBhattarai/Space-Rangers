import pygame
import random
from pygame import mixer

class Neptune:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Underwater Adventure")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.SKY = (135, 206, 235)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (169, 169, 169)
        self.GREEN = (0, 255, 0)

        # Load background music
        mixer.music.load('neptunebgm.mp3')

        # Player settings
        self.player_width, self.player_height = 50, 30
        self.player_x, self.player_y = self.WIDTH // 2 - self.player_width // 2, self.HEIGHT // 2 - self.player_height // 2
        self.player_speed = 2  # Default speed for up, down, right
        self.player_speed_left = 4  # Faster speed for left

        # Coin settings
        self.coin_width, self.coin_height = 30, 30

        # Obstacle settings
        self.obstacle_width, self.obstacle_height = 50, 50

        # Fish settings
        self.fish_width, self.fish_height = 50, 30

        # Distance settings
        self.finish_line_distance = 500  # meters

        # Font
        self.font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 48)

        # Initialize game variables
        self.clock = pygame.time.Clock()
        self.player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
        self.coins = []
        self.obstacles = []
        self.fishes = []
        self.distance_travelled = 0
        self.coins_collected = 0
        self.game_over = False
        self.game_won = False
        self.paused = False

        # Pause menu options
        self.menu_options = ["Resume (ESC)", "Restart (R)", "Quit (Q)"]
        self.selected_option = 0

        self.reset_game()

        # Load images
        self.player_img = pygame.image.load("submarine.png")
        self.player_width, self.player_height = 100, 60  # Adjust dimensions as needed
        self.player_img = pygame.transform.scale(self.player_img, (self.player_width, self.player_height))

        self.fish_img = pygame.image.load("fish.png")
        self.fish_img = pygame.transform.scale(self.fish_img, (self.fish_width, self.fish_height))

        self.obstacle_img = pygame.image.load("wooden-box.png")
        self.obstacle_img = pygame.transform.scale(self.obstacle_img, (self.obstacle_width, self.obstacle_height))

    def reset_game(self):
        self.player_y = self.HEIGHT // 2 - self.player_height // 2
        self.player_rect.topleft = (self.player_x, self.player_y)
        self.coins = [self.spawn_object(self.coin_width, self.coin_height) for _ in range(2)]
        self.obstacles = []
        self.fishes = []
        self.distance_travelled = 0
        self.coins_collected = 0
        self.game_over = False
        self.game_won = False
        self.paused = False

    def draw_player(self):
        self.screen.blit(self.player_img, self.player_rect.topleft)

    def draw_coin(self, coin_rect):
        pygame.draw.ellipse(self.screen, self.YELLOW, coin_rect)

    def draw_obstacle(self, obstacle_rect):
        self.screen.blit(self.obstacle_img, obstacle_rect.topleft)

    def draw_fish(self, fish_rect):
        self.screen.blit(self.fish_img, fish_rect.topleft)

    def draw_text(self, text, size, x, y, color):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def game_over_screen(self):
        mixer.music.stop()  # Stop BGM
        self.screen.fill(self.SKY)
        self.draw_text("Game Over", 74, self.WIDTH // 2 - 100, self.HEIGHT // 2 - 50, self.WHITE)
        self.draw_text("Press R to restart or Q to quit", 36, self.WIDTH // 2 - 150, self.HEIGHT // 2 + 50, self.WHITE)
        pygame.display.flip()

    def game_won_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Translucent black
        self.screen.blit(overlay, (0, 0))

        # Draw game won message
        self.draw_text("Congratulations!", 74, self.WIDTH // 2 - 150, self.HEIGHT // 2 - 50, self.WHITE)
        self.draw_text("Press R to restart or Q to quit", 36, self.WIDTH // 2 - 150, self.HEIGHT // 2 + 50, self.WHITE)

        pygame.display.flip()

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

    def spawn_object(self, width, height):
        while True:
            rect = pygame.Rect(self.WIDTH + random.randint(100, 300), random.randint(0, self.HEIGHT - height), width, height)
            if not any(rect.colliderect(obj) for obj in self.coins + self.obstacles + self.fishes):
                return rect

    def check_collisions(self):
        # Check collision with coins
        for coin in self.coins:
            if self.player_rect.colliderect(coin):
                self.coins.remove(coin)
                self.coins_collected += 1
                self.coins.append(self.spawn_object(self.coin_width, self.coin_height))

        # Check collision with obstacles
        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle):
                self.game_over = True

        # Check collision with fishes
        for fish in self.fishes:
            if self.player_rect.colliderect(fish):
                self.game_over = True

    def main(self):
        # Start background music
        mixer.music.play(-1)

        running = True
        while running:
            self.screen.fill(self.SKY)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over or self.game_won:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            mixer.music.play(-1)  # Restart BGM
                        elif event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"  # Return to main menu
                    elif event.key == pygame.K_ESCAPE:
                        if self.paused:
                            if self.selected_option == 0:  # Resume
                                self.paused = False
                            elif self.selected_option == 1:  # Restart
                                self.reset_game()
                                mixer.music.play(-1)  # Restart BGM
                            elif self.selected_option == 2:  # Quit
                                pygame.mixer.music.stop()
                                return "main_menu"  # Return to main menu
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
                                mixer.music.play(-1)  # Restart BGM
                            elif self.selected_option == 2:  # Quit
                                pygame.mixer.music.stop()
                                return "main_menu"  # Return to main menu
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle mouse click for pause menu options
                    if self.paused:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        for idx, option in enumerate(self.menu_options):
                            text_surface = self.menu_font.render(option, True, self.WHITE)
                            text_width, text_height = text_surface.get_size()
                            option_x = self.WIDTH // 2 - text_width // 2
                            option_y = self.HEIGHT // 2 - 50 + idx * 50
                            if option_x <= mouse_x <= option_x + text_width and option_y <= mouse_y <= option_y + text_height:
                                if idx == 0:  # Resume
                                    self.paused = False
                                elif idx == 1:  # Restart
                                    self.reset_game()
                                    mixer.music.play(-1)  # Restart BGM
                                elif idx == 2:  # Quit
                                    pygame.mixer.music.stop()
                                    return "main_menu"  # Return to main menu

            if not self.game_over and not self.game_won and not self.paused:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP] and self.player_rect.top > 0:
                    self.player_rect.y -= self.player_speed
                if keys[pygame.K_DOWN] and self.player_rect.bottom < self.HEIGHT:
                    self.player_rect.y += self.player_speed
                if keys[pygame.K_LEFT] and self.player_rect.left > 0:
                    self.player_rect.x -= self.player_speed_left  # Faster leftward movement
                if keys[pygame.K_RIGHT] and self.player_rect.right < self.WIDTH:
                    self.player_rect.x += self.player_speed

                self.distance_travelled += 0.1  # Increase distance travelled slightly faster

                if self.distance_travelled >= self.finish_line_distance and self.coins_collected < 10:
                    self.game_over = True
                if self.distance_travelled >= self.finish_line_distance and self.coins_collected >= 10:
                    self.game_won = True

                self.player_rect.y += 1  # Simulate sinking

                for coin in self.coins:
                    coin.x -= self.player_speed
                    if coin.x < 0:
                        coin.x = self.WIDTH + random.randint(100, 300)
                        coin.y = random.randint(0, self.HEIGHT - self.coin_height)

                # Spawn obstacles and fishes until finish line
                if self.distance_travelled < self.finish_line_distance:
                    if random.randint(0, 100) < 5 and len(self.obstacles) < 5:
                        self.obstacles.append(self.spawn_object(self.obstacle_width, self.obstacle_height))

                    for obstacle in self.obstacles:
                        obstacle.x -= self.player_speed
                        if obstacle.x < 0:
                            obstacle.x = self.WIDTH + random.randint(100, 300)
                            obstacle.y = random.randint(0, self.HEIGHT - self.obstacle_height)

                    if random.randint(0, 100) < 10 and len(self.fishes) < 7:
                        self.fishes.append(self.spawn_object(self.fish_width, self.fish_height))

                    for fish in self.fishes:
                        fish.x -= self.player_speed
                        if fish.x < 0:
                            fish.x = self.WIDTH + random.randint(100, 300)
                            fish.y = random.randint(0, self.HEIGHT - self.fish_height)

                self.check_collisions()

                for coin in self.coins:
                    self.draw_coin(coin)
                for obstacle in self.obstacles:
                    self.draw_obstacle(obstacle)
                for fish in self.fishes:
                    self.draw_fish(fish)

                self.draw_player()
                self.draw_text(f"Coins: {self.coins_collected}/10", 24, 10, 10, self.WHITE)
                self.draw_text(f"Distance: {int(self.distance_travelled)} m", 24, 10, 40, self.WHITE)

            if self.game_over:
                self.game_over_screen()
            elif self.game_won:
                self.game_won_screen()

            if self.paused:
                self.draw_pause_menu()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return "main_menu"  # Return to main menu when the game loop ends

if __name__ == "__main__":
    game = Neptune()
    game.main()