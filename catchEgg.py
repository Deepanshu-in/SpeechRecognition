import pygame
import random
import sys
import math
import time
from PIL import Image, ImageDraw

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Eggs")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
NIGHT_BLUE = (25, 25, 112)  # Midnight Blue for night sky

# Helper function to convert PIL image to Pygame surface
def pil_to_pygame(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

# Create beautiful images with PIL
def create_background(is_night=False):
    if is_night:
        sky_color = NIGHT_BLUE
        grass_color = (21, 71, 22)  # Darker green for night
    else:
        sky_color = SKY_BLUE
        grass_color = (34, 139, 34)  # Regular green

    img = Image.new('RGB', (WIDTH, HEIGHT), sky_color)
    draw = ImageDraw.Draw(img)
    
    # Draw ground (green grass)
    draw.rectangle([(0, HEIGHT-50), (WIDTH, HEIGHT)], fill=grass_color)
    return pil_to_pygame(img)

def create_sun(size):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw sun with gradient
    center_x, center_y = size[0]//2, size[1]//2
    radius = min(center_x, center_y)
    
    for r in range(radius, 0, -1):
        # Create gradient from bright yellow to orange
        ratio = r / radius
        color = (
            int(255),  # Red
            int(255 * ratio + 165 * (1 - ratio)),  # Green (fade from yellow to orange)
            int(0 + 255 * ratio)  # Blue
        )
        draw.ellipse(
            [(center_x - r, center_y - r), (center_x + r, center_y + r)],
            fill=color
        )
    # Draw sun rays
    ray_length = radius * 0.3
    for angle in range(0, 360, 30):
        rad_angle = angle * 3.14159 / 180
        x1 = center_x + (radius + 2) * math.cos(rad_angle)
        y1 = center_y + (radius + 2) * math.sin(rad_angle)
        x2 = center_x + (radius + ray_length) * math.cos(rad_angle)
        y2 = center_y + (radius + ray_length) * math.sin(rad_angle)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 0), width=3)
    
    return pil_to_pygame(img)

