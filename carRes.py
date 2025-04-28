import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400  # 3:2 ratio
FPS = 60
CAR_WIDTH, CAR_HEIGHT = 40, 20
CAR_SPEED = 5 / FPS
ACCELERATION = CAR_SPEED / 30  # Half second to full speed
OBSTACLE_SIZE = 20
CIRCLE_RADIUS = 10

# Colors
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

# Game variables
car_x = 50
car_y = HEIGHT // 2
car_speed_y = 0
level = 1
score = 0
multiplier = 1.0
frames = 0
obstacles = []

# Font
font = pygame.font.SysFont(None, 36)

def draw_car(x, y):
    # Car body
    pygame.draw.rect(screen, RED, (x, y, CAR_WIDTH, CAR_HEIGHT))
    # Car roof
    pygame.draw.rect(screen, RED, (x + 10, y - 10, 20, 10))
    # Windows
    pygame.draw.rect(screen, BLUE, (x + 12, y - 8, 6, 6))
    pygame.draw.rect(screen, BLUE, (x + 22, y - 8, 6, 6))
    # Wheels
    pygame.draw.circle(screen, BLACK, (x + 10, y + CAR_HEIGHT), 5)
    pygame.draw.circle(screen, BLACK, (x + 30, y + CAR_HEIGHT), 5)
    # Taillight
    pygame.draw.rect(screen, YELLOW, (x - 5, y + 5, 5, 10))

def draw_obstacle(obstacle):
    if obstacle['type'] == 'X':
        x, y = obstacle['pos']
        pygame.draw.line(screen, RED, (x, y), (x + OBSTACLE_SIZE, y + OBSTACLE_SIZE), 3)
        pygame.draw.line(screen, RED, (x + OBSTACLE_SIZE, y), (x, y + OBSTACLE_SIZE), 3)
    elif obstacle['type'] == 'circle':
        x, y = obstacle['pos']
        pygame.draw.circle(screen, RED, (x, y), CIRCLE_RADIUS)

def spawn_obstacle():
    if level < 4:
        obstacle_type = 'X'
    else:
        obstacle_type = 'circle' if frames // 500 % 2 == 0 else 'X'
    
    y = random.randint(0, HEIGHT - OBSTACLE_SIZE)
    obstacles.append({'type': obstacle_type, 'pos': [WIDTH, y], 'offset': random.uniform(0, 2 * math.pi)})

def update_obstacles():
    global score, multiplier
    for obstacle in obstacles:
        if obstacle['type'] == 'circle':
            obstacle['pos'][1] += 50 * math.sin((obstacle['pos'][0] / 100) + obstacle['offset'])
        obstacle['pos'][0] -= level
        if obstacle['pos'][0] < -OBSTACLE_SIZE:
            obstacles.remove(obstacle)
        else:
            # Check for close dodge
            if (0 < obstacle['pos'][0] - car_x < 5) and (abs(obstacle['pos'][1] - car_y) < 30):
                score += 50
                multiplier += 0.1

def draw_interface():
    score_text = font.render(f'Score: {int(score)}', True, BLACK)
    level_text = font.render(f'Level: {level}', True, BLACK)
    multiplier_text = font.render(f'Multiplier: {multiplier:.1f}', True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    screen.blit(multiplier_text, (10, 70))

def main():
    global car_y, car_speed_y, level, score, multiplier, frames, obstacles
    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        screen.fill(SKY_BLUE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                # Restart the game
                car_y = HEIGHT // 2
                car_speed_y = 0
                level = 1
                score = 0
                multiplier = 1.0
                frames = 0
                obstacles = []
                game_over = False

        if not game_over:
            # Update car position
            mouse_y = pygame.mouse.get_pos()[1]
            if car_y < mouse_y:
                car_speed_y = min(car_speed_y + ACCELERATION, CAR_SPEED)
            elif car_y > mouse_y:
                car_speed_y = max(car_speed_y - ACCELERATION, -CAR_SPEED)
            car_y += car_speed_y

            # Update obstacles
            if frames % (500 // level) == 0:
                spawn_obstacle()
            update_obstacles()

            # Update score
            score += level * multiplier / FPS

            # Check for collisions
            for obstacle in obstacles:
                if obstacle['type'] == 'X':
                    if (car_x < obstacle['pos'][0] + OBSTACLE_SIZE and
                        car_x + CAR_WIDTH > obstacle['pos'][0] and
                        car_y < obstacle['pos'][1] + OBSTACLE_SIZE and
                        car_y + CAR_HEIGHT > obstacle['pos'][1]):
                        game_over = True
                elif obstacle['type'] == 'circle':
                    if math.hypot(car_x - obstacle['pos'][0], car_y - obstacle['pos'][1]) < CIRCLE_RADIUS + CAR_WIDTH / 2:
                        game_over = True

            # Level progression
            frames += 1
            if frames % 500 == 0:
                level += 1
                if level > 5:
                    game_over = True

            # Draw everything
            draw_car(car_x, car_y)
            for obstacle in obstacles:
                draw_obstacle(obstacle)
            draw_interface()

        else:
            # Display game over or win message
            if level > 5:
                message = "YOU WIN!"
            else:
                message = "GAME OVER"
            message_text = font.render(message, True, BLACK)
            final_score_text = font.render(f'Final Score: {int(score)}', True, BLACK)
            restart_text = font.render('Click to Restart', True, BLACK)
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()