import pygame
import math
import random
import time
from pygame import mixer
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

    def set_text(self, text):
        self.text = text
        self.rendered_text = []
        self.text_content = []
        wrapped_text = textwrap.wrap(text, width=self.rect.width // 10)
        for line in wrapped_text:
            self.rendered_text.append(self.font.render(line, True, (255, 255, 255)))
            self.text_content.append(line)
        self.reveal_index = 0

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


class Sun:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1200, 750))

        self.background = pygame.image.load('src/sun.jpg')

        pygame.display.set_caption("Level Sun")
        icon = pygame.image.load('src/ufo.png')
        pygame.display.set_icon(icon)

        # Background Sound
        mixer.music.load('src/background.wav')
        mixer.music.play(-1)

        # Player
        self.playerImg = pygame.image.load('src/user.png')
        self.playerX = 600
        self.playerY = 640
        self.playerX_change = 0

        # Enemy
        self.enemyImg = []
        self.enemyX = []
        self.enemyY = []
        self.enemyX_change = []
        self.enemyY_change = []
        self.number_of_enemy = 1

        for i in range(self.number_of_enemy):
            original_enemy_img = pygame.image.load('src/alien.png')
            scaled_enemy_img = pygame.transform.scale(original_enemy_img, (original_enemy_img.get_width() * 1, original_enemy_img.get_height() * 1))
            self.enemyImg.append(scaled_enemy_img)
            self.enemyX.append(600)
            self.enemyY.append(75)
            self.enemyX_change.append(1)  # Slower enemy movement
            self.enemyY_change.append(20)

        # Laser
        self.laserImg = pygame.image.load('src/bullet.png')
        self.laserX = 0
        self.laserY = 640
        self.laserX_change = 0
        self.laserY_change = 2.5  # Slower laser movement
        self.laser_state = "ready"

        # Enemy Bullet
        self.enemy_bullet_img = pygame.image.load('src/bullet.png')
        self.enemy_bullets = []
        self.bulletY_change = 2.5  # Slower enemy bullet movement

        # Health
        self.hp_value = 100
        self.hp_self = 3

        # Fonts
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.over_font = pygame.font.Font('freesansbold.ttf', 96)  # Smaller font for "Congratulations"
        self.menu_font = pygame.font.Font('freesansbold.ttf', 36)

        self.textX = 10
        self.textY = 10

        self.last_fired_time = time.time()
        self.fire_interval = random.uniform(1, 3)

        # Pause menu variables
        self.paused = False
        self.menu_text_color = (255, 255, 255)
        self.menu_background_color = (0, 0, 0, 180)  # Translucent black
        self.menu_options = ["Resume (ESC)", "Restart (R)", "Quit (Q)"]
        self.menu_option_positions = [(500, 300), (500, 370), (500, 440)]
        self.selected_option = 0

        # Text box and game state
        self.text_box = TextBox(50, 600, 1100, 150)
        self.game_state = "intro"
        self.intro_text = "John! It's the alien boss! Shoot lasers to defeat him. Beware of his lasers too!"
        self.victory_text = "Yeah! We did it!! The alien boss is defeated! Now let's activate the shield machine."
        self.defeat_text = "He's too strong..."

    def show_hp(self, x, y):
        hp = self.font.render("HP: " + str(self.hp_value), True, (255, 255, 255))
        self.screen.blit(hp, (x, y))

    def player(self, x, y):
        self.screen.blit(self.playerImg, (x, y))

    def enemy(self, x, y, i):
        self.screen.blit(self.enemyImg[i], (x, y))

    def fire_laser(self, x, y):
        self.laser_state = "fire"
        self.screen.blit(self.laserImg, (x + 16, y + 10))

    def fire_enemy_bullet(self, x, y):
        self.enemy_bullets.append([x, y])

    def isCollision(self, enemyX, enemyY, laserX, laserY):
        distance = math.sqrt(math.pow(enemyX - laserX, 2) + math.pow(enemyY - laserY, 2))
        return distance < 27

    def isCollision2(self, playerX, playerY, bulletX, bulletY):
        distance = math.sqrt(math.pow(playerX - bulletX, 2) + math.pow(playerY - bulletY, 2))
        return distance < 27

    def draw_pause_menu(self):
        overlay = pygame.Surface((1200, 800), pygame.SRCALPHA)
        overlay.fill(self.menu_background_color)
        self.screen.blit(overlay, (0, 0))

        for idx, option in enumerate(self.menu_options):
            text_surface = self.menu_font.render(option, True, self.menu_text_color)
            self.screen.blit(text_surface, self.menu_option_positions[idx])

            if idx == self.selected_option:
                pygame.draw.rect(self.screen, (255, 255, 255), (*self.menu_option_positions[idx], text_surface.get_width(), text_surface.get_height()), 3)

    def handle_pause_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif keys[pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif keys[pygame.K_RETURN]:
            if self.selected_option == 0:  # Resume
                self.paused = False
            elif self.selected_option == 1:  # Restart
                self.__init__()  # Restart the game
                self.text_box.set_text(self.intro_text)  # Set the intro text when restarting
            elif self.selected_option == 2:  # Quit
                pygame.mixer.music.stop()
                return "main_menu"

    def main(self):
        running = True

        self.text_box.set_text(self.intro_text)

        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused

                    if self.game_state == "intro" and event.key == pygame.K_SPACE:
                        if self.text_box.is_finished():
                            self.game_state = "playing"
                        else:
                            self.text_box.reveal_index = sum(len(line) for line in self.text_box.text_content)

                    if not self.paused and self.game_state == "playing":
                        if event.key == pygame.K_LEFT:
                            self.playerX_change = -1.5  # Slower player movement
                        if event.key == pygame.K_RIGHT:
                            self.playerX_change = 1.5  # Slower player movement
                        if event.key == pygame.K_SPACE:
                            if self.laser_state == "ready":
                                bullet_sound = mixer.Sound('src/laser.wav')
                                bullet_sound.play()
                                self.laserX = self.playerX
                                self.fire_laser(self.laserX, self.laserY)

                    if self.game_state in ["victory", "defeat"]:
                        if event.key == pygame.K_r:
                            self.__init__()
                            self.text_box.set_text(self.intro_text)  # Set the intro text when restarting
                        elif event.key == pygame.K_q:
                            pygame.mixer.music.stop()
                            return "main_menu"

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.playerX_change = 0

            if self.paused:
                self.draw_pause_menu()
                result = self.handle_pause_input()
                if result == "main_menu":
                    running = False
                    return "main_menu"

            if self.game_state == "intro":
                self.text_box.update()
                self.text_box.draw(self.screen)

            elif self.game_state == "playing":
                self.playerX += self.playerX_change
                if self.playerX <= 0:
                    self.playerX = 0
                elif self.playerX >= 1136:
                    self.playerX = 1136

                for i in range(self.number_of_enemy):
                    self.enemyX[i] += self.enemyX_change[i]
                    if self.enemyX[i] <= 0:
                        self.enemyX_change[i] = 0.5  # Slower enemy direction change
                    elif self.enemyX[i] >= 1136:
                        self.enemyX_change[i] = -0.5  # Slower enemy direction change

                    current_time = time.time()
                    if current_time - self.last_fired_time >= self.fire_interval:
                        self.fire_enemy_bullet(self.enemyX[i], self.enemyY[i])
                        self.last_fired_time = current_time
                        self.fire_interval = random.uniform(1, 3)

                    collision = self.isCollision(self.enemyX[i], self.enemyY[i], self.laserX, self.laserY)
                    if collision:
                        explosion_sound = mixer.Sound('src/explosion.wav')
                        explosion_sound.play()
                        self.laserY = 640
                        self.laser_state = "ready"
                        self.hp_value -= 10

                        if self.hp_value == 0:
                            self.enemyY[i] = 2000
                            self.game_state = "victory"
                            self.text_box.set_text(self.victory_text)

                    self.enemy(self.enemyX[i], self.enemyY[i], i)

                if self.laserY <= 0:
                    self.laserY = 640
                    self.laser_state = "ready"

                if self.laser_state == "fire":
                    self.fire_laser(self.laserX, self.laserY)
                    self.laserY -= self.laserY_change

                for bullet in self.enemy_bullets:
                    bullet[1] += self.bulletY_change
                    self.screen.blit(self.enemy_bullet_img, (bullet[0], bullet[1]))
                    collision2 = self.isCollision2(self.playerX, self.playerY, bullet[0], bullet[1])
                    if collision2:
                        explosion_sound = mixer.Sound('src/explosion.wav')
                        explosion_sound.play()
                        self.enemy_bullets.remove(bullet)
                        self.hp_self -= 1
                        if self.hp_self == 0:
                            self.game_state = "defeat"
                            self.text_box.set_text(self.defeat_text)

                    if bullet[1] >= 800:
                        self.enemy_bullets.remove(bullet)

                self.player(self.playerX, self.playerY)
                self.show_hp(self.textX, self.textY)

            elif self.game_state == "victory":
                congrats_text = self.font.render("CONGRATULATIONS", True, (255, 255, 255))
                congrats_rect = congrats_text.get_rect(center=(600, 300))
                self.screen.blit(congrats_text, congrats_rect)

                retry_text = self.font.render("Press R to Retry", True, (255, 255, 255))
                quit_text = self.font.render("Press Q to Quit", True, (255, 255, 255))
                retry_rect = retry_text.get_rect(center=(600, 400))
                quit_rect = quit_text.get_rect(center=(600, 450))
                self.screen.blit(retry_text, retry_rect)
                self.screen.blit(quit_text, quit_rect)

                self.text_box.update()
                self.text_box.draw(self.screen)

            elif self.game_state == "defeat":
                game_over_text = self.over_font.render("GAME OVER", True, (255, 255, 255))
                game_over_rect = game_over_text.get_rect(center=(600, 300))
                self.screen.blit(game_over_text, game_over_rect)

                retry_text = self.font.render("Press R to Retry", True, (255, 255, 255))
                quit_text = self.font.render("Press Q to Quit", True, (255, 255, 255))
                retry_rect = retry_text.get_rect(center=(600, 400))
                quit_rect = quit_text.get_rect(center=(600, 450))
                self.screen.blit(retry_text, retry_rect)
                self.screen.blit(quit_text, quit_rect)

                self.text_box.update()
                self.text_box.draw(self.screen)

            if self.paused:
                self.draw_pause_menu()
                self.handle_pause_input()

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Sun()
    game.main()
