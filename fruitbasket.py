import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Sorting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (184, 115, 51)
DARK_BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
STEM_COLOR = (101, 67, 33)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)

# Font setup
font = pygame.font.Font(None, 24)

# Basket properties
basket = pygame.Rect(WIDTH // 2, HEIGHT - 50, 60, 40)
basket_speed = 5  
basket_types = ["cherry", "banana", "berry"]
basket_index = 0  
basket_change_cooldown = 0  

# Fruit properties
fruit = None
fruit_speed = 2
spawn_timer = 0
fruit_types = ["cherry", "banana", "berry", "bomb"]
score = 0
lives = 5
game_over = False
running = True
clock = pygame.time.Clock()

# Function to draw an cherry
def draw_cherry(surface, position, size):
    x, y = position
    points = []
    for i in range(360):
        angle = math.radians(i)
        radius = size + 6 * math.sin(2 * angle)
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))

    pygame.draw.polygon(surface, RED, points)
    pygame.draw.line(surface, STEM_COLOR, (x, y - size), (x + 5, y - size - 20), 5)
    pygame.draw.ellipse(surface, GREEN, pygame.Rect(x + 5, y - size - 20, 20, 10))

# Function to draw a detailed banana
def draw_detailed_banana(surface, position):
    x, y = position
    banana_points = [
        (x, y + 20),  
        (x + 50, y - 20),  
        (x + 45, y),  
        (x + 30, y + 20),  
        (x + 10, y + 30), 
    ]

    pygame.draw.polygon(surface, YELLOW, banana_points)

    # Left tip
    pygame.draw.polygon(surface, BROWN, [
        (x - 5, y + 20),
        (x, y + 30),
        (x + 5, y + 25),
        (x, y + 15)
    ])

    # Right tip
    pygame.draw.polygon(surface, BROWN, [
        (x + 45, y - 25),
        (x + 55, y - 20),
        (x + 50, y - 15),
        (x + 40, y - 20)
    ])

