import pygame
import sys
import math
import random

pygame.init()

width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Basketball Game")

ORANGE = (255, 140, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (240, 240, 240)
RED = (255, 0, 0)
GRAY = (120, 120, 120)
COURT_BROWN = (205, 133, 63)
COURT_LINES = (255, 215, 0)

def draw_basketball(surface, center, radius):
    pygame.draw.circle(surface, ORANGE, center, radius)
    pygame.draw.circle(surface, BLACK, center, radius, 3)  
    
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius/3, radius*2, radius/1.5), 0, 3.14, 3)
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius/6, radius*2, radius/3), 3.14, 6.28, 3)
    
    pygame.draw.arc(surface, BLACK, (center[0] - radius/3, center[1] - radius, radius/1.5, radius*2), 1.57, 4.71, 3)
    pygame.draw.arc(surface, BLACK, (center[0] - radius/6, center[1] - radius, radius/3, radius*2), 4.71, 7.85, 3)
    
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius, radius*2, radius*2), 0.785, 2.356, 3)
    pygame.draw.arc(surface, BLACK, (center[0] - radius, center[1] - radius, radius*2, radius*2), 3.927, 5.498, 3)

def draw_basketball_hoop(surface, x, y, width, height):
    backboard_width = width
    backboard_height = height * 2

    pygame.draw.rect(surface, WHITE, (x, y - backboard_height + height, backboard_width, backboard_height))
    pygame.draw.rect(surface, BLACK, (x, y - backboard_height + height, backboard_width, backboard_height), 2)
    
    rim_width = width * 0.8
    rim_height = height * 0.4
    rim_x = x + (width - rim_width) / 2
    rim_y = y + height * 0.6
    pygame.draw.ellipse(surface, RED, (rim_x, rim_y, rim_width, rim_height))
    pygame.draw.ellipse(surface, BLACK, (rim_x, rim_y, rim_width, rim_height), 2)
    
    net_segments = 8
    net_length = height * 1.5
    segment_width = rim_width / net_segments
    
    for i in range(net_segments + 1):
        start_x = rim_x + i * segment_width
        end_x = rim_x + (rim_width / 2) + (i - net_segments / 2) * (segment_width * 0.7)
        pygame.draw.line(surface, BLACK, (start_x, rim_y + rim_height / 2), 
                         (end_x, rim_y + rim_height / 2 + net_length), 1)
    
    for j in range(3):
        y_pos = rim_y + rim_height / 2 + (j + 1) * (net_length / 4)
        curve_factor = (j + 1) / 4 
        for i in range(net_segments):
            start_x = rim_x + i * segment_width
            end_x = rim_x + (i + 1) * segment_width
            
            mid_y_offset = curve_factor * 5 * math.sin(math.pi * (i + 0.5) / net_segments)
            
            pygame.draw.line(surface, BLACK, 
                            (start_x, y_pos + (0 if i == 0 else mid_y_offset)), 
                            (end_x, y_pos + (0 if i == net_segments-1 else mid_y_offset)), 1)

