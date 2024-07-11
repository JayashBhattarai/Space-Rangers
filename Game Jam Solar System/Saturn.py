import pygame
import random

class Saturn:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Alien Jigsaw Puzzle")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (169, 169, 169)
        self.TRANSPARENT = (0, 0, 0, 0)  # Transparent color for overlay

        # Load image
        self.alien_image = pygame.image.load('alien.png')

        # Resize image
        self.sign_size = 300
        self.alien_image = pygame.transform.scale(self.alien_image, (self.sign_size, self.sign_size))

        # Split image into pieces
        self.pieces_per_row = 3
        self.piece_size = self.sign_size // self.pieces_per_row
        self.alien_pieces = []
        for y in range(self.pieces_per_row):
            for x in range(self.pieces_per_row):
                rect = pygame.Rect(x * self.piece_size, y * self.piece_size, self.piece_size, self.piece_size)
                self.alien_pieces.append(self.alien_image.subsurface(rect))

        # Game variables
        self.total_pieces = self.pieces_per_row * self.pieces_per_row
        self.grid = list(range(self.total_pieces))
        random.shuffle(self.grid)
        self.dragging_piece = None
        self.game_over = False
        self.result_text = None

        # Centering variables
        self.center_x = (self.WIDTH - self.pieces_per_row * self.piece_size) // 2
        self.center_y = (self.HEIGHT - self.pieces_per_row * self.piece_size) // 2 + 50  # Adjusted for space

        # Pause menu variables
        self.pause_menu_active = False
        self.selected_option = 0  # 0: Resume, 1: Retry, 2: Quit
        self.pause_menu_font = pygame.font.Font(None, 36)

    def draw_grid(self):
        for i in range(self.total_pieces):
            x = (i % self.pieces_per_row) * self.piece_size + self.center_x
            y = (i // self.pieces_per_row) * self.piece_size + self.center_y
            piece_index = self.grid[i]
            piece = self.alien_pieces[piece_index]
            self.screen.blit(piece, (x, y))
            pygame.draw.rect(self.screen, self.BLACK, (x, y, self.piece_size, self.piece_size), 1)

    def check_correct_placement(self):
        return self.grid == list(range(self.total_pieces))

    def draw_pause_menu(self):
        # Create a translucent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # 100 alpha for translucency
        self.screen.blit(overlay, (0, 0))

        # Draw pause menu options
        resume_text = self.pause_menu_font.render("Resume", True, self.WHITE if self.selected_option != 0 else self.BLACK)
        retry_text = self.pause_menu_font.render("Retry", True, self.WHITE if self.selected_option != 1 else self.BLACK)
        quit_text = self.pause_menu_font.render("Quit", True, self.WHITE if self.selected_option != 2 else self.BLACK)

        menu_height = resume_text.get_height() * 3  # Height for all three options
        menu_width = max(resume_text.get_width(), retry_text.get_width(), quit_text.get_width()) + 40

        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, self.WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        self.screen.blit(resume_text, (menu_x + 20, menu_y + 20))
        self.screen.blit(retry_text, (menu_x + 20, menu_y + 20 + resume_text.get_height()))
        self.screen.blit(quit_text, (menu_x + 20, menu_y + 20 + resume_text.get_height() * 2))

    def draw_congratulations(self):
        # Clear the screen
        self.screen.fill(self.WHITE)

        # Draw 'Congratulations!' message
        congratulations_text = self.pause_menu_font.render("Congratulations!", True, self.BLACK)
        self.screen.blit(congratulations_text,
                         (self.WIDTH // 2 - congratulations_text.get_width() // 2,
                          self.HEIGHT // 2 - congratulations_text.get_height() // 2))

        # Draw retry and quit options
        retry_text = self.pause_menu_font.render("Retry", True, self.BLACK if self.selected_option != 0 else self.WHITE)
        quit_text = self.pause_menu_font.render("Quit", True, self.BLACK if self.selected_option != 1 else self.WHITE)

        options_width = max(retry_text.get_width(), quit_text.get_width()) + 40
        options_height = retry_text.get_height() + quit_text.get_height() + 20
        options_x = (self.WIDTH - options_width) // 2
        options_y = self.HEIGHT // 2 + congratulations_text.get_height() // 2 + 20

        pygame.draw.rect(self.screen, self.WHITE, (options_x, options_y, options_width, options_height), 2)
        self.screen.blit(retry_text, (options_x + 20, options_y + 20))
        self.screen.blit(quit_text, (options_x + 20, options_y + 20 + retry_text.get_height() + 10))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.pause_menu_active:
                x, y = event.pos
                if self.center_x <= x < self.center_x + self.pieces_per_row * self.piece_size and \
                   self.center_y <= y < self.center_y + self.pieces_per_row * self.piece_size:
                    grid_x = (x - self.center_x) // self.piece_size
                    grid_y = (y - self.center_y) // self.piece_size
                    piece_index = grid_y * self.pieces_per_row + grid_x
                    self.dragging_piece = piece_index
            elif event.type == pygame.MOUSEBUTTONUP and self.dragging_piece is not None and not self.game_over and not self.pause_menu_active:
                x, y = event.pos
                if self.center_x <= x < self.center_x + self.pieces_per_row * self.piece_size and \
                   self.center_y <= y < self.center_y + self.pieces_per_row * self.piece_size:
                    grid_x = (x - self.center_x) // self.piece_size
                    grid_y = (y - self.center_y) // self.piece_size
                    target_index = grid_y * self.pieces_per_row + grid_x
                    # Swap pieces
                    self.grid[self.dragging_piece], self.grid[target_index] = self.grid[target_index], self.grid[self.dragging_piece]
                    self.dragging_piece = None

                    # Check if the puzzle is solved immediately after each move
                    if self.check_correct_placement():
                        self.game_over = True
                        self.result_text = pygame.font.Font(None, 74).render("Congratulations!", True, self.BLACK)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu_active = not self.pause_menu_active
                    self.selected_option = 0

                if self.pause_menu_active:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Resume
                            self.pause_menu_active = False
                        elif self.selected_option == 1:  # Retry
                            self.reset_game()
                        elif self.selected_option == 2:  # Quit
                            pygame.quit()
                            sys.exit()

    def reset_game(self):
        random.shuffle(self.grid)
        self.game_over = False
        self.result_text = None

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()

            self.screen.fill(self.WHITE)

            # Draw reference image
            small_sign_size = 100
            self.screen.blit(pygame.transform.scale(self.alien_image, (small_sign_size, small_sign_size)),
                             (self.WIDTH // 2 - small_sign_size // 2, 10))

            self.draw_grid()

            if self.result_text:
                if not self.pause_menu_active:
                    self.draw_congratulations()

            if self.pause_menu_active:
                self.draw_pause_menu()

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    game = Saturn()
    game.run()
