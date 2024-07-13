import pygame
import random

class Venus:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen setup
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Zodiac Memory Card Game")

        self.background = pygame.image.load('venus.jpg')

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.CARD_BACK = (50, 50, 200)
        self.GOLD = (255, 215, 0)
        self.SEMI_TRANSPARENT_BLACK = (0, 0, 0, 128)

        # Card dimensions
        self.CARD_WIDTH, self.CARD_HEIGHT = 100, 150
        self.CARD_MARGIN = 20

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
        self.font = pygame.font.Font(None, 36)
        self.card_font = pygame.font.Font(None, 24)
        self.congrats_font = pygame.font.Font(None, 48)

        # Initialize mixer and load background music
        pygame.mixer.init()
        pygame.mixer.music.load('venus.mp3')
        pygame.mixer.music.set_volume(0.1)  # Set initial volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # -1 makes the music loop indefinitely

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

        next_level_text = self.font.render("Press N for Next Level", True, self.WHITE)
        self.screen.blit(next_level_text, (
            self.WIDTH // 2 - next_level_text.get_width() // 2,
            self.HEIGHT // 2 - next_level_text.get_height() // 2 + 50))

        restart_level_text = self.font.render("Press R to Restart Level", True, self.WHITE)
        self.screen.blit(restart_level_text, (
            self.WIDTH // 2 - restart_level_text.get_width() // 2,
            self.HEIGHT // 2 - restart_level_text.get_height() // 2 + 100))

        pygame.display.flip()

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

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
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
                elif not self.paused:
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

            if self.paused:
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

                # Control the game speed
                clock.tick(30)
            else:
                self.show_congratulations()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_n:  # Proceed to next level
                            self.level_complete = False
                            self.matched_pairs = 0
                            self.attempts = 0
                            self.cards = self.create_cards()
                        elif event.key == pygame.K_r:  # Restart current level
                            self.level_complete = False
                            self.matched_pairs = 0
                            self.attempts = 0
                            self.cards = self.create_cards()
                        elif event.key == pygame.K_q:  # Quit game
                            pygame.mixer.music.stop()
                            return "main_menu"

            pygame.display.flip()

        pygame.mixer.music.stop()  # Stop music when quitting the game
        pygame.quit()

if __name__ == "__main__":
    game = Venus()
    game.main()
