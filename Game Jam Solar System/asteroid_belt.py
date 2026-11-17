"""A short, continuous asteroid blockade with persistent per-flight cut corridors."""
from dataclasses import dataclass
from collections import defaultdict
import math
import random
import pygame


def circle_entry(start, end, center, radius):
    """First swept contact, including crossings that skip an entire obstacle."""
    delta, relative = end - start, start - center
    if relative.length_squared() <= radius * radius:
        return 0.0
    a = delta.length_squared()
    if a == 0:
        return None
    b = 2 * relative.dot(delta)
    c = relative.length_squared() - radius * radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return None
    root = (-b - math.sqrt(discriminant)) / (2 * a)
    return root if 0 <= root <= 1 else None


@dataclass
class Asteroid:
    position: pygame.Vector2
    radius: float
    vertices: tuple
    color: tuple
    previous_position: object = None


class AsteroidBelt:
    def __init__(self, au_pixels, scale):
        self.inner = au_pixels * 2.6 - 310 * scale
        self.outer = au_pixels * 2.6 + 310 * scale
        self.cell_size = 256 * scale
        self.max_radius = 55 * scale
        self.angular_speed = math.tau / (360 * 2.6 ** 1.5)
        self.max_motion = 0.0
        self.rocks = {}
        self.cells = defaultdict(list)
        rng = random.Random(2417)
        for row in range(4):
            radius = self.inner + (65 + 160 * row) * scale
            count = int(math.tau * radius / (105 * scale))
            for i in range(count):
                angle = (i + row * .37) * math.tau / count
                distance = radius + rng.uniform(-15, 15) * scale
                pos = pygame.Vector2(math.cos(angle), math.sin(angle)) * distance
                size = rng.uniform(36, 55) * scale
                points = tuple((math.cos(j * math.tau / 8) * size * rng.uniform(.8, 1),
                                math.sin(j * math.tau / 8) * size * rng.uniform(.8, 1)) for j in range(8))
                shade = rng.randint(80, 115)
                rock = Asteroid(pos, size, points, (shade, shade - 9, shade - 18))
                index = len(self.rocks)
                self.rocks[index] = rock
                self.cells[self.cell(pos)].append(index)

    def update(self, dt):
        """Orbit the whole belt; removed rocks stay removed as corridors rotate."""
        rotation = math.degrees(self.angular_speed * dt)
        self.max_motion = 0.0
        self.cells.clear()
        for index, rock in self.rocks.items():
            rock.previous_position = rock.position.copy()
            rock.position = rock.position.rotate(rotation)
            self.max_motion = max(self.max_motion, rock.position.distance_to(rock.previous_position))
            self.cells[self.cell(rock.position)].append(index)

    def cell(self, point):
        return math.floor(point[0] / self.cell_size), math.floor(point[1] / self.cell_size)

    def candidates(self, start, end, padding=0):
        padding += self.max_radius
        low = self.cell((min(start.x, end.x) - padding, min(start.y, end.y) - padding))
        high = self.cell((max(start.x, end.x) + padding, max(start.y, end.y) + padding))
        for x in range(low[0], high[0] + 1):
            for y in range(low[1], high[1] + 1):
                for index in self.cells.get((x, y), ()):
                    rock = self.rocks.get(index)
                    if rock is not None:
                        yield index, rock

    def first_collision(self, start, end, ship_radius, moving=False):
        earliest = None
        for _, rock in self.candidates(start, end, ship_radius + (self.max_motion if moving else 0)):
            radius = rock.radius + ship_radius
            old_position = rock.previous_position if moving and rock.previous_position is not None else rock.position
            relative_start = start + rock.position - old_position
            if relative_start.distance_to(rock.position) < radius and end.distance_to(rock.position) > relative_start.distance_to(rock.position):
                continue  # A ship already touching a rock can back away.
            contact = circle_entry(relative_start, end, rock.position, radius)
            if contact is not None and (earliest is None or contact < earliest):
                earliest = contact
        return earliest

    def cut(self, start, end, width):
        """Remove every intersected rock, never just the first one hit."""
        removed = []
        for index, rock in list(self.candidates(start, end, width / 2)):
            if circle_entry(start, end, rock.position, rock.radius + width / 2) is not None:
                removed.append(rock)
                del self.rocks[index]
        return removed

    def locked_position(self, start, end, ship_radius):
        """Repel on the approached side of the complete annulus, regardless of gaps."""
        inner, outer = self.inner - ship_radius - 15, self.outer + ship_radius + 15
        radius = start.length()
        if radius < inner:
            if end.length() < inner:
                return None
            # Find the exit point by solving the reversed segment's entry.
            contact = circle_entry(end, start, pygame.Vector2(), inner)
            fraction = 1 - contact if contact is not None else 0
        elif radius > outer:
            fraction = circle_entry(start, end, pygame.Vector2(), outer)
            if fraction is None:
                return None
        else:
            direction = start.normalize() if radius else pygame.Vector2(1, 0)
            return direction * (inner - 5 if radius < (inner + outer) / 2 else outer + 5)
        delta = end - start
        margin = min(fraction, 5 / max(delta.length(), 1))
        return start + delta * (fraction - margin)

    def draw(self, screen, zoom, offset):
        world_start = -offset / zoom
        world_end = (pygame.Vector2(screen.get_size()) - offset) / zoom
        for _, rock in self.candidates(world_start, world_end):
            center = rock.position * zoom + offset
            if not screen.get_rect().inflate(120, 120).collidepoint(center):
                continue
            points = [center + pygame.Vector2(point) * zoom for point in rock.vertices]
            pygame.draw.polygon(screen, rock.color, points)
            pygame.draw.polygon(screen, (160, 139, 105), points, max(1, int(2 * zoom)))
            pygame.draw.circle(screen, (55, 49, 45), center + pygame.Vector2(-.2, .15) * rock.radius * zoom,
                               max(1, int(rock.radius * zoom * .23)))
