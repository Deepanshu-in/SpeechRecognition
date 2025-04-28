import pygame
import math
import random
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WALL_HEIGHT = int(SCREEN_HEIGHT * 0.6)  # 60% of screen height

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tank Battle Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BRICK_COLOR = (139, 69, 19)
ROAD_COLOR = (40, 40, 40)
DARK_BLUE = (0, 0, 50)
TEAL = (0, 128, 128)
DARK_TEAL = (0, 64, 64)
LIGHT_TEAL = (128, 192, 192)
GRASS_COLOR = (34, 139, 34)
LIGHT_GRASS_COLOR = (124, 252, 0)

# Tank dimensions
TANK_WIDTH = 80
TANK_HEIGHT = 50
CANNON_LENGTH = 60
CANNON_WIDTH = 10

# Game settings
TANK_SPEED = 3
CANNON_ROTATION_SPEED = 2
PROJECTILE_SPEED = 10
GRAVITY = 0.27

# Tank class
class Tank:
    def __init__(self, x, y, color_set, facing_left=False):
        self.x = x
        self.y = y
        self.facing_left = facing_left
        self.cannon_angle = 0 if not facing_left else 180
        self.health = 100
        self.colors = {
            'light_tan': color_set.get('light_tan', (237, 217, 161)),
            'medium_tan': color_set.get('medium_tan', (237, 88, 88)), 
            'dark_tan': color_set.get('dark_tan', (247, 12, 12)),
            'darker_tan': color_set.get('darker_tan', (145, 115, 74)),
            'black': color_set.get('black', (237, 88, 88)),
            'highlight': color_set.get('highlight', (255, 255, 255, 100)),
            'cannon': (255, 0, 0)}
        self.scale = 0.1  # Adjust as needed
        self.create_tank_surface()
        
    def create_tank_surface(self):
        # Calculate scaled dimensions
        width = int(1000 * self.scale)
        height = int(600 * self.scale)
        
        # Create PIL Image and Draw objects
        pil_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_img)
        self.draw_tracks(draw, width, height)
        self.draw_hull(draw, width, height)
        self.draw_turret(draw, width, height)
        self.draw_gun(draw, width, height)
        if self.facing_left:
            pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
            
        mode = pil_img.mode
        size = pil_img.size
        data = pil_img.tobytes()
        self.surface = pygame.image.fromstring(data, size, mode).convert_alpha()
        
    def draw_hull(self, draw, width, height):   # Main hull body
        scale = self.scale
        hull_points = [
            (int(100 * scale), int(380 * scale)),
            (int(900 * scale), int(380 * scale)),
            (int(850 * scale), int(300 * scale)),
            (int(180 * scale), int(300 * scale))]
        draw.polygon(hull_points, fill=self.colors['light_tan'], outline=self.colors['black'])
        front_points = [ # Front angular section
            (int(100 * scale), int(380 * scale)),
            (int(180 * scale), int(300 * scale)),
            (int(80 * scale), int(340 * scale))]
        draw.polygon(front_points, fill=self.colors['medium_tan'], outline=self.colors['black'])
        hull_top_points = [  # Hull top plate
            (int(180 * scale), int(300 * scale)),
            (int(850 * scale), int(300 * scale)),
            (int(820 * scale), int(270 * scale)),
            (int(210 * scale), int(270 * scale))]
        draw.polygon(hull_top_points, fill=self.colors['light_tan'], outline=self.colors['black'])
        for i in range(4):  # Side armor panels
            x = int((200 + i * 160) * scale)
            y = int(300 * scale)
            self.draw_armor_panel(draw, x, y, int(150 * scale), int(80 * scale))
            
        hull_highlight = [   # Hull highlights
            (int(200 * scale), int(270 * scale)),
            (int(780 * scale), int(270 * scale)),
            (int(770 * scale), int(280 * scale)),
            (int(210 * scale), int(280 * scale))]
        draw.polygon(hull_highlight, fill=self.colors['highlight'])
            
    def draw_armor_panel(self, draw, x, y, width, height):
        panel_points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)]
        draw.polygon(panel_points, fill=self.colors['medium_tan'], outline=self.colors['black'])
        shadow_points = [ # Add shadow effect on left side
            (x, y),
            (x + int(20 * self.scale), y),
            (x + int(20 * self.scale), y + height),
            (x, y + height)]
        draw.polygon(shadow_points, fill=self.colors['dark_tan'])
    
    def draw_tracks(self, draw, width, height):
        scale = self.scale
        
        track_points = [ # Track outline
            (int(70 * scale), int(380 * scale)),
            (int(900 * scale), int(380 * scale)),
            (int(930 * scale), int(420 * scale)),
            (int(930 * scale), int(480 * scale)),
            (int(900 * scale), int(520 * scale)),
            (int(100 * scale), int(520 * scale)),
            (int(70 * scale), int(480 * scale)),
            (int(70 * scale), int(420 * scale))]
        draw.polygon(track_points, fill=self.colors['darker_tan'], outline=self.colors['black'])
        wheel_centers = [ # Wheels
            (int(130 * scale), int(490 * scale)),
            (int(230 * scale), int(490 * scale)),
            (int(330 * scale), int(490 * scale)),
            (int(430 * scale), int(490 * scale)),
            (int(530 * scale), int(490 * scale)),
            (int(630 * scale), int(490 * scale)),
            (int(730 * scale), int(490 * scale)),
            (int(830 * scale), int(490 * scale))]
        
        for center in wheel_centers:
            self.draw_wheel(draw, center[0], center[1], int(40 * scale))
            
        for i in range(30): # Track segments
            x = int((70 + i * 29) * scale)
            draw.rectangle((x, int(390 * scale), x + int(25 * scale), int(405 * scale)), 
                         fill=self.colors['darker_tan'], outline=self.colors['black'])
            draw.rectangle((x, int(495 * scale), x + int(25 * scale), int(510 * scale)), 
                         fill=self.colors['darker_tan'], outline=self.colors['black'])
    
    def draw_wheel(self, draw, x, y, radius):  # wheel
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                     fill=self.colors['dark_tan'], outline=self.colors['black'])
        inner_radius = int(radius * 0.6)
        draw.ellipse((x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius), 
                     fill=self.colors['darker_tan'], outline=self.colors['black'])
        center_radius = int(radius * 0.2)  # Center point
        draw.ellipse((x - center_radius, y - center_radius, x + center_radius, y + center_radius), 
                     fill=self.colors['black'])
    
    def draw_turret(self, draw, width, height): # Main turret body
        scale = self.scale
        turret_points = [
            (int(350 * scale), int(270 * scale)),
            (int(650 * scale), int(270 * scale)),
            (int(630 * scale), int(210 * scale)),
            (int(580 * scale), int(180 * scale)),
            (int(400 * scale), int(180 * scale)),
            (int(330 * scale), int(210 * scale))]
        draw.polygon(turret_points, fill=self.colors['medium_tan'], outline=self.colors['black']) # Commander's hatch
        hatch_points = [
            (int(510 * scale), int(180 * scale)),
            (int(550 * scale), int(180 * scale)),
            (int(550 * scale), int(140 * scale)),
            (int(510 * scale), int(140 * scale))]
        draw.polygon(hatch_points, fill=self.colors['medium_tan'], outline=self.colors['black'])  # Turret front angular section
        front_turret = [
            (int(330 * scale), int(210 * scale)),
            (int(350 * scale), int(270 * scale)),
            (int(300 * scale), int(240 * scale))]
        draw.polygon(front_turret, fill=self.colors['dark_tan'], outline=self.colors['black'])
        draw.rectangle((int(470 * scale), int(210 * scale), int(520 * scale), int(240 * scale)), 
                      fill=self.colors['dark_tan'], outline=self.colors['black'])   # Turret details
        
        turret_highlight = [  # Turret highlight
            (int(350 * scale), int(180 * scale)),
            (int(580 * scale), int(180 * scale)),
            (int(570 * scale), int(190 * scale)),
            (int(360 * scale), int(190 * scale))]
        draw.polygon(turret_highlight, fill=self.colors['highlight'])
    
    def draw_gun(self, draw, width, height):
        scale = self.scale  # Main gun barrel
        gun_points = [
            (int(300 * scale), int(220 * scale)),
            (int(300 * scale), int(240 * scale)),
            (int(750 * scale), int(240 * scale)),
            (int(750 * scale), int(220 * scale))
        ]
        draw.polygon(gun_points, fill=self.colors['medium_tan'], outline=self.colors['black'])  # Gun sections/reinforcements
        for i in range(3):
            x = int((450 + i * 100) * scale)
            draw.rectangle((x, int(215 * scale), x + int(70 * scale), int(245 * scale)), 
                          fill=self.colors['dark_tan'], outline=self.colors['black'])
    
    def draw(self, surface):   # Draw the tank body
        tank_x = self.x
        tank_y = self.y - TANK_HEIGHT  # Adjusting for the bottom of the tank
        surface.blit(self.surface, (tank_x, tank_y - self.surface.get_height() + TANK_HEIGHT))
        cannon_x = self.x + (TANK_WIDTH // 3 if not self.facing_left else TANK_WIDTH * 2 // 3) # Draw cannon
        cannon_y = self.y - TANK_HEIGHT * 0.7
        angle_rad = math.radians(self.cannon_angle)
        end_x = cannon_x + math.cos(angle_rad) * CANNON_LENGTH
        end_y = cannon_y + math.sin(angle_rad) * CANNON_LENGTH
        pygame.draw.line(surface, RED, (cannon_x, cannon_y), (end_x, end_y), CANNON_WIDTH)  # Draw the cannon in red
        health_bar_width = TANK_WIDTH # Draw health bar
        health_bar_height = 5
        health_color = GREEN
        if self.health < 70:
            health_color = YELLOW
        if self.health < 30:
            health_color = RED
        
        pygame.draw.rect(surface, RED, (self.x, self.y - TANK_HEIGHT - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, health_color, (self.x, self.y - TANK_HEIGHT - 10, health_bar_width * self.health // 100, health_bar_height))
    
    def move(self, direction):
        self.x += direction * TANK_SPEED
        wall_x = SCREEN_WIDTH // 2 - 30  # Middle of screen - half wall width
        if direction > 0:
            if not self.facing_left and self.x + TANK_WIDTH > wall_x:
                self.x = wall_x - TANK_WIDTH
            elif self.facing_left and self.x + TANK_WIDTH > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - TANK_WIDTH
        else:
            if not self.facing_left and self.x < 0:
                self.x = 0
            elif self.facing_left and self.x < wall_x:
                self.x = wall_x
    
    def rotate_cannon(self, direction):
        self.cannon_angle += direction * CANNON_ROTATION_SPEED
        if not self.facing_left:
            if self.cannon_angle < -70:
                self.cannon_angle = -70
            elif self.cannon_angle > 70:
                self.cannon_angle = 70
        else:
            if self.cannon_angle < 110:
                self.cannon_angle = 110
            elif self.cannon_angle > 250:
                self.cannon_angle = 250
    
    def get_cannon_end(self):
        cannon_x = self.x + (TANK_WIDTH // 3 if not self.facing_left else TANK_WIDTH * 2 // 3)
        cannon_y = self.y - TANK_HEIGHT * 0.7
        
        angle_rad = math.radians(self.cannon_angle)
        end_x = cannon_x + math.cos(angle_rad) * CANNON_LENGTH
        end_y = cannon_y + math.sin(angle_rad) * CANNON_LENGTH
        
        return (end_x, end_y)

# Road class
class Road:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.road_y = height - 20
        self.lane_width = 3
        self.dash_length = 30
        self.gap_length = 20
        self.grass_patches = []
        
        # Generate random grass patches
        num_patches = 30
        for _ in range(num_patches):
            x = random.randint(0, width)
            y = self.road_y - random.randint(5, 15)
            size = random.randint(5, 15)
            self.grass_patches.append((x, y, size))
    
    def draw(self, surface):
        # Draw main road
        pygame.draw.rect(surface, ROAD_COLOR, (0, self.road_y, self.width, self.height - self.road_y))
        lane_y = self.road_y + 10
        total_dashes = self.width // (self.dash_length + self.gap_length) + 1
        
        for i in range(total_dashes):
            x = i * (self.dash_length + self.gap_length)
            pygame.draw.rect(surface, YELLOW, (x, lane_y, self.dash_length, self.lane_width))
            
        for patch in self.grass_patches:
            x, y, size = patch
            color = GRASS_COLOR if random.random() > 0.3 else LIGHT_GRASS_COLOR
            points = [   # Draw a simple grass tuft
                (x, y),
                (x - size//2, y + size),
                (x + size//2, y + size)]
            pygame.draw.polygon(surface, color, points)
            offset_x = x + random.randint(-3, 3)
            offset_y = y + random.randint(-2, 2)
            points = [
                (offset_x, offset_y),
                (offset_x - size//2, offset_y + size),
                (offset_x + size//2, offset_y + size)]
            pygame.draw.polygon(surface, color, points)

# Projectile class
class Projectile:
    def __init__(self, x, y, angle, color=(255, 165, 0)):
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color
        self.speed = PROJECTILE_SPEED
        self.velocity_x = math.cos(math.radians(angle)) * self.speed
        self.velocity_y = math.sin(math.radians(angle)) * self.speed - 5
        self.gravity = GRAVITY
        self.radius = 4
        self.trail = []
        self.max_trail_length = 10
    
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
    
    def draw(self, surface): # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (min(255, self.color[0] + 50), 
                          min(255, self.color[1] + 50), 
                          min(255, self.color[2] + 50), 
                          alpha)
            trail_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, trail_color, (self.radius, self.radius), self.radius * (i / len(self.trail)))
            surface.blit(trail_surf, (trail_x - self.radius, trail_y - self.radius))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
    
    def check_collision(self, tank, wall_x, wall_y, wall_width, wall_height):   # Check wall collision
        if (wall_x <= self.x <= wall_x + wall_width and 
            wall_y <= self.y <= wall_y + wall_height):
            return "wall"
        tank_rect = pygame.Rect(tank.x, tank.y - TANK_HEIGHT, TANK_WIDTH, TANK_HEIGHT)
        if tank_rect.collidepoint((self.x, self.y)):
            return "tank"
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y > SCREEN_HEIGHT:
            return "out"
        return None

# Star class for background
class Star:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.flicker_value = random.random()
        self.flicker_direction = random.choice([-0.01, 0.01])
    
    def update(self):
        self.flicker_value += self.flicker_direction
        if self.flicker_value > 1.0 or self.flicker_value < 0.3:
            self.flicker_direction = -self.flicker_direction
    
    def draw(self, surface):
        alpha = int(self.flicker_value * 255)
        color = (255, 255, 255)  # RGB without alpha
        star_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, color, (self.size, self.size), self.size * self.flicker_value)
        star_surf.set_alpha(alpha)  # Set alpha on the surface instead
        surface.blit(star_surf, (self.x - self.size, self.y - self.size))

# Create explosion animation frames
def create_explosion_frames(num_frames=10, max_size=40):
    frames = []
    for i in range(num_frames):
        size = int((i + 1) * max_size / num_frames)
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA) 
        colors = [(255, 255, 0, 180), (255, 165, 0, 200), (255, 0, 0, 220)]  # Draw explosion
        for j, color in enumerate(colors):
            radius = size * (1 - j * 0.2)
            pygame.draw.circle(surf, color, (size, size), radius)
        
        frames.append(surf)
    return frames

explosion_frames = create_explosion_frames()

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frames = explosion_frames
        self.max_frames = len(self.frames)
        self.frame_delay = 2
        self.frame_counter = 0
    
    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame += 1
        return self.frame < self.max_frames
    
    def draw(self, surface):
        if self.frame < self.max_frames:
            frame = self.frames[self.frame]
            surface.blit(frame, (self.x - frame.get_width()//2, self.y - frame.get_height()//2))

# Create stars for night background
stars = []
for _ in range(100):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT * 0.7)
    size = random.uniform(0.5, 2.0)
    stars.append(Star(x, y, size))

road = Road(SCREEN_WIDTH, SCREEN_HEIGHT)

# Create tanks with desert colors
desert_colors = {
    'light_tan': (237, 217, 161),
    'medium_tan': (215, 186, 130),
    'dark_tan': (173, 140, 89),
    'darker_tan': (145, 115, 74),
    'black': (20, 20, 20),
    'highlight': (255, 255, 255, 100)
}

forest_colors = {
    'light_tan': (90, 120, 80),
    'medium_tan': (70, 100, 60),
    'dark_tan': (50, 80, 40),
    'darker_tan': (30, 60, 30),
    'black': (20, 20, 20),
    'highlight': (180, 200, 180, 100)
}

tank1 = Tank(50, SCREEN_HEIGHT - 20, desert_colors)
tank2 = Tank(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 20, forest_colors, facing_left=True)
projectiles = []
explosions = []
game_over = False
winner = None
clock = pygame.time.Clock()
running = True

while running:   # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                cannon_end = tank1.get_cannon_end()
                projectiles.append(Projectile(cannon_end[0], cannon_end[1], tank1.cannon_angle))
            elif event.key == pygame.K_RETURN:
                cannon_end = tank2.get_cannon_end()
                projectiles.append(Projectile(cannon_end[0], cannon_end[1], tank2.cannon_angle))
    
    if not game_over:
        keys = pygame.key.get_pressed()
        # Tank 1 controls 
        if keys[pygame.K_a]:
            tank1.move(-1)
        if keys[pygame.K_s]:
            tank1.move(1)
        if keys[pygame.K_e]:
            tank1.rotate_cannon(-1)
        if keys[pygame.K_d]:
            tank1.rotate_cannon(1)
        if keys[pygame.K_LEFT]:
            tank2.move(-1)
        if keys[pygame.K_RIGHT]:
            tank2.move(1)
        if keys[pygame.K_UP]:
            tank2.rotate_cannon(-1)
        if keys[pygame.K_DOWN]:
            tank2.rotate_cannon(1)
    
    for proj in projectiles[:]:  # Update projectiles
        proj.update()
        collision_tank1 = proj.check_collision(tank1, SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT - WALL_HEIGHT, 30, WALL_HEIGHT)
        collision_tank2 = proj.check_collision(tank2, SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT - WALL_HEIGHT, 30, WALL_HEIGHT)
        
        if collision_tank1 == "tank":
            tank1.health -= 20
            explosions.append(Explosion(proj.x, proj.y))
            projectiles.remove(proj)
            if tank1.health <= 0:
                game_over = True
                winner = "Player 2"
        elif collision_tank2 == "tank":
            tank2.health -= 20
            explosions.append(Explosion(proj.x, proj.y))
            projectiles.remove(proj)
            if tank2.health <= 0:
                game_over = True
                winner = "Player 1"
        elif collision_tank1 == "wall" or collision_tank2 == "wall":
            explosions.append(Explosion(proj.x, proj.y))
            projectiles.remove(proj)
        elif collision_tank1 == "out" or collision_tank2 == "out":
            projectiles.remove(proj)
    
    for explosion in explosions[:]: # Update explosions
        if not explosion.update():
            explosions.remove(explosion)
            
    for star in stars:
        star.update()
    
    screen.fill(DARK_BLUE)
    for star in stars:
        star.draw(screen)
        
    pygame.draw.circle(screen, (220, 220, 220), (700, 100), 40) # Draw moon
    pygame.draw.circle(screen, DARK_BLUE, (680, 90), 40)
    road.draw(screen)
    wall_x = SCREEN_WIDTH // 2 - 15
    wall_y = SCREEN_HEIGHT - WALL_HEIGHT
    pygame.draw.rect(screen, BRICK_COLOR, (wall_x, wall_y, 30, WALL_HEIGHT))
    
    brick_height = 10  # Draw brick pattern
    brick_width = 30
    for y in range(0, WALL_HEIGHT, brick_height):
        offset = brick_width // 2 if (y // brick_height) % 2 else 0
        for x in range(0, 30, brick_width):
            pygame.draw.rect(screen, (160, 80, 30), (wall_x + x, wall_y + y, brick_width - 1, brick_height - 1))
            pygame.draw.line(screen, (80, 40, 10), (wall_x + x, wall_y + y), (wall_x + x + brick_width - 1, wall_y + y), 1)
            pygame.draw.line(screen, (80, 40, 10), (wall_x + x, wall_y + y), (wall_x + x, wall_y + y + brick_height - 1), 1)
    
    tank1.draw(screen) # Draw tanks
    tank2.draw(screen)
    for proj in projectiles:
        proj.draw(screen)
    
    for explosion in explosions:
        explosion.draw(screen)
    
    if game_over:  # Draw game over screen if needed
        font = pygame.font.SysFont(None, 64)
        game_over_text = font.render("GAME OVER", True, WHITE)
        winner_text = font.render(f"{winner} Wins!", True, WHITE)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - game_over_text.get_height() - 20))
        screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        

        font_small = pygame.font.SysFont(None, 32)  # Draw restart instructions
        restart_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            tank1 = Tank(50, SCREEN_HEIGHT - 20, desert_colors)
            tank2 = Tank(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 20, forest_colors, facing_left=True)
            projectiles = []
            explosions = []
            game_over = False
            winner = None
        elif keys[pygame.K_q]:
            running = False
    
    font = pygame.font.SysFont(None, 30)  # Draw player info
    p1_text = font.render("Player 1", True, WHITE)
    p2_text = font.render("Player 2", True, WHITE)
    screen.blit(p1_text, (tank1.x + TANK_WIDTH//2 - p1_text.get_width()//2, tank1.y - TANK_HEIGHT - 30))
    screen.blit(p2_text, (tank2.x + TANK_WIDTH//2 - p2_text.get_width()//2, tank2.y - TANK_HEIGHT - 30))
    
    if not projectiles and not game_over: # Show controls on screen when game starts
        controls_font = pygame.font.SysFont(None, 24)
        controls1 = controls_font.render("Player 1: A/S = Move, E/D = Aim, SPACE = Fire", True, WHITE)
        controls2 = controls_font.render("Player 2: LEFT/RIGHT = Move, UP/DOWN = Aim, ENTER = Fire", True, WHITE)
        screen.blit(controls1, (10, 10))
        screen.blit(controls2, (10, 40))
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()