def create_moon(size):
    # Draw moon with gradient
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center_x, center_y = size[0]//2, size[1]//2
    radius = min(center_x, center_y)
    
    # Main moon circle (light gray/white)
    for r in range(radius, 0, -1):
        # Create subtle gradient
        ratio = r / radius
        color = (
            int(230 + 25 * ratio),  # Red
            int(230 + 25 * ratio),  # Green 
            int(230 + 25 * ratio)   # Blue
        )
        draw.ellipse(
            [(center_x - r, center_y - r), (center_x + r, center_y + r)],
            fill=color
        )
    
    # Add some craters
    num_craters = 5
    for _ in range(num_craters):
        crater_x = center_x + random.randint(-radius//2, radius//2)
        crater_y = center_y + random.randint(-radius//2, radius//2)
        crater_size = random.randint(radius//10, radius//5)
        
        crater_color = (200, 200, 200)  # Slightly darker than the moon
        draw.ellipse(
            [(crater_x - crater_size, crater_y - crater_size),
             (crater_x + crater_size, crater_y + crater_size)],
            fill=crater_color
        )
    return pil_to_pygame(img)

def create_cloud(size, shape_type=None):
    # Choose random cloud shape if not specified
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if shape_type is None:
        shape_type = random.choice(["round", "elongated", "puffy", "wispy"])
    cloud_color = (255, 255, 255, 220)  # Slightly transparent white
    
    if shape_type == "round":
        # Simple round cloud (3-4 circles)
        circles = [
            (size[0]//3, size[1]//2, size[1]//2.5),  # Left circle
            (size[0]//2, size[1]//2.5, size[1]//2),  # Top circle
            (size[0]*2//3, size[1]//2, size[1]//2.5),  # Right circle
            (size[0]//2, size[1]//1.8, size[1]//2)   # Bottom circle
        ]
        
        for x, y, r in circles:
            draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=cloud_color)
    
    elif shape_type == "elongated":
        # Elongated cloud (horizontal)
        draw.ellipse(
            [(size[0]//6, size[1]//3), 
             (size[0]*5//6, size[1]*2//3)], 
            fill=cloud_color
        )
        bumps = 4
        for i in range(bumps):
            x = size[0]//6 + i * (size[0]*2//3) // (bumps-1)
            y = size[1]//3 - random.randint(0, size[1]//6)
            r = random.randint(size[1]//6, size[1]//4)
            draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=cloud_color)
    
    elif shape_type == "puffy":
        center_x, center_y = size[0]//2, size[1]//2
        main_radius = min(size[0], size[1])//3
        
        # Main center puff
        draw.ellipse(
            [(center_x-main_radius, center_y-main_radius),
             (center_x+main_radius, center_y+main_radius)],
            fill=cloud_color
        )
        
        # Multiple smaller puffs around
        num_puffs = random.randint(5, 8)
        for i in range(num_puffs):
            angle = i * (2 * math.pi / num_puffs)
            distance = main_radius * 0.8
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            r = main_radius * random.uniform(0.4, 0.7)
            draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=cloud_color)
    
    elif shape_type == "wispy":
        # Wispy, stretched cloud and wave line
        points = []
        center_y = size[1]//2
        num_points = 10
        for i in range(num_points):
            x = i * size[0]//(num_points-1)
            y = center_y + random.randint(-size[1]//6, size[1]//6)
            points.append((x, y))
        
        # Draw lines between points with varying width
        for i in range(1, len(points)):
            width = random.randint(size[1]//10, size[1]//5)
            draw.line([points[i-1], points[i]], fill=cloud_color, width=width)
        
        # Add some small puffs along the path
        for x, y in points[1:-1]:
            if random.random() < 0.7:  # 70% chance to add a puff
                r = random.randint(size[1]//12, size[1]//8)
                draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=cloud_color)
    
    return pil_to_pygame(img)

def create_basket(size):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw basket
    basket_color = (139, 69, 19)  # Brown
    wicker_color = (205, 133, 63)  # Light brown for wicker pattern
    draw.rectangle([(10, 20), (size[0]-10, size[1]-5)], fill=basket_color)
    draw.rectangle([(5, 15), (size[0]-5, 25)], fill=wicker_color)
    
    # Wicker pattern (horizontal lines)
    for y in range(35, size[1]-10, 10):
        draw.line([(10, y), (size[0]-10, y)], fill=wicker_color, width=2)
    
    # Wicker pattern (vertical lines)
    for x in range(15, size[0]-10, 15):
        draw.line([(x, 25), (x, size[1]-5)], fill=wicker_color, width=1)
    
    # Basket handle
    handle_height = 15
    draw.arc([(20, -handle_height*2), (size[0]-20, 30)], 180, 0, fill=wicker_color, width=3)
    
    return pil_to_pygame(img)

def create_egg(size, color_scheme=1):
    # Different egg color schemes
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if color_scheme == 1:
        main_color = (255, 255, 255)  # White
        accent_color = (245, 245, 245)  # Slightly off-white
    elif color_scheme == 2:
        main_color = (255, 230, 230)  # Light pink
        accent_color = (255, 200, 200)  # Darker pink
    else:
        main_color = (230, 230, 255)  # Light blue
        accent_color = (200, 200, 255)  # Darker blue
    
    # Draw egg shape
    width, height = size
    egg_x, egg_y = width//2, height//2
    egg_width, egg_height = width - 10, height - 6
    
    # Draw egg base
    draw.ellipse(
        [(egg_x - egg_width//2, egg_y - egg_height//2), 
         (egg_x + egg_width//2, egg_y + egg_height//2)], 
        fill=main_color, outline=(200, 200, 200)
    )
    # Add egg patterns or decorations based on color scheme
    if color_scheme == 1:
        # Add shine
        shine_w, shine_h = egg_width//4, egg_height//4
        draw.ellipse(
            [(egg_x - shine_w//2, egg_y - shine_h*1.5), 
             (egg_x + shine_w//2, egg_y - shine_h//2)], 
            fill=(255, 255, 255, 200)
        )
    elif color_scheme == 2: 
        # Add spots
        spots = 5
        for _ in range(spots):
            spot_x = random.randint(egg_x - egg_width//3, egg_x + egg_width//3)
            spot_y = random.randint(egg_y - egg_height//3, egg_y + egg_height//3)
            spot_size = random.randint(2, 5)
            draw.ellipse(
                [(spot_x - spot_size, spot_y - spot_size), 
                 (spot_x + spot_size, spot_y + spot_size)], 
                fill=accent_color
            )
    else: 
        # Add stripes
        stripes = 3
        stripe_width = 3
        for i in range(stripes):
            y_pos = egg_y - egg_height//4 + i * egg_height//3
            draw.line(
                [(egg_x - egg_width//3, y_pos), 
                 (egg_x + egg_width//3, y_pos)], 
                fill=accent_color, width=stripe_width
            )
    
    return pil_to_pygame(img)

def create_obstacle(size):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rock obstacle
    rock_color = (100, 100, 100)
    highlight_color = (150, 150, 150) 
    
    # Main rock shape
    draw.ellipse([(5, 5), (size[0]-5, size[1]-5)], fill=rock_color)
    
    # Add some texture/cracks to the rock
    for _ in range(3):
        x1 = random.randint(10, size[0]-10)
        y1 = random.randint(10, size[1]-10)
        x2 = random.randint(10, size[0]-10)
        y2 = random.randint(10, size[1]-10)
        draw.line([(x1, y1), (x2, y2)], fill=highlight_color, width=1)
    
    # Add highlights
    draw.ellipse(
        [(size[0]//3, size[1]//3), 
         (size[0]//3 + 5, size[1]//3 + 5)], 
        fill=highlight_color
    )
    return pil_to_pygame(img)

def create_star(size):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Star color
    star_color = (255, 255, 240)  # Slightly off-white
    
    # Star center
    center_x, center_y = size[0]//2, size[1]//2
    outer_radius = min(size[0], size[1])//2 - 2
    inner_radius = outer_radius // 2
    
    # Draw a 5-pointed star
    points = []
    for i in range(10):
        angle = math.pi/2 + i * math.pi/5
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle)
        points.append((x, y))
    
    draw.polygon(points, fill=star_color)
    return pil_to_pygame(img)

# Game assets
day_background = create_background(is_night=False)
night_background = create_background(is_night=True)
sun_img = create_sun((120, 120))
moon_img = create_moon((100, 100))
stars = []

# Create different cloud shapes
cloud_shapes = ["round", "elongated", "puffy", "wispy"]
cloud_imgs = {shape: create_cloud((random.randint(100, 180), random.randint(50, 80)), shape) for shape in cloud_shapes}
basket_img = create_basket((100, 70))
egg_imgs = [
    create_egg((30, 40), 1),
    create_egg((40, 50), 2),
    create_egg((35, 45), 3)
]
obstacle_img = create_obstacle((40, 40))
star_img = create_star((20, 20))

# Game variables
clock = pygame.time.Clock()
score = 0
lives = 3
game_over = False
basket_x = WIDTH // 2 - 50
basket_speed = 7

# Day-night cycle variables
game_start_time = time.time()
day_duration = 60  # 60 seconds = 1 minute per cycle
night_duration = 60  # 60 seconds for night as well
is_night = False
transition_duration = 5  # 5 seconds to transition
sky_color = SKY_BLUE  # Start with day sky
cycle_counter = 0  # Keep track of cycles

# Fixed positions for sun and moon
sun_x = 100
sun_y = 80  # Fixed position for sun
moon_x = WIDTH - 150
moon_y = 80  # Fixed position for moon

# Egg and obstacle properties
class FallingObject:
    def __init__(self, object_type, x=None):
        self.object_type = object_type
        if object_type == "obstacle":
            self.image = obstacle_img
            self.points = -1
        else:
            egg_idx = int(object_type[-1]) - 1
            self.image = egg_imgs[egg_idx]
            self.points = (egg_idx + 1) * 10
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x if x is not None else random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(3, 7)
    
    def update(self):
        self.y += self.speed
        
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
    
    def is_off_screen(self):
        return self.y > HEIGHT
    
    def collides_with_basket(self, basket_x, basket_y, basket_width):
        if (self.y + self.height > basket_y and
            self.x + self.width > basket_x and
            self.x < basket_x + basket_width):
            return True
        return False

# Clouds for background
class Cloud:
    def __init__(self):
        shape = random.choice(list(cloud_imgs.keys()))
        self.image = cloud_imgs[shape]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = random.randint(-self.width, WIDTH)
        self.y = random.randint(0, HEIGHT // 3)
        self.speed = random.uniform(0.5, 1.5)
        scale = random.uniform(0.7, 1.3)
        new_width = int(self.width * scale)
        new_height = int(self.height * scale)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.width, self.height = new_width, new_height
    
    def update(self):
        self.x += self.speed
        if self.x > WIDTH:
            # Reset cloud position and possibly change its shape
            shape = random.choice(list(cloud_imgs.keys()))
            self.image = cloud_imgs[shape]
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            scale = random.uniform(0.7, 1.3)
            new_width = int(self.width * scale)
            new_height = int(self.height * scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
            self.width, self.height = new_width, new_height
            self.x = -self.width
            self.y = random.randint(0, HEIGHT // 3)
            self.speed = random.uniform(0.5, 1.5)
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# Star for night sky
class Star:
    def __init__(self):
        self.image = star_img
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT // 2)
        self.twinkle_speed = random.uniform(0.02, 0.1)
        self.alpha = random.randint(50, 255)
        self.alpha_change = self.twinkle_speed * (1 if random.random() > 0.5 else -1)
    
    def update(self):
        # Make stars twinkle by changing alpha
        self.alpha += self.alpha_change
        if self.alpha >= 255 or self.alpha <= 50:
            self.alpha_change *= -1
    
    def draw(self, surface):
        # Apply alpha to star
        temp_img = self.image.copy()
        temp_img.set_alpha(int(self.alpha))
        surface.blit(temp_img, (self.x, self.y))

# Create initial clouds
clouds = [Cloud() for _ in range(8)] 
stars = [Star() for _ in range(40)]

# Falling objects
falling_objects = []
spawn_timer = 0
spawn_delay = 60  # Frames between spawns

# Basket properties
basket_y = HEIGHT - 100
basket_width = basket_img.get_width()
basket_height = basket_img.get_height()

# Font for text
font = pygame.font.SysFont(None, 36)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_over:
                # Reset game
                score = 0
                lives = 3
                game_over = False
                falling_objects = []
                game_start_time = time.time()
                spawn_timer = 0
                is_night = False
    
    current_time = time.time()
    
    # Game logic for active game
    if not game_over:
        time_elapsed = current_time - game_start_time
        cycle_duration = day_duration + night_duration
        time_in_cycle = time_elapsed % cycle_duration
        
        # Determine day or night based on cycle position
        is_night = time_in_cycle >= day_duration
        
        # Set the background based on day/night
        if not is_night:
            background = day_background
        else:
            background = night_background
        
        # Handle basket movement with smoother controls and boundary checks
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket_x = max(0, basket_x - basket_speed)
        if keys[pygame.K_RIGHT]:
            basket_x = min(WIDTH - basket_width, basket_x + basket_speed)
        
        # Update clouds
        for cloud in clouds:
            cloud.update()
        
        # Update stars during night
        if is_night:
            for star in stars:
                star.update()
                
        spawn_timer += 1
        adjusted_spawn_delay = max(30, spawn_delay - score // 100)
        
        if spawn_timer >= adjusted_spawn_delay:
            spawn_timer = 0
            obstacle_chance = min(0.4, 0.2 + score / 1000)
            if random.random() < obstacle_chance:
                falling_objects.append(FallingObject("obstacle"))
            else:
                egg_type = f"egg{random.randint(1, 3)}"
                if is_night and random.random() < 0.2:
                    obj = FallingObject(egg_type)
                    obj.points *= 2
                    falling_objects.append(obj)
                else:
                    falling_objects.append(FallingObject(egg_type))
        
        # Update falling objects with list comprehension for efficiency
        for obj in falling_objects[:]:
            obj.update()
            
            # Check for collisions with basket
            if obj.collides_with_basket(basket_x, basket_y, basket_width):
                if obj.object_type == "obstacle":
                    lives -= 1
                else:
                    score += obj.points
                falling_objects.remove(obj)
                continue
            
            if obj.is_off_screen():
                falling_objects.remove(obj)
        
        # Check for game over
        if lives <= 0:
            game_over = True
    
    # Draw everything
    screen.blit(background, (0, 0))
    
    if is_night:
        # Draw stars at night
        for star in stars:
            star.draw(screen)
        # Draw moon at night
        screen.blit(moon_img, (moon_x, moon_y))
    else:
        # Draw sun during day
        screen.blit(sun_img, (sun_x, sun_y))
    
    # Clouds
    for cloud in clouds:
        cloud.draw(screen)
    
    # Falling objects
    for obj in falling_objects:
        obj.draw(screen)
    
    # Basket
    screen.blit(basket_img, (basket_x, basket_y))
    
    # Score and lives with better contrast
    score_text = font.render(f"Score: {score}", True, BLACK if not is_night else WHITE)
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"Lives: {lives}", True, BLACK if not is_night else WHITE)
    screen.blit(lives_text, (WIDTH - 150, 10))
    
    # Show day/night status with countdown
    if not game_over:
        if not is_night:
            time_to_night = max(0, day_duration - time_in_cycle)
            time_text = font.render(f"Night in: {int(time_to_night)}s", True, BLACK)
        else:
            time_to_day = max(0, cycle_duration - time_in_cycle)
            time_text = font.render(f"Day in: {int(time_to_day)}s", True, WHITE)
        
        screen.blit(time_text, (WIDTH // 2 - 70, 10))
    
    # Game over message
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        screen.blit(overlay, (0, 0))
        game_over_text = font.render("GAME OVER! Press SPACE to play again", True, RED)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 240, HEIGHT // 2 - 20))
        screen.blit(final_score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    clock.tick(60)
# Quit pygame
pygame.quit()
sys.exit()