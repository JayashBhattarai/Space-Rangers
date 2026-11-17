from asteroid_belt import AsteroidBelt
from campaign import campaign, STORY_ORDER
from display_settings import game_size
import pygame
import math
import sys
import os
import random
from pygame import mixer
from importlib import import_module
from pathlib import Path
import ctypes


def load_image(name):
    return pygame.image.load(str(Path(__file__).parent / 'planets' / f'{name}.png'))


class SolarSystem:
    def __init__(self, progress=None):
        self.progress = progress if progress is not None else campaign
        # Initialize Pygame
        pygame.init()

        # Get the screen size
        self.WIDTH, self.HEIGHT = game_size()

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
        # Circular approximation of Kepler's third law: period scales as AU ** 1.5.
        # One Earth year takes six minutes of active flight. Phases are illustrative.
        self.earth_year_seconds = 360.0
        orbital_data = {
            'mercury': (0.387, 20, 0.6), 'venus': (0.723, 35, 2.4),
            'earth': (1.0, 40, 0.0), 'mars': (1.524, 30, 1.2),
            'jupiter': (5.203, 70, 3.3), 'saturn': (9.537, 60, 4.4),
            'uranus': (19.191, 50, 5.2), 'neptune': (30.069, 50, 2.1),
        }
        self.PLANETS = {
            name: (au * 4500 * scale_factor, radius * scale_factor,
                   math.tau / (self.earth_year_seconds * au ** 1.5))
            for name, (au, radius, _) in orbital_data.items()
        }
        self.angles = {name: phase for name, (_, _, phase) in orbital_data.items()}
        self.destination = self.recommended_destination()
        self.radar_remaining = 0.0
        self.radar_cooldown = 0.0
        self.radar_duration = 5.0
        self.radar_recharge = 20.0
        self.boost_multiplier = 6.0  # 75% of the previous 8x cruise speed.
        self.escape_held = False
        self.belt = AsteroidBelt(self.PLANETS['earth'][0], scale_factor)
        self.beam_range = 2500 * scale_factor
        self.beam_width = 110 * scale_factor
        self.beam_remaining = 0.0
        self.beam_cooldown = 0.0
        self.beam_start = pygame.Vector2()
        self.beam_end = pygame.Vector2()
        self.belt_hit_cooldown = 0.0
        self.debris = []
        self.enemy_lasers = []
        self.warning = ""
        self.warning_time = 0.0
        self.enemies = []
        self.lasers = []
        self.health = 100
        self.shield_remaining = 0.0
        self.shield_charges = 0
        self.shield_cooldown = 0.0
        self.score = 0
        self.spawn_timer = 3.0
        self.fire_timer = 0.0
        self.landing_lock = None

        # Setup display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Space Rangers - Alien Invasion")
        pygame.mixer.music.stop()

        # Sun's details
        self.sun_pos = (0, 0)
        self.sun_radius = 100 * scale_factor

        # Spaceship details
        self.spaceship_pos = [4500 * scale_factor + 160, 0]  # Start near Earth
        self.spaceship_speed = 18 * scale_factor
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
        self.mouse_shot = None
        self.block_mouse_fire = True
        self.pause_button = pygame.Rect(15, self.HEIGHT - 45, 110, 32)
        self.radar_button = pygame.Rect(135, self.HEIGHT - 45, 170, 32)
        self.beam_button = pygame.Rect(315, self.HEIGHT - 45, 190, 32)
        self.shield_button = pygame.Rect(515, self.HEIGHT - 45, 240, 32)
        hud_scale = min(1, self.WIDTH / 780)
        self.hud_font = pygame.font.Font(None, max(14, int(24 * hud_scale)))
        for button in (self.pause_button, self.radar_button, self.beam_button, self.shield_button):
            button.x = int(button.x * hud_scale)
            button.width = int(button.width * hud_scale)

    def create_starry_background(self):
        background = pygame.Surface((self.WIDTH, self.HEIGHT))
        background.fill(self.BLACK)
        for _ in range(300):  # Increased number of stars
            x = random.randrange(self.WIDTH)
            y = random.randrange(self.HEIGHT)
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

    def draw_solar_system(self, angles, present=True):
        # Draw starry background
        self.screen.blit(self.starry_background, (0, 0))

        offset_x = self.WIDTH // 2 - self.spaceship_pos[0] * self.zoom_level
        offset_y = self.HEIGHT // 2 - self.spaceship_pos[1] * self.zoom_level

        self.draw_orbits(offset_x, offset_y)
        self.belt.draw(self.screen, self.zoom_level, pygame.Vector2(offset_x, offset_y))

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
            label = self.small_font.render(planet.title(), True, self.WHITE)
            self.screen.blit(label, (int(planet_screen_pos[0]), int(planet_screen_pos[1] + radius * self.zoom_level)))
            planet_image = pygame.transform.scale(self.images[planet], (
                int(radius * 2 * self.zoom_level), int(radius * 2 * self.zoom_level)))
            self.screen.blit(planet_image, (
                int(planet_screen_pos[0] - radius * self.zoom_level),
                int(planet_screen_pos[1] - radius * self.zoom_level)))


        self.draw_beam(pygame.Vector2(offset_x, offset_y))

        # Draw Spaceship in the center of the screen
        spaceship_image = pygame.transform.scale(self.images['spaceship'], (
            int(self.spaceship_radius * 2 * self.zoom_level), int(self.spaceship_radius * 2 * self.zoom_level)))
        rotated_spaceship = pygame.transform.rotate(spaceship_image, -math.degrees(self.spaceship_angle))
        spaceship_rect = rotated_spaceship.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(rotated_spaceship, spaceship_rect)

        # Exact target locations are exposed during a radar scan.
        if self.radar_remaining > 0:
            self.draw_minimap(angles, offset_x, offset_y)
        if self.radar_remaining > 0 or self.training_beacon:
            self.draw_target_beacon(offset_x, offset_y)

        self.draw_combat(offset_x, offset_y)
        if present:
            pygame.display.update()

    def draw_minimap(self, angles, offset_x, offset_y):
        minimap = pygame.Surface((self.MINIMAP_WIDTH, self.MINIMAP_HEIGHT))
        minimap.fill((8, 25, 35))

        # Draw Sun on minimap
        sun_minimap_pos = (self.MINIMAP_WIDTH // 2, self.MINIMAP_HEIGHT // 2)
        sun_minimap_image = pygame.transform.scale(self.images['sun'], (10, 10))
        minimap.blit(sun_minimap_image, (sun_minimap_pos[0] - 5, sun_minimap_pos[1] - 5))

        # Calculate maximum distance from sun
        max_distance = max(self.PLANETS.values(), key=lambda x: x[0])[0]

        # Scale factors
        scale_x = scale_y = min(self.MINIMAP_WIDTH, self.MINIMAP_HEIGHT) / (2.2 * max_distance)
        for distance, _, _ in self.PLANETS.values():
            pygame.draw.circle(minimap, (18, 65, 65), sun_minimap_pos, max(1, int(distance * scale_x)), 1)

        pygame.draw.circle(minimap, (150, 110, 65), sun_minimap_pos,
                           max(1, int((self.belt.inner + self.belt.outer) * .5 * scale_x)), 2)
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

        target = self.planet_position(self.destination)
        target_point = pygame.Vector2(sun_minimap_pos) + target * scale_x
        pygame.draw.circle(minimap, (100, 255, 190), target_point, 6, 2)
        pygame.draw.line(minimap, (45, 135, 115), spaceship_minimap_pos, target_point, 1)
        self.screen.blit(minimap, (self.WIDTH - self.MINIMAP_WIDTH - 10, 10))

    def recommended_destination(self):
        return next((name for name in STORY_ORDER if name not in self.progress.completed), 'sun')

    def select_destination(self, name):
        if name not in (*STORY_ORDER, 'sun'):
            raise ValueError('Unknown destination')
        self.destination = name

    def destination_distance(self):
        return pygame.Vector2(self.spaceship_pos).distance_to(self.planet_position(self.destination)) / self.PLANETS['earth'][0]

    @property
    def training_beacon(self):
        return not self.progress.radar_unlocked and self.destination in ('earth', 'mars')

    def activate_shield(self):
        if self.paused or self.health <= 0 or self.shield_cooldown > 0:
            return False
        self.shield_remaining = 5.0
        self.shield_charges = 3
        self.shield_cooldown = 12.0
        return True

    @staticmethod
    def shield_impact(tier, kind='scout'):
        return min(3, max(1 + (tier - 1) // 3,
                          {'scout': 1, 'raider': 2, 'guardian': 3}[kind]))

    def take_damage(self, damage, shield_cost=1):
        if self.shield_remaining > 0 and self.shield_charges > 0:
            self.shield_charges = max(0, self.shield_charges - shield_cost)
            if self.shield_charges == 0:
                self.shield_remaining = 0
            return  # The shield fully absorbs even the hit that breaks it.
        self.health = max(0, self.health - damage)

    def activate_radar(self):
        if self.paused or self.health <= 0:
            return False
        if not self.progress.radar_unlocked:
            self.warning, self.warning_time = 'Complete Earth and Mars to unlock radar.', 4
            return False
        if self.radar_cooldown > 0:
            return False
        self.radar_remaining = self.radar_duration
        self.radar_cooldown = self.radar_recharge
        return True

    def update_navigation(self, dt):
        if self.paused:
            return
        self.belt.update(dt)
        self.shield_remaining = max(0, self.shield_remaining - dt)
        self.shield_cooldown = max(0, self.shield_cooldown - dt)
        if self.shield_remaining == 0:
            self.shield_charges = 0
        self.previous_planet_positions = {name: self.planet_position(name) for name in self.PLANETS}
        for name, (_, _, speed) in self.PLANETS.items():
            self.angles[name] = (self.angles[name] + speed * dt) % math.tau
        self.radar_remaining = max(0, self.radar_remaining - dt)
        self.radar_cooldown = max(0, self.radar_cooldown - dt)

    def draw_target_beacon(self, offset_x, offset_y):
        target = self.planet_position(self.destination) * self.zoom_level + pygame.Vector2(offset_x, offset_y)
        center = pygame.Vector2(self.WIDTH / 2, self.HEIGHT / 2)
        color = (100, 255, 190)
        bounds = self.screen.get_rect().inflate(-90, -160)
        if bounds.collidepoint(target):
            pygame.draw.circle(self.screen, color, target, 38, 2)
            point = target + pygame.Vector2(0, 45)
        else:
            delta = target - center
            factor = min((self.WIDTH / 2 - 60) / max(abs(delta.x), .001),
                         (self.HEIGHT / 2 - 110) / max(abs(delta.y), .001))
            tip = center + delta * factor
            direction = delta.normalize()
            side = pygame.Vector2(-direction.y, direction.x)
            pygame.draw.polygon(self.screen, color, [tip, tip - direction * 22 + side * 10,
                                                     tip - direction * 22 - side * 10])
            point = tip - direction * 38
        label = pygame.font.Font(None, 24).render(self.destination.title(), True, color)
        self.screen.blit(label, label.get_rect(center=point))

    def fire_gem_beam(self, mouse_pos=None):
        if self.paused or self.health <= 0:
            return False
        if not self.progress.beam_unlocked:
            self.warning, self.warning_time = 'Gem beam needs Aries, Cancer, Gemini and Virgo. Complete Earth, Mars and Venus.', 5
            return False
        if self.beam_cooldown > 0:
            return False
        direction = pygame.Vector2(math.cos(self.spaceship_angle), math.sin(self.spaceship_angle))
        if mouse_pos is not None:
            aim = pygame.Vector2(mouse_pos) - pygame.Vector2(self.WIDTH / 2, self.HEIGHT / 2)
            if aim.length_squared():
                direction = aim.normalize()
        self.beam_start = pygame.Vector2(self.spaceship_pos)
        self.beam_end = self.beam_start + direction * self.beam_range
        self.beam_remaining = .4
        self.beam_cooldown = 4.0
        destroyed = self.belt.cut(self.beam_start, self.beam_end, self.beam_width)
        for rock in destroyed:
            for _ in range(5):
                velocity = pygame.Vector2(random.uniform(-160, 160), random.uniform(-160, 160))
                self.debris.append([rock.position.copy(), velocity, .65])
        for enemy in self.enemies[:]:
            if self.segment_distance(enemy['pos'], self.beam_start, self.beam_end) < self.beam_width / 2 + 22:
                self.enemies.remove(enemy)
                self.score += 1
        return True

    def update_belt(self, dt):
        if self.paused:
            return
        self.beam_remaining = max(0, self.beam_remaining - dt)
        self.beam_cooldown = max(0, self.beam_cooldown - dt)
        self.belt_hit_cooldown = max(0, self.belt_hit_cooldown - dt)
        for particle in self.debris[:]:
            particle[0] += particle[1] * dt
            particle[2] -= dt
            if particle[2] <= 0:
                self.debris.remove(particle)
        start = pygame.Vector2(getattr(self, 'previous_pos', self.spaceship_pos))
        end = pygame.Vector2(self.spaceship_pos)
        if not self.progress.beam_unlocked:
            blocked = self.belt.locked_position(start, end, self.spaceship_radius)
            if blocked is not None:
                self.spaceship_pos = list(blocked)
                self.warning = ('Asteroid blockade! Find Gemini and Virgo on Venus.' if self.progress.radar_unlocked
                                else 'Asteroid blockade! Complete Earth, Mars and Venus for the gem beam.')
                self.warning_time = 5
                return
        contact = self.belt.first_collision(start, end, self.spaceship_radius, moving=True)
        if contact is not None:
            travel = end - start
            fraction = max(0, contact - 3 / max(1, travel.length()))
            self.spaceship_pos = list(start + travel * fraction)
            if self.belt_hit_cooldown <= 0:
                self.take_damage(12)
                self.belt_hit_cooldown = .8
            self.warning, self.warning_time = 'Dense asteroids. Right-click or F to cut a corridor.', 3

    def draw_beam(self, offset):
        for position, _, remaining in self.debris:
            point = position * self.zoom_level + offset
            pygame.draw.circle(self.screen, (255, 190, 90), point, max(1, int(4 * remaining * self.zoom_level)))
        if self.beam_remaining <= 0:
            return
        start = self.beam_start * self.zoom_level + offset
        end = self.beam_end * self.zoom_level + offset
        width = self.beam_width * self.zoom_level
        pygame.draw.line(self.screen, (20, 65, 95), start, end, max(1, int(width * 1.3)))
        pygame.draw.line(self.screen, (50, 210, 255), start, end, max(1, int(width)))
        pygame.draw.line(self.screen, (225, 255, 255), start, end, max(1, int(width * .28)))

    def update_spaceship(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
                                   int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w]))
        if not direction.length_squared():
            return False
        target = math.atan2(direction.y, direction.x)
        difference = (target - self.spaceship_angle + math.pi) % math.tau - math.pi
        turn = self.rotation_speed * dt * 60
        self.spaceship_angle += max(-turn, min(turn, difference))
        boost = self.boost_multiplier if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1
        # Keep thrust active throughout the turn, producing a continuous arc.
        speed = self.spaceship_speed * 60 * boost
        self.spaceship_pos[0] += math.cos(self.spaceship_angle) * speed * dt
        self.spaceship_pos[1] += math.sin(self.spaceship_angle) * speed * dt
        return True

    @staticmethod
    def segment_distance(point, start, end):
        segment = end - start
        fraction = max(0, min(1, (point - start).dot(segment) / max(segment.length_squared(), 0.0001)))
        return point.distance_to(start + segment * fraction)

    @property
    def solar_zone(self):
        return self.PLANETS['earth'][0] * 0.30

    @property
    def quiet_approach(self):
        return self.progress.sun_unlocked and pygame.Vector2(self.spaceship_pos).length() < self.solar_zone

    def encounter_tier(self):
        ship = pygame.Vector2(self.spaceship_pos)
        nearest = min(self.PLANETS, key=lambda name: ship.distance_to(self.planet_position(name)))
        return min(8, max(STORY_ORDER.index(nearest) + 1,
                          1 + sum(name in self.progress.completed for name in STORY_ORDER)))

    def planet_position(self, name):
        if name == "sun":
            return pygame.Vector2()
        distance = self.PLANETS[name][0]
        return pygame.Vector2(distance * math.cos(self.angles[name]),
                              distance * math.sin(self.angles[name]))

    def launch_stage(self, name):
        reason = self.progress.lock_reason(name)
        if reason:
            self.warning, self.warning_time = reason, 4
            return
        radar_before = self.progress.radar_unlocked
        beam_before = self.progress.beam_unlocked
        completed_before = name in self.progress.completed
        self.landing_lock = name
        module = import_module(name.capitalize())
        stage = getattr(module, name.capitalize())()
        getattr(stage, 'run' if name == 'saturn' else 'main')()
        if not pygame.get_init():
            sys.exit()
        if not radar_before and self.progress.radar_unlocked:
            self.warning, self.warning_time = 'Radar acquired! Press T for a five-second scan.', 6
        if not beam_before and self.progress.beam_unlocked:
            self.warning, self.warning_time = 'Resonance Beam online! Right-click or F to clear the asteroid belt.', 7
        self.beam_remaining = 0
        self.debris.clear()
        if self.destination == name and not completed_before and name in self.progress.completed:
            self.destination = self.recommended_destination()
        self.previous_planet_positions = {}
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Space Rangers - Alien Invasion')
        pygame.mixer.music.stop()
        radius = self.sun_radius if name == 'sun' else self.PLANETS[name][1]
        self.spaceship_pos = list(self.planet_position(name) + pygame.Vector2(radius + self.spaceship_radius + 100, 0))
        self.previous_pos = self.spaceship_pos.copy()
        self.enemies.clear()
        self.lasers.clear()
        self.enemy_lasers.clear()
        self.health = 100
        self.spawn_timer = 3
        pygame.time.set_timer(pygame.USEREVENT, 0)
        pygame.event.clear()
        self.block_mouse_fire = True
        self.mouse_shot = None

    def check_arrival(self):
        ship = pygame.Vector2(self.spaceship_pos)
        previous = pygame.Vector2(getattr(self, 'previous_pos', self.spaceship_pos))
        barrier = self.solar_zone * 0.8
        if not self.progress.sun_unlocked and self.segment_distance(pygame.Vector2(), previous, ship) < barrier:
            # Stop on the near side even if a boosted frame crosses the whole barrier.
            direction = previous if previous.length_squared() else pygame.Vector2(1, 0)
            self.spaceship_pos = list(direction.normalize() * (barrier + self.spaceship_radius + 10))
            self.warning = "It's too hot! Alien energy blocks the Sun. Collect all planet gems."
            self.warning_time = 4
            return
        if not self.progress.mercury_unlocked:
            mercury = self.planet_position('mercury')
            heat_radius = self.PLANETS['mercury'][1] + self.spaceship_radius + 90
            old_mercury = getattr(self, 'previous_planet_positions', {}).get('mercury', mercury)
            if self.segment_distance(pygame.Vector2(), previous - old_mercury, ship - mercury) < heat_radius:
                direction = previous - mercury
                if not direction.length_squared():
                    direction = pygame.Vector2(1, 0)
                self.spaceship_pos = list(mercury + direction.normalize() * (heat_radius + 10))
                self.warning, self.warning_time = self.progress.lock_reason('mercury'), 4
                return
        if self.landing_lock:
            name = self.landing_lock
            radius = self.sun_radius if name == 'sun' else self.PLANETS[name][1]
            if ship.distance_to(self.planet_position(name)) > radius + self.spaceship_radius + 180:
                self.landing_lock = None
        bodies = [(name, values[1]) for name, values in self.PLANETS.items()]
        if self.progress.sun_unlocked:
            bodies.append(('sun', self.sun_radius))
        for name, radius in bodies:
            current_planet = self.planet_position(name)
            old_planet = getattr(self, 'previous_planet_positions', {}).get(name, current_planet)
            if name != self.landing_lock and self.segment_distance(pygame.Vector2(), previous - old_planet, ship - current_planet) < radius + self.spaceship_radius:
                self.launch_stage(name)
                return

    def update_combat(self, dt):
        self.warning_time = max(0, self.warning_time - dt)
        if self.quiet_approach:
            self.mouse_shot = None
            self.enemies.clear()
            self.lasers.clear()
            self.enemy_lasers.clear()
            self.spawn_timer = 3
            return
        ship = pygame.Vector2(self.spaceship_pos)
        self.fire_timer -= dt
        self.spawn_timer -= dt
        keys = pygame.key.get_pressed()
        mouse_down = pygame.mouse.get_pressed()[0]
        if not mouse_down:
            self.block_mouse_fire = False
        mouse_fire = not self.block_mouse_fire and (mouse_down or self.mouse_shot is not None)
        if (keys[pygame.K_SPACE] or mouse_fire) and self.fire_timer <= 0:
            direction = pygame.Vector2(math.cos(self.spaceship_angle), math.sin(self.spaceship_angle))
            if mouse_fire:
                aim = pygame.Vector2(self.mouse_shot or pygame.mouse.get_pos()) - pygame.Vector2(self.WIDTH / 2, self.HEIGHT / 2)
                if aim.length_squared():
                    direction = aim.normalize()
            speed = 2200 + self.spaceship_speed * 60 * (self.boost_multiplier if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1)
            self.lasers.append([ship + direction * (self.spaceship_radius + 8), direction * speed, 1.2])
            self.fire_timer = 0.16
        self.mouse_shot = None
        tier = self.encounter_tier()
        if self.spawn_timer <= 0 and len(self.enemies) < 4 + tier:
            angle = random.uniform(0, math.tau)
            kind = 'scout' if tier < 3 else random.choice(['scout', 'raider'] if tier < 6 else ['raider', 'guardian'])
            hp = {'scout': 1, 'raider': 2, 'guardian': 4}[kind]
            self.enemies.append({'pos': ship + pygame.Vector2(math.cos(angle), math.sin(angle)) * 650,
                                 'kind': kind, 'hp': hp, 'max_hp': hp, 'tier': tier,
                                 'cooldown': 1.5, 'phase': angle})
            self.spawn_timer = max(0.8, 3.2 - tier * 0.28)
        for laser in self.lasers[:]:
            previous = laser[0].copy()
            laser[0] += laser[1] * dt
            laser[2] -= dt
            if self.belt.first_collision(previous, laser[0], 0) is not None:
                laser[2] = 0
                self.lasers.remove(laser)
                continue
            for enemy in self.enemies[:]:
                if self.segment_distance(enemy['pos'], previous, laser[0]) < 32:
                    enemy['hp'] -= 1
                    if enemy['hp'] <= 0:
                        self.enemies.remove(enemy)
                        self.score += 1
                    laser[2] = 0
                    break
            if laser[2] <= 0:
                self.lasers.remove(laser)
        for enemy in self.enemies[:]:
            delta = ship - enemy['pos']
            distance = delta.length()
            if distance < self.spaceship_radius + 22:
                self.take_damage(10 + enemy['tier'] * 2, self.shield_impact(enemy['tier'], enemy['kind']))
                self.enemies.remove(enemy)
            elif distance > 2600:
                self.enemies.remove(enemy)
            else:
                direction = delta.normalize()
                enemy['phase'] += dt * 3
                speed = 220 + enemy['tier'] * 30
                if enemy['kind'] == 'raider':
                    direction = direction.rotate(math.sin(enemy['phase']) * 30)
                if enemy['kind'] != 'guardian' or distance > 350:
                    enemy['pos'] += direction * speed * dt
                if enemy['kind'] == 'guardian':
                    enemy['cooldown'] -= dt
                    if enemy['cooldown'] <= 0:
                        self.enemy_lasers.append([enemy['pos'].copy(), delta.normalize() * 600, 3, self.shield_impact(enemy['tier'], enemy['kind'])])
                        enemy['cooldown'] = 1.8
        for shot in self.enemy_lasers[:]:
            previous = shot[0].copy()
            shot[0] += shot[1] * dt
            shot[2] -= dt
            if self.segment_distance(ship, previous, shot[0]) < self.spaceship_radius:
                self.take_damage(18, shot[3] if len(shot) > 3 else 1)
                shot[2] = 0
            if shot[2] <= 0:
                self.enemy_lasers.remove(shot)

    def draw_combat(self, offset_x, offset_y):
        def screen_point(pos):
            return pos * self.zoom_level + pygame.Vector2(offset_x, offset_y)
        for enemy in self.enemies:
            center = screen_point(enemy['pos'])
            color = {'scout': (190, 70, 240), 'raider': (255, 150, 60), 'guardian': (255, 60, 90)}[enemy['kind']]
            pygame.draw.circle(self.screen, color, center, max(4, int(22 * self.zoom_level)))
            for pip in range(enemy['hp']):
                pygame.draw.circle(self.screen, color, center + pygame.Vector2(pip * 6 - 9, -30), 2)
            pygame.draw.circle(self.screen, (80, 255, 150), center, max(2, int(9 * self.zoom_level)))
        for pos, velocity, _ in self.lasers:
            pygame.draw.line(self.screen, (80, 255, 240), screen_point(pos),
                             screen_point(pos - velocity.normalize() * 25), 3)
        for shot in self.enemy_lasers:
            pos = shot[0]
            pygame.draw.circle(self.screen, (255, 90, 90), screen_point(pos), 5)
        barrier_color = (80, 220, 230) if self.progress.sun_unlocked else (255, 110, 55)
        pygame.draw.circle(self.screen, barrier_color, screen_point(pygame.Vector2()),
                           int(self.solar_zone * 0.8 * self.zoom_level), 2)
        if not self.progress.mercury_unlocked:
            radius = self.PLANETS['mercury'][1] + self.spaceship_radius + 90
            pygame.draw.circle(self.screen, (255, 135, 65), screen_point(self.planet_position('mercury')),
                               max(1, int(radius * self.zoom_level)), 2)
        if self.shield_remaining > 0:
            center = (self.WIDTH // 2, self.HEIGHT // 2)
            radius = max(16, int((self.spaceship_radius + 18) * self.zoom_level))
            pygame.draw.circle(self.screen, (80, 200, 255), center, radius, 3)
            for pip in range(self.shield_charges):
                pygame.draw.circle(self.screen, (160, 240, 255), (center[0] - 10 + pip * 10, center[1] - radius - 8), 3)
        lines = [f'Hull {self.health}%   Gems {len(self.progress.gems)}/12',
                 f'{self.destination.title()}  {self.destination_distance():.2f} AU']
        for i, line in enumerate(lines):
            self.screen.blit(self.small_font.render(line, True, self.WHITE), (15, 15 + i * 32))
        alert = self.progress.save_error or (self.warning if self.warning_time > 0 else '')
        if not alert and self.quiet_approach:
            alert = 'Gem shield active. Only the boss remains.'
        if alert:
            text = self.small_font.render(alert, True, (255, 215, 120))
            if text.get_width() > self.WIDTH - 30:
                text = pygame.transform.smoothscale(text, (self.WIDTH - 30, int(text.get_height() * (self.WIDTH - 30) / text.get_width())))
            self.screen.blit(text, (15, self.HEIGHT - 90))
        pygame.draw.rect(self.screen, (25, 40, 65), self.pause_button, border_radius=6)
        label = self.hud_font.render('Pause / Help', True, self.WHITE)
        self.screen.blit(label, label.get_rect(center=self.pause_button.center))
        radar_label = 'Radar locked' if not self.progress.radar_unlocked else (
            f'Scan {self.radar_remaining:.0f}s' if self.radar_remaining > 0 else
            f'Recharge {math.ceil(self.radar_cooldown)}s' if self.radar_cooldown > 0 else 'Radar [T]')
        pygame.draw.rect(self.screen, (25, 40, 65), self.radar_button, border_radius=6)
        text = self.hud_font.render(radar_label, True, self.WHITE)
        self.screen.blit(text, text.get_rect(center=self.radar_button.center))
        beam_label = ('Gem beam locked' if not self.progress.beam_unlocked else
                      f'Beam {math.ceil(self.beam_cooldown)}s' if self.beam_cooldown > 0 else 'Gem beam [F]')
        pygame.draw.rect(self.screen, (35, 45, 85), self.beam_button, border_radius=6)
        text = self.hud_font.render(beam_label, True, self.WHITE)
        self.screen.blit(text, text.get_rect(center=self.beam_button.center))

        shield_label = (f'Shield {self.shield_remaining:.1f}s | {self.shield_charges}/3' if self.shield_remaining > 0 else
                        f'Shield recharge {math.ceil(self.shield_cooldown)}s' if self.shield_cooldown > 0 else 'Shield [E]')
        pygame.draw.rect(self.screen, (25, 65, 90), self.shield_button, border_radius=6)
        text = self.hud_font.render(shield_label, True, self.WHITE)
        self.screen.blit(text, text.get_rect(center=self.shield_button.center))

    def destination_options(self):
        names = (*STORY_ORDER, 'sun')
        width, height = int(self.WIDTH * .24), int(self.HEIGHT * .065)
        return [(name, pygame.Rect(int(self.WIDTH * .12) + (i % 3) * int(self.WIDTH * .26),
                                   int(self.HEIGHT * .30) + (i // 3) * int(self.HEIGHT * .085), width, height))
                for i, name in enumerate(names)]

    def pause_options(self):
        actions = [('Resume', 'resume')] if self.health > 0 else []
        actions += [('Retry flight', 'restart'), ('Main menu', 'quit')]
        width = int(self.WIDTH * .22)
        left = (self.WIDTH - len(actions) * (width + 12) + 12) // 2
        return [(label, action, pygame.Rect(left + i * (width + 12), int(self.HEIGHT * .64), width, 44))
                for i, (label, action) in enumerate(actions)]

    def set_paused(self, paused):
        self.paused = paused
        self.block_mouse_fire = True
        self.mouse_shot = None

    def pause_menu(self):
        # Compose the full frame before presenting it; no unpaused intermediate flash.
        self.draw_solar_system(self.angles, present=False)
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render('Paused' if self.health > 0 else 'Rocket destroyed', True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * .13))))
        help_font = pygame.font.Font(None, max(18, int(self.HEIGHT * .03)))
        subtitle = help_font.render('Choose destination - click a planet or use Left / Right', True, (185, 205, 220))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * .24))))
        for name, rect in self.destination_options():
            color = (35, 100, 105) if name == self.destination else (25, 45, 65)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            label = name.title() + (' [Locked]' if self.progress.lock_reason(name) else '')
            text = help_font.render(label, True, self.WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))
        for label, action, rect in self.pause_options():
            color = (45, 90, 120) if rect.collidepoint(pygame.mouse.get_pos()) else (25, 45, 65)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            text = help_font.render(label, True, self.WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))
        radar_help = 'T: radar (5s scan / 20s recharge)' if self.progress.radar_unlocked else 'Radar unlock: complete Earth + Mars (training beacons available)'
        for i, line in enumerate(['WASD / Arrows: fly   Shift: boost   Wheel: zoom',
                                  'Left click / Space: lasers   Right click / F: gem beam (4s recharge)', radar_help,
                                  'E: shield (5s / 3 charges, 12s recharge)',
                                  'Esc / R: resume   N: retry   Q: menu']):
            text = help_font.render(line, True, (185, 205, 220))
            self.screen.blit(text, text.get_rect(center=(self.WIDTH // 2, self.HEIGHT * .76 + i * self.HEIGHT * .04)))
        pygame.display.update()

    def main(self):
        clock = pygame.time.Clock()
        angles = self.angles

        running = True

        while running:
            dt = min(clock.tick(self.FPS) / 1000, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWFOCUSLOST:
                    self.escape_held = False
                    self.set_paused(True)
                elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    self.escape_held = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.health > 0:
                        if not self.escape_held and not getattr(event, 'repeat', False):
                            self.set_paused(not self.paused)
                        self.escape_held = True
                    elif self.paused and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        names = (*STORY_ORDER, 'sun')
                        step = 1 if event.key == pygame.K_RIGHT else -1
                        self.select_destination(names[(names.index(self.destination) + step) % len(names)])
                    elif event.key == pygame.K_f and not self.paused:
                        self.fire_gem_beam()
                    elif event.key == pygame.K_e and not self.paused:
                        self.activate_shield()
                    elif event.key == pygame.K_t and not self.paused:
                        self.activate_radar()
                    elif event.key == pygame.K_r and self.paused and self.health > 0:
                        self.set_paused(False)
                    elif event.key == pygame.K_n and self.paused:
                        self.__init__(self.progress)
                        angles = self.angles
                    elif event.key == pygame.K_q and self.paused:
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not self.paused:
                    self.fire_gem_beam(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.paused:
                        destination = next((name for name, rect in self.destination_options() if rect.collidepoint(event.pos)), None)
                        if destination:
                            self.select_destination(destination)
                        action = next((action for _, action, rect in self.pause_options() if rect.collidepoint(event.pos)), None)
                        if action == 'quit':
                            return
                        if action == 'restart':
                            self.__init__(self.progress)
                            angles = self.angles
                        elif action == 'resume':
                            self.set_paused(False)
                        self.block_mouse_fire = True
                    elif self.pause_button.collidepoint(event.pos):
                        self.set_paused(True)
                    elif self.beam_button.collidepoint(event.pos):
                        self.fire_gem_beam()
                        self.block_mouse_fire = True
                    elif self.shield_button.collidepoint(event.pos):
                        self.activate_shield()
                        self.block_mouse_fire = True
                    elif self.radar_button.collidepoint(event.pos):
                        self.activate_radar()
                        self.block_mouse_fire = True
                    else:
                        self.mouse_shot = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                    if event.button == 4:  # Scroll up
                        self.zoom_level = min(self.zoom_level + 0.1, self.max_zoom_out)
                    elif event.button == 5:  # Scroll down
                        self.zoom_level = max(self.zoom_level - 0.1, self.max_zoom_in)

            if not self.paused:
                if self.health > 0:
                    self.previous_pos = self.spaceship_pos.copy()
                    self.update_spaceship(dt)
                    self.update_navigation(dt)
                    self.update_belt(dt)
                    if self.health > 0:
                        self.check_arrival()
                        self.update_combat(dt)
                    if not pygame.get_init():
                        return
                else:
                    self.paused = True
                self.draw_solar_system(angles)
            else:
                self.pause_menu()



        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SolarSystem()
    game.main()
