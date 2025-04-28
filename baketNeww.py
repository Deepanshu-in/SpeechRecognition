import pygame
import sys
import math
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ping Pong")

# Colors
ORANGE = (255, 140, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (240, 240, 240)
RED = (255, 0, 0)
COURT_RED = (207, 83, 45)  # Darker red-orange for the court
COURT_RED_LIGHT = (224, 105, 49)  # Lighter red-orange for the court
COURT_BORDER = (136, 47, 26)  # Darker border
LINE_COLOR = (255, 255, 255)  # White lines

# Function to draw basketball 
def draw_basketball(surface, center, radius):
    # Main orange ball with gradient effect
    for r in range(radius, 0, -1):
        intensity = 255 - int((radius - r) * 40 / radius)  # Creates darker orange toward center
        color = (255, max(110, intensity), 0)
        pygame.draw.circle(surface, color, center, r)
    
    # Black outlines
    pygame.draw.circle(surface, BLACK, center, radius, 2)  
    
    # Horizontal lines 
    rect_h = pygame.Rect(center[0] - radius, center[1] - radius/4, radius*2, radius/2)
    pygame.draw.arc(surface, BLACK, rect_h, 0, math.pi, 2)
    pygame.draw.arc(surface, BLACK, rect_h, math.pi, 2*math.pi, 2)
    
    # Vertical lines 
    rect_v = pygame.Rect(center[0] - radius/4, center[1] - radius, radius/2, radius*2)
    pygame.draw.arc(surface, BLACK, rect_v, math.pi/2, 3*math.pi/2, 2)
    pygame.draw.arc(surface, BLACK, rect_v, 3*math.pi/2, 5*math.pi/2, 2)
    
    # Diagonal lines
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius, radius*2, radius*2), math.pi/4, 5*math.pi/4, 2)
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius, radius*2, radius*2), 5*math.pi/4, 9*math.pi/4, 2)
    
    # Add texture dots 
    for _ in range(50):
        angle = random.uniform(0, 2 * math.pi)
        dot_distance = random.uniform(0, radius * 0.8)  # Keep dots within ball
        dot_x = center[0] + math.cos(angle) * dot_distance
        dot_y = center[1] + math.sin(angle) * dot_distance
        dot_size = random.randint(1, 2)
        dot_color = (200, 100, 0)  # Slightly darker orange
        pygame.draw.circle(surface, dot_color, (int(dot_x), int(dot_y)), dot_size)
        

