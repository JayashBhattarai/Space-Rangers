import sys
from pygame import mixer
import pygame

pygame.init()

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)

pygame.font.init()
TITLE_FONT = pygame.font.Font(None, 74)
MENU_FONT = pygame.font.Font(None, 50)

background = pygame.image.load("src/background.png")
background = pygame.transform.scale(background, (screen_width, screen_height))

# Load and play background music
mixer.music.load('src/main.mp3')
mixer.music.play(-1)

main_menu_options = ["Start Game", "Space Navigation", "Quit"]
level_options = ["Stage 0 Prologue", "Stage 1 Earth", "Stage 2 Mars", "Stage 3 Venus", "Stage 4 Jupiter", "Stage 5 Saturn",
                 "Stage 6 Uranus", "Stage 7 Neptune", "Stage 8 Mercury", "Stage 9 Sun", "Stage Final Epilogue"]
selected_option = 0

def draw_main_menu():
    screen.blit(background, (0, 0))

    title_surface = TITLE_FONT.render("SPACE RANGERS", True, WHITE)
    title_rect = title_surface.get_rect(center=(screen_width / 2, screen_height / 4))
    screen.blit(title_surface, title_rect)

    for i, option in enumerate(main_menu_options):
        color = WHITE if i == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height / 2 + i * 75))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

def draw_level_selection_menu():
    screen.blit(background, (0, 0))

    title_surface = TITLE_FONT.render("Level Selection", True, WHITE)
    title_rect = title_surface.get_rect(center=(screen_width / 2, screen_height / 4))
    screen.blit(title_surface, title_rect)

    levels_left = level_options[:5]
    levels_right = level_options[5:10]
    level_bottom = [level_options[10]]

    vertical_position = screen_height / 2 - 75

    for i, option in enumerate(levels_left):
        color = WHITE if i == selected_option and selected_option < 5 else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(screen_width / 3, vertical_position + i * 60))
        screen.blit(text_surface, text_rect)

    for i, option in enumerate(levels_right):
        color = WHITE if i + 5 == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(2 * screen_width / 3, vertical_position + i * 60))
        screen.blit(text_surface, text_rect)

    for i, option in enumerate(level_bottom):
        color = WHITE if i + 10 == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height - 150))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

def main_screen():
    global selected_option
    current_screen = "main_menu"
    music_playing = False

    running = True
    while running:
        if current_screen == "main_menu" and not music_playing:
            mixer.music.load('src/main.mp3')
            mixer.music.play(-1)
            music_playing = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if current_screen == "main_menu":
                        selected_option = (selected_option + 1) % len(main_menu_options)
                    elif current_screen == "level_selection":
                        selected_option = (selected_option + 1) % len(level_options)
                elif event.key == pygame.K_UP:
                    if current_screen == "main_menu":
                        selected_option = (selected_option - 1) % len(main_menu_options)
                    elif current_screen == "level_selection":
                        selected_option = (selected_option - 1) % len(level_options)
                elif event.key == pygame.K_RETURN:
                    if current_screen == "main_menu":
                        if selected_option == 0:
                            current_screen = "level_selection"
                            selected_option = 0
                        elif selected_option == 1:
                            print("SPACE NAVIGATION")
                            mixer.music.stop()
                            music_playing = False
                            pygame.time.wait(100)
                            from solarsystem import SolarSystem
                            game = SolarSystem()
                            game.main()
                            current_screen = "main_menu"
                            selected_option = 0
                        elif selected_option == 2:
                            pygame.quit()
                            sys.exit()
                    elif current_screen == "level_selection":
                        mixer.music.stop()
                        music_playing = False
                        if selected_option == 0:
                            print("Prologue selected")
                            from prologue import Prologue
                            game = Prologue()
                            result = game.run()
                        elif selected_option == 1:
                            print("Level 1 selected")
                            from Earth import Earth
                            game = Earth()
                            result = game.main()
                        elif selected_option == 2:
                            print("Level 2 selected")
                            from Mars import Mars
                            game = Mars()
                            result = game.main()
                        elif selected_option == 3:
                            print("Level 3 selected")
                            from Venus import Venus
                            game = Venus()
                            result = game.main()
                        elif selected_option == 4:
                            print("Level 4 selected")
                            from Jupiter import Jupiter
                            game = Jupiter()
                            result = game.main()
                        elif selected_option == 5:
                            print("Level 5 selected")
                            from Saturn import Saturn
                            game = Saturn()
                            result = game.run()
                        elif selected_option == 6:
                            print("Level 6 selected")
                            from Uranus import Uranus
                            game = Uranus()
                            result = game.main()
                        elif selected_option == 7:
                            print("Level 7 selected")
                            from Neptune import Neptune
                            game = Neptune()
                            result = game.main()
                        elif selected_option == 8:
                            print("Level 8 selected")
                            from Mercury import Mercury
                            game = Mercury()
                            result = game.main()
                        elif selected_option == 9:
                            print("Level 9 selected")
                            from Sun import Sun
                            game = Sun()
                            result = game.main()
                        elif selected_option == 10:
                            print("Final selected")
                            from final import Epilogue
                            game = Epilogue()
                            result = game.run()

                        if result == "main_menu":
                            current_screen = "main_menu"
                            selected_option = 0
                elif event.key == pygame.K_BACKSPACE:
                    if current_screen == "level_selection":
                        current_screen = "main_menu"
                        selected_option = 0

        if current_screen == "main_menu":
            draw_main_menu()
        elif current_screen == "level_selection":
            draw_level_selection_menu()

    mixer.music.stop()

if __name__ == "__main__":
    main_screen()
