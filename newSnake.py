import pygame
import random
import math

# Initialize pygame
pygame.init()
pygame.font.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCORE_FONT = pygame.font.SysFont('Arial', 28)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 64)

# Colors
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (0, 200, 0),
    "RED": (255, 0, 0),
    "BACKGROUND": (15, 15, 40),
    "SNAKE_BODY": (126, 217, 87),
    "SNAKE_SPOTS": (98, 168, 68),
    "EYE_WHITE": (255, 255, 255),
    "EYE_BLACK": (0, 0, 0),
    "FOOD": (255, 215, 0),
    "FOOD_OUTLINE": (184, 134, 11),
    "ASTEROID_DARK": (100, 84, 78),
    "ASTEROID_LIGHT": (150, 134, 119)
}

class Snake:
    def __init__(self):
        self.reset()
        self.time_counter = 0
        self.speed_boost = False
        self.boost_cooldown = 0
        self.boost_factor = 1.0
        
    def reset(self):
        # Start in the middle of the screen
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT // 2
        self.body = [(self.x, self.y)]
        self.direction = (0, -1)  # Moving up initially
        self.grow_pending = 3  # Start with length 4
        self.speed_boost = False
        self.boost_cooldown = 0
        self.boost_factor = 1.0  # Normal speed is reduced, boost brings it to normal/faster
        
        # Snake appearance
        self.body_colors = [
            COLORS["SNAKE_BODY"],
            (116, 207, 77),
            (136, 227, 97)
        ]
        self.spot_color = COLORS["SNAKE_SPOTS"]
        self.eye_color = COLORS["EYE_WHITE"]
        self.pupil_color = COLORS["EYE_BLACK"]
    
    def change_direction(self, dir_x, dir_y):
        # Prevent 180-degree turns
        if (dir_x, dir_y) != (-self.direction[0], -self.direction[1]):
            self.direction = (dir_x, dir_y)
            
            # Activate speed boost when key is pressed
            self.speed_boost = True
            self.boost_factor = 2.0  # Double speed during boost
            self.boost_cooldown = 10  # Duration of boost in frames
    
    def update_boost(self):
        # Handle boost cooldown
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1
        else:
            self.speed_boost = False
            self.boost_factor = 1.0  # Back to default speed factor
    
    def move(self):
        # Get current head position
        head_x, head_y = self.body[0]
        
        # Calculate new head position
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]
        
        # Insert new head at the beginning of the body list
        self.body.insert(0, (new_x, new_y))
        
        # Check if snake needs to grow
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            # Remove the tail if not growing
            self.body.pop()
        
        # Update time counter for animations
        self.time_counter += 0.1
        
        # Return new head position
        return new_x, new_y
    
    def check_collision(self):
        head_x, head_y = self.body[0]
        
        # Check wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Check self collision
        if (head_x, head_y) in self.body[1:]:
            return True
            
        return False
    
    def grow(self):
        self.grow_pending += 1
    
    def draw(self, surface):
        # Draw each segment of the snake
        for i, (x, y) in enumerate(self.body):
            # Calculate position for the segment
            pos_x = x * GRID_SIZE
            pos_y = y * GRID_SIZE
            
            # Determine segment color 
            color_index = i % len(self.body_colors)
            segment_color = self.body_colors[color_index]
            
            if self.speed_boost and i < 3:
                # Brighten the color
                r, g, b = segment_color
                boost_color = (min(255, r + 50), min(255, g + 50), min(255, b + 50))
                segment_color = boost_color
            
            # Add subtle wave effect to segments
            if i > 0:
                wave_offset = math.sin(self.time_counter + i * 0.3) * 2
                if self.direction[0] == 0:  # Moving vertically
                    pos_x += wave_offset
                else:  # Moving horizontally
                    pos_y += wave_offset
            
            # Calculate segment size
            if i == 0:  # Head
                segment_size = GRID_SIZE
            else:  # Body segments get slightly smaller toward tail
                tail_factor = max(0.7, 1.0 - (i / len(self.body) * 0.3))
                segment_size = int(GRID_SIZE * tail_factor)
            
            # Position adjustment for smaller segments
            pos_adjust = (GRID_SIZE - segment_size) // 2
            pos_x += pos_adjust
            pos_y += pos_adjust
            
            # Create rect for this segment
            rect = pygame.Rect(pos_x, pos_y, segment_size, segment_size)
            
            # Draw segment
            pygame.draw.rect(surface, segment_color, rect, border_radius=8)
            
            # Add spots to some body segments for variety
            if i > 0 and i % 3 == 0:
                spot_size = segment_size // 3
                spot_x = rect.centerx - spot_size // 2
                spot_y = rect.centery - spot_size // 2
                spot_rect = pygame.Rect(spot_x, spot_y, spot_size, spot_size)
                pygame.draw.rect(surface, self.spot_color, spot_rect, border_radius=4)
        
        # Draw eyes on the head
        head_x, head_y = self.body[0]
        head_rect = pygame.Rect(head_x * GRID_SIZE, head_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        # Draw eyes based on direction
        eye_size = GRID_SIZE // 5
        pupil_size = eye_size // 2
        
        # Calculate eye positions based on direction
        if self.direction == (0, -1):  # Up
            left_eye_pos = (head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = (head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
        elif self.direction == (0, 1):  # Down
            left_eye_pos = (head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
            right_eye_pos = (head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        elif self.direction == (-1, 0):  # Left
            left_eye_pos = (head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = (head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        else:  # Right
            left_eye_pos = (head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = (head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        
        # Draw eyes
        pygame.draw.circle(surface, self.eye_color, left_eye_pos, eye_size)
        pygame.draw.circle(surface, self.eye_color, right_eye_pos, eye_size)
        
        # Draw pupils with slight offset in movement direction
        left_pupil_pos = (left_eye_pos[0] + self.direction[0] * 2, left_eye_pos[1] + self.direction[1] * 2)
        right_pupil_pos = (right_eye_pos[0] + self.direction[0] * 2, right_eye_pos[1] + self.direction[1] * 2)
        
        pygame.draw.circle(surface, self.pupil_color, left_pupil_pos, pupil_size)
        pygame.draw.circle(surface, self.pupil_color, right_pupil_pos, pupil_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse_counter = 0
        self.pulse_direction = 1
        self.pulse_speed = 0.15
        
        # Food types and their properties
        self.food_types = {
            "standard": {
                "colors": [
                    ((50, 205, 50), (34, 139, 34)),    # Green
                    ((30, 144, 255), (0, 0, 139)),     # Blue
                    ((255, 105, 180), (199, 21, 133)), # Pink
                    ((148, 0, 211), (75, 0, 130)),     # Purple
                    ((255, 69, 0), (178, 34, 34))      # Red-Orange
                ],
                "points": 10,
                "rarity": 0.7,  # 70% chance
                "label": "R",
                "effect": None
            },
            "golden": {
                "colors": [((255, 215, 0), (184, 134, 11))],  # Gold
                "points": 25,
                "rarity": 0.2,  # 20% chance
                "label": "G",
                "effect": None
            },
            "shrink": {
                "colors": [((210, 0, 210), (145, 0, 145))],  # Purple
                "points": 30,
                "rarity": 0.1,  # 10% chance
                "label": "S",
                "effect": "shrink"
            }
        }
        
        self.type = "standard"  # Default type
        self.points = 10  # Default points
        self.effect = None  # Default effect
        self.spawn()
    
    def spawn(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
        
        # Determine food type based on rarity
        r = random.random()
        cumulative_rarity = 0
        for food_type, properties in self.food_types.items():
            cumulative_rarity += properties["rarity"]
            if r <= cumulative_rarity:
                self.type = food_type
                break
        
        # Set properties based on food type
        food_properties = self.food_types[self.type]
        self.color, self.outline_color = random.choice(food_properties["colors"])
        self.points = food_properties["points"]
        self.effect = food_properties["effect"]
        self.label = food_properties["label"]
    
    def update(self):
        # Update pulsing effect
        self.pulse_counter += self.pulse_speed * self.pulse_direction
        if self.pulse_counter > 5:
            self.pulse_direction = -1
        elif self.pulse_counter < 0:
            self.pulse_direction = 1
    
    def draw(self, surface):
        # Update pulsing effect
        self.update()
        
        # Calculate position and size
        x, y = self.position
        
        # Adjust size based on food type
        base_size_factor = 1.0
        if self.type == "golden":
            base_size_factor = 1.1  # Slightly larger
        elif self.type == "shrink":
            base_size_factor = 0.9  # Slightly smaller
        
        size_factor = base_size_factor + (self.pulse_counter / 25)
        food_size = int(GRID_SIZE * 0.8 * size_factor)
        
        # Draw glow with the food's color but with transparency
        glow_size = int(food_size * 1.5)
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        # Create glow color based on food color but with alpha
        r, g, b = self.color
        
        # Enhanced glow for golden food
        alpha = 40
        if self.type == "golden":
            alpha = 70  # Stronger glow
            
        glow_color = (r, g, b, alpha)  # Add alpha channel
        pygame.draw.circle(
            glow_surface,
            glow_color,
            (glow_size // 2, glow_size // 2),
            glow_size // 2
        )
        glow_x = x * GRID_SIZE + (GRID_SIZE - glow_size) // 2
        glow_y = y * GRID_SIZE + (GRID_SIZE - glow_size) // 2
        surface.blit(glow_surface, (glow_x, glow_y))
        
        # Draw main food
        rect = pygame.Rect(
            x * GRID_SIZE + (GRID_SIZE - food_size) // 2,
            y * GRID_SIZE + (GRID_SIZE - food_size) // 2,
            food_size,
            food_size
        )
        
        # Draw coin
        pygame.draw.circle(surface, self.color, rect.center, rect.width // 2)
        pygame.draw.circle(surface, self.outline_color, rect.center, rect.width // 2, 2)
        
        # Add text sign
        font_size = max(10, rect.width // 2)
        text_font = pygame.font.SysFont('Arial Bold', font_size)
        text_sign = text_font.render(self.label, True, COLORS["BLACK"])
        text_rect = text_sign.get_rect(center=rect.center)
        surface.blit(text_sign, text_rect)
        
        # Add shine
        shine_size = max(3, rect.width // 6)
        shine_rect = pygame.Rect(
            rect.centerx - rect.width // 4,
            rect.centery - rect.height // 4,
            shine_size,
            shine_size
        )
        pygame.draw.ellipse(surface, COLORS["WHITE"], shine_rect)
        
        # Extra particles for golden food
        if self.type == "golden":
            small_particles = 4
            for i in range(small_particles):
                angle = (2 * math.pi * i / small_particles) + (pygame.time.get_ticks() / 1000)
                distance = rect.width * 0.7
                particle_x = rect.centerx + math.cos(angle) * distance
                particle_y = rect.centery + math.sin(angle) * distance
                particle_size = shine_size // 2
                pygame.draw.circle(surface, COLORS["WHITE"], (particle_x, particle_y), particle_size)

class Asteroid:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # Random asteroid properties
        self.size = random.uniform(0.8, 1.2) * GRID_SIZE
        self.rotation = random.randint(0, 360)
        self.rot_speed = random.uniform(-0.5, 0.5)
        self.color = COLORS["ASTEROID_DARK"]
        
        # Generate a random polygon shape for the asteroid
        self.points = []
        num_points = random.randint(6, 10)
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Add some randomness to the radius
            distance = self.size * random.uniform(0.7, 1.0)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            self.points.append((x, y))
        
        # Create asteroid details
        self.details = []
        num_details = random.randint(2, 4)
        for _ in range(num_details):
            # Random position within the asteroid
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.2, 0.6) * self.size
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            # Random size for the crater
            radius = random.uniform(0.1, 0.25) * self.size
            self.details.append((x, y, radius))
    
    def update(self):
        # Rotate the asteroid
        self.rotation += self.rot_speed
    
    def draw(self, surface):
        # Calculate center position on the screen
        center_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        center_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        
        # Create a temporary surface for the asteroid
        surf_size = int(self.size * 2.5)
        asteroid_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        surf_center = surf_size // 2
        
        # Rotate points based on current rotation
        rad_rotation = math.radians(self.rotation)
        rotated_points = []
        for x, y in self.points:
            # Rotate the point
            rx = x * math.cos(rad_rotation) - y * math.sin(rad_rotation)
            ry = x * math.sin(rad_rotation) + y * math.cos(rad_rotation)
            # Move to center of surface
            rotated_points.append((surf_center + rx, surf_center + ry))
        
        # Draw the asteroid body
        pygame.draw.polygon(asteroid_surf, self.color, rotated_points)
        
        # Draw a lighter outline
        pygame.draw.polygon(asteroid_surf, COLORS["ASTEROID_LIGHT"], rotated_points, 2)
        
        # Draw craters/details
        for x, y, radius in self.details:
            # Rotate the crater position
            rx = x * math.cos(rad_rotation) - y * math.sin(rad_rotation)
            ry = x * math.sin(rad_rotation) + y * math.cos(rad_rotation)
            # Draw the crater
            crater_pos = (surf_center + rx, surf_center + ry)
            pygame.draw.circle(asteroid_surf, 
                              (max(0, self.color[0] - 30), 
                               max(0, self.color[1] - 30), 
                               max(0, self.color[2] - 30)), 
                              crater_pos, radius)
            pygame.draw.circle(asteroid_surf, COLORS["ASTEROID_LIGHT"], crater_pos, radius, 1)
        
        # Position to blit on main surface
        blit_pos = (center_x - surf_center, center_y - surf_center)
        surface.blit(asteroid_surf, blit_pos)

class ObstacleField:
    def __init__(self):
        self.asteroids = []
        self.grid_positions = []  # For collision detection
    
    def add_asteroid(self, grid_x, grid_y):
        self.asteroids.append(Asteroid(grid_x, grid_y))
        self.grid_positions.append((grid_x, grid_y))
    
    def update(self):
        for asteroid in self.asteroids:
            asteroid.update()
    
    def draw(self, surface):
        for asteroid in self.asteroids:
            asteroid.draw(surface)

def generate_obstacles(level):
    obstacles = ObstacleField()
    # More obstacles as level increases
    num_obstacles = min(level * 5, 50)  # Cap at 50 obstacles
    
    # Create obstacles near edges
    for _ in range(num_obstacles):
        side = random.choice(["left", "right"])
        if side == "left":
            x = random.randint(0, GRID_WIDTH // 4)
        else:
            x = random.randint(3 * GRID_WIDTH // 4, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        obstacles.add_asteroid(x, y)
    
    return obstacles

def draw_score(surface, score, level, snake_boosting):
    score_surface = SCORE_FONT.render(f"Score: {score}", True, COLORS["WHITE"])
    level_surface = SCORE_FONT.render(f"Level: {level}", True, COLORS["WHITE"])
    
    # Display boost status
    boost_color = COLORS["WHITE"]
    if snake_boosting:
        boost_color = (255, 215, 0)  # Gold for active boost
        boost_text = "BOOSTING"
    else:
        boost_color = (100, 100, 100)  # Gray for normal/slow speed
        boost_text = "NORMAL SPEED"
    
    boost_surface = SCORE_FONT.render(boost_text, True, boost_color)
    
    surface.blit(score_surface, (10, 10))
    surface.blit(level_surface, (10, 50))
    surface.blit(boost_surface, (10, 90))

def draw_food_legend(surface):
    # Draw a small legend for food types
    legend_font = pygame.font.SysFont('Arial', 16)
    
    legend_items = [
        ("R: Regular (10pts)", (50, 205, 50)),
        ("G: Golden (25pts)", (255, 215, 0)),
        ("S: Shrink (30pts)", (210, 0, 210))
    ]
    
    for i, (text, color) in enumerate(legend_items):
        text_surface = legend_font.render(text, True, COLORS["WHITE"])
        # Draw a small colored circle before text
        circle_pos = (SCREEN_WIDTH - 160, 20 + i * 25)
        text_pos = (SCREEN_WIDTH - 140, 15 + i * 25)
        
        pygame.draw.circle(surface, color, circle_pos, 8)
        pygame.draw.circle(surface, COLORS["WHITE"], circle_pos, 8, 1)
        surface.blit(text_surface, text_pos)

def draw_pause_screen(surface):
    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(COLORS["BLACK"])
    overlay.set_alpha(100)  # Less opaque than game over screen
    surface.blit(overlay, (0, 0))
    
    # Pause text
    pause_text = GAME_OVER_FONT.render("PAUSED", True, COLORS["WHITE"])
    resume_text = SCORE_FONT.render("Press SPACE to resume", True, COLORS["WHITE"])
    
    # Position text
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    
    # Draw text
    surface.blit(pause_text, pause_rect)
    surface.blit(resume_text, resume_rect)

def draw_game_over(surface, score, level):
    # Create overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(COLORS["BLACK"])
    overlay.set_alpha(180)
    surface.blit(overlay, (0, 0))
    
    # Game over text
    game_over_text = GAME_OVER_FONT.render("GAME OVER", True, COLORS["WHITE"])
    score_text = SCORE_FONT.render(f"Final Score: {score}", True, COLORS["WHITE"])
    restart_text = SCORE_FONT.render("Press SPACE to restart", True, COLORS["WHITE"])
    
    # Position text
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    
    # Draw text
    surface.blit(game_over_text, game_over_rect)
    surface.blit(score_text, score_rect)
    surface.blit(restart_text, restart_rect)

def draw_instructions(surface):
    # Create background overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((20, 20, 50))  # Slightly different than background
    surface.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    title_text = title_font.render("SPACE SNAKE", True, COLORS["WHITE"])
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    surface.blit(title_text, title_rect)
    
    # Instructions
    instruction_font = pygame.font.SysFont('Arial', 24)
    instructions = [
        "Use ARROW KEYS to move the snake",
        "Hold keys for SPEED BOOST",
        "Collect food to grow and score points:",
        "R: Regular food (10 pts)",
        "G: Golden food (25 pts)",
        "S: Shrink food (30 pts, reduces length)",
        "Avoid walls and asteroid obstacles",
        "Press SPACE to pause/resume",
        "Press ESC to quit"
    ]
    
    # Draw each instruction line
    for i, instruction in enumerate(instructions):
        text_surface = instruction_font.render(instruction, True, COLORS["WHITE"])
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
        surface.blit(text_surface, text_rect)
    
    # Skip instructions text
    skip_text = instruction_font.render("Press SPACE to start", True, (255, 255, 100))
    skip_rect = skip_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    surface.blit(skip_text, skip_rect)
    
def main():
    # Set up the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Snake")
    
    # Initialize game objects
    snake = Snake()
    food = Food()
    clock = pygame.time.Clock()
    
    # Game state variables
    score = 0
    level = 1
    game_over = False
    paused = False
    show_instructions = True
    global show_instructions_start_time
    show_instructions_start_time = pygame.time.get_ticks()
    
    obstacles = generate_obstacles(level)
    last_key_press_time = 0
    key_press_interval = 150  # milliseconds
    
    # Create stars for background
    stars = []
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        stars.append((x, y, size, brightness))
    
    # Make sure food doesn't spawn on obstacles or snake
    def respawn_food():
        while True:
            food.spawn()
            if food.position not in snake.body and food.position not in obstacles.grid_positions:
                break
    
    respawn_food()
    
    # Main game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if show_instructions:
                        # Skip instructions
                        show_instructions = False
                    elif game_over:
                        # Reset game
                        snake.reset()
                        score = 0
                        level = 1
                        obstacles = generate_obstacles(level)
                        respawn_food()
                        game_over = False
                    else:
                        # Toggle pause state
                        paused = not paused
                
                # Direction controls with speed boost on continuous press
                if not game_over and not paused and not show_instructions:
                    if event.key == pygame.K_UP:
                        snake.change_direction(0, -1)
                        last_key_press_time = current_time
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(0, 1)
                        last_key_press_time = current_time
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(-1, 0)
                        last_key_press_time = current_time
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(1, 0)
                        last_key_press_time = current_time
            
            # Check for key repeat to maintain speed boost
            elif event.type == pygame.KEYUP and not game_over and not paused and not show_instructions:
                # When key is released, start decreasing boost
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    snake.boost_cooldown = 5  # Short cooldown after release
        
        # Check if we should exit the instructions screen after 5 seconds
        if show_instructions and current_time - show_instructions_start_time > 5000:
            show_instructions = False
        
        # Update game state if not game over, not paused, and not showing instructions
        if not game_over and not paused and not show_instructions:
            # Check for continuous key presses to maintain speed boost
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                current_time = pygame.time.get_ticks()
                if current_time - last_key_press_time < key_press_interval:
                    # Continuous pressing detected
                    snake.speed_boost = True
                    snake.boost_factor = 2.0  # Double speed
                    snake.boost_cooldown = 5
                last_key_press_time = current_time
            
            # Update snake boost state
            snake.update_boost()
            
            # Update obstacles
            obstacles.update()
            
            # Move snake
            snake.move()
            
            # Check for food collision
            if snake.body[0] == food.position:
                # Apply food effects
                if food.effect == "shrink" and len(snake.body) > 3:
                    # Shrink the snake (remove up to 2 segments)
                    shrink_amount = min(2, len(snake.body) - 3)  # Keep at least 3 segments
                    for _ in range(shrink_amount):
                        snake.body.pop()
                else:
                    # Standard growth for normal and golden food
                    snake.grow()
                
                # Add points based on food type
                score += food.points
                
                # Level up every 100 points
                if score % 100 == 0:
                    level += 1
                    obstacles = generate_obstacles(level)
                
                # Respawn food
                respawn_food()
            
            # Check for collision with walls, self, or obstacles
            if snake.check_collision() or snake.body[0] in obstacles.grid_positions:
                game_over = True
        
        # Drawing
        # Fill background
        screen.fill(COLORS["BACKGROUND"])
        
        # Draw stars with simple twinkling
        for i, (x, y, size, brightness) in enumerate(stars):
            if i % 20 == int(pygame.time.get_ticks() / 200) % 20:
                pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size+1)
            else:
                pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        
        if show_instructions:
            # Draw instructions screen
            draw_instructions(screen)
        else:
            # Draw game elements
            obstacles.draw(screen)
            food.draw(screen)
            snake.draw(screen)
            
            # Draw score and level
            draw_score(screen, score, level, snake.speed_boost)
            
            # Draw food type legend
            draw_food_legend(screen)
            
            # Draw game over or pause screen if needed
            if game_over:
                draw_game_over(screen, score, level)
            elif paused:
                draw_pause_screen(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Base speed is now LOWER by default
        base_speed = min(4 + level, 15)  # Reduced base speed
        
        # Apply boost factor if active - brings speed to normal or faster
        current_speed = base_speed
        if snake.speed_boost:
            current_speed = base_speed * snake.boost_factor  # Double speed when boosting
        
        clock.tick(current_speed)
    
    pygame.quit()

if __name__ == "__main__":
    # Global variable for instruction screen timer
    show_instructions_start_time = 0
    main()