# Function to draw basketball court based on the provided image
def draw_basketball_court(surface):
    # Draw court background with two-tone diagonal
    pygame.draw.rect(surface, COURT_BORDER, (0, 0, width, height))
    pygame.draw.rect(surface, COURT_RED, (20, 20, width - 40, height - 40))
    
    # Draw diagonal light area
    points = [(width - 40, 20), (width - 40, height - 40), (20, height - 40)]
    pygame.draw.polygon(surface, COURT_RED_LIGHT, points)
    
    # Draw court outline
    pygame.draw.rect(surface, LINE_COLOR, (50, 50, width - 100, height - 100), 3)
    
    # Draw center line
    pygame.draw.line(surface, LINE_COLOR, (width // 2, 50), (width // 2, height - 50), 3)
    
    # Draw center circle
    pygame.draw.circle(surface, LINE_COLOR, (width // 2, height // 2), 60, 3)
    
    # Draw the key areas 
    key_width = 150
    key_height = 190
    pygame.draw.rect(surface, LINE_COLOR, (50, height // 2 - key_height // 2, key_width, key_height), 3)
    pygame.draw.circle(surface, LINE_COLOR, (50 + key_width, height // 2), 60, 3, False, True, False, False)
    pygame.draw.rect(surface, LINE_COLOR, (width - 50 - key_width, height // 2 - key_height // 2, key_width, key_height), 3)
    pygame.draw.circle(surface, LINE_COLOR, (width - 50 - key_width, height // 2), 60, 3, False, False, False, True)
    pygame.draw.line(surface, LINE_COLOR, (50 + key_width, height // 2 - key_height // 2), 
                    (50 + key_width, height // 2 + key_height // 2), 3)
    pygame.draw.line(surface, LINE_COLOR, (width - 50 - key_width, height // 2 - key_height // 2), 
                    (width - 50 - key_width, height // 2 + key_height // 2), 3)
    line_mark_width = 10
    pygame.draw.line(surface, LINE_COLOR, (width // 2 - line_mark_width, 50), 
                    (width // 2 + line_mark_width, 50), 3)
    pygame.draw.line(surface, LINE_COLOR, (width // 2 - line_mark_width, height - 50), 
                    (width // 2 + line_mark_width, height - 50), 3)
    
    # Draw small sideline marks
    pygame.draw.line(surface, LINE_COLOR, (50, height // 2 - line_mark_width), 
                    (50, height // 2 + line_mark_width), 3)
    pygame.draw.line(surface, LINE_COLOR, (width - 50, height // 2 - line_mark_width), 
                    (width - 50, height // 2 + line_mark_width), 3)

def draw_paddle(surface, x, y, width, height, color):
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)

def draw_score(surface, left_score, right_score):
    font = pygame.font.SysFont(None, 72)
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    
    # Draw score in the key areas
    surface.blit(left_text, (100, height // 2 - 20))
    surface.blit(right_text, (width - 120, height // 2 - 20))

def draw_game_over_screen(surface, left_score, right_score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  
    surface.blit(overlay, (0, 0))
    
    large_font = pygame.font.SysFont(None, 72)
    game_over_text = large_font.render("GAME OVER", True, RED)
    surface.blit(game_over_text, (width//2 - game_over_text.get_width()//2, height//2 - 100))
    
    if left_score > right_score:
        winner_text = large_font.render("Left Player Wins!", True, WHITE)
    else:
        winner_text = large_font.render("Right Player Wins!", True, WHITE)
    surface.blit(winner_text, (width//2 - winner_text.get_width()//2, height//2 - 30))
    
    medium_font = pygame.font.SysFont(None, 48)
    score_text = medium_font.render(f"Final Score: {left_score} - {right_score}", True, WHITE)
    surface.blit(score_text, (width//2 - score_text.get_width()//2, height//2 + 40))
    
    small_font = pygame.font.SysFont(None, 36)
    restart_text = small_font.render("Press SPACE to restart", True, WHITE)
    surface.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 100))

def main():
    clock = pygame.time.Clock()
    
    # Ball properties
    ball_radius = 20
    ball_x = width // 2
    ball_y = height // 2
    ball_speed_x = 5 * random.choice([-1, 1])
    ball_speed_y = 5 * random.choice([-1, 1])
    
    # Paddle properties
    paddle_width = 15
    paddle_height = 100
    paddle_speed = 7
    
    left_paddle_x = 70  # Moved in to avoid overlapping court lines
    left_paddle_y = height // 2 - paddle_height // 2
    
    right_paddle_x = width - 70 - paddle_width  # Moved in to avoid overlapping court lines
    right_paddle_y = height // 2 - paddle_height // 2
    
    # Score
    left_score = 0
    right_score = 0
    
    game_state = "playing"
    max_score = 5
    
    def reset_ball():
        nonlocal ball_x, ball_y, ball_speed_x, ball_speed_y
        ball_x = width // 2
        ball_y = height // 2
        ball_speed_x = 5 * random.choice([-1, 1])
        ball_speed_y = 5 * random.choice([-1, 1])
    
    def reset_game():
        nonlocal left_score, right_score, game_state, left_paddle_y, right_paddle_y
        left_score = 0
        right_score = 0
        game_state = "playing"
        left_paddle_y = height // 2 - paddle_height // 2
        right_paddle_y = height // 2 - paddle_height // 2
        reset_ball()
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == "game_over":
                    reset_game()
        
        if game_state == "playing":
            keys = pygame.key.get_pressed()
            
            # Left paddle movement
            if keys[pygame.K_w] and left_paddle_y > 55:
                left_paddle_y -= paddle_speed
            if keys[pygame.K_s] and left_paddle_y < height - paddle_height - 55:
                left_paddle_y += paddle_speed
            
            # Right paddle movement
            if keys[pygame.K_UP] and right_paddle_y > 55:
                right_paddle_y -= paddle_speed
            if keys[pygame.K_DOWN] and right_paddle_y < height - paddle_height - 55:
                right_paddle_y += paddle_speed
            
            ball_x += ball_speed_x
            ball_y += ball_speed_y
            
            # Ball collision with top and bottom walls
            if ball_y <= ball_radius + 50 or ball_y >= height - ball_radius - 50:
                ball_speed_y *= -1
                ball_speed_y += random.uniform(-0.5, 0.5)  # Add slight randomness
            
            # Ball collision with paddles
            left_paddle_rect = pygame.Rect(left_paddle_x, left_paddle_y, paddle_width, paddle_height)
            right_paddle_rect = pygame.Rect(right_paddle_x, right_paddle_y, paddle_width, paddle_height)
            
            if left_paddle_rect.collidepoint(ball_x - ball_radius, ball_y):
                ball_speed_x = abs(ball_speed_x) * 1.05  # Speed up slightly
                ball_speed_y += random.uniform(-1, 1)  # Add some randomness
            
            if right_paddle_rect.collidepoint(ball_x + ball_radius, ball_y):
                ball_speed_x = -abs(ball_speed_x) * 1.05  # Speed up slightly
                ball_speed_y += random.uniform(-1, 1)  # Add some randomness
            
            # Scoring 
            if ball_x < 50:
                right_score += 1
                reset_ball()
            
            if ball_x > width - 50:
                left_score += 1
                reset_ball()
            
            # Check for game over
            if left_score >= max_score or right_score >= max_score:
                game_state = "game_over"
        
        draw_basketball_court(screen)
        draw_paddle(screen, left_paddle_x, left_paddle_y, paddle_width, paddle_height, WHITE)
        draw_paddle(screen, right_paddle_x, right_paddle_y, paddle_width, paddle_height, WHITE)
        draw_basketball(screen, (ball_x, ball_y), ball_radius)
        draw_score(screen, left_score, right_score)
        
        # Draw instructions
        small_font = pygame.font.SysFont(None, 24)
        instructions_bg = pygame.Rect(width//2 - 250, height - 40, 500, 30)
        pygame.draw.rect(screen, BLACK, instructions_bg, 0)
        instructions = small_font.render("Left player: W/S keys | Right player: UP/DOWN arrow keys", True, WHITE)
        screen.blit(instructions, (width//2 - instructions.get_width()//2, height - 30))
        
        if game_state == "game_over":
            draw_game_over_screen(screen, left_score, right_score)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()