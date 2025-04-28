import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gem Sorting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (184, 115, 51)
DARK_BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
BLUE = (65, 105, 225)  # Diamond
GREEN = (46, 139, 87)  # Emerald
RED = (178, 34, 34)    # Ruby
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
SKY_BLUE = (135, 206, 235)
DARK_GRAY = (50, 50, 50)

# Font setup
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 48)

# Basket properties
basket = pygame.Rect(WIDTH // 2, HEIGHT - 50, 60, 40)
basket_speed = 5  
basket_types = ["diamond", "emerald", "ruby"]
basket_index = 0  
basket_change_cooldown = 0  

# Gem properties
gem = None
gem_speed = 2
spawn_timer = 0
gem_types = ["diamond", "emerald", "ruby", "bomb"]
score = 0
lives = 5
game_over = False
running = True
clock = pygame.time.Clock()

# Background elements
stars = []
for _ in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT//2)
    size = random.randint(1, 3)
    twinkle_speed = random.uniform(0.02, 0.1)
    twinkle_state = random.uniform(0, math.pi)
    stars.append({"x": x, "y": y, "size": size, "twinkle_speed": twinkle_speed, "twinkle_state": twinkle_state})

clouds = []
for _ in range(5):
    x = random.randint(-100, WIDTH+100)
    y = random.randint(30, 120)
    speed = random.uniform(0.2, 0.5)
    size = random.uniform(0.8, 1.5)
    clouds.append({"x": x, "y": y, "speed": speed, "size": size})

mountains = []
for i in range(3):
    height = random.randint(80, 150)
    width = random.randint(150, 250)
    x = i * (WIDTH // 3) - random.randint(0, 50)
    color_value = random.randint(70, 110)
    color = (color_value, color_value, color_value)
    mountains.append({"x": x, "height": height, "width": width, "color": color})

# Animation effects
gem_rotations = {}
particles = []
explosion_particles = []

# Function to draw a diamond
def draw_diamond(surface, position, size, rotation=0):
    x, y = position
    
    # Diamond shape points with rotation
    diamond_points = []
    for angle_offset in [0, 90, 180, 270]:
        angle = math.radians(angle_offset + rotation)
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        diamond_points.append((px, py))
    
    # Draw the main diamond shape
    pygame.draw.polygon(surface, BLUE, diamond_points)
    
    # Draw highlights
    highlight_angle1 = math.radians(45 + rotation)
    highlight_angle2 = math.radians(0 + rotation)
    highlight_angle3 = math.radians(225 + rotation)
    
    highlight_points = [
        (x + size//2 * math.cos(highlight_angle1), y + size//2 * math.sin(highlight_angle1)),
        (x + size//2 * math.cos(highlight_angle2), y + size//2 * math.sin(highlight_angle2)),
        (x + size//2 * math.cos(highlight_angle3), y + size//2 * math.sin(highlight_angle3))
    ]
    pygame.draw.polygon(surface, LIGHT_BLUE, highlight_points)
    
    # Draw outline
    pygame.draw.polygon(surface, BLACK, diamond_points, 1)

# Function to draw an emerald
def draw_emerald(surface, position, size, rotation=0):
    x, y = position
    
    # Emerald shape
    emerald_points = []
    for i in range(8):
        angle = math.pi/4 * i + math.pi/8 + math.radians(rotation)  # Add rotation
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        emerald_points.append((px, py))
    
    # Draw the main emerald shape
    pygame.draw.polygon(surface, GREEN, emerald_points)
    
    # Draw highlights
    highlight_angle1 = math.radians(315 + rotation)
    highlight_angle2 = math.radians(45 + rotation)
    highlight_angle3 = math.radians(180 + rotation)
    
    highlight_points = [
        (x + size//2 * math.cos(highlight_angle1), y + size//2 * math.sin(highlight_angle1)),
        (x + size//2 * math.cos(highlight_angle2), y + size//2 * math.sin(highlight_angle2)),
        (x + size//2 * math.cos(highlight_angle3), y + size//2 * math.sin(highlight_angle3))
    ]
    pygame.draw.polygon(surface, LIGHT_GREEN, highlight_points)
    
    # Draw outline
    pygame.draw.polygon(surface, BLACK, emerald_points, 1)

# Function to draw a ruby
def draw_ruby(surface, position, size, rotation=0):
    x, y = position
    
    # Ruby shape
    ruby_points = []
    for i in range(6):
        angle = math.pi/3 * i + math.radians(rotation)  # Add rotation
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        ruby_points.append((px, py))
    
    # Draw the main ruby shape
    pygame.draw.polygon(surface, RED, ruby_points)
    
    # Draw highlights
    highlight_angle1 = math.radians(240 + rotation)
    highlight_angle2 = math.radians(0 + rotation)
    highlight_angle3 = math.radians(120 + rotation)
    
    highlight_points = [
        (x + size//2 * math.cos(highlight_angle1), y + size//2 * math.sin(highlight_angle1)),
        (x + size//2 * math.cos(highlight_angle2), y + size//2 * math.sin(highlight_angle2)),
        (x + size//2 * math.cos(highlight_angle3), y + size//2 * math.sin(highlight_angle3))
    ]
    pygame.draw.polygon(surface, LIGHT_RED, highlight_points)
    
    # Draw outline
    pygame.draw.polygon(surface, BLACK, ruby_points, 1)

# Function to draw a bomb
def draw_bomb(surface, x, y):
    # Bomb body
    pygame.draw.circle(surface, BLACK, (x, y), 30)

    # Fuse base
    pygame.draw.rect(surface, BLACK, (x - 10, y - 50, 20, 15))

    # Fuse wire
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

# Function to draw animated background
def draw_background():
    # Draw sky gradient
    for y in range(HEIGHT):
        # Calculate gradient color
        gradient_factor = y / HEIGHT
        color = (
            int(SKY_BLUE[0] + (200 - SKY_BLUE[0]) * gradient_factor),
            int(SKY_BLUE[1] + (220 - SKY_BLUE[1]) * gradient_factor),
            int(SKY_BLUE[2] + (255 - SKY_BLUE[2]) * gradient_factor)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Draw stars with twinkling effect
    for star in stars:
        # Calculate twinkling effect
        star["twinkle_state"] += star["twinkle_speed"]
        brightness = int(200 + 55 * math.sin(star["twinkle_state"]))
        star_color = (brightness, brightness, brightness)
        
        # Draw star
        pygame.draw.circle(screen, star_color, (star["x"], star["y"]), star["size"])
    
    # Draw mountains in the distance
    for mountain in mountains:
        mountain_points = [
            (mountain["x"], HEIGHT - 100),  # Left base
            (mountain["x"] + mountain["width"] // 2, HEIGHT - 100 - mountain["height"]),  # Peak
            (mountain["x"] + mountain["width"], HEIGHT - 100),  # Right base
        ]
        pygame.draw.polygon(screen, mountain["color"], mountain_points)
        
        # Add snow on top
        snow_height = mountain["height"] // 4
        snow_points = [
            (mountain["x"] + mountain["width"] // 2 - snow_height, HEIGHT - 100 - mountain["height"] + snow_height),
            (mountain["x"] + mountain["width"] // 2, HEIGHT - 100 - mountain["height"]),
            (mountain["x"] + mountain["width"] // 2 + snow_height, HEIGHT - 100 - mountain["height"] + snow_height),
        ]
        pygame.draw.polygon(screen, WHITE, snow_points)
    
    # Draw moving clouds
    for cloud in clouds:
        # Move cloud
        cloud["x"] += cloud["speed"]
        if cloud["x"] > WIDTH + 100:
            cloud["x"] = -100
            cloud["y"] = random.randint(30, 120)
        
        # Draw cloud
        size = 30 * cloud["size"]
        pygame.draw.circle(screen, WHITE, (int(cloud["x"]), int(cloud["y"])), int(size))
        pygame.draw.circle(screen, WHITE, (int(cloud["x"] + size*0.8), int(cloud["y"])), int(size*0.7))
        pygame.draw.circle(screen, WHITE, (int(cloud["x"] - size*0.8), int(cloud["y"])), int(size*0.6))
        pygame.draw.circle(screen, WHITE, (int(cloud["x"]), int(cloud["y"] - size*0.5)), int(size*0.8))
    
    # Draw ground
    ground_rect = pygame.Rect(0, HEIGHT - 100, WIDTH, 100)
    pygame.draw.rect(screen, DARK_GRAY, ground_rect)
    
    # Draw floor tiles
    tile_size = 20
    for x in range(0, WIDTH, tile_size):
        for y in range(HEIGHT - 100, HEIGHT, tile_size):
            if (x // tile_size + y // tile_size) % 2 == 0:
                pygame.draw.rect(screen, (80, 80, 80), (x, y, tile_size, tile_size))
            else:
                pygame.draw.rect(screen, (60, 60, 60), (x, y, tile_size, tile_size))

# Create particle effect when catching gems
def create_catch_particles(x, y, color):
    for _ in range(20):
        speed_x = random.uniform(-3, 3)
        speed_y = random.uniform(-5, 0)
        size = random.randint(2, 5)
        lifetime = random.randint(20, 40)
        particles.append({
            "x": x, "y": y,
            "speed_x": speed_x, "speed_y": speed_y,
            "size": size, "color": color,
            "lifetime": lifetime
        })

# Create explosion effect when bomb hits
def create_explosion(x, y):
    for _ in range(50):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 10)
        speed_x = math.cos(angle) * speed
        speed_y = math.sin(angle) * speed
        size = random.randint(3, 8)
        lifetime = random.randint(30, 60)
        color_choice = random.choice([ORANGE, RED, YELLOW])
        explosion_particles.append({
            "x": x, "y": y,
            "speed_x": speed_x, "speed_y": speed_y,
            "size": size, "color": color_choice,
            "lifetime": lifetime
        })

# Update particles
def update_particles():
    global particles, explosion_particles
    
    # Regular particles
    for particle in particles[:]:
        particle["x"] += particle["speed_x"]
        particle["y"] += particle["speed_y"]
        particle["speed_y"] += 0.1  # Gravity
        particle["lifetime"] -= 1
        
        if particle["lifetime"] <= 0:
            particles.remove(particle)
    
    # Explosion particles
    for particle in explosion_particles[:]:
        particle["x"] += particle["speed_x"]
        particle["y"] += particle["speed_y"]
        particle["speed_x"] *= 0.95  # Slow down
        particle["speed_y"] *= 0.95  # Slow down
        particle["lifetime"] -= 1
        
        if particle["lifetime"] <= 0:
            explosion_particles.remove(particle)

# Draw particles
def draw_particles():
    # Regular particles
    for particle in particles:
        alpha = min(255, int(255 * particle["lifetime"] / 40))
        color = list(particle["color"])
        if len(color) == 3:  # RGB to RGBA
            color.append(alpha)
        else:  # Update alpha in RGBA
            color[3] = alpha
        
        s = pygame.Surface((particle["size"] * 2, particle["size"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (particle["size"], particle["size"]), particle["size"])
        screen.blit(s, (particle["x"] - particle["size"], particle["y"] - particle["size"]))
    
    # Explosion particles
    for particle in explosion_particles:
        alpha = min(255, int(255 * particle["lifetime"] / 60))
        color = list(particle["color"])
        if len(color) == 3:  # RGB to RGBA
            color.append(alpha)
        else:  # Update alpha in RGBA
            color[3] = alpha
        
        s = pygame.Surface((particle["size"] * 2, particle["size"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (particle["size"], particle["size"]), particle["size"])
        screen.blit(s, (particle["x"] - particle["size"], particle["y"] - particle["size"]))

# Draw chest with animation
def draw_chest(x, y, type_name):
    # Chest base
    pygame.draw.rect(screen, BROWN, (x - 30, y, 80, 40), border_radius=5)
    pygame.draw.rect(screen, DARK_BROWN, (x - 40, y - 10, 100, 20), border_radius=5)
    
    # Add chest details
    pygame.draw.rect(screen, GRAY, (x, y + 15, 20, 10))  # Lock
    
    # Draw three small gems on the chest to match its type
    gem_positions = [(x - 20, y + 10), (x + 10, y + 5), (x + 40, y + 10)]
    gem_color = BLUE if type_name == "diamond" else GREEN if type_name == "emerald" else RED
    highlight_color = LIGHT_BLUE if type_name == "diamond" else LIGHT_GREEN if type_name == "emerald" else LIGHT_RED
    
    for gem_pos in gem_positions:
        pygame.draw.circle(screen, gem_color, gem_pos, 5)
        pygame.draw.circle(screen, highlight_color, (gem_pos[0]-1, gem_pos[1]-1), 2)
    
    # Display chest type
    chest_label = font.render(f"{type_name.capitalize()}", True, BLACK)
    screen.blit(chest_label, (x - 25, y + 15))

# Main game loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit game
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                # Reset game
                score = 0
                lives = 5
                game_over = False
                gem = None
                basket_index = 0
                particles = []
                explosion_particles = []

    # Draw background
    draw_background()
    
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

        # Spawn new gem if none exists
        if gem is None and spawn_timer == 0:
            gem_x = random.randint(20, WIDTH - 40)
            gem_type = random.choices(gem_types, weights=[3, 3, 3, 2])[0]  
            gem_speed = random.randint(2, 5)
            gem = {"rect": pygame.Rect(gem_x, 0, 30, 30), "type": gem_type, "rotation": 0}
            spawn_timer = 60  # Delay next spawn
            
            # Initial rotation speed
            if gem_type != "bomb":
                gem_rotations[id(gem)] = random.uniform(-5, 5)  # Degrees per frame
            
        elif spawn_timer > 0:
            spawn_timer -= 1

        if gem:
            gem["rect"].y += gem_speed  # Move gem downward
            
            # Update gem rotation
            if gem["type"] != "bomb" and id(gem) in gem_rotations:
                gem["rotation"] += gem_rotations[id(gem)]

            # Check for collision with the basket
            if gem["rect"].y > HEIGHT - 50 and basket.colliderect(gem["rect"]):
                if gem["type"] == "bomb":
                    game_over = True  # Game ends if bomb is caught
                    create_explosion(gem["rect"].x + 15, gem["rect"].y + 15)
                elif gem["type"] == basket_type:
                    score += 10  # Correct gem caught
                    gem_color = BLUE if gem["type"] == "diamond" else GREEN if gem["type"] == "emerald" else RED
                    create_catch_particles(gem["rect"].x + 15, gem["rect"].y + 15, gem_color)
                else:
                    lives -= 1  # Wrong gem caught
                    gem_color = BLUE if gem["type"] == "diamond" else GREEN if gem["type"] == "emerald" else RED
                    create_catch_particles(gem["rect"].x + 15, gem["rect"].y + 15, gem_color)
                
                # Remove rotation entry
                if id(gem) in gem_rotations:
                    del gem_rotations[id(gem)]
                gem = None

            # Remove missed gem
            elif gem["rect"].y > HEIGHT:
                if gem["type"] != "bomb":
                    lives -= 1
                
                # Remove rotation entry
                if id(gem) in gem_rotations:
                    del gem_rotations[id(gem)]
                gem = None

        # Draw the basket
        draw_chest(basket.x, basket.y, basket_type)

        # Draw falling gem or bomb
        if gem:
            if gem["type"] == "diamond":
                draw_diamond(screen, (gem["rect"].x + 15, gem["rect"].y + 15), 15, gem["rotation"])
            elif gem["type"] == "emerald":
                draw_emerald(screen, (gem["rect"].x + 15, gem["rect"].y + 15), 15, gem["rotation"])
            elif gem["type"] == "ruby":
                draw_ruby(screen, (gem["rect"].x + 15, gem["rect"].y + 15), 15, gem["rotation"])
            else:
                draw_bomb(screen, gem["rect"].x + 15, gem["rect"].y + 15)

        # Update and draw particles
        update_particles()
        draw_particles()

        # Display score and lives
        score_text = font.render(f"Score: {score}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 30))

        # Display controls reminder
        controls = font.render("Left/Right to move   Up/Down to change gem type", True, BLACK)
        screen.blit(controls, (WIDTH // 2 - 150, 10))

    # Check game over conditions
    if lives <= 0:
        game_over = True
        game_over_reason = "Game Over! No Lives Left"
    elif game_over:
        game_over_reason = "Game Over! Bomb in the Chest"

    if game_over:
        # Keep drawing particles until they're all gone
        update_particles()
        draw_particles()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = title_font.render(game_over_reason, True, RED)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press SPACE to play again", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        
        screen.blit(game_over_text, text_rect)
        screen.blit(final_score_text, score_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(30)  # Control frame rate

pygame.quit()  # Exit game