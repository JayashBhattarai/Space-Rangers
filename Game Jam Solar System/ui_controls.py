"""Small, shared mouse buttons for existing stage and story controls."""
import pygame

def options(stage):
    name = type(stage).__name__
    paused = any(getattr(stage, flag, False) for flag in ('paused', 'show_pause_menu', 'pause_menu_active'))
    if name == 'Mercury':
        paused = getattr(stage, 'show_pause_menu', False)
    state = getattr(stage, 'game_state', '')
    if getattr(stage, 'show_end_options', False):
        return [('Reread', pygame.K_r), ('Menu', pygame.K_m)]
    if name in ('Prologue', 'Epilogue') or state == 'intro' and not paused:
        return [('Continue', pygame.K_SPACE if name == 'Sun' else pygame.K_RETURN)]
    if paused:
        resume = pygame.K_ESCAPE if name in ('Sun', 'Neptune', 'Uranus', 'Saturn') else pygame.K_r
        restart = pygame.K_t if name in ('Mercury', 'Venus') else pygame.K_r if name in ('Sun', 'Neptune', 'Uranus') else pygame.K_n
        return [('Resume', resume), ('Retry', restart), ('Menu', pygame.K_q)]
    if state in ('victory', 'defeat') or getattr(stage, 'congratulations_active', False):
        return [('Retry', pygame.K_t if name == 'Mercury' else pygame.K_r), ('Menu', pygame.K_q)]
    return []

def buttons(stage):
    screen = stage.screen
    width = min(112, screen.get_width() // 7)
    entries = options(stage)
    left = screen.get_width() - len(entries) * (width + 8) - 12
    return [(label, key, pygame.Rect(left + i * (width + 8), 10, width, 32)) for i, (label, key) in enumerate(entries)]

def mouse_key(stage, pos):
    for label, key, rect in buttons(stage):
        if not rect.collidepoint(pos):
            continue
        name = type(stage).__name__
        if label == 'Continue' and not stage.text_box.is_finished():
            stage.text_box.reveal_index = sum(map(len, stage.text_box.text_content))
            return None
        if name == 'Saturn':
            if stage.pause_menu_active:
                stage.selected_option = {'Resume': 0, 'Retry': 1, 'Menu': 2}[label]
                return pygame.K_RETURN
            if stage.congratulations_active:
                stage.congratulations_selected = 0 if label == 'Retry' else 1
                return pygame.K_RETURN
        return key
    return False

def draw_options(stage):
    font = pygame.font.Font(None, 24)
    for label, _, rect in buttons(stage):
        color = (45, 90, 120) if rect.collidepoint(pygame.mouse.get_pos()) else (25, 40, 65)
        pygame.draw.rect(stage.screen, color, rect, border_radius=6)
        text = font.render(label, True, 'white')
        stage.screen.blit(text, text.get_rect(center=rect.center))
