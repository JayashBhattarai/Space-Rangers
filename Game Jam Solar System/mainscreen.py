import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)

pygame.font.init()
TITLE_FONT = pygame.font.Font(None, 74)
MENU_FONT = pygame.font.Font(None, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Menu")

main_menu_options = ["Start Game", "Space Navigation", "Quit"]
level_options = ["Stage 1 Earth", "Stage 2 Mars", "Stage 3 Venus", "Stage 4 Jupiter", "Stage 5 Saturn", "Stage 6 Uranus", "Stage 7 Neptune", "Stage 8 Mercury", "Stage 9 Sun"]
selected_option = 0

def draw_main_menu():
    screen.fill(BLACK)

    title_surface = TITLE_FONT.render("SPACE RANGERS", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH / 2, HEIGHT / 4))
    screen.blit(title_surface, title_rect)

    # Draw the menu options
    for i, option in enumerate(main_menu_options):
        color = WHITE if i == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + i * 75))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

def draw_level_selection_menu():
    screen.fill(BLACK)

    title_surface = TITLE_FONT.render("Level Selection", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH / 2, HEIGHT / 4))
    screen.blit(title_surface, title_rect)

    # Divide the levels into two groups
    levels_left = level_options[:4]
    levels_right = level_options[4:8]
    level_bottom = [level_options[8]]

    # Calculate vertical position for the columns
    vertical_position = HEIGHT / 2 - 75  # Start higher than the center

    # Draw the left column of levels
    for i, option in enumerate(levels_left):
        color = WHITE if i == selected_option and selected_option < 4 else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH / 3, vertical_position + i * 60))
        screen.blit(text_surface, text_rect)

    # Draw the right column of levels
    for i, option in enumerate(levels_right):
        color = WHITE if i + 4 == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(2 * WIDTH / 3, vertical_position + i * 60))
        screen.blit(text_surface, text_rect)

    # Draw the bottom center level
    for i, option in enumerate(level_bottom):
        color = WHITE if i + 8 == selected_option else GRAY
        text_surface = MENU_FONT.render(option, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT - 150))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()




def main_screen():
    global selected_option
    current_screen = "main_menu"

    running = True
    while running:
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
                            selected_option = 0  # Reset selected option for level selection
                        elif selected_option == 1:
                            print("SPACE NAVIGATION")
                            from solarsystem import SolarSystem
                            game = SolarSystem()
                            game.main()
                            selected_option = 0
                        elif selected_option == 2:
                            pygame.quit()
                            sys.exit()
                    elif current_screen == "level_selection":
                        if selected_option == 0:
                            print("Level 1 selected")
                            from Earth import Earth
                            game = Earth()
                            game.main()
                        elif selected_option == 1:
                            print("Level 2 selected")
                            from Mars import Mars
                            game = Mars()
                            game.main()
                        elif selected_option == 2:
                            print("Level 3 selected")
                            from Venus import Venus
                            game = Venus()
                            game.main()
                        elif selected_option == 3:
                            print("Level 4 selected")
                            from Jupiter import Jupiter
                            game = Jupiter()
                            game.main()
                        elif selected_option == 4:
                            print("Level 5 selected")
                        elif selected_option == 5:
                            print("Level 6 selected")
                            from Uranus import Uranus
                            game = Uranus()
                            game.main()
                        elif selected_option == 6:
                            print("Level 7 selected")
                            from Neptune import Neptune
                            game = Neptune()
                            game.main()
                        elif selected_option == 7:
                            print("Level 8 selected")
                            from Mercury import Mercury
                            game = Mercury()
                            game.main()
                        elif selected_option == 8:
                            print("Level 9 selected")
                            from Sun import Sun
                            game = Sun()
                            game.main()

                elif event.key == pygame.K_BACKSPACE:
                    if current_screen == "level_selection":
                        current_screen = "main_menu"
                        selected_option = 0  # Reset selected option for main menu

        if current_screen == "main_menu":
            draw_main_menu()
        elif current_screen == "level_selection":
            draw_level_selection_menu()


if __name__ == "__main__":
    main_screen()

