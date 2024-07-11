import pygame
import sys

class Mercury:
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

        # Initialize screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Trolley Problem")

        # Trolley position
        self.trolley_x = self.screen_width // 2
        self.trolley_y = 50
        self.trolley_speed = 5

        # Tracks positions
        self.left_track = self.screen_width // 4
        self.right_track = 3 * self.screen_width // 4
        self.middle_track = self.screen_width // 2

        # Trolley direction (0: no move, 1: left, 2: right)
        self.direction = 0

        # Font for text
        self.font = pygame.font.SysFont(None, 55)

        # Questions and answers
        self.questions = [
            {"question": "What is 2 + 2?", "left": "3", "right": "4", "correct": "right"},
            {"question": "What is the capital of France?", "left": "Paris", "right": "London", "correct": "left"},
            {"question": "What is the largest planet?", "left": "Earth", "right": "Jupiter", "correct": "right"}
        ]
        self.current_question = 0
        self.show_question = False
        self.answered = False
        self.paused = False
        self.at_divergence = False
        self.correct_answers = 0
        self.game_completed = False
        self.incorrect = False

    def draw_trolley(self, x, y):
        pygame.draw.rect(self.screen, self.red, [x - 25, y - 25, 50, 50])

    def draw_text(self, text, x, y):
        screen_text = self.font.render(text, True, self.black)
        self.screen.blit(screen_text, [x, y])

    def draw_question(self, question_data):
        self.draw_text(question_data["question"], 50, self.screen_height // 2 - 50)
        self.draw_text("LEFT: " + question_data["left"], 50, self.screen_height // 2)
        self.draw_text("RIGHT: " + question_data["right"], 50, self.screen_height // 2 + 50)

    def main(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.direction = 1
                        self.answered = True
                    if event.key == pygame.K_RIGHT:
                        self.direction = 2
                        self.answered = True
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.direction = 0

            if self.game_completed:
                self.screen.fill(self.white)
                self.draw_text("Congratulations! You won!", 100, self.screen_height // 2)
                pygame.display.flip()
                continue

            if not self.paused:
                # Move the trolley
                self.trolley_y += self.trolley_speed

            # Check if it's time to show a question (at the divergence point)
            if self.trolley_y > self.screen_height // 2 and not self.show_question and not self.at_divergence:
                self.show_question = True
                self.paused = True
                self.at_divergence = True

            # Handle answering the question
            if self.show_question and self.answered:
                correct = self.questions[self.current_question]["correct"]
                chosen_track = self.left_track if self.direction == 1 else self.right_track
                if (correct == "left" and self.direction == 1) or (correct == "right" and self.direction == 2):
                    self.trolley_x = chosen_track
                    self.paused = False
                    self.show_question = False
                    self.answered = False
                    self.correct_answers += 1
                    self.incorrect = False
                    self.current_question += 1
                else:
                    self.trolley_x = chosen_track
                    self.paused = False
                    self.show_question = False
                    self.answered = False
                    self.incorrect = True

            if not self.show_question and not self.paused:
                # Check if the trolley reached the bottom
                if self.trolley_y >= self.screen_height - 25:
                    self.trolley_y = 50  # Reset trolley position for next question
                    self.trolley_x = self.middle_track
                    self.at_divergence = False
                    if self.incorrect:
                        self.draw_text("CRASH! Game Over.", 200, 300)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        running = False
                    else:
                        if self.current_question >= len(self.questions):
                            if self.correct_answers == 3:
                                self.game_completed = True
                            else:
                                self.draw_text("CRASH! Game Over.", 200, 300)
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                running = False

            # Fill the screen with white
            self.screen.fill(self.white)

            # Draw tracks
            pygame.draw.line(self.screen, self.black, (self.middle_track, 0), (self.middle_track, self.screen_height // 2), 5)
            pygame.draw.line(self.screen, self.black, (self.left_track, self.screen_height // 2), (self.left_track, self.screen_height), 5)
            pygame.draw.line(self.screen, self.black, (self.right_track, self.screen_height // 2), (self.right_track, self.screen_height), 5)

            # Draw trolley
            self.draw_trolley(self.trolley_x, self.trolley_y)

            # Draw question if needed
            if self.show_question:
                self.draw_question(self.questions[self.current_question])

            # Draw instructions
            if not self.show_question and not self.paused:
                self.draw_text("Press LEFT or RIGHT to choose track", 100, 10)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            pygame.time.Clock().tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Mercury()
    game.main()
