"""One window size shared by the menu, flight and every stage."""
import pygame

_size = None

def game_size():
    global _size
    if _size is None:
        desktop = pygame.display.get_desktop_sizes()[0]
        scale = min(1.0, (desktop[0] - 80) / 1280, (desktop[1] - 100) / 800)
        _size = (int(1280 * scale), int(800 * scale))
    return _size
