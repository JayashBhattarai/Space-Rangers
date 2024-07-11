import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zodiac Jigsaw Puzzle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)

# Load images
scorpio_image = pygame.image.load('alien.png')
capricorn_image = pygame.image.load('user.png')

# Resize images
sign_size = 300
scorpio_image = pygame.transform.scale(scorpio_image, (sign_size, sign_size))
capricorn_image = pygame.transform.scale(capricorn_image, (sign_size, sign_size))

# Split images into pieces
pieces_per_row = 3
piece_size = sign_size // pieces_per_row
scorpio_pieces = []
capricorn_pieces = []

for y in range(pieces_per_row):
    for x in range(pieces_per_row):
        rect = pygame.Rect(x * piece_size, y * piece_size, piece_size, piece_size)
        scorpio_pieces.append(scorpio_image.subsurface(rect))
        capricorn_pieces.append(capricorn_image.subsurface(rect))

# Game variables
total_pieces = pieces_per_row * pieces_per_row
puzzle_size = 2 * pieces_per_row  # total grid size for both images
grid = list(range(total_pieces * 2))
random.shuffle(grid)
dragging_piece = None
correctly_placed = [False] * (total_pieces * 2)
game_over = False
result_text = None

# Centering variables
center_x = (WIDTH - puzzle_size * piece_size) // 2
center_y = (HEIGHT - puzzle_size * piece_size) // 2 + 100  # Adjust for reference images

# Main game loop
running = True
clock = pygame.time.Clock()

def draw_grid():
    for i in range(total_pieces * 2):
        x = (i % (2 * pieces_per_row)) * piece_size + center_x
        y = (i // (2 * pieces_per_row)) * piece_size + center_y
        piece_index = grid[i]
        if piece_index < total_pieces:
            piece = scorpio_pieces[piece_index]
        else:
            piece = capricorn_pieces[piece_index - total_pieces]

        screen.blit(piece, (x, y))

        if correctly_placed[i]:
            pygame.draw.rect(screen, GRAY, (x, y, piece_size, piece_size), 3)

def check_correct_placement():
    for i in range(total_pieces * 2):
        if grid[i] == i:
            correctly_placed[i] = True
        else:
            correctly_placed[i] = False
    return all(correctly_placed)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = event.pos
            if center_x <= x < center_x + puzzle_size * piece_size and center_y <= y < center_y + pieces_per_row * piece_size:
                grid_x = (x - center_x) // piece_size
                grid_y = (y - center_y) // piece_size
                piece_index = grid_y * puzzle_size + grid_x
                if piece_index < len(grid):
                    dragging_piece = piece_index
        elif event.type == pygame.MOUSEBUTTONUP and dragging_piece is not None and not game_over:
            x, y = event.pos
            if center_x <= x < center_x + puzzle_size * piece_size and center_y <= y < center_y + pieces_per_row * piece_size:
                grid_x = (x - center_x) // piece_size
                grid_y = (y - center_y) // piece_size
                target_index = grid_y * puzzle_size + grid_x
                if target_index < len(grid):
                    # Swap pieces
                    grid[dragging_piece], grid[target_index] = grid[target_index], grid[dragging_piece]
                    dragging_piece = None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if check_correct_placement():
                game_over = True
                result_text = pygame.font.Font(None, 74).render("Congratulations!", True, BLACK)
            else:
                result_text = pygame.font.Font(None, 74).render("Incorrect", True, BLACK)
                retry_text = pygame.font.Font(None, 50).render("Try Again", True, BLACK)

    screen.fill(WHITE)

    # Increase vertical space between reference images and puzzle grid
    center_y = (HEIGHT - puzzle_size * piece_size) // 2 + 150  # Adjusted for more space

    # Draw reference images with increased space
    small_sign_size = 100  # Adjust the size of the smaller reference images
    screen.blit(pygame.transform.scale(scorpio_image, (small_sign_size, small_sign_size)), (center_x, 10))
    screen.blit(pygame.transform.scale(capricorn_image, (small_sign_size, small_sign_size)),
                (center_x + small_sign_size + 20, 10))

    draw_grid()

    if result_text:
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - result_text.get_height() // 2))
        if not game_over:
            screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + result_text.get_height()))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
