import pygame
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
        self.current_text_index = 0

    def set_text(self, text):
        if isinstance(text, list):
            self.text = text
            self.current_text_index = 0
            self.set_current_text()
        else:
            self.text = [text]
            self.set_current_text()

    def set_current_text(self):
        current_text = self.text[self.current_text_index]
        self.rendered_text = []
        self.text_content = []
        wrapped_text = self.wrap_text(current_text, self.rect.width - 20)
        for line in wrapped_text:
            self.rendered_text.append(self.font.render(line, True, (255, 255, 255)))
            self.text_content.append(line)
        self.reveal_index = 0

    def wrap_text(self, text, max_width):
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            words = line.split(' ')
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
        if self.reveal_index >= sum(len(line) for line in self.text_content):
            if self.current_text_index < len(self.text) - 1:
                self.current_text_index += 1
                self.set_current_text()
                return False
            return True
        return False


class Mercury:
    def __init__(self):
        pygame.init()

        # Get the screen info
        screen_info = pygame.display.Info()
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.translucent_gray = (128, 128, 128, 128)

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Trolley Problem")

        # Load and scale background image
        self.background = pygame.image.load('src/mercury.jpg').convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        # Load and scale trolley image
        self.trolley_image = pygame.image.load('src/trolley.png')
        trolley_size = int(min(self.screen_width, self.screen_height) * 0.1)
        self.trolley_image = pygame.transform.scale(self.trolley_image, (trolley_size, trolley_size))

        # Load and scale track image
        self.track_image = pygame.image.load('src/tracks.png')
        track_width = int(self.screen_width * 0.04)
        track_height = int(self.screen_height * 0.1)
        self.track_image = pygame.transform.scale(self.track_image, (track_width, track_height))
        self.track_image = pygame.transform.rotate(self.track_image, 90)

        self.trolley_x = int(self.screen_width * 0.05)
        self.trolley_y = self.screen_height // 2
        self.trolley_speed = int(self.screen_width * 0.004)

        self.upper_track_y = self.screen_height // 4
        self.lower_track_y = 3 * self.screen_height // 4
        self.middle_track_y = self.screen_height // 2

        self.divergence_x = self.screen_width // 2

        self.direction = 0

        self.font = pygame.font.SysFont(None, int(self.screen_height * 0.05))

        self.questions = [
            {"question": "Where is the largest Volcano in the Solar System?", "up": "Saturn", "down": "Mars", "correct": "down"},
            {"question": "How many moons does Jupiter have?", "up": "79", "down": "81", "correct": "up"},
            {"question": "What is the largest moon in the solar system?", "up": "Titan", "down": "Ganymede", "correct": "down"},
            {"question": "Which planet is closest in size to Earth?", "up": "Neptune", "down": "Venus", "correct": "down"},
            {"question": "Which is the coldest planet in the solar system?", "up": "Uranus", "down": "Neptune", "correct": "up"}
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

        # Load and play background music
        pygame.mixer.music.load('src/mercurybgm.mp3')
        pygame.mixer.music.play(-1)  # -1 loops indefinitely, 0 plays once

        # Load explosion sound
        self.explosion_sound = pygame.mixer.Sound('src/explosion.wav')

        # Text box and game state
        text_box_width = int(self.screen_width * 0.9)
        text_box_height = int(self.screen_height * 0.2)
        text_box_x = (self.screen_width - text_box_width) // 2
        text_box_y = int(self.screen_height * 0.75)
        self.text_box = TextBox(text_box_x, text_box_y, text_box_width, text_box_height)
        self.game_state = "intro"
        self.intro_text = "Welcome to Mercury! John, your mission is to get past the cave! Choose the right path wisely!"
        self.victory_text = ["Congratulations! You've successfully gone past the cave! Obtained the Taurus gem.",
                            "John! It seems like the alien boss is in the Sun.",
                             "We need to defeat him and reactivate the shield machine"]
        self.defeat_text = "Mission failed. Rethink about your choices, John. Try again!"

    def draw_trolley(self, x, y):
        self.screen.blit(self.trolley_image, (x - self.trolley_image.get_width()//2, y - self.trolley_image.get_height()//2))

    def draw_track(self, x, y, angle=0):
        track = pygame.transform.rotate(self.track_image, angle)
        self.screen.blit(track, (x, y - track.get_height()//2))

    def draw_vertical_track(self, x, y_start, y_end):
        if y_start > y_end:
            y_start, y_end = y_end, y_start  # Ensure y_start is always less than y_end
        y = y_start
        while y < y_end:
            self.draw_track(x, y, angle=90)
            y += self.track_image.get_width()

    def draw_text(self, text, x, y):
        screen_text = self.font.render(text, True, self.white)
        text_rect = screen_text.get_rect(center=(x, y))
        self.screen.blit(screen_text, text_rect)

    def draw_question(self, question_data):
        self.draw_text(question_data["question"], self.screen_width // 2, int(self.screen_height * 0.05))
        self.draw_text("UP: " + question_data["up"], self.screen_width // 2, int(self.screen_height * 0.15))
        self.draw_text("DOWN: " + question_data["down"], self.screen_width // 2, int(self.screen_height * 0.2))

    def draw_pause_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(self.background, (0, 0))

        self.draw_text("PAUSE MENU", self.screen_width // 2, self.screen_height // 2 - int(self.screen_height * 0.1))
        self.draw_text("Press R to Resume", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2 + int(self.screen_height * 0.07))
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + int(self.screen_height * 0.14))

    def draw_game_over_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(self.background, (0, 0))

        self.text_box.draw(self.screen)
        self.draw_text("CRASH! Game Over.", self.screen_width // 2, self.screen_height // 2 - int(self.screen_height * 0.1))
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + int(self.screen_height * 0.07))

    def draw_congratulations_menu(self):
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill(self.translucent_gray)
        self.screen.blit(self.background, (0, 0))

        self.text_box.draw(self.screen)
        self.draw_text("Congratulations! You won!", self.screen_width // 2, self.screen_height // 2 - int(self.screen_height * 0.1))
        self.draw_text("Press T to Retry", self.screen_width // 2, self.screen_height // 2)
        self.draw_text("Press Q to Quit", self.screen_width // 2, self.screen_height // 2 + int(self.screen_height * 0.07))

    def reset_game(self):
        self.trolley_x = int(self.screen_width * 0.05)
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
        self.game_state = "intro"
        self.text_box.set_text(self.intro_text)

    def main(self):
        running = True

        self.text_box.set_text(self.intro_text)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.game_state == "intro":
                        if event.key == pygame.K_RETURN:
                            if self.text_box.is_finished():
                                self.game_state = "playing"
                            else:
                                self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)
                    elif event.key == pygame.K_ESCAPE:
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
                    elif self.game_state in ["victory", "defeat"]:
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
                self.game_state = "victory"
                self.screen.fill(self.white)
                self.draw_congratulations_menu()
                pygame.display.flip()
                continue

            if self.game_over:
                self.game_state = "defeat"
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
                if self.trolley_x >= self.screen_width - self.trolley_image.get_width():
                    self.trolley_x = int(self.screen_width * 0.05)
                    self.trolley_y = self.middle_track_y
                    self.at_divergence = False
                    if self.incorrect:
                        self.explosion_sound.play()  # Play explosion sound on crash
                        self.game_over = True
                    else:
                        if self.current_question >= len(self.questions):
                            if self.correct_answers == 5:
                                self.game_completed = True
                            else:
                                self.game_over = True

            if self.game_state == "playing":
                if self.game_completed:
                    self.game_state = "victory"
                    self.text_box.set_text(self.victory_text)
                elif self.game_over:
                    self.game_state = "defeat"
                    self.text_box.set_text(self.defeat_text)

                # Draw background
            self.screen.blit(self.background, (0, 0))

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)
            elif self.game_state == "playing":
                track_spacing = int(self.screen_width * 0.04)
                for x in range(0, self.screen_width, track_spacing):
                    if x < self.divergence_x:
                        self.draw_track(x, self.middle_track_y)
                    if x >= self.divergence_x:
                        self.draw_track(x, self.upper_track_y)
                        self.draw_track(x, self.lower_track_y)

                self.draw_vertical_track(self.divergence_x, self.middle_track_y, self.upper_track_y)
                self.draw_vertical_track(self.divergence_x, self.middle_track_y, self.lower_track_y)

                self.draw_trolley(self.trolley_x, self.trolley_y)

                if self.show_question:
                    self.draw_question(self.questions[self.current_question])

                if not self.show_question and not self.paused and not self.show_pause_menu:
                    self.draw_text("Press UP or DOWN to choose track", self.screen_width // 2,
                                   int(self.screen_height * 0.05))

                if self.show_pause_menu:
                    self.draw_pause_menu()

            elif self.game_state == "victory":
                self.text_box.update()
                self.draw_congratulations_menu()
            elif self.game_state == "defeat":
                self.text_box.update()
                self.draw_game_over_menu()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Mercury()
    game.main()