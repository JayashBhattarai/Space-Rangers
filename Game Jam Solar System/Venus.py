import pygame
import random
import textwrap

class TextBox:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.rect = pygame.Rect(int(x * screen_width), int(y * screen_height),
                                int(width * screen_width), int(height * screen_height))
        self.text = ""
        self.rendered_text = []
        self.text_content = []
        self.reveal_index = 0
        self.line_spacing = 5
        self.font = pygame.font.Font(None, int(screen_height * 0.04))

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


class Venus:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen setup
        info = pygame.display.Info()
        self.WIDTH, self.HEIGHT = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Zodiac Memory Card Game")

        self.background = pygame.image.load('src/venus.jpg')
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.CARD_BACK = (50, 50, 200)
        self.GOLD = (255, 215, 0)
        self.SEMI_TRANSPARENT_BLACK = (0, 0, 0, 128)

        # Card dimensions
        self.CARD_WIDTH = int(self.WIDTH * 0.08)
        self.CARD_HEIGHT = int(self.HEIGHT * 0.15)
        self.CARD_MARGIN = int(self.WIDTH * 0.01)

        # Zodiac signs
        self.ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo"]

        # Calculate grid position
        self.GRID_WIDTH = 4 * (self.CARD_WIDTH + self.CARD_MARGIN) - self.CARD_MARGIN
        self.GRID_HEIGHT = 3 * (self.CARD_HEIGHT + self.CARD_MARGIN) - self.CARD_MARGIN
        self.GRID_LEFT = (self.WIDTH - self.GRID_WIDTH) // 2
        self.GRID_TOP = (self.HEIGHT - self.GRID_HEIGHT) // 2

        self.cards = self.create_cards()

        # Game variables
        self.flipped_cards = []
        self.matched_pairs = 0
        self.attempts = 0
        self.level_complete = False
        self.paused = False

        # Font setup
        self.font = pygame.font.Font(None, int(self.HEIGHT * 0.045))
        self.card_font = pygame.font.Font(None, int(self.HEIGHT * 0.03))
        self.congrats_font = pygame.font.Font(None, int(self.HEIGHT * 0.06))

        # Initialize mixer and load background music
        pygame.mixer.init()
        pygame.mixer.music.load('src/venus.mp3')
        pygame.mixer.music.set_volume(0.1)  # Set initial volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # -1 makes the music loop indefinitely

        self.text_box = TextBox(0.04, 0.75, 0.92, 0.19, self.WIDTH, self.HEIGHT)
        self.game_state = "intro"
        self.intro_text = "Welcome to Venus! John, your mission is to match the cards with same zodiac name"
        self.victory_text = "Congratulations! You've successfully matched all the cards! Obtained the Gemini and the Virgo gem. John! It seems like we can not go to Mercury because of the heat barrier. We need to find Aquarius and Pisces to go through it!"

    def create_cards(self):
        card_values = self.ZODIAC_SIGNS * 2
        random.shuffle(card_values)

        cards = []
        for row in range(3):
            for col in range(4):
                x = self.GRID_LEFT + col * (self.CARD_WIDTH + self.CARD_MARGIN)
                y = self.GRID_TOP + row * (self.CARD_HEIGHT + self.CARD_MARGIN)
                card = {
                    'rect': pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT),
                    'value': card_values.pop(),
                    'flipped': False
                }
                cards.append(card)
        return cards

    def draw_card(self, surface, card):
        if card['flipped']:
            pygame.draw.rect(surface, self.WHITE, card['rect'])
            pygame.draw.rect(surface, self.BLACK, card['rect'], 2)

            # Draw card corners
            corner_text = self.card_font.render(card['value'][:2], True, self.RED)
            surface.blit(corner_text, (card['rect'].left + 5, card['rect'].top + 5))
            surface.blit(corner_text, (card['rect'].right - 25, card['rect'].bottom - 25))

            # Draw card center
            center_text = self.card_font.render(card['value'], True, self.BLACK)
            text_rect = center_text.get_rect(center=card['rect'].center)
            surface.blit(center_text, text_rect)
        else:
            pygame.draw.rect(surface, self.CARD_BACK, card['rect'])
            pygame.draw.rect(surface, self.BLACK, card['rect'], 2)

            # Draw card back design
            pygame.draw.rect(surface, self.BLACK, card['rect'].inflate(-10, -10), 2)
            pygame.draw.rect(surface, self.BLACK, card['rect'].inflate(-20, -20), 2)

    def show_congratulations(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.SEMI_TRANSPARENT_BLACK)

        self.screen.blit(overlay, (0, 0))

        # Draw the congratulations message
        congrats_text = self.congrats_font.render("Congratulations!", True, self.WHITE)
        self.screen.blit(congrats_text, (
            self.WIDTH // 2 - congrats_text.get_width() // 2,
            self.HEIGHT // 2 - congrats_text.get_height() // 2))

        retry_text = self.font.render("Press R to Retry", True, self.WHITE)
        self.screen.blit(retry_text, (
            self.WIDTH // 2 - retry_text.get_width() // 2,
            self.HEIGHT // 2 - retry_text.get_height() // 2 + 50))

        quit_text = self.font.render("Press Q to Quit", True, self.WHITE)
        self.screen.blit(quit_text, (
            self.WIDTH // 2 - quit_text.get_width() // 2,
            self.HEIGHT // 2 - quit_text.get_height() // 2 + 100))

    def pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.congrats_font.render("Paused", True, self.WHITE)
        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - 150))

        resume_text = self.font.render("Press 'R' to Resume", True, self.WHITE)
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, self.HEIGHT // 2 - 50))

        restart_text = self.font.render("Press 'T' to Restart", True, self.WHITE)
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2))

        quit_text = self.font.render("Press 'Q' to Quit", True, self.WHITE)
        self.screen.blit(quit_text, (self.WIDTH // 2 - quit_text.get_width() // 2, self.HEIGHT // 2 + 50))

    def main(self):
        # Main game loop
        clock = pygame.time.Clock()
        running = True

        self.text_box.set_text(self.intro_text)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif self.game_state == "intro" and event.key == pygame.K_RETURN:
                        if self.text_box.is_finished():
                            self.game_state = "playing"
                        else:
                            self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)
                    if self.paused:
                        if event.key == pygame.K_r:
                            self.paused = False
                        elif event.key == pygame.K_t:
                            self.cards = self.create_cards()
                            self.flipped_cards = []
                            self.matched_pairs = 0
                            self.attempts = 0
                            self.level_complete = False
                            self.paused = False
                        elif event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"
                elif not self.paused and self.game_state == "playing":
                    if event.type == pygame.MOUSEBUTTONDOWN and len(self.flipped_cards) < 2:
                        pos = pygame.mouse.get_pos()
                        for card in self.cards:
                            if card['rect'].collidepoint(pos) and not card['flipped']:
                                card['flipped'] = True
                                self.flipped_cards.append(card)
                                if len(self.flipped_cards) == 2:
                                    self.attempts += 1
                                    if self.flipped_cards[0]['value'] == self.flipped_cards[1]['value']:
                                        self.matched_pairs += 1
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)  # Set timer for 1 second
                    elif event.type == pygame.USEREVENT:
                        pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
                        if len(self.flipped_cards) == 2:
                            if self.flipped_cards[0]['value'] != self.flipped_cards[1]['value']:
                                self.flipped_cards[0]['flipped'] = False
                                self.flipped_cards[1]['flipped'] = False
                            self.flipped_cards.clear()

            self.screen.blit(self.background, (0, 0))

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)
            elif self.paused:
                self.pause_menu()
            elif not self.level_complete:
                # Draw cards
                for card in self.cards:
                    self.draw_card(self.screen, card)

                # Draw game info
                info_text = f"Pairs: {self.matched_pairs}/6 | Attempts: {self.attempts}"
                info_surface = self.font.render(info_text, True, self.WHITE)
                self.screen.blit(info_surface, (self.WIDTH // 2 - info_surface.get_width() // 2, 20))

                # Check for game over
                if self.matched_pairs == 6:
                    self.level_complete = True
                    self.game_state = "victory"
                    self.text_box.set_text(self.victory_text)

                # Control the game speed
                clock.tick(30)
            else:
                self.show_congratulations()
                self.text_box.update()
                self.text_box.draw(self.screen)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # Retry current level
                            self.level_complete = False
                            self.matched_pairs = 0
                            self.attempts = 0
                            self.cards = self.create_cards()
                            self.game_state = "playing"
                        elif event.key == pygame.K_q:  # Quit game
                            pygame.mixer.music.stop()
                            return "main_menu"

            pygame.display.flip()

        pygame.mixer.music.stop()  # Stop music when quitting the game
        pygame.quit()

if __name__ == "__main__":
    game = Venus()
    game.main()