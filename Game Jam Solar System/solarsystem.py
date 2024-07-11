import pygame
import math
import sys

class SolarSystem:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Constants
        self.WIDTH, self.HEIGHT = 1200, 800
        self.MINIMAP_WIDTH, self.MINIMAP_HEIGHT = 200, 200
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREY = (169, 169, 169)
        self.FPS = 60

        # Colors for the planets
        self.COLORS = {
            'sun': (255, 255, 0),
            'mercury': (169, 169, 169),
            'venus': (255, 140, 0),
            'earth': (0, 0, 255),
            'mars': (255, 0, 0),
            'jupiter': (255, 165, 0),
            'saturn': (210, 180, 140),
            'uranus': (0, 255, 255),
            'neptune': (0, 0, 128),
        }

        # Orbital details: (distance from sun, radius, speed)
        self.PLANETS = {
            'mercury': (1500, 20, 0.0005),
            'venus': (3000, 35, 0.0004),
            'earth': (4500, 40, 0.0003),
            'mars': (6000, 30, 0.00025),
            'jupiter': (9000, 70, 0.0002),
            'saturn': (12000, 60, 0.00015),
            'uranus': (15000, 50, 0.0001),
            'neptune': (18000, 50, 0.00008),
        }

        # Setup display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("2D Solar System")

        # Sun's details
        self.sun_pos = (0, 0)
        self.sun_radius = 100

        # Spaceship details
        self.spaceship_pos = [4500, 0]  # Start near Earth
        self.spaceship_speed = 2
        self.spaceship_color = self.WHITE
        self.spaceship_radius = 25

        # Zoom level and scaling factor
        self.zoom_level = 1.0
        self.max_zoom_in = 0.1
        self.max_zoom_out = 2.0

    # Function to draw the solar system
    def draw_solar_system(self, angles):
        self.screen.fill(self.BLACK)

        # Calculate offset based on spaceship position and zoom level
        offset_x = self.WIDTH // 2 - self.spaceship_pos[0] * self.zoom_level
        offset_y = self.HEIGHT // 2 - self.spaceship_pos[1] * self.zoom_level

        # Draw Sun
        sun_screen_pos = (self.sun_pos[0] * self.zoom_level + offset_x, self.sun_pos[1] * self.zoom_level + offset_y)
        pygame.draw.circle(self.screen, self.COLORS['sun'], (int(sun_screen_pos[0]), int(sun_screen_pos[1])), int(self.sun_radius * self.zoom_level))

        # Draw Planets
        for planet, (distance, radius, speed) in self.PLANETS.items():
            angle = angles[planet]
            x = self.sun_pos[0] + distance * math.cos(angle)
            y = self.sun_pos[1] + distance * math.sin(angle)
            planet_screen_pos = (x * self.zoom_level + offset_x, y * self.zoom_level + offset_y)
            pygame.draw.circle(self.screen, self.COLORS[planet], (int(planet_screen_pos[0]), int(planet_screen_pos[1])), int(radius * self.zoom_level))
            angles[planet] += speed

        # Draw Spaceship in the center of the screen
        pygame.draw.circle(self.screen, self.spaceship_color, (int(self.WIDTH // 2), int(self.HEIGHT // 2)), int(self.spaceship_radius * self.zoom_level))

        # Draw Minimap
        self.draw_minimap(angles, offset_x, offset_y)

        pygame.display.update()

    # Function to draw the minimap
    def draw_minimap(self, angles, offset_x, offset_y):
        minimap = pygame.Surface((self.MINIMAP_WIDTH, self.MINIMAP_HEIGHT))
        minimap.fill((100, 120, 140))  # Bluish grey background color

        # Draw Sun on minimap
        sun_minimap_pos = (self.MINIMAP_WIDTH // 2, self.MINIMAP_HEIGHT // 2)
        pygame.draw.circle(minimap, self.COLORS['sun'], sun_minimap_pos, 5)

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
            pygame.draw.circle(minimap, self.COLORS[planet], (int(x), int(y)), max(1, int(radius / 10)))

        # Draw Spaceship on minimap
        spaceship_minimap_pos = (sun_minimap_pos[0] + self.spaceship_pos[0] * scale_x,
                                 sun_minimap_pos[1] + self.spaceship_pos[1] * scale_y)
        pygame.draw.circle(minimap, self.spaceship_color, (int(spaceship_minimap_pos[0]), int(spaceship_minimap_pos[1])), 3)

        self.screen.blit(minimap, (self.WIDTH - self.MINIMAP_WIDTH - 10, 10))

    # Main game loop
    def main(self):
        clock = pygame.time.Clock()
        angles = {planet: 0 for planet in self.PLANETS}  # Initial angles for planets

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        self.zoom_level = min(self.zoom_level + 0.1, self.max_zoom_out)
                    elif event.button == 5:  # Scroll down
                        self.zoom_level = max(self.zoom_level - 0.1, self.max_zoom_in)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.spaceship_pos[0] -= self.spaceship_speed
            if keys[pygame.K_RIGHT]:
                self.spaceship_pos[0] += self.spaceship_speed
            if keys[pygame.K_UP]:
                self.spaceship_pos[1] -= self.spaceship_speed
            if keys[pygame.K_DOWN]:
                self.spaceship_pos[1] += self.spaceship_speed

            self.draw_solar_system(angles)
            clock.tick(self.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SolarSystem()
    game.main()
