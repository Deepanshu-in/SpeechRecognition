import pygame
import random
import sys
import math
from PIL import Image, ImageDraw

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
lives = 3
font = pygame.font.SysFont('Arial', 24)
game_over = False

# Generate background image using PIL
def create_background():
    # Create sky with gradient
    img = Image.new('RGB', (WIDTH, HEIGHT), (135, 206, 235))  # Sky blue
    draw = ImageDraw.Draw(img)
    draw.ellipse((650, 50, 750, 150), fill=(255, 223, 0)) # Draw sun
    
    # Draw clouds
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(20, 150)
        size = random.randint(30, 70)
        for i in range(3):
            draw.ellipse((x + i*size//2, y, x + size + i*size//2, y + size), 
                         fill=(255, 255, 255))
    
    # Draw ground
    draw.rectangle((0, HEIGHT-50, WIDTH, HEIGHT), fill=(101, 67, 33))  # Brown ground
    draw.ellipse((-100, HEIGHT-100, 300, HEIGHT+50), fill=(34, 139, 34))
    draw.ellipse((200, HEIGHT-80, 600, HEIGHT+50), fill=(34, 139, 34))
    draw.ellipse((500, HEIGHT-120, 900, HEIGHT+50), fill=(34, 139, 34))
    
    # Convert to pygame surface
    mode = img.mode
    size = img.size
    data = img.tobytes()
    background = pygame.image.fromstring(data, size, mode)
    return background

# Create archer sprite based on aim angle
def create_archer(aim_angle=0, arrow_loaded=True):
    img = Image.new('RGBA', (150, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw legs
    draw.polygon([(50, 120), (40, 180), (60, 180), (70, 120)], fill=(0, 51, 102))  # Left leg 
    draw.polygon([(80, 120), (90, 180), (110, 180), (95, 120)], fill=(0, 51, 102))  # Right leg
    
    # Draw yellow stripe on pants
    draw.line([(50, 140), (70, 140)], fill=(255, 165, 0), width=3)  # Left leg stripe
    draw.line([(80, 140), (95, 140)], fill=(255, 165, 0), width=3)  # Right leg stripe
    
    # Draw shoes
    draw.ellipse((35, 170, 65, 190), fill=(0, 0, 0))  # Left shoe
    draw.ellipse((85, 170, 115, 190), fill=(0, 0, 0))  # Right shoe
    
    # Draw body
    draw.polygon([(60, 60), (50, 120), (95, 120), (85, 60)], fill=(144, 238, 144))  # Green shirt
    
    # Draw head
    skin_tone = (210, 180, 140)  # Light skin tone
    draw.ellipse((60, 30, 85, 60), fill=skin_tone)  # Head
    
    # Draw hair 
    draw.ellipse((55, 35, 70, 50), fill=(70, 40, 20))  # Hair bun
    draw.line([(55, 42), (45, 60)], fill=(70, 40, 20), width=5)  # Ponytail
    
    # Calculate arm and bow positions based on aim angle
    angle_rad = math.radians(aim_angle)
    
    # Adjust bow position based on angle
    bow_center_x = 105
    bow_center_y = 90 - math.sin(angle_rad) * 20  # Move bow up/down based on angle
    
    # Draw both arms positioned to hold the bow
    draw.line([(65, 80), (bow_center_x - 5, bow_center_y + 15)], fill=skin_tone, width=8)  # Back arm
    
    # Draw bow with adjusted angle
    bow_height = 60
    bow_arc_start = 260 - aim_angle
    bow_arc_end = 100 - aim_angle
    
    # Draw bow
    draw.arc((bow_center_x - 15, bow_center_y - bow_height/2, 
              bow_center_x + 15, bow_center_y + bow_height/2), 
             start=bow_arc_start, end=bow_arc_end, fill=(139, 69, 19), width=4)  # Bow
    
    # Calculate bowstring points
    string_top_x = bow_center_x + math.sin(math.radians(bow_arc_start)) * 10
    string_top_y = bow_center_y - math.cos(math.radians(bow_arc_start)) * bow_height/2
    string_bottom_x = bow_center_x + math.sin(math.radians(bow_arc_end)) * 10
    string_bottom_y = bow_center_y - math.cos(math.radians(bow_arc_end)) * bow_height/2
    
    # Calculate pulled string position
    string_pulled_x = bow_center_x - 10  # Pulled back from bow
    string_pulled_y = bow_center_y
    
    # Draw bowstring with pulled shape when arrow is loaded
    if arrow_loaded:
        # Draw pulled bowstring
        draw.line([(string_top_x, string_top_y), (string_pulled_x, string_pulled_y)], fill=(139, 69, 19), width=1)
        draw.line([(string_pulled_x, string_pulled_y), (string_bottom_x, string_bottom_y)], fill=(139, 69, 19), width=1)
        
        # Draw arrow with adjusted angle
        arrow_angle_rad = math.radians(aim_angle)
        arrow_length = 55
        arrow_end_x = string_pulled_x + math.cos(arrow_angle_rad) * arrow_length
        arrow_end_y = string_pulled_y - math.sin(arrow_angle_rad) * arrow_length
        
        # Draw arrow shaft
        draw.line([(string_pulled_x, string_pulled_y), (arrow_end_x, arrow_end_y)], fill=(139, 69, 19), width=2)
        
        # Draw arrowhead
        arrowhead_size = 5
        draw.polygon([
            (arrow_end_x, arrow_end_y),
            (arrow_end_x - math.cos(arrow_angle_rad) * arrowhead_size - math.sin(arrow_angle_rad) * arrowhead_size, 
             arrow_end_y + math.sin(arrow_angle_rad) * arrowhead_size - math.cos(arrow_angle_rad) * arrowhead_size),
            (arrow_end_x - math.cos(arrow_angle_rad) * arrowhead_size + math.sin(arrow_angle_rad) * arrowhead_size, 
             arrow_end_y + math.sin(arrow_angle_rad) * arrowhead_size + math.cos(arrow_angle_rad) * arrowhead_size)
        ], fill=(128, 128, 128))  # Arrowhead
        
        # Draw arrow fletching at the string contact point
        fletching_size = 5
        draw.polygon([
            (string_pulled_x, string_pulled_y),
            (string_pulled_x + fletching_size, string_pulled_y - fletching_size),
            (string_pulled_x + fletching_size, string_pulled_y + fletching_size)
        ], fill=(255, 0, 0))  
    else:
        # Draw regular bowstring when no arrow is loaded
        draw.line([(string_top_x, string_top_y), (string_bottom_x, string_bottom_y)], fill=(139, 69, 19), width=1)
    
    # Draw hand on the string when arrow is loaded
    if arrow_loaded:
        draw.ellipse((string_pulled_x - 5, string_pulled_y - 5, string_pulled_x + 5, string_pulled_y + 5), fill=skin_tone)
    
    mode = img.mode
    size = img.size
    data = img.tobytes()
    archer_surf = pygame.image.fromstring(data, size, mode).convert_alpha()
    return archer_surf

# Create arrow sprite
def create_arrow():
    img = Image.new('RGBA', (50, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)  # Draw arrow
    draw.line((0, 5, 40, 5), fill=(139, 69, 19), width=2)  # Shaft
    draw.polygon([(40, 5), (35, 0), (35, 10)], fill=(128, 128, 128))  # Arrowhead
    draw.polygon([(0, 5), (10, 0), (10, 10)], fill=(255, 0, 0))  # Fletching
    mode = img.mode
    size = img.size
    data = img.tobytes()
    arrow_surf = pygame.image.fromstring(data, size, mode).convert_alpha()
    return arrow_surf

# Create balloon sprite
def create_balloon(color):
    img = Image.new('RGBA', (40, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pil_color = tuple(color)
    
    # Draw balloon
    draw.ellipse((0, 0, 40, 50), fill=pil_color)
    draw.polygon([(20, 50), (15, 60), (25, 60)], fill=pil_color)
    
    # Add shine effect
    draw.ellipse((10, 10, 15, 15), fill=(255, 255, 255, 180))
    
    mode = img.mode
    size = img.size
    data = img.tobytes()
    balloon_surf = pygame.image.fromstring(data, size, mode).convert_alpha()
    return balloon_surf

# Create bird sprite - Updated to face left
def create_bird(color=(5, 193, 255)):  
    img = Image.new('RGBA', (60, 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw bird body
    draw.ellipse((10, 10, 50, 35), fill=color)
    
    # Draw wings
    wing_color = tuple(c - 30 if c > 30 else c for c in color)  # Darker shade for wings
    draw.ellipse((20, 5, 45, 20), fill=wing_color)
    
    # Draw head and beak - now on the left side
    draw.ellipse((0, 15, 15, 30), fill=color)
    draw.polygon([(2, 22), (-10, 22), (2, 28)], fill=(255, 165, 0))  # Orange beak facing left
    
    # Draw eye
    draw.ellipse((4, 18, 8, 22), fill=BLACK)
    
    # Draw tail - now on the right side
    draw.polygon([(50, 20), (60, 15), (60, 25)], fill=color)
    
    mode = img.mode
    size = img.size
    data = img.tobytes()
    bird_surf = pygame.image.fromstring(data, size, mode).convert_alpha()
    return bird_surf

# Create heart sprite
def create_heart():
    img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a heart shape
    draw.polygon([
        (10, 17), (2, 10), (2, 5), 
        (5, 2), (10, 5), (15, 2), 
        (18, 5), (18, 10)
    ], fill=(255, 0, 0))
    
    mode = img.mode
    size = img.size
    data = img.tobytes()
    heart_surf = pygame.image.fromstring(data, size, mode).convert_alpha()
    return heart_surf

# Archer class 
class Archer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.aim_angle = 0  # Horizontal is 0 degrees
        self.arrow_loaded = True  # Start with an arrow loaded
        self.image = create_archer(self.aim_angle, self.arrow_loaded)
        self.rect = self.image.get_rect(midbottom=(150, HEIGHT-50))  # Fixed to bottom
        self.last_shot_time = 0
        self.reload_time = 500  # milliseconds

    def update(self):
        # Adjust aim with up/down arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.aim_angle < 60:  # Reversed limit
            self.aim_angle += 2  # Reversed direction
        if keys[pygame.K_DOWN] and self.aim_angle > -30:  # Reversed limit
            self.aim_angle -= 2  # Reversed direction
        self.image = create_archer(self.aim_angle, self.arrow_loaded) # Update archer image based on aim angle and arrow loaded state
        self.rect = self.image.get_rect(midbottom=(150, HEIGHT-50))  # Maintain position
        current_time = pygame.time.get_ticks()   # Check if arrow is ready to reload
        if not self.arrow_loaded and current_time - self.last_shot_time > self.reload_time:
            self.arrow_loaded = True
            self.image = create_archer(self.aim_angle, self.arrow_loaded)
    
    def shoot(self):
        if self.arrow_loaded:  # Calculate arrow start position based on aim angle
            angle_rad = math.radians(self.aim_angle)
            start_x = self.rect.left + 105 - 10  # Match the pulled string position from create_archer
            start_y = self.rect.top + 90 - math.sin(angle_rad) * 20  # Match bow_center_y
            arrow = Arrow(start_x, start_y, self.aim_angle)
            self.arrow_loaded = False
            self.last_shot_time = pygame.time.get_ticks()
            self.image = create_archer(self.aim_angle, self.arrow_loaded)    # Update the image to show unloaded bow
            return arrow
        return None

class Arrow(pygame.sprite.Sprite):  # Arrow class with angle trajectory
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = create_arrow()
        self.original_image = self.image
        self.rect = self.image.get_rect(midleft=(x, y))
        self.angle = angle
        self.speed = 10
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        angle_rad = math.radians(angle)
        self.vel_x = math.cos(angle_rad) * self.speed
        self.vel_y = -math.sin(angle_rad) * self.speed
        self.float_x = float(x)
        self.float_y = float(y)

    def update(self):
        self.float_x += self.vel_x
        self.float_y += self.vel_y # Apply slight gravity effect to make the arrow arc
        self.vel_y += 0.1 # Update rect position from float position
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)  # Update rotation based on trajectory
        trajectory_angle = math.degrees(math.atan2(-self.vel_y, self.vel_x))
        self.image = pygame.transform.rotate(self.original_image, trajectory_angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        if (self.rect.left > WIDTH or self.rect.right < 0 or 
            self.rect.top > HEIGHT or self.rect.bottom < 0):
            self.kill()

class Balloon(pygame.sprite.Sprite):   # Balloon class
    def __init__(self):
        super().__init__()
        self.color = random.choice(COLORS)
        self.image = create_balloon(self.color)
        self.rect = self.image.get_rect(center=(WIDTH + 50, random.randint(HEIGHT * 0.2, HEIGHT * 0.7)))
        self.speed = random.randint(2, 5)
        self.point_value = 6 - self.speed 
        self.float_x = float(self.rect.x)  # Add float positions for more precise movement
        self.float_y = float(self.rect.y)
        self.bob_speed = random.uniform(0.02, 0.05)
        self.bob_amplitude = random.randint(5, 15)
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.horizontal_variation = random.uniform(-0.5, 0.5)

    def update(self): # Move horizontally with precise position 
        self.float_x -= self.speed
        self.float_x += math.sin(self.bob_offset * 0.5) * self.horizontal_variation
        self.rect.x = int(self.float_x)
        self.bob_offset += self.bob_speed
        self.float_y = self.rect.y + math.sin(self.bob_offset) * self.bob_amplitude
        self.rect.y = int(self.float_y)
        if self.rect.right < 0:
            self.kill()
            
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Generate random bird color variations
        color = (
            random.randint(120, 180),  # Red component
            random.randint(30, 80),    # Green component
            random.randint(20, 60)     # Blue component
        )
        self.image = create_bird(color)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH + 50, random.randint(HEIGHT * 0.1, HEIGHT * 0.7)))
        self.speed = random.randint(3, 7)
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y) # More dynamic movement patterns for birds
        self.bob_speed = random.uniform(0.04, 0.08)  # Faster than balloons
        self.bob_amplitude = random.randint(10, 25)  # More pronounced than balloons
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.horizontal_variation = random.uniform(-0.2, 0.8)
        self.flap_timer = 0
        self.flap_speed = 20  # Flap wings every 20 frames

    def update(self): # Move horizontally with precise position 
        self.float_x -= self.speed
        self.float_x += math.sin(self.bob_offset) * self.horizontal_variation
        self.rect.x = int(self.float_x)
        self.bob_offset += self.bob_speed
        vertical_movement = math.sin(self.bob_offset) * self.bob_amplitude
        if random.random() < 0.01:  # 1% chance per frame
            vertical_movement += random.randint(-5, 5)
        self.float_y += vertical_movement * 0.1  # Smooth the movement
        self.rect.y = int(self.float_y)
        if self.rect.top < 0:
            self.rect.top = 0
            self.float_y = float(self.rect.y)
        elif self.rect.bottom > HEIGHT - 100:  
            self.rect.bottom = HEIGHT - 100
            self.float_y = float(self.rect.y)
        self.flap_timer += 1
        if self.flap_timer >= self.flap_speed:
            self.flap_timer = 0
            self.image = pygame.transform.flip(self.image, False, True)
        if self.rect.right < 0:
            self.kill()

heart_sprite = create_heart()

# Function to reset the game
def reset_game():
    global score, lives, game_over
    score = 0
    lives = 3
    game_over = False
    
    # Clear all sprite groups
    all_sprites.empty()
    arrows.empty()
    balloons.empty()
    birds.empty()
    
    # Create archer
    archer = Archer()
    all_sprites.add(archer)
    
    return archer

# Create sprite groups
all_sprites = pygame.sprite.Group()
arrows = pygame.sprite.Group()
balloons = pygame.sprite.Group()
birds = pygame.sprite.Group()

# Create archer
archer = Archer()
all_sprites.add(archer)
background = create_background()
balloon_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(balloon_spawn_event, 1000)  # Spawn every 1 second
bird_spawn_event = pygame.USEREVENT + 2
pygame.time.set_timer(bird_spawn_event, 3000)  # Spawn every 3 seconds

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Spawn new balloon
        if event.type == balloon_spawn_event and not game_over:
            new_balloon = Balloon()
            all_sprites.add(new_balloon)
            balloons.add(new_balloon)
        
        # Spawn new bird
        if event.type == bird_spawn_event and not game_over:
            new_bird = Bird()
            all_sprites.add(new_bird)
            birds.add(new_bird)
        
        # Shoot arrow with spacebar
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                arrow = archer.shoot()
                if arrow:
                    all_sprites.add(arrow)
                    arrows.add(arrow)
            
            # Restart game if game over and R is pressed
            if event.key == pygame.K_r and game_over:
                archer = reset_game()
    
    # Update all sprites
    if not game_over:
        all_sprites.update()
    
    # Check for collisions between arrows and balloons
    balloon_hits = pygame.sprite.groupcollide(arrows, balloons, True, True)
    for arrow, balloon_list in balloon_hits.items():
        for balloon in balloon_list:
            score += balloon.point_value
    
    # Check for collisions between arrows and birds
    bird_hits = pygame.sprite.groupcollide(arrows, birds, True, True)
    if bird_hits:
        lives -= 1
        if lives <= 0:
            game_over = True
    
    # Draw everything
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    # Display score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    # Display lives
    for i in range(lives):
        screen.blit(heart_sprite, (WIDTH - 30 - i*25, 10))
    
    # Display reload status
    if archer.arrow_loaded and not game_over:
        status_text = font.render("Shoot!", True, GREEN)
    elif not game_over:
        status_text = font.render("Reloading...", True, RED)
    else:
        status_text = font.render("Game Over! Press R to restart", True, RED)
    screen.blit(status_text, (10, 40))
    
    # Display instructions
    if not game_over:
        warning_text = font.render("", True, RED)
        screen.blit(warning_text, (WIDTH - 350, 40))
        
    pygame.display.flip()

pygame.quit()
sys.exit()