# Function to draw a berry
def draw_berry(surface, position, size):
    x, y = position
    pygame.draw.ellipse(surface, PINK, pygame.Rect(x - size, y - size, 2 * size, 2.5 * size))
    
    # Draw leaves
    for i in range(3):
        leaf_x = x - size + (i * (size // 1.5))
        leaf_y = y - size - 5
        pygame.draw.ellipse(surface, GREEN, pygame.Rect(leaf_x, leaf_y, size // 1.5, size // 2))

# Function to draw a bomb
def draw_bomb(surface, x, y):
    # Bomb body
    pygame.draw.circle(surface, BLACK, (x, y), 30)

    # Fuse base
    pygame.draw.rect(surface, BLACK, (x - 10, y - 50, 20, 15))

    # Fuse wire (curved)
    fuse_points = [(x, y - 50)]
    for i in range(10):
        angle = math.pi * i / 10
        fuse_x = x + int(30 * math.sin(angle))
        fuse_y = y - 50 - int(20 * i / 10)
        fuse_points.append((fuse_x, fuse_y))
    pygame.draw.lines(surface, BLACK, False, fuse_points, 4)

    # Explosion effect at the tip
    explosion_center = fuse_points[-1]
    explosion_points = [
        (explosion_center[0], explosion_center[1] - 10),
        (explosion_center[0] + 5, explosion_center[1] - 5),
        (explosion_center[0] + 10, explosion_center[1] - 10),
        (explosion_center[0] + 7, explosion_center[1] + 2),
        (explosion_center[0] + 15, explosion_center[1] + 5),
        (explosion_center[0] + 2, explosion_center[1] + 7),
        (explosion_center[0], explosion_center[1] + 15),
        (explosion_center[0] - 2, explosion_center[1] + 7),
        (explosion_center[0] - 15, explosion_center[1] + 5),
        (explosion_center[0] - 7, explosion_center[1] + 2),
        (explosion_center[0] - 10, explosion_center[1] - 10),
        (explosion_center[0] - 5, explosion_center[1] - 5),
    ]
    pygame.draw.polygon(surface, ORANGE, explosion_points)
    pygame.draw.polygon(surface, YELLOW, explosion_points, 2)


# Main game loop
while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 2)  # Draw game boundary

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit game

    if not game_over:
        keys = pygame.key.get_pressed()

        # Move basket left and right
        if keys[pygame.K_LEFT] and basket.x > 40:
            basket.x -= basket_speed
        if keys[pygame.K_RIGHT] and basket.x < WIDTH - basket.width - 3:
            basket.x += basket_speed

        # Handle basket type change with cooldown
        if basket_change_cooldown > 0:
            basket_change_cooldown -= 1
        if keys[pygame.K_UP] and basket_change_cooldown == 0:
            basket_index = (basket_index - 1) % len(basket_types)
            basket_change_cooldown = 10  
        if keys[pygame.K_DOWN] and basket_change_cooldown == 0:
            basket_index = (basket_index + 1) % len(basket_types)
            basket_change_cooldown = 10  

        basket_type = basket_types[basket_index]  # Current basket type

        # Spawn new fruit if none exists
        if fruit is None and spawn_timer == 0:
            fruit_x = random.randint(0, WIDTH - 20)
            fruit_type = random.choices(fruit_types, weights=[3, 3, 3, 2])[0]  # Adjusted bomb frequency
            fruit_speed = random.randint(2, 5)
            fruit = {"rect": pygame.Rect(fruit_x, 0, 20, 20), "type": fruit_type}
            spawn_timer = 60  # Delay next spawn
        elif spawn_timer > 0:
            spawn_timer -= 1

        if fruit:
            fruit["rect"].y += fruit_speed  # Move fruit downward

            # Check for collision with the basket
            if fruit["rect"].y > HEIGHT - 50 and basket.colliderect(fruit["rect"]):
                if fruit["type"] == "bomb":
                    game_over = True  # Game ends if bomb is caught
                elif fruit["type"] == basket_type:
                    score += 10  # Correct fruit caught
                else:
                    lives -= 1  # Wrong fruit caught
                fruit = None  

            # Remove missed fruit
            elif fruit["rect"].y > HEIGHT:
                if fruit["type"] != "bomb":
                    lives -= 1
                fruit = None  

        # Draw the basket
        pygame.draw.rect(screen, BROWN, (basket.x - 30, basket.y, 80, 40), border_radius=15)
        pygame.draw.rect(screen, DARK_BROWN, (basket.x - 40, basket.y - 10, 100, 20), border_radius=10)

        # Display basket type
        basket_label = font.render(f"{basket_type.capitalize()}", True, BLACK)
        screen.blit(basket_label, (basket.x - 25, basket.y + 15))

        # Draw falling fruit or bomb
        if fruit:
            if fruit["type"] == "cherry":
                draw_cherry(screen, (fruit["rect"].x + 10, fruit["rect"].y + 10), 10)
            elif fruit["type"] == "banana":
                draw_detailed_banana(screen, (fruit["rect"].x, fruit["rect"].y))
            elif fruit["type"] == "berry":
                draw_berry(screen, (fruit["rect"].x + 10, fruit["rect"].y + 10), 10)
            else:
                draw_bomb(screen, fruit["rect"].x + 10, fruit["rect"].y + 10)

        # Display score and lives
        score_text = font.render(f"Score: {score}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 30))

    # Check game over conditions
    if lives <= 0:
        game_over = True
        game_over_reason = "Game Over! No Lives Left"
    elif game_over:
        game_over_reason = "Game Over! Bomb in the Basket"

    if game_over:
        screen.fill(WHITE)
        game_over_text = font.render(game_over_reason, True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

    pygame.display.flip()
    clock.tick(30)  # Control frame rate

pygame.quit()  # Exit game