def draw_basketball_court(surface):
    pygame.draw.rect(surface, COURT_BROWN, (0, 0, width, height))
    
    pygame.draw.circle(surface, COURT_LINES, (width // 2, height // 2), 50, 2)
    pygame.draw.circle(surface, COURT_LINES, (width // 2, height // 2), 10, 2)
    
    pygame.draw.line(surface, COURT_LINES, (50, 100), (width - 50, 100), 2)
    pygame.draw.line(surface, COURT_LINES, (50, height - 100), (width - 50, height - 100), 2)
    
    pygame.draw.arc(surface, COURT_LINES, (width // 2 - 125, height - 250, 250, 250), math.pi, 2 * math.pi, 2)
    
    pygame.draw.rect(surface, COURT_LINES, (25, 25, width - 50, height - 50), 3)
    
    for i in range(0, height, 20):
        line_color = (190, 120, 50) if i % 40 == 0 else (180, 110, 45)
        pygame.draw.line(surface, line_color, (0, i), (width, i), 1)

class Crowd:
    def __init__(self):
        self.people = []
        self.colors = [
            (255, 0, 0), (0, 0, 255), (0, 255, 0), 
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (200, 150, 150), (150, 200, 150), (150, 150, 200)
        ]
        
        for i in range(30):
            x = random.randint(10, width - 10)
            y = random.randint(5, 20)
            color = random.choice(self.colors)
            self.people.append((x, y, color))
            
        for i in range(40):
            x = random.randint(10, width - 10)
            y = random.randint(height - 20, height - 5)
            color = random.choice(self.colors)
            self.people.append((x, y, color))
    
    def draw(self, surface):
        for person in self.people:
            x, y, color = person
            pygame.draw.circle(surface, color, (x, y), 5)
    
    def cheer(self, surface):
        for i, person in enumerate(self.people):
            x, y, color = person
            if random.random() > 0.7:
                y_offset = random.randint(-3, 3)
                pygame.draw.circle(surface, color, (x, y + y_offset), 5)
            else:
                pygame.draw.circle(surface, color, (x, y), 5)

def draw_game_over_screen(surface, score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  
    surface.blit(overlay, (0, 0))
    
    large_font = pygame.font.SysFont(None, 72)
    game_over_text = large_font.render("GAME OVER", True, RED)
    surface.blit(game_over_text, (width//2 - game_over_text.get_width()//2, height//2 - 60))
    
    medium_font = pygame.font.SysFont(None, 48)
    score_text = medium_font.render(f"Final Score: {score}", True, WHITE)
    surface.blit(score_text, (width//2 - score_text.get_width()//2, height//2))
    
    small_font = pygame.font.SysFont(None, 36)
    restart_text = small_font.render("Press SPACE to restart", True, WHITE)
    surface.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 60))

def main():
    def reset_game():
        nonlocal ball_x, ball_y, ball_y_ground, is_jumping, jump_velocity
        nonlocal target_x, target_direction, score, score_changed
        nonlocal message, message_timer, lives, game_state
        
        ball_x = width // 2
        ball_y = ball_y_ground
        is_jumping = False
        jump_velocity = 0
        
        target_x = width // 2 - target_width // 2
        target_direction = 1
        
        score = 0
        lives = 3
        score_changed = False
        message = ""
        message_timer = 0
        game_state = "playing"
    
    clock = pygame.time.Clock()
    
    ball_radius = 30
    ball_x = width // 2
    ball_y_ground = height - ball_radius - 10 
    ball_y = ball_y_ground
    ball_speed = 5
    
    is_jumping = False
    jump_velocity = 0
    jump_power = 20
    gravity = 0.5
    
    target_width = 80
    target_height = 20
    target_x = width // 2 - target_width // 2
    target_y = 30
    target_speed = 2
    target_direction = 1 
    
    score = 0
    lives = 3
    score_changed = False
    message = ""
    message_timer = 0
    
    crowd = Crowd()
    
    scored_recently = False
    cheer_timer = 0
    game_state = "playing"  
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "playing" and not is_jumping:
                        is_jumping = True
                        jump_velocity = -jump_power
                        score_changed = False  
                    elif game_state == "game_over":
                        reset_game()
        
        if game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and ball_x - ball_speed >= ball_radius:
                ball_x -= ball_speed
            if keys[pygame.K_RIGHT] and ball_x + ball_speed <= width - ball_radius:
                ball_x += ball_speed
            
            if is_jumping:
                ball_y += jump_velocity
                jump_velocity += gravity
                
                if ball_y >= ball_y_ground:
                    ball_y = ball_y_ground
                    is_jumping = False
                    jump_velocity = 0
                    
                    if not score_changed:
                        lives -= 1
                        if lives <= 0:
                            game_state = "game_over"
                        else:
                            message = f"Miss! {lives} lives left"
                            message_timer = 60 
            
            target_x += target_speed * target_direction
            
            if target_x <= 0 or target_x + target_width >= width:
                target_direction *= -1
            
            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
            rim_width = target_width * 0.8
            rim_height = target_height * 0.4
            rim_x = target_x + (target_width - rim_width) / 2
            rim_y = target_y + target_height * 0.6
            target_rect = pygame.Rect(rim_x, rim_y, rim_width, rim_height)
            
            if ball_rect.colliderect(target_rect) and not score_changed and is_jumping:
                score += 10  
                score_changed = True
                message = "Score! +10 points"
                message_timer = 60  
                scored_recently = True
                cheer_timer = 30  
        
        draw_basketball_court(screen)
        
        draw_basketball_hoop(screen, target_x, target_y, target_width, target_height)
        
        draw_basketball(screen, (ball_x, ball_y), ball_radius)
        
        if cheer_timer > 0:
            crowd.cheer(screen)
            cheer_timer -= 1
        else:
            crowd.draw(screen)
        
        font = pygame.font.SysFont(None, 36)
        
        pygame.draw.rect(screen, BLACK, (10, 10, 150, 80))
        
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (20, 55))
        
        if message_timer > 0:
            message_color = (0, 255, 0) if "Score" in message else (255, 0, 0)
            message_text = font.render(message, True, message_color)
            message_bg = pygame.Rect(width//2 - message_text.get_width()//2 - 10, 60, 
                                    message_text.get_width() + 20, 40)
            pygame.draw.rect(screen, BLACK, message_bg)
            screen.blit(message_text, (width//2 - message_text.get_width()//2, 70))
            message_timer -= 1
        
        small_font = pygame.font.SysFont(None, 24)
        instructions_bg = pygame.Rect(0, height - 40, width, 60)
        pygame.draw.rect(screen, BLACK, instructions_bg, 0)
        instructions1 = small_font.render("Use LEFT and RIGHT arrow keys to move", True, WHITE)
        instructions2 = small_font.render("Press SPACE to jump and try to hit the target", True, WHITE)
        screen.blit(instructions1, (width//2 - instructions1.get_width()//2, height - 35))
        screen.blit(instructions2, (width//2 - instructions2.get_width()//2, height - 15))
        
        if game_state == "game_over":
            draw_game_over_screen(screen, score)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()