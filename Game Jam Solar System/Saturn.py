from ui_controls import draw_options
from input_controls import get_events, pressed_keys
from campaign import complete_level
from dialogue import DialogueBox
from display_settings import game_size
import pygame
import random
import sys
import textwrap
from pygame import mixer

class TextBox(DialogueBox):
    def __init__(self, x, y, width, height, screen_width, screen_height):
        super().__init__(int(x * screen_width), int(y * screen_height), int(width * screen_width), int(height * screen_height), int(screen_height * 0.04))


class Saturn:
    def __init__(self):
        pygame.init()

        # Screen setup
        self.WIDTH, self.HEIGHT = game_size()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Alien Jigsaw Puzzle")
        self.background = pygame.image.load("src/saturnbackground.jpg")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        mixer.music.load('src/saturnbgm.mp3')
        mixer.music.play(-1)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (169, 169, 169)

        # Load image
        self.alien_image = pygame.image.load('src/saturn.png')

        # Resize image
        self.sign_size = int(0.375 * self.HEIGHT)
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
        self.center_y = (self.HEIGHT - self.pieces_per_row * self.piece_size) // 2 + int(0.0625 * self.HEIGHT)

        # Pause menu variables
        self.pause_menu_active = False
        self.selected_option = 0  # 0: Resume, 1: Retry, 2: Quit
        self.pause_menu_font = pygame.font.Font(None, int(0.045 * self.HEIGHT))

        # Congratulations screen variables
        self.congratulations_active = False
        self.congratulations_font = pygame.font.Font(None, int(0.06 * self.HEIGHT))
        self.options_font = pygame.font.Font(None, int(0.045 * self.HEIGHT))
        self.congratulations_options = ["Retry", "Quit"]
        self.congratulations_selected = 0

        self.text_box = TextBox(0.0417, 0.75, 0.9167, 0.1875, self.WIDTH, self.HEIGHT)
        self.game_state = "intro"
        self.intro_text = "Welcome to Saturn! John, there's a puzzle! The puzzle should look like the image on top!"
        self.victory_text = "Congratulations! You've successfully completed the Saturn stage! Obtained the Scorpio and the Capricorn gem"

    def draw_grid(self):
        for i in range(self.total_pieces):
            x = (i % self.pieces_per_row) * self.piece_size + self.center_x
            y = (i // self.pieces_per_row) * self.piece_size + self.center_y
            piece_index = self.grid[i]
            piece = self.alien_pieces[piece_index]
            self.screen.blit(piece, (x, y))
            pygame.draw.rect(self.screen, self.BLACK, (x, y, self.piece_size, self.piece_size), 1)

    def draw_reference_image(self):
        small_sign_size = int(0.125 * self.HEIGHT)
        self.screen.blit(pygame.transform.scale(self.alien_image, (small_sign_size, small_sign_size)),
                         (self.WIDTH // 2 - small_sign_size // 2, int(0.0125 * self.HEIGHT)))

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
        menu_width = max(resume_text.get_width(), retry_text.get_width(), quit_text.get_width()) + int(0.0333 * self.WIDTH)

        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, self.WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        self.screen.blit(resume_text, (menu_x + int(0.0167 * self.WIDTH), menu_y + int(0.025 * self.HEIGHT)))
        self.screen.blit(retry_text, (menu_x + int(0.0167 * self.WIDTH), menu_y + int(0.025 * self.HEIGHT) + resume_text.get_height()))
        self.screen.blit(quit_text, (menu_x + int(0.0167 * self.WIDTH), menu_y + int(0.025 * self.HEIGHT) + resume_text.get_height() * 2))

    def draw_congratulations(self):
        self.screen.blit(self.background, (0, 0))  # Draw the background image

        self.text_box.draw(self.screen)

        congratulations_text = self.congratulations_font.render("Congratulations! The puzzle is solved.", True,
                                                                self.WHITE)
        text_rect = congratulations_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - int(0.125 * self.HEIGHT)))
        self.screen.blit(congratulations_text, text_rect)

        for i, option in enumerate(self.congratulations_options):
            color = self.BLACK if self.congratulations_selected == i else self.WHITE
            option_text = self.options_font.render(option, True, color)
            text_x = self.WIDTH // 2 - option_text.get_width() // 2
            text_y = self.HEIGHT // 2 + int(0.0625 * self.HEIGHT) + i * (option_text.get_height() + int(0.025 * self.HEIGHT))

            if self.congratulations_selected == i:
                rect = option_text.get_rect(center=(self.WIDTH // 2, text_y + option_text.get_height() // 2))
                pygame.draw.rect(self.screen, self.WHITE, rect.inflate(int(0.0167 * self.WIDTH), int(0.0125 * self.HEIGHT)))

            self.screen.blit(option_text, (text_x, text_y))

    def handle_events(self):
        for event in get_events(self):
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "intro":
                    if event.key == pygame.K_RETURN:
                        if self.text_box.is_finished():
                            self.game_state = "playing"
                        else:
                            self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)
                elif event.key == pygame.K_ESCAPE:
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
                            pygame.mixer.music.stop()
                            return "main_menu"

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
                            pygame.mixer.music.stop()
                            return "main_menu"

            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing" and not self.game_over and not self.pause_menu_active:
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
                        complete_level("saturn")

                self.dragging_piece = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.congratulations_active:
                        self.pause_menu_active = not self.pause_menu_active
                        self.selected_option = 0

        return None

    def reset_game(self):
        self.dragging_piece = None
        self.pause_menu_active = False
        random.shuffle(self.grid)
        self.game_over = False
        self.congratulations_active = False
        self.selected_option = 0
        self.congratulations_selected = 0
        self.game_state = "intro"
        self.text_box.set_text(self.intro_text)

    def run(self):
        clock = pygame.time.Clock()
        self.text_box.set_text(self.intro_text)
        while True:
            action = self.handle_events()
            if action == "main_menu":
                return "main_menu"

            self.screen.blit(self.background, (0, 0))

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)
            elif self.congratulations_active:
                if self.text_box.text != self.victory_text:
                    self.text_box.set_text(self.victory_text)
                self.text_box.update()
                self.draw_congratulations()
            elif self.game_state == "playing":
                self.draw_reference_image()
                self.draw_grid()

            if self.pause_menu_active and not self.congratulations_active:
                self.draw_pause_menu()

            draw_options(self)
            pygame.display.flip()
            clock.tick(30)


if __name__ == "__main__":
    game = Saturn()
    game.run()
