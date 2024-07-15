import pygame
import math
import sys
import os
import random
from pygame import mixer
from mainscreen import main_screen
import ctypes


def load_image(name):
    return pygame.image.load(os.path.join('planets', f"{name}.png"))


class SolarSystem:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Get the screen size
        user32 = ctypes.windll.user32
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)

        # Adjust minimap size based on screen dimensions
        self.MINIMAP_WIDTH = int(self.WIDTH * 0.15)
        self.MINIMAP_HEIGHT = int(self.HEIGHT * 0.15)

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREY = (169, 169, 169)
        self.FPS = 60

        # Load images
        self.images = {
            'sun': load_image('sun'),
            'mercury': load_image('mercury'),
            'venus': load_image('venus'),
            'earth': load_image('earth'),
            'mars': load_image('mars'),
            'jupiter': load_image('jupiter'),
            'saturn': load_image('saturn'),
            'uranus': load_image('uranus'),
            'neptune': load_image('neptune'),
            'spaceship': load_image('spaceship'),
        }

        # Rotate spaceship image 45 degrees clockwise
        self.images['spaceship'] = pygame.transform.rotate(self.images['spaceship'], -45)

        # Adjust orbital details based on screen size
        scale_factor = min(self.WIDTH, self.HEIGHT) / 800
        self.PLANETS = {
            'mercury': (1500 * scale_factor, 20 * scale_factor, 0.0005),
            'venus': (3000 * scale_factor, 35 * scale_factor, 0.0004),
            'earth': (4500 * scale_factor, 40 * scale_factor, 0.0003),
            'mars': (6000 * scale_factor, 30 * scale_factor, 0.00025),
            'jupiter': (9000 * scale_factor, 70 * scale_factor, 0.0002),
            'saturn': (12000 * scale_factor, 60 * scale_factor, 0.00015),
            'uranus': (15000 * scale_factor, 50 * scale_factor, 0.0001),
            'neptune': (18000 * scale_factor, 50 * scale_factor, 0.00008),
        }

        # Setup display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("2D Solar System")
        pygame.mixer.music.stop()

        # Sun's details
        self.sun_pos = (0, 0)
        self.sun_radius = 100 * scale_factor

        # Spaceship details
        self.spaceship_pos = [4500 * scale_factor, 0]  # Start near Earth
        self.spaceship_speed = 7 * scale_factor
        self.spaceship_radius = 25 * scale_factor
        self.spaceship_angle = 0  # Angle in radians, 0 is now pointing right
        self.rotation_speed = 0.1  # Radians per frame

        # Zoom level and scaling factor
        self.zoom_level = 1.0
        self.max_zoom_in = 0.1
        self.max_zoom_out = 2.0

        # Create starry background
        self.starry_background = self.create_starry_background()

        self.font = pygame.font.Font(None, int(74 * scale_factor))
        self.small_font = pygame.font.Font(None, int(36 * scale_factor))

        # Pause state
        self.paused = False

    def create_starry_background(self):
        background = pygame.Surface((self.WIDTH, self.HEIGHT))
        background.fill(self.BLACK)
        for _ in range(300):  # Increased number of stars
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            brightness = random.randint(100, 255)  # Increased minimum brightness
            star_size = random.choice([1, 1, 1, 2])  # Most stars are 1 pixel, some are 2
            if star_size == 1:
                background.set_at((x, y), (brightness, brightness, brightness))
            else:
                pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), star_size)
        return background

    def draw_orbits(self, offset_x, offset_y):
        for planet, (distance, radius, speed) in self.PLANETS.items():
            orbit_radius = distance * self.zoom_level
            orbit_pos = (
                int(self.sun_pos[0] * self.zoom_level + offset_x),
                int(self.sun_pos[1] * self.zoom_level + offset_y)
            )
            pygame.draw.circle(self.screen, self.WHITE, orbit_pos, int(orbit_radius), 1)

    def draw_solar_system(self, angles):
        # Draw starry background
        self.screen.blit(self.starry_background, (0, 0))

        offset_x = self.WIDTH // 2 - self.spaceship_pos[0] * self.zoom_level
        offset_y = self.HEIGHT // 2 - self.spaceship_pos[1] * self.zoom_level

        self.draw_orbits(offset_x, offset_y)

        # Draw Sun
        sun_screen_pos = (self.sun_pos[0] * self.zoom_level + offset_x, self.sun_pos[1] * self.zoom_level + offset_y)
        sun_image = pygame.transform.scale(self.images['sun'], (
            int(self.sun_radius * 2 * self.zoom_level), int(self.sun_radius * 2 * self.zoom_level)))
        self.screen.blit(sun_image, (int(sun_screen_pos[0] - self.sun_radius * self.zoom_level),
                                     int(sun_screen_pos[1] - self.sun_radius * self.zoom_level)))

        # Draw Planets
        for planet, (distance, radius, speed) in self.PLANETS.items():
            angle = angles[planet]
            x = self.sun_pos[0] + distance * math.cos(angle)
            y = self.sun_pos[1] + distance * math.sin(angle)
            planet_screen_pos = (x * self.zoom_level + offset_x, y * self.zoom_level + offset_y)
            planet_image = pygame.transform.scale(self.images[planet], (
                int(radius * 2 * self.zoom_level), int(radius * 2 * self.zoom_level)))
            self.screen.blit(planet_image, (
                int(planet_screen_pos[0] - radius * self.zoom_level),
                int(planet_screen_pos[1] - radius * self.zoom_level)))
            angles[planet] += speed

        # Draw Spaceship in the center of the screen
        spaceship_image = pygame.transform.scale(self.images['spaceship'], (
            int(self.spaceship_radius * 2 * self.zoom_level), int(self.spaceship_radius * 2 * self.zoom_level)))
        rotated_spaceship = pygame.transform.rotate(spaceship_image, -math.degrees(self.spaceship_angle))
        spaceship_rect = rotated_spaceship.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(rotated_spaceship, spaceship_rect)

        # Draw Minimap
        self.draw_minimap(angles, offset_x, offset_y)

        pygame.display.update()

    def draw_minimap(self, angles, offset_x, offset_y):
        minimap = pygame.Surface((self.MINIMAP_WIDTH, self.MINIMAP_HEIGHT))
        minimap.fill((100, 120, 140))  # Bluish grey background color

        # Draw Sun on minimap
        sun_minimap_pos = (self.MINIMAP_WIDTH // 2, self.MINIMAP_HEIGHT // 2)
        sun_minimap_image = pygame.transform.scale(self.images['sun'], (10, 10))
        minimap.blit(sun_minimap_image, (sun_minimap_pos[0] - 5, sun_minimap_pos[1] - 5))

        # Calculate maximum distance from sun
        max_distance = max(self.PLANETS.values(), key=lambda x: x[0])[0]

        # Scale factors
        scale_x = self.MINIMAP_WIDTH / (2 * max_distance)
        scale_y = self.MINIMAP_HEIGHT / (2 * max_distance)

        # Draw Planets on minimap
        for planet, (distance, radius, speed) in self.PLANETS.items():
            angle = angles[planet]
            x = sun_minimap_pos[0] + distance * scale_x * math.cos(angle)
            y = sun_minimap_pos[1] + distance * scale_y * math.sin(angle)
            planet_minimap_image = pygame.transform.scale(self.images[planet],
                                                          (max(2, int(radius / 5)), max(2, int(radius / 5))))
            minimap.blit(planet_minimap_image, (
                int(x - planet_minimap_image.get_width() / 2), int(y - planet_minimap_image.get_height() / 2)))

        # Draw Spaceship on minimap
        spaceship_minimap_pos = (sun_minimap_pos[0] + self.spaceship_pos[0] * scale_x,
                                 sun_minimap_pos[1] + self.spaceship_pos[1] * scale_y)
        spaceship_minimap_image = pygame.transform.scale(self.images['spaceship'], (6, 6))
        rotated_minimap_spaceship = pygame.transform.rotate(spaceship_minimap_image,
                                                            -math.degrees(self.spaceship_angle))
        minimap.blit(rotated_minimap_spaceship, (int(spaceship_minimap_pos[0] - 3), int(spaceship_minimap_pos[1] - 3)))

        self.screen.blit(minimap, (self.WIDTH - self.MINIMAP_WIDTH - 10, 10))

    def update_spaceship(self):
        keys = pygame.key.get_pressed()
        moved = False

        target_angle = None
        if keys[pygame.K_LEFT]:
            target_angle = math.pi
        elif keys[pygame.K_RIGHT]:
            target_angle = 0
        elif keys[pygame.K_UP]:
            target_angle = 3 * math.pi / 2
        elif keys[pygame.K_DOWN]:
            target_angle = math.pi / 2

        if target_angle is not None:
            angle_diff = (target_angle - self.spaceship_angle + math.pi) % (2 * math.pi) - math.pi

            if abs(angle_diff) < self.rotation_speed:
                self.spaceship_angle = target_angle
                # Move in the direction we're facing
                self.spaceship_pos[0] += self.spaceship_speed * math.cos(self.spaceship_angle)
                self.spaceship_pos[1] += self.spaceship_speed * math.sin(self.spaceship_angle)
                moved = True
            else:
                # Rotate towards the target angle
                self.spaceship_angle += math.copysign(self.rotation_speed, angle_diff)
                self.spaceship_angle %= 2 * math.pi

        return moved

    def pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("Paused", True, self.WHITE)
        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - 150))

        resume_text = self.small_font.render("Press 'R' to Resume", True, self.WHITE)
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, self.HEIGHT // 2 - 50))

        restart_text = self.small_font.render("Press 'N' to Restart", True, self.WHITE)
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2))

        quit_text = self.small_font.render("Press 'Q' to Quit", True, self.WHITE)
        self.screen.blit(quit_text, (self.WIDTH // 2 - quit_text.get_width() // 2, self.HEIGHT // 2 + 50))

        pygame.display.update()

    def main(self):
        clock = pygame.time.Clock()
        angles = {planet: 0 for planet in self.PLANETS}  # Initial angles for planets

        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.paused:
                        self.paused = False
                    elif event.key == pygame.K_n and self.paused:
                        self.__init__()
                    elif event.key == pygame.K_q and self.paused:
                        return # main_screen()
                        # running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                    if event.button == 4:  # Scroll up
                        self.zoom_level = min(self.zoom_level + 0.1, self.max_zoom_out)
                    elif event.button == 5:  # Scroll down
                        self.zoom_level = max(self.zoom_level - 0.1, self.max_zoom_in)

            if not self.paused:
                self.update_spaceship()
                self.draw_solar_system(angles)
            else:
                self.pause_menu()

            clock.tick(self.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SolarSystem()
    game.main()
