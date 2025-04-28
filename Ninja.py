import pygame
import random
import math
import sys
import os
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
ICE_BLUE = (150, 210, 255)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()
FPS = 60
score = 0
high_score = 0
lives = 3
game_over = False
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 64)
show_instructions = True
instruction_timer = 5 * FPS
slow_mode = False
slow_mode_timer = 0
freeze_mode = False
freeze_mode_timer = 0
double_points_mode = False
double_points_timer = 0
fruit_counter = 0

high_score_file = "highscore.txt"

def load_high_score():
    if os.path.exists(high_score_file):
        try:
            with open(high_score_file, 'r') as file:
                return int(file.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    with open(high_score_file, 'w') as file:
        file.write(str(score))

high_score = load_high_score()

def draw_background():
    for y in range(HEIGHT):
        gradient_factor = y / HEIGHT
        blue_value = max(0, int(80 * (1 - gradient_factor)))
        pygame.draw.line(window, (0, 0, blue_value), (0, y), (WIDTH, y))

class Fruit:
    def __init__(self):
        self.reset()
        
    def reset(self):
        global fruit_counter
        fruit_counter += 1
        
        self.radius = random.randint(25, 45)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(2, 3.5)
        self.gravity = 0.1
        self.rotation = random.uniform(0, 2*math.pi)
        self.rotate_speed = random.uniform(-0.02, 0.02)
        self.sliced = False
        self.remove = False
        self.slice_angle = random.uniform(0, math.pi)
        self.slice_offset = random.randint(-10, 10)
        
        if fruit_counter % 30 == 0:
            self.fruit_type = 'double_points_star'
            self.is_special = True
            self.special_effect = 'double_points'
            self.color = YELLOW
            self.highlight_color = (255, 255, 200)
            self.points = 20
            self.star_points = []
            self.glow_size = 0
            self.glow_direction = 1
        elif fruit_counter % 25 == 0:
            self.fruit_type = 'snowflake'
            self.is_special = True
            self.special_effect = 'freeze'
            self.color = (200, 230, 255)
            self.highlight_color = (240, 248, 255)
            self.points = 15
            self.sparkle_points = []
        elif fruit_counter % 20 == 0:
            self.fruit_type = 'blueberry'
            self.is_special = True
            self.special_effect = 'slow'
            self.color = (65, 105, 225)
            self.highlight_color = (135, 206, 250)
            self.points = 10
        elif random.random() < 0.07:
            self.fruit_type = 'golden_apple'
            self.is_special = True
            self.special_effect = 'bonus'
            self.color = GOLD
            self.highlight_color = (255, 240, 150)
            self.stem_color = (139, 69, 19)
            self.points = 25
            self.glow_size = 0
            self.glow_direction = 1
        else:
            self.fruit_type = random.choice(['apple', 'orange'])
            self.is_special = False
            self.special_effect = None
            
            if self.fruit_type == 'apple':
                self.color = (220, 0, 0)
                self.highlight_color = (255, 180, 180)
                self.stem_color = (101, 67, 33)
            else:
                self.color = (255, 140, 0)
                self.highlight_color = (255, 200, 160)
                self.texture_color = (255, 160, 0)
            self.points = 10
        
    def update(self):
        global lives, game_over, slow_mode, slow_mode_timer, freeze_mode, freeze_mode_timer, double_points_mode, double_points_timer
        
        if freeze_mode:
            return
            
        speed_multiplier = 0.5 if slow_mode else 1.0
        
        if not self.sliced:
            self.x += self.speed_x * speed_multiplier
            self.y += self.speed_y * speed_multiplier
            self.speed_y += self.gravity * speed_multiplier
            
            if self.fruit_type in ['golden_apple', 'double_points_star']:
                self.glow_size += 0.2 * self.glow_direction
                if self.glow_size > 5: self.glow_direction = -1
                elif self.glow_size < 0: self.glow_direction = 1
            
            if self.y > HEIGHT + self.radius:
                if not game_over and self.fruit_type not in ['snowflake', 'blueberry', 'golden_apple', 'double_points_star']:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                self.remove = True
        else:
            self.x += self.speed_x * speed_multiplier
            self.y += self.speed_y * speed_multiplier
            self.speed_y += self.gravity * speed_multiplier
            
            if self.is_special and not self.remove:
                if self.special_effect == 'slow' and not slow_mode:
                    slow_mode = True
                    slow_mode_timer = 5 * FPS
                elif self.special_effect == 'freeze' and not freeze_mode:
                    freeze_mode = True
                    freeze_mode_timer = 3 * FPS
                elif self.special_effect == 'double_points' and not double_points_mode:
                    double_points_mode = True
                    double_points_timer = 5 * FPS
                self.special_effect = None
            
            if self.y > HEIGHT + self.radius:
                self.remove = True
    
    def draw(self):
        self.rotation += self.rotate_speed
        
        if not self.sliced:
            if self.fruit_type == 'golden_apple':
                glow_surface = pygame.Surface((self.radius*2 + 20, self.radius*2 + 20), pygame.SRCALPHA)
                for r in range(10, 0, -2):
                    alpha = 150 - (10 - r) * 15
                    pygame.draw.circle(glow_surface, (255, 215, 0, alpha), 
                                     (self.radius + 10, self.radius + 10), 
                                     self.radius + r + self.glow_size)
                window.blit(glow_surface, (int(self.x - self.radius - 10), int(self.y - self.radius - 10)))
            
            elif self.fruit_type == 'snowflake':
                glow_surface = pygame.Surface((self.radius*2 + 20, self.radius*2 + 20), pygame.SRCALPHA)
                for r in range(10, 0, -2):
                    alpha = 120 - (10 - r) * 12
                    pygame.draw.circle(glow_surface, (150, 210, 255, alpha), 
                                     (self.radius + 10, self.radius + 10), self.radius + r)
                window.blit(glow_surface, (int(self.x - self.radius - 10), int(self.y - self.radius - 10)))
            
            elif self.fruit_type == 'double_points_star':
                glow_surface = pygame.Surface((self.radius*2 + 20, self.radius*2 + 20), pygame.SRCALPHA)
                for r in range(10, 0, -2):
                    alpha = 150 - (10 - r) * 15
                    pygame.draw.circle(glow_surface, (255, 255, 0, alpha), 
                                     (self.radius + 10, self.radius + 10), 
                                     self.radius + r + self.glow_size)
                window.blit(glow_surface, (int(self.x - self.radius - 10), int(self.y - self.radius - 10)))
                
                points = []
                for i in range(10):
                    angle = math.pi/2 + i * math.pi/5 + self.rotation
                    radius = self.radius if i % 2 == 0 else self.radius * 0.4
                    point_x = self.x + math.cos(angle) * radius
                    point_y = self.y + math.sin(angle) * radius
                    points.append((point_x, point_y))
                
                pygame.draw.polygon(window, self.color, points)
                pygame.draw.circle(window, self.highlight_color, (int(self.x), int(self.y)), self.radius//4)
                return
            
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
            highlight_pos = (int(self.x - self.radius/3), int(self.y - self.radius/3))
            pygame.draw.circle(window, self.highlight_color, highlight_pos, self.radius//3)
            
            if self.fruit_type == 'apple' or self.fruit_type == 'golden_apple':
                stem_x, stem_y = int(self.x), int(self.y - self.radius - 5)
                stem_points = [
                    (stem_x, stem_y),
                    (stem_x + 7, stem_y - 10),
                    (stem_x + 3, stem_y - 10),
                    (stem_x, stem_y)
                ]
                pygame.draw.polygon(window, self.stem_color, stem_points)
                
            elif self.fruit_type == 'orange':
                for i in range(8):
                    angle = i * math.pi / 4 + self.rotation
                    end_x = self.x + math.cos(angle) * (self.radius - 5)
                    end_y = self.y + math.sin(angle) * (self.radius - 5)
                    pygame.draw.line(window, self.texture_color, (self.x, self.y), (end_x, end_y), 2)
                    
            elif self.fruit_type == 'snowflake':
                for i in range(6):
                    angle = i * math.pi / 3 + self.rotation
                    end_x = self.x + math.cos(angle) * (self.radius - 2)
                    end_y = self.y + math.sin(angle) * (self.radius - 2)
                    pygame.draw.line(window, (240, 248, 255), (self.x, self.y), (end_x, end_y), 3)
                    
                    branch_length = self.radius * 0.4
                    p1_x = self.x + math.cos(angle) * (self.radius/3)
                    p1_y = self.y + math.sin(angle) * (self.radius/3)
                    
                    for branch_angle in [angle + math.pi/6, angle - math.pi/6]:
                        b_x = p1_x + math.cos(branch_angle) * branch_length
                        b_y = p1_y + math.sin(branch_angle) * branch_length
                        pygame.draw.line(window, (240, 248, 255), (p1_x, p1_y), (b_x, b_y), 2)
        
        else:
            if self.fruit_type == 'double_points_star':
                for _ in range(15):
                    particle_x = self.x + random.uniform(-self.radius*1.5, self.radius*1.5)
                    particle_y = self.y + random.uniform(-self.radius*1.5, self.radius*1.5)
                    particle_size = random.randint(2, 5)
                    particle_color = (255, 255, random.randint(0, 100))
                    pygame.draw.circle(window, particle_color, (int(particle_x), int(particle_y)), particle_size)
                
                x2_text = font.render("x2", True, YELLOW)
                text_alpha = min(255, int(300 - (self.y - self.sliced_y) * 2)) if hasattr(self, 'sliced_y') else 255
                x2_text.set_alpha(text_alpha)
                window.blit(x2_text, (int(self.x - x2_text.get_width()//2), int(self.y - 30)))
                return
            
            angle = self.slice_angle
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            offset_x, offset_y = sin_a * self.slice_offset, -cos_a * self.slice_offset
            
            semi_rect1 = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), 
                                  self.radius*2, self.radius*2)
            pygame.draw.arc(window, self.color, semi_rect1, angle, angle + math.pi, self.radius)
                         
            semi_rect2 = pygame.Rect(int(self.x - self.radius + offset_x), int(self.y - self.radius + offset_y), 
                                  self.radius*2, self.radius*2)
            pygame.draw.arc(window, self.color, semi_rect2, angle + math.pi, angle + 2*math.pi, self.radius)
            
            if self.fruit_type == 'orange':
                inside_color = (255, 220, 180)
                for i in range(6):
                    seg_angle = angle + math.pi/6 + i * math.pi/3
                    end_x = self.x + math.cos(seg_angle) * (self.radius - 5)
                    end_y = self.y + math.sin(seg_angle) * (self.radius - 5)
                    pygame.draw.line(window, inside_color, (self.x, self.y), (end_x, end_y), 3)
            
            elif self.fruit_type == 'golden_apple':
                inside_color = (255, 240, 200)
                for i in range(6):
                    seg_angle = angle + math.pi/6 + i * math.pi/3
                    end_x = self.x + math.cos(seg_angle) * (self.radius - 5)
                    end_y = self.y + math.sin(seg_angle) * (self.radius - 5)
                    pygame.draw.line(window, inside_color, (self.x, self.y), (end_x, end_y), 3)
                    
            elif self.fruit_type in ['blueberry', 'snowflake']:
                particle_color = (100, 200, 255) if self.fruit_type == 'blueberry' else (200, 230, 255)
                particle_count = 5 if self.fruit_type == 'blueberry' else 15
                
                for _ in range(particle_count):
                    sparkle_x = self.x + random.uniform(-self.radius, self.radius)
                    sparkle_y = self.y + random.uniform(-self.radius, self.radius)
                    sparkle_size = random.randint(1, 3)
                    pygame.draw.circle(window, particle_color, (int(sparkle_x), int(sparkle_y)), sparkle_size)
    
    def get_points(self):
        points_multiplier = 2 if double_points_mode else 1
        return self.points * points_multiplier

class BladeTrail:
    def __init__(self):
        self.points = []
        self.max_points = 20
        self.active = False
        self.last_pos = None
    
    def add_point(self, pos):
        if pos != self.last_pos:
            self.points.append(pos)
            self.last_pos = pos
            if len(self.points) > self.max_points:
                self.points.pop(0)
    
    def draw(self):
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                start_pos = self.points[i]
                end_pos = self.points[i+1]
                
                for width, alpha in [(20, 30), (12, 70), (6, 150), (2, 255)]:
                    temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(temp_surface, (200, 200, 255, alpha), start_pos, end_pos, width)
                    window.blit(temp_surface, (0, 0))
    
    def check_collisions(self, fruits):
        if len(self.points) < 2 or not self.active:
            return []
        
        sliced_fruits = []
        for i in range(len(self.points) - 1):
            p1, p2 = self.points[i], self.points[i + 1]
            
            for fruit in fruits:
                if not fruit.sliced and self.line_circle_collision(p1, p2, (fruit.x, fruit.y), fruit.radius):
                    fruit.sliced = True
                    fruit.sliced_y = fruit.y
                    sliced_fruits.append(fruit)
        
        return sliced_fruits
    
    def line_circle_collision(self, p1, p2, circle_center, circle_radius):
        v1x, v1y = p2[0] - p1[0], p2[1] - p1[1]
        v2x, v2y = circle_center[0] - p1[0], circle_center[1] - p1[1]
        
        length_squared = v1x * v1x + v1y * v1y
        if length_squared == 0:
            return False
        
        t = max(0, min(1, (v1x * v2x + v1y * v2y) / length_squared))
        
        closest_x = p1[0] + t * v1x
        closest_y = p1[1] + t * v1y
        
        dx, dy = closest_x - circle_center[0], closest_y - circle_center[1]
        distance_squared = dx * dx + dy * dy
        
        return distance_squared <= (circle_radius * circle_radius)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    window.blit(img, (x, y))

def draw_lives(lives):
    for i in range(lives):
        heart_x, heart_y = WIDTH - 40 - (i * 40), 30
        heart_size = 15
        
        pygame.draw.circle(window, RED, (heart_x - heart_size//2, heart_y), heart_size//2)
        pygame.draw.circle(window, RED, (heart_x + heart_size//2, heart_y), heart_size//2)
        
        triangle_points = [
            (heart_x - heart_size, heart_y),
            (heart_x + heart_size, heart_y),
            (heart_x, heart_y + heart_size*1.2)
        ]
        pygame.draw.polygon(window, RED, triangle_points)
        
        highlight_color = (255, 150, 150)
        pygame.draw.circle(window, highlight_color, (heart_x - heart_size//2 + 2, heart_y - 2), 3)

def draw_effect_bars():
    bar_y_offset = 0
    
    if slow_mode and slow_mode_timer > 0:
        bar_width, bar_height = 200, 20
        bar_x, bar_y = WIDTH // 2 - bar_width // 2, 20 + bar_y_offset
        
        pygame.draw.rect(window, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (slow_mode_timer / (5 * FPS)))
        pygame.draw.rect(window, (100, 150, 255), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(window, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        slow_text = font.render("SLOW MODE", True, WHITE)
        window.blit(slow_text, (WIDTH // 2 - slow_text.get_width() // 2, bar_y + bar_height + 5))
        bar_y_offset += 60
    
    if freeze_mode and freeze_mode_timer > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 200, 255, 30))
        window.blit(overlay, (0, 0))
        
        for _ in range(5):
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            size = random.randint(2, 5)
            pygame.draw.circle(window, (255, 255, 255, 200), (x, y), size)
        
        bar_width, bar_height = 200, 20
        bar_x, bar_y = WIDTH // 2 - bar_width // 2, 20 + bar_y_offset
        
        pygame.draw.rect(window, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (freeze_mode_timer / (3 * FPS)))
        pygame.draw.rect(window, ICE_BLUE, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(window, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        freeze_text = font.render("FREEZE", True, WHITE)
        window.blit(freeze_text, (WIDTH // 2 - freeze_text.get_width() // 2, bar_y + bar_height + 5))
        bar_y_offset += 60
    
    if double_points_mode and double_points_timer > 0:
        if random.random() < 0.1:
            for _ in range(3):
                x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
                size = random.randint(2, 4)
                pygame.draw.circle(window, (255, 255, 100), (x, y), size)
        
        bar_width, bar_height = 200, 20
        bar_x, bar_y = WIDTH // 2 - bar_width // 2, 20 + bar_y_offset
        
        pygame.draw.rect(window, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (double_points_timer / (5 * FPS)))
        pygame.draw.rect(window, YELLOW, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(window, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        dp_text = font.render("DOUBLE POINTS", True, YELLOW)
        window.blit(dp_text, (WIDTH // 2 - dp_text.get_width() // 2, bar_y + bar_height + 5))
        
        x2_icon = big_font.render("×2", True, YELLOW)
        x2_rect = x2_icon.get_rect(center=(WIDTH - 70, HEIGHT - 70))
        
        glow_size = 5 + 3 * math.sin(pygame.time.get_ticks() / 200)
        for r in range(int(glow_size), 0, -1):
            alpha = 100 - r * 10
            glow_surf = pygame.Surface((x2_icon.get_width() + r*2, x2_icon.get_height() + r*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 255, 0, max(0, alpha)), 
                           (0, 0, x2_icon.get_width() + r*2, x2_icon.get_height() + r*2), 
                           border_radius=10)
            window.blit(glow_surf, (x2_rect.x - r, x2_rect.y - r))
        
        window.blit(x2_icon, x2_rect)

def draw_score_info():
    draw_text(f"Score: {score}", font, WHITE, 10, 10)
    draw_text(f"High Score: {high_score}", font, (200, 200, 100), 10, 50)

    if score > high_score and not game_over:
        new_record_text = font.render("NEW RECORD!", True, GOLD)
        window.blit(new_record_text, (10, 90))

def draw_game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    window.blit(overlay, (0, 0))
    
    game_over_text = big_font.render("GAME OVER", True, (255, 0, 0))
    window.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    window.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
    
    if score > high_score:
        high_score_text = font.render(f"NEW HIGH SCORE!", True, GOLD)
        window.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 20))
    else:
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        window.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 20))
    
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    window.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

def draw_instructions():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    window.blit(overlay, (0, 0))
    
    title_text = big_font.render("FRUIT NINJA", True, RED)
    window.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
    
    instructions = [
        "• Slice fruits by swiping with your mouse",
        "• Miss 3 fruits and it's game over!",
        "• Special Power-Ups:",
        "  - Blue Fruit: Slows down time",
        "  - Snowflake: Freezes all fruits",
        "  - Yellow Star: Double Points for 5 seconds",
        "  - Golden Apple: Bonus points",
        "Press SPACE to start or skip timer",
    ]
    
    for i, line in enumerate(instructions):
        y_pos = 180 + i * 40
        line_text = small_font.render(line, True, WHITE)
        window.blit(line_text, (WIDTH//2 - line_text.get_width()//2, y_pos))
    
    time_left = instruction_timer // FPS
    if time_left > 0:
        timer_text = font.render(f"Starting in: {time_left}...", True, YELLOW)
        window.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, HEIGHT - 100))

def spawn_fruits():
    if not game_over and random.random() < 0.02 and len(fruits) < 10:
        fruits.append(Fruit())

def reset_game():
    global score, lives, game_over, fruits, slow_mode, slow_mode_timer, freeze_mode, freeze_mode_timer
    global double_points_mode, double_points_timer, fruit_counter, show_instructions, instruction_timer
    score = 0
    lives = 3
    game_over = False
    slow_mode = False
    slow_mode_timer = 0
    freeze_mode = False
    freeze_mode_timer = 0
    double_points_mode = False
    double_points_timer = 0
    fruit_counter = 0
    show_instructions = True
    instruction_timer = 5 * FPS
    fruits = []

fruits = []
blade = BladeTrail()

def game_loop():
    global score, lives, game_over, slow_mode, slow_mode_timer, freeze_mode, freeze_mode_timer
    global double_points_mode, double_points_timer, high_score, show_instructions, instruction_timer
    
    running = True
    while running:
        draw_background()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                if score > high_score:
                    save_high_score(score)
                running = False
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and not game_over and not show_instructions:
                blade.active = True
                blade.points = []
                blade.add_point(pygame.mouse.get_pos())
            
            if event.type == MOUSEBUTTONUP and event.button == 1:
                blade.active = False
                blade.points = []
                
            if event.type == KEYDOWN and event.key == K_SPACE:
                if game_over:
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    reset_game()
                elif show_instructions:
                    show_instructions = False
                    instruction_timer = 0
        
        if show_instructions:
            instruction_timer -= 1
            if instruction_timer <= 0:
                show_instructions = False
            draw_instructions()
        else:
            if blade.active and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                blade.add_point(mouse_pos)
                
                sliced_fruits = blade.check_collisions(fruits)
                for fruit in sliced_fruits:
                    score += fruit.get_points()
                    if score > high_score:
                        high_score = score
            else:
                blade.points = []
            
            if slow_mode:
                slow_mode_timer -= 1
                if slow_mode_timer <= 0:
                    slow_mode = False
                    
            if freeze_mode:
                freeze_mode_timer -= 1
                if freeze_mode_timer <= 0:
                    freeze_mode = False

            if double_points_mode:
                double_points_timer -= 1
                if double_points_timer <= 0:
                    double_points_mode = False
            
            spawn_fruits()
            
            for fruit in fruits[:]:
                fruit.update()
                fruit.draw()
                
                if fruit.remove:
                    fruits.remove(fruit)
            
            blade.draw()
            draw_score_info()
            draw_lives(lives)
            draw_effect_bars()
            
            if game_over:
                draw_game_over_screen()
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()