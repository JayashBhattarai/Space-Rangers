"""Main menu and story stage selection."""
import os
import sys
from pathlib import Path
from importlib import import_module
import pygame
from pygame import mixer
from campaign import campaign, STORY_ORDER
from display_settings import game_size

os.chdir(Path(__file__).resolve().parent)
STAGES = [('prologue', 'Prologue', 'run')] + [(name.capitalize(), name.capitalize(), 'run' if name == 'saturn' else 'main') for name in STORY_ORDER] + [('Sun', 'Sun', 'main'), ('final', 'Epilogue', 'run')]

def menu_buttons(width, height, choosing_level):
    if not choosing_level:
        return [pygame.Rect(int(width * .32), int(height * (.43 + i * .1) - height * .033),
                            int(width * .36), int(height * .066)) for i in range(3)]
    return [pygame.Rect(int(width * (.07 if i < 5 else .53)),
                        int(height * (.34 + (i % 5) * .085) - height * .032),
                        int(width * .40), int(height * .064)) for i in range(10)] + [
        pygame.Rect(int(width * .30), int(height * .768), int(width * .40), int(height * .064))]


def main_screen():
    pygame.init()
    width, height = game_size()
    screen = pygame.display.set_mode((width, height))
    background = pygame.transform.scale(pygame.image.load('src/background.png'), (width, height))
    title_font = pygame.font.Font(None, int(height * 0.085))
    menu_font = pygame.font.Font(None, int(height * 0.045))
    small_font = pygame.font.Font(None, int(height * 0.03))
    back_button = pygame.Rect(20, 20, 110, 40)
    selected = 0
    choosing_level = False
    message = ''
    clock = pygame.time.Clock()
    music_playing = False
    while True:
        clock.tick(60)
        if not music_playing:
            pygame.display.set_caption('Space Rangers - Main Menu')
            mixer.music.load('src/main.mp3')
            mixer.music.play(-1)
            music_playing = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            buttons = menu_buttons(width, height, choosing_level)
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                hit = next((i for i, rect in enumerate(buttons) if rect.collidepoint(event.pos)), None)
                if hit is not None:
                    selected = hit
                if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                    continue
                if choosing_level and back_button.collidepoint(event.pos):
                    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
                elif hit is not None:
                    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                else:
                    continue
            if event.type != pygame.KEYDOWN:
                continue
            count = len(STAGES) if choosing_level else 3
            if event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_s, pygame.K_w):
                selected = (selected + (1 if event.key in (pygame.K_DOWN, pygame.K_s) else -1)) % count
                message = ''
            elif event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE) and choosing_level:
                choosing_level = False
                selected = 0
            elif event.key == pygame.K_RETURN:
                if not choosing_level and selected == 0:
                    choosing_level = True
                    selected = 0
                elif not choosing_level and selected == 2:
                    pygame.quit()
                    return
                else:
                    if choosing_level:
                        message = campaign.lock_reason(STAGES[selected][0].lower())
                        if message:
                            continue
                    mixer.music.stop()
                    if choosing_level:
                        module_name, class_name, method = STAGES[selected]
                        stage = getattr(import_module(module_name), class_name)()
                        getattr(stage, method)()
                    else:
                        from solarsystem import SolarSystem
                        SolarSystem().main()
                    if not pygame.get_init():
                        return
                    screen = pygame.display.set_mode((width, height))
                    music_playing = False
                    choosing_level = False
                    selected = 0
                    pygame.event.clear()
                    break
        screen.blit(background, (0, 0))
        title = title_font.render('Level Selection' if choosing_level else 'SPACE RANGERS', True, 'white')
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))
        if choosing_level:
            labels = ['Prologue'] + [name.title() + ('  [Locked]' if campaign.lock_reason(name) else '  [Gem collected]' if name in campaign.completed else '') for name in STORY_ORDER] + ['Sun' + ('  [Unlocked]' if campaign.sun_unlocked else '  [Locked]'), 'Final Epilogue' + ('' if campaign.epilogue_unlocked else '  [Locked]')]
            for i, label in enumerate(labels):
                if i < 10:
                    x = width * (0.27 if i < 5 else 0.73)
                    y = height * (0.34 + (i % 5) * 0.085)
                else:
                    x, y = width / 2, height * 0.80
                text = menu_font.render(('> ' if i == selected else '') + label, True, 'white' if i == selected else (170, 180, 205))
                screen.blit(text, text.get_rect(center=(x, y)))
        else:
            for i, label in enumerate(['Start Game', 'Space Navigation', 'Quit']):
                text = menu_font.render(('> ' if i == selected else '') + label, True, 'white' if i == selected else (170, 180, 205))
                screen.blit(text, text.get_rect(center=(width / 2, height * (0.43 + i * 0.1))))
        if choosing_level:
            pygame.draw.rect(screen, (25, 40, 65), back_button, border_radius=8)
            screen.blit(small_font.render('< Back', True, 'white'), (36, 31))
        status = message or campaign.save_error or f'Gems {len(campaign.gems)}/12 | Click to select | W/S or arrows + Enter'
        text = small_font.render(status, True, (255, 225, 140))
        screen.blit(text, text.get_rect(center=(width / 2, height * 0.93)))
        pygame.display.flip()

if __name__ == '__main__':
    main_screen()
