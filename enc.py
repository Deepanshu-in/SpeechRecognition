
import pygame
import random

# Pygame initialize karna
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 600  # Window ka size
GRID_SIZE = 30  # Ek block ka size
COLUMNS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE  # Grid ke columns aur rows
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (128, 128, 128)  # Colors
COLORS = [(0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)]

# Tetromino shapes (alag-alag blocks ki shapes)
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

class Tetromino:
    """
    Tetromino class ek tetromino (block) ko represent karta hai.
    """
    def __init__(self, x, y):
        self.shape = random.choice(SHAPES)  # Random shape choose karna
        self.color = random.choice(COLORS)  # Random color choose karna
        self.x, self.y = x, y  # Block ka position

    def rotate(self):
        """
        Tetromino ko rotate karta hai.
        """
        rotated = [list(row) for row in zip(*self.shape[::-1])]
        self.shape = rotated

def draw_grid(surface):
    """
    Grid lines draw karta hai.
    """
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))

def check_collision(grid, tetromino, offset_x=0, offset_y=0):
    """
    Collision check karta hai ki block kisi doosre block ya boundary se takra raha hai ya nahi.
    """
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x, new_y = tetromino.x + x + offset_x, tetromino.y + y + offset_y
                if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or grid[new_y][new_x]:
                    return True
    return False

def merge_tetromino(grid, tetromino):
    """
    Tetromino ko grid me merge karta hai jab woh neeche gir jata hai.
    """
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[tetromino.y + y][tetromino.x + x] = tetromino.color

def clear_rows(grid):
    """
    Puri row clear karta hai agar woh completely bhari ho.
    """
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_grid)
    grid[:] = [[0] * COLUMNS] * lines_cleared + new_grid
    return lines_cleared

def draw_grid_content(surface, grid):
    """
    Grid ke andar stored blocks ko draw karta hai.
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, cell, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def main():
    """
    Main game loop ko handle karta hai.
    """
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    grid = [[0] * COLUMNS for _ in range(ROWS)]  # Empty grid create karna
    current_tetromino = Tetromino(COLUMNS // 2 - 1, 0)  # Naya Tetromino shuru karna
    score, fall_speed = 0, 500
    last_fall_time = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid(screen)
        draw_grid_content(screen, grid)

        # Current Tetromino ko draw karna
        for y, row in enumerate(current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, current_tetromino.color, 
                                     ((current_tetromino.x + x) * GRID_SIZE, (current_tetromino.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # User ke inputs ko handle karna
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  # Left move karna
                    if not check_collision(grid, current_tetromino, offset_x=-1):
                        current_tetromino.x -= 1
                elif event.key == pygame.K_RIGHT:  # Right move karna
                    if not check_collision(grid, current_tetromino, offset_x=1):
                        current_tetromino.x += 1
                elif event.key == pygame.K_UP:  # Rotate karna
                    original_shape = current_tetromino.shape[:]
                    current_tetromino.rotate()
                    if check_collision(grid, current_tetromino):
                        current_tetromino.shape = original_shape  # Agar collision ho toh undo karna
                elif event.key == pygame.K_DOWN:  # Fast drop
                    while not check_collision(grid, current_tetromino, offset_y=1):
                        current_tetromino.y += 1

        # Tetromino neeche girta rahega
        current_time = pygame.time.get_ticks()
        if current_time - last_fall_time >= fall_speed:
            if not check_collision(grid, current_tetromino, offset_y=1):
                current_tetromino.y += 1
            else:
                merge_tetromino(grid, current_tetromino)
                score += clear_rows(grid) * 10
                current_tetromino = Tetromino(COLUMNS // 2 - 1, 0)
                if check_collision(grid, current_tetromino):  # Game over check
                    running = False
            last_fall_time = current_time

        pygame.display.flip()
        clock.tick(30)

    print(f"Game Over! Final Score: {score}")
    pygame.quit()

if __name__ == "__main__":
    main()