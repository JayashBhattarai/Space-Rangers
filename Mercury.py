import pygame
import sys

class Mercury:
    def __init__(self):
        pygame.init()

        self.screen_width = 1200
        self.screen_height = 800

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.translucent_gray = (128, 128, 128, 128)

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Trolley Problem")

        self.trolley_image = pygame.image.load('trolley.png')
        self.trolley_image = pygame.transform.scale(self.trolley_image, (100, 100))

        self.track_image = pygame.image.load('tracks.png')
        self.track_image = pygame.transform.scale(self.track_image, (50, 100))
        self.track_image = pygame.transform.rotate(self.track_image, 90)

        # self.cross_image = self.create_cross_image()

        self.trolley_x = 50
        self.trolley_y = self.screen_height // 2
        self.trolley_speed = 5

        self.upper_track_y = self.screen_height // 4
        self.lower_track_y = 3 * self.screen_height // 4
        self.middle_track_y = self.screen_height // 2

        self.divergence_x = self.screen_width // 2
        self.cross_x = int(self.screen_width * 0.9)

        self.direction = 0

        self.font = pygame.font.SysFont(None, 55)

        self.questions = [
            {"question": "What is 2 + 2?", "up": "3", "down": "4", "correct": "down"},
            {"question": "What is the capital of France?", "up": "Paris", "down": "London", "correct": "up"},
            {"question": "What is the largest planet?", "up": "Earth", "down": "Jupiter", "correct": "down"},
            {"question": "What is the square root of 16?", "up": "3", "down": "4", "correct": "down"},
            {"question": "What is the chemical symbol for water?", "up": "H2O", "down": "CO2", "correct": "up"}
        ]
        self.current_question = 0
        self.show_question = False
        self.answered = False
        self.paused = False
        self.at_divergence = False
        self.correct_answers = 0
        self.game_completed = False
        self.incorrect = False
        self.show_pause_menu = False
        self.game_over = False

    def create_cross_image(self):
        cross_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, self.red, (0, 0), (50, 50), 5)
        pygame.draw.line(cross_surface, self.red, (50, 0), (0, 50), 5)
        return cross_surface

    def draw_trolley(self, x, y):
        self.screen.blit(self.trolley_image, (x - 50, y - 50))

    def draw_track(self, x, y, angle=0):
        track = pygame.transform.rotate(self.track_image, angle)
        self.screen.blit(track, (x, y - 25))

    def draw_vertical_track(self, x, y_start, y_end):
        if y_start > y_end:
            y_start, y_end = y_end, y_start  # Ensure y_start is always less than y_end
        y = y_start
        while y < y_end:
            self.draw_track(x, y, angle=90)
            y += 50

    # def draw_cross(self, x, y):
        # self.screen.blit(self.cross_image, (x - 25, y - 25))

    def draw_text(self, text, x, y):
        screen_text = self.font.render(text, True, self.black)
        text_rect = screen_text.get_rect(center=(x, y))
        self.screen.blit(screen_text, text_rect)

    def draw_question(self, question_data):
        self.draw_text(question_data["question"], self.screen_width // 2, 50)
        self.draw_text("UP: " + question_data["up"], self.screen_width // 2, 110)
        self.draw_text("DOWN: " + question_data["down"], self.screen_width // 2, 170)

    def draw_pause_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(s, (0, 0))

        self.draw_text("PAUSE MENU", self.screen_width // 2, self.screen_height // 2 - 100)
        self.draw_text("Press R to Resume", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2 + 60)
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + 120)

    def draw_game_over_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(s, (0, 0))

        self.draw_text("CRASH! Game Over.", self.screen_width // 2, self.screen_height // 2 - 100)
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + 60)

    def draw_congratulations_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(s, (0, 0))

        self.draw_text("Congratulations! You won!", self.screen_width // 2, self.screen_height // 2 - 100)
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + 60)

    def reset_game(self):
        self.trolley_x = 50
        self.trolley_y = self.middle_track_y
        self.current_question = 0
        self.show_question = False
        self.answered = False
        self.paused = False
        self.at_divergence = False
        self.correct_answers = 0
        self.game_completed = False
        self.incorrect = False
        self.show_pause_menu = False
        self.game_over = False

    def main(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.show_pause_menu:
                            self.paused = False
                            self.show_pause_menu = False
                        else:
                            self.paused = not self.paused
                            self.show_pause_menu = self.paused

                    if self.show_pause_menu:
                        if event.key == pygame.K_r:
                            self.paused = False
                            self.show_pause_menu = False
                        if event.key == pygame.K_t:
                            self.reset_game()
                        if event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"
                    elif self.game_completed or self.game_over:
                        if event.key == pygame.K_t:
                            self.reset_game()
                        if event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"
                    elif self.show_question:
                        if event.key == pygame.K_UP:
                            self.direction = 1
                            self.answered = True
                        if event.key == pygame.K_DOWN:
                            self.direction = 2
                            self.answered = True
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.direction = 0

            if self.game_completed:
                self.screen.fill(self.white)
                self.draw_congratulations_menu()
                pygame.display.flip()
                continue

            if self.game_over:
                self.screen.fill(self.white)
                self.draw_game_over_menu()
                pygame.display.flip()
                continue

            if not self.paused and not self.show_pause_menu:
                self.trolley_x += self.trolley_speed

            if self.trolley_x > self.divergence_x and not self.show_question and not self.at_divergence:
                self.show_question = True
                self.paused = True
                self.at_divergence = True

            if self.show_question and self.answered:
                correct = self.questions[self.current_question]["correct"]
                chosen_track_y = self.upper_track_y if self.direction == 1 else self.lower_track_y
                if (correct == "up" and self.direction == 1) or (correct == "down" and self.direction == 2):
                    self.trolley_y = chosen_track_y
                    self.paused = False
                    self.show_question = False
                    self.answered = False
                    self.correct_answers += 1
                    self.incorrect = False
                    self.current_question += 1
                else:
                    self.trolley_y = chosen_track_y
                    self.paused = False
                    self.show_question = False
                    self.answered = False
                    self.incorrect = True

            if not self.show_question and not self.paused and not self.show_pause_menu:
                if self.trolley_x >= self.screen_width - 50:
                    self.trolley_x = 50
                    self.trolley_y = self.middle_track_y
                    self.at_divergence = False
                    if self.incorrect:
                        self.game_over = True
                    else:
                        if self.current_question >= len(self.questions):
                            if self.correct_answers == 5:
                                self.game_completed = True
                            else:
                                self.game_over = True

            self.screen.fill(self.white)

            for x in range(0, self.screen_width, 50):
                if x < self.divergence_x:
                    self.draw_track(x, self.middle_track_y)
                if x >= self.divergence_x:
                    self.draw_track(x, self.upper_track_y)
                    self.draw_track(x, self.lower_track_y)

            self.draw_vertical_track(self.divergence_x, self.middle_track_y, self.upper_track_y)
            self.draw_vertical_track(self.divergence_x, self.middle_track_y, self.lower_track_y)

            # self.draw_cross(self.divergence_x, self.middle_track_y)
            self.draw_trolley(self.trolley_x, self.trolley_y)

            if self.show_question:
                self.draw_question(self.questions[self.current_question])

            if not self.show_question and not self.paused and not self.show_pause_menu:
                self.draw_text("Press UP or DOWN to choose track", self.screen_width // 2, 50)

            if self.show_pause_menu:
                self.draw_pause_menu()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Mercury()
    game.main()
