import pygame
import math
import random
import time
from pygame import mixer


class Sun:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        self.background = pygame.image.load('background.png')
        pygame.display.set_caption("Level Sun")
        icon = pygame.image.load('ufo.png')
        pygame.display.set_icon(icon)

        # Background Sound
        mixer.music.load('background.wav')
        mixer.music.play(-1)

        # Player
        self.playerImg = pygame.image.load('user.png')
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
            self.enemyImg.append(pygame.image.load('alien.png'))
            self.enemyX.append(600)
            self.enemyY.append(75)
            self.enemyX_change.append(2)
            self.enemyY_change.append(40)

        # Laser
        self.laserImg = pygame.image.load('bullet.png')
        self.laserX = 0
        self.laserY = 640
        self.laserX_change = 0
        self.laserY_change = 5
        self.laser_state = "ready"

        # Enemy Bullet
        self.enemy_bullet_img = pygame.image.load('bullet.png')
        self.enemy_bullets = []
        self.bulletY_change = 5

        # Health
        self.hp_value = 100
        self.hp_self = 3

        # Fonts
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.over_font = pygame.font.Font('freesansbold.ttf', 128)

        self.textX = 10
        self.textY = 10

        self.last_fired_time = time.time()
        self.fire_interval = random.uniform(1, 3)

        # Pause menu variables
        self.paused = False
        self.menu_font = pygame.font.Font('freesansbold.ttf', 36)
        self.menu_text_color = (255, 255, 255)
        self.menu_background_color = (0, 0, 0, 180)  # Translucent black
        self.menu_options = ["Resume (ESC)", "Restart (R)", "Quit (Q)"]
        self.menu_option_positions = [(500, 300), (500, 370), (500, 440)]
        self.selected_option = 0

    def show_hp(self, x, y):
        hp = self.font.render("HP: " + str(self.hp_value), True, (255, 255, 255))
        self.screen.blit(hp, (x, y))

    def game_over_text(self):
        over_text = self.over_font.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(over_text, (350, 200))

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
        # Draw translucent background
        overlay = pygame.Surface((1200, 800), pygame.SRCALPHA)
        overlay.fill(self.menu_background_color)
        self.screen.blit(overlay, (0, 0))

        # Draw menu options
        for idx, option in enumerate(self.menu_options):
            text_surface = self.menu_font.render(option, True, self.menu_text_color)
            self.screen.blit(text_surface, self.menu_option_positions[idx])

            # Highlight selected option
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
            elif self.selected_option == 2:  # Quit
                pygame.quit()
                quit()

    def main(self):
        running = True
        game_over = False

        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background, (0, 0))

            if not game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = not self.paused

                        if not self.paused:
                            if event.key == pygame.K_LEFT:
                                self.playerX_change = -3.5
                            if event.key == pygame.K_RIGHT:
                                self.playerX_change = 3.5
                            if event.key == pygame.K_SPACE:
                                if self.laser_state == "ready":
                                    bullet_sound = mixer.Sound('laser.wav')
                                    bullet_sound.play()
                                    self.laserX = self.playerX
                                    self.fire_laser(self.laserX, self.laserY)

                        if event.key == pygame.K_r:
                            if self.paused:
                                self.__init__()  # Restart the game

                        if event.key == pygame.K_q:
                            if self.paused:
                                pygame.quit()  # Quit the game

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            self.playerX_change = 0

                if not self.paused:
                    self.playerX += self.playerX_change
                    if self.playerX <= 0:
                        self.playerX = 0
                    elif self.playerX >= 1136:
                        self.playerX = 1136

                    for i in range(self.number_of_enemy):
                        self.enemyX[i] += self.enemyX_change[i]
                        if self.enemyX[i] <= 0:
                            self.enemyX_change[i] = 1
                        elif self.enemyX[i] >= 1136:
                            self.enemyX_change[i] = -1

                        current_time = time.time()
                        if current_time - self.last_fired_time >= self.fire_interval:
                            self.fire_enemy_bullet(self.enemyX[i], self.enemyY[i])
                            self.last_fired_time = current_time
                            self.fire_interval = random.uniform(1, 3)

                        collision = self.isCollision(self.enemyX[i], self.enemyY[i], self.laserX, self.laserY)
                        if collision:
                            explosion_sound = mixer.Sound('explosion.wav')
                            explosion_sound.play()
                            self.laserY = 640
                            self.laser_state = "ready"
                            self.hp_value -= 10

                            if self.hp_value == 0:
                                self.enemyY[i] = 2000
                                game_over = True

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
                            explosion_sound = mixer.Sound('explosion.wav')
                            explosion_sound.play()
                            self.enemy_bullets.remove(bullet)
                            self.hp_self -= 1
                            if self.hp_self == 0:
                                game_over = True

                        if bullet[1] >= 800:
                            self.enemy_bullets.remove(bullet)

                    self.player(self.playerX, self.playerY)
                    self.show_hp(self.textX, self.textY)
                else:
                    self.draw_pause_menu()
                    self.handle_pause_input()

            else:
                self.game_over_text()

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Sun()
    game.main()
