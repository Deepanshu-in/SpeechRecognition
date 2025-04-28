import pygame
import random

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 400, 600
LANE_WIDTH = WIDTH // 4
CAR_WIDTH, CAR_HEIGHT = 60, 100
ROAD_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)
SILVER = (192, 192, 192)

# Traffic car colors
TRAFFIC_CAR_COLORS = [YELLOW, CYAN, ORANGE, GREEN, PURPLE, BROWN, SILVER]

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Dodge Game")

# Load Fonts
font = pygame.font.Font(None, 36)

# Player Car
player_x = (WIDTH // 2) - (CAR_WIDTH // 2)
player_y = HEIGHT - CAR_HEIGHT - 10
player_speed = 5
player_acceleration = 0

# Traffic Cars
traffic_cars = []
difficulty = 30  # Spawn rate control
score = 0

def draw_car(x, y, color):
    pygame.draw.rect(screen, color, (x, y, CAR_WIDTH, CAR_HEIGHT))  # Body
    pygame.draw.rect(screen, BLUE, (x + 10, y + 10, 40, 30))  # Windshield
    pygame.draw.rect(screen, YELLOW, (x + 10, y + CAR_HEIGHT - 20, 40, 10))  # Headlights
    pygame.draw.circle(screen, BLACK, (x + 10, y + 80), 10)  # Left Tire
    pygame.draw.circle(screen, BLACK, (x + 50, y + 80), 10)  # Right Tire

def draw_lane():
    screen.fill(GREEN)  # Grass
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))  # Road
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (LANE_WIDTH - 5, i + lane_offset, 10, 20))
        pygame.draw.rect(screen, WHITE, (2 * LANE_WIDTH - 5, i + lane_offset, 10, 20))
        pygame.draw.rect(screen, WHITE, (3 * LANE_WIDTH - 5, i + lane_offset, 10, 20))
    pygame.draw.rect(screen, WHITE, (0, 0, 5, HEIGHT))  # Left Border
    pygame.draw.rect(screen, WHITE, (WIDTH - 5, 0, 5, HEIGHT))  # Right Border

def move_traffic():
    global score, difficulty
    for car in traffic_cars:
        car[1] += car[2]
        if car[1] > HEIGHT:
            traffic_cars.remove(car)
            score += 10
            if score % 50 == 0:
                difficulty = max(10, difficulty - 5)

# Game Loop
running = True
clock = pygame.time.Clock()
lane_offset = 0
game_over = False
while running:
    screen.fill(GREEN)
    draw_lane()
    
    if not game_over:
        player_y += player_acceleration
        player_y = max(HEIGHT - CAR_HEIGHT - 10, min(player_y, HEIGHT - CAR_HEIGHT - 30))
        draw_car(player_x, player_y, RED)
        move_traffic()
        
        if random.randint(1, difficulty) == 1:
            lane = random.choice([0, 1, 2, 3])
            traffic_cars.append([lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2, -CAR_HEIGHT, random.randint(3, 7), random.choice(TRAFFIC_CAR_COLORS)])
        
        for car in traffic_cars:
            draw_car(car[0], car[1], car[3])
            if player_x < car[0] + CAR_WIDTH and player_x + CAR_WIDTH > car[0] and player_y < car[1] + CAR_HEIGHT and player_y + CAR_HEIGHT > car[1]:
                game_over = True
    
    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if game_over:
        game_over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - 140, HEIGHT//2))
    
    pygame.display.flip()
    clock.tick(30)
    lane_offset = (lane_offset + ROAD_SPEED) % 40
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and player_x > 5:
                player_x -= LANE_WIDTH
            if event.key == pygame.K_RIGHT and player_x < WIDTH - CAR_WIDTH - 5:
                player_x += LANE_WIDTH
            if event.key == pygame.K_UP:
                player_acceleration = -2
            if event.key == pygame.K_r and game_over:
                traffic_cars.clear()
                score = 0
                difficulty = 30
                game_over = False
                player_x = (WIDTH // 2) - (CAR_WIDTH // 2)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_acceleration = 0

pygame.quit()