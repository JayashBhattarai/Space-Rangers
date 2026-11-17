"""WASD aliases while retaining each stage's existing arrow controls."""
import pygame

ALIASES = {pygame.K_w: pygame.K_UP, pygame.K_a: pygame.K_LEFT,
           pygame.K_s: pygame.K_DOWN, pygame.K_d: pygame.K_RIGHT}

_mouse_keys = set()

def get_events(stage=None):
    global _mouse_keys
    _mouse_keys = set()
    events = pygame.event.get()
    for event in events:
        if stage is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            from ui_controls import mouse_key
            key = mouse_key(stage, event.pos)
            if key is None:
                continue
            if key is not False:
                _mouse_keys.add(key)
                yield pygame.event.Event(pygame.KEYDOWN, key=key, unicode='')
                continue
        if event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key in ALIASES:
            values = event.dict.copy()
            values['key'] = ALIASES[event.key]
            yield pygame.event.Event(event.type, values)
        else:
            yield event

class MovementKeys:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
    def __getitem__(self, key):
        aliases = {arrow: letter for letter, arrow in ALIASES.items()}
        return key in _mouse_keys or self.keys[key] or (key in aliases and self.keys[aliases[key]])

def pressed_keys():
    return MovementKeys()
