import pygame
import random
import sys
from pygame import mixer


class Saturn:
    def __init__(self):
        pygame.init()

        # Screen setup
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Alien Jigsaw Puzzle")
        self.background = pygame.image.load("saturnbackground.jpg")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        mixer.music.load('saturnbgm.mp3')
        mixer.music.play(-1)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (169, 169, 169)

        # Load image
        self.alien_image = pygame.image.load('saturn.png')

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

        # Centering variables
        self.center_x = (self.WIDTH - self.pieces_per_row * self.piece_size) // 2
        self.center_y = (self.HEIGHT - self.pieces_per_row * self.piece_size) // 2 + 50  # Adjusted for space

        # Pause menu variables
        self.pause_menu_active = False
        self.selected_option = 0  # 0: Resume, 1: Retry, 2: Quit
        self.pause_menu_font = pygame.font.Font(None, 36)

        # Congratulations screen variables
        self.congratulations_active = False
        self.congratulations_font = pygame.font.Font(None, 48)
        self.options_font = pygame.font.Font(None, 36)
        self.congratulations_options = ["Retry", "Quit"]
        self.congratulations_selected = 0

    def draw_grid(self):
        for i in range(self.total_pieces):
            x = (i % self.pieces_per_row) * self.piece_size + self.center_x
            y = (i // self.pieces_per_row) * self.piece_size + self.center_y
            piece_index = self.grid[i]
            piece = self.alien_pieces[piece_index]
            self.screen.blit(piece, (x, y))
            pygame.draw.rect(self.screen, self.BLACK, (x, y, self.piece_size, self.piece_size), 1)

    def draw_reference_image(self):
        small_sign_size = 100
        self.screen.blit(pygame.transform.scale(self.alien_image, (small_sign_size, small_sign_size)),
                         (self.WIDTH // 2 - small_sign_size // 2, 10))

    def check_correct_placement(self):
        return self.grid == list(range(self.total_pieces))

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # 100 alpha for translucency
        self.screen.blit(overlay, (0, 0))

        resume_text = self.pause_menu_font.render("Resume", True,
                                                  self.WHITE if self.selected_option != 0 else self.BLACK)
        retry_text = self.pause_menu_font.render("Retry", True, self.WHITE if self.selected_option != 1 else self.BLACK)
        quit_text = self.pause_menu_font.render("Quit", True, self.WHITE if self.selected_option != 2 else self.BLACK)

        menu_height = resume_text.get_height() * 3
        menu_width = max(resume_text.get_width(), retry_text.get_width(), quit_text.get_width()) + 40

        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, self.WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        self.screen.blit(resume_text, (menu_x + 20, menu_y + 20))
        self.screen.blit(retry_text, (menu_x + 20, menu_y + 20 + resume_text.get_height()))
        self.screen.blit(quit_text, (menu_x + 20, menu_y + 20 + resume_text.get_height() * 2))

    def draw_congratulations(self):
        self.screen.blit(self.background, (0, 0))  # Draw the background image

        congratulations_text = self.congratulations_font.render("Congratulations! The puzzle is solved.", True,
                                                                self.WHITE)
        text_rect = congratulations_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 100))
        self.screen.blit(congratulations_text, text_rect)

        for i, option in enumerate(self.congratulations_options):
            color = self.BLACK if self.congratulations_selected == i else self.WHITE
            option_text = self.options_font.render(option, True, color)
            text_x = self.WIDTH // 2 - option_text.get_width() // 2
            text_y = self.HEIGHT // 2 + 50 + i * (option_text.get_height() + 20)

            if self.congratulations_selected == i:
                rect = option_text.get_rect(center=(self.WIDTH // 2, text_y + option_text.get_height() // 2))
                pygame.draw.rect(self.screen, self.WHITE, rect.inflate(20, 10))

            self.screen.blit(option_text, (text_x, text_y))

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
                    self.grid[self.dragging_piece], self.grid[target_index] = self.grid[target_index], self.grid[
                        self.dragging_piece]
                    self.dragging_piece = None

                    # Check if the puzzle is solved after each move
                    if self.check_correct_placement():
                        self.game_over = True
                        self.congratulations_active = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.congratulations_active:
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

                if self.congratulations_active:
                    if event.key == pygame.K_UP:
                        self.congratulations_selected = (self.congratulations_selected - 1) % len(
                            self.congratulations_options)
                    elif event.key == pygame.K_DOWN:
                        self.congratulations_selected = (self.congratulations_selected + 1) % len(
                            self.congratulations_options)
                    elif event.key == pygame.K_RETURN:
                        if self.congratulations_selected == 0:  # Retry
                            self.reset_game()
                        elif self.congratulations_selected == 1:  # Quit
                            pygame.quit()
                            sys.exit()

    def reset_game(self):
        random.shuffle(self.grid)
        self.game_over = False
        self.congratulations_active = False
        self.selected_option = 0
        self.congratulations_selected = 0

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()

            self.screen.blit(self.background, (0, 0))

            if self.congratulations_active:
                self.draw_congratulations()
            else:
                self.draw_reference_image()
                self.draw_grid()

            if self.pause_menu_active and not self.congratulations_active:
                self.draw_pause_menu()

            pygame.display.flip()
            clock.tick(30)


if __name__ == "__main__":
    game = Saturn()
    game.run()