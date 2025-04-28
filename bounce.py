import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 20
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -12  # Negative because y-axis is inverted in pygame
GROUND_HEIGHT = HEIGHT - 50  # Position of the ground
INITIAL_GROUND_SPEED = 3  # Initial speed at which the ground moves
INITIAL_OBSTACLE_SPEED = 5  # Initial speed at which obstacles move
SPEED_INCREASE_INTERVAL = 5  # Increase speed after this many points
SPEED_INCREASE_AMOUNT = 0.5  # How much to increase speed each time
OBSTACLE_SPAWN_RATE = 1500  # Time between obstacle spawns in milliseconds
OBSTACLE_MIN_GAP = 500  # Minimum time gap between obstacles

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (25, 25, 112)
CLOUD_WHITE = (240, 240, 240)
SUN_YELLOW = (255, 255, 0)
MOON_GRAY = (200, 200, 200)
STAR_COLOR = (255, 255, 200)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Jump Game")
clock = pygame.time.Clock()

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_y = 0
        self.on_ground = True
        self.jump_count = 0
        self.max_jumps = 1
    
    def update(self):
        # Apply gravity if the ball is not on the ground
        self.velocity_y += GRAVITY
        
        # Update position
        self.y += self.velocity_y
        
        # Check for collision with the ground
        if self.y + self.radius >= GROUND_HEIGHT:
            self.y = GROUND_HEIGHT - self.radius
            self.velocity_y = 0
            self.on_ground = True
            self.jump_count = 0
        else:
            self.on_ground = False
    
    def jump(self):
        # Only allow jump if the ball is on the ground or has jumps left
        if self.on_ground or (self.jump_count < self.max_jumps):
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False
            self.jump_count += 1
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        # Add a highlight for 3D effect
        pygame.draw.circle(surface, (255, 150, 150), (int(self.x - self.radius/3), int(self.y - self.radius/3)), self.radius//4)
    
    def get_rect(self):
        # Return a rectangle representing the ball's collision box
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), 
                           self.radius * 2, self.radius * 2)

class Obstacle:
    def __init__(self, x, y, width, height, speed):
        self.x = float(x)  # Store as float for smooth movement
        self.y = float(y)  # Store as float for smooth movement
        self.width = width
        self.height = height
        self.speed = speed
        self.passed = False
        self.color = BLUE
    
    def update(self):
        # Update position as float for smoother movement
        self.x -= self.speed
    
    def draw(self, surface):
        # Convert to int only when drawing
        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.width, self.height))
        # Add a highlight effect
        pygame.draw.rect(surface, (100, 100, 255), (int(self.x), int(self.y), self.width, 5))
    
    def get_rect(self):
        # Use integer coordinates for collision detection to prevent jitter
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width < 0

class ScrollingGround:
    def __init__(self, ground_height, width, speed):
        self.ground_height = ground_height
        self.width = width
        self.speed = speed
        self.segment_width = 100  # Width of one ground segment
        self.offset = 0.0  # Current offset for scrolling effect as float
        # Add some grass tufts
        self.grass_tufts = []
        for _ in range(15):
            x = random.randint(0, width)
            height = random.randint(5, 12)
            self.grass_tufts.append((x, height))
    
    def update(self):
        # Update the offset for scrolling using float for smoother movement
        self.offset = (self.offset + self.speed) % self.segment_width
        
        # Update grass tuft positions
        for i, (x, height) in enumerate(self.grass_tufts):
            new_x = x - self.speed
            if new_x < -10:
                new_x = self.width + random.randint(0, 20)
            self.grass_tufts[i] = (new_x, height)
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def draw(self, surface):
        # Draw the main ground area
        pygame.draw.rect(surface, GREEN, (0, self.ground_height, self.width, HEIGHT - self.ground_height))
        
        # Draw the darker segments for scrolling effect, using int for drawing
        segment_offset = int(self.offset)
        for x in range(-segment_offset, self.width, self.segment_width):
            pygame.draw.rect(surface, DARK_GREEN, (x, self.ground_height, self.segment_width // 2, 10))
        
        # Draw grass tufts
        for x, height in self.grass_tufts:
            pygame.draw.line(surface, DARK_GREEN, (x, self.ground_height), (x, self.ground_height - height), 2)

class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        # Create a more complex cloud shape with multiple circles
        self.circles = []
        base_size = random.randint(20, 40)
        num_circles = random.randint(4, 7)
        width = 0
        
        for i in range(num_circles):
            circle_size = base_size - random.randint(0, 10)
            x_offset = width
            y_offset = random.randint(-10, 10)
            self.circles.append((x_offset, y_offset, circle_size))
            width += circle_size // 2
        
        self.width = width + base_size // 2
        self.height = base_size * 2
        self.opacity = random.randint(180, 240)
    
    def update(self):
        self.x -= self.speed
        if self.x + self.width < 0:
            self.x = WIDTH + random.randint(50, 200)
            self.y = random.randint(50, 150)
            # Rebuild cloud with new dimensions
            base_size = random.randint(20, 40)
            num_circles = random.randint(4, 7)
            width = 0
            self.circles = []
            
            for i in range(num_circles):
                circle_size = base_size - random.randint(0, 10)
                x_offset = width
                y_offset = random.randint(-10, 10)
                self.circles.append((x_offset, y_offset, circle_size))
                width += circle_size // 2
            
            self.width = width + base_size // 2
            self.height = base_size * 2
    
    def draw(self, surface, time_factor):
        # Adjust cloud color based on time of day
        brightness = 240 + int(15 * time_factor)
        cloud_color = (brightness, brightness, brightness)
        
        # Create a temporary surface for the cloud with alpha
        cloud_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        
        # Draw multiple overlapping circles for a fluffy look
        for x_offset, y_offset, size in self.circles:
            pygame.draw.circle(cloud_surface, cloud_color + (self.opacity,), 
                              (x_offset + size, self.height//2 + y_offset), size)
        
        # Draw the cloud to the main surface
        surface.blit(cloud_surface, (int(self.x - 10), int(self.y - 10)))

class Star:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.brightness = random.random()
        self.twinkle_speed = random.uniform(0.02, 0.05)
    
    def update(self, time):
        # Make stars twinkle
        self.brightness = 0.5 + 0.5 * math.sin(time * self.twinkle_speed)
    
    def draw(self, surface, darkness_factor):
        # Only show stars when it's getting dark
        if darkness_factor > 0.3:
            alpha = int(self.brightness * 255 * min(1, darkness_factor * 2))
            brightness = int(200 + 55 * self.brightness)
            color = (brightness, brightness, brightness, alpha)
            
            # Create a small surface for the star with alpha
            star_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, color, (self.size, self.size), self.size)
            
            # Draw the star to the main surface
            surface.blit(star_surface, (int(self.x - self.size), int(self.y - self.size)))

class DynamicBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0  # Game time in seconds
        self.day_length = 60  # One day/night cycle lasts this many seconds
        self.mountains = []
        
        # Create some mountains in the background
        num_mountains = 5
        for i in range(num_mountains):
            height = random.randint(80, 150)
            width = random.randint(200, 400)
            x = i * (self.width // (num_mountains - 1)) - width // 2
            self.mountains.append((x, height, width))
        
        # Create clouds
        self.clouds = []
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(50, 150)
            cloud_speed = random.uniform(0.5, 1.5)
            self.clouds.append(Cloud(x, y, cloud_speed))
        
        # Create stars
        self.stars = []
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(10, GROUND_HEIGHT - 100)
            size = random.randint(1, 3)
            self.stars.append(Star(x, y, size))
    
    def update(self, dt):
        # Update game time
        self.time = (self.time + dt) % self.day_length
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
        
        # Update stars
        time_factor = self.get_time_factor()
        darkness_factor = 1 - time_factor if time_factor < 0.5 else time_factor - 0.5
        for star in self.stars:
            star.update(self.time)
    
    def get_time_factor(self):
        # Returns a value between 0 and 1 indicating time of day
        # 0 = midnight, 0.5 = noon, 1 = midnight again
        return self.time / self.day_length
    
    def draw(self, surface):
        time_factor = self.get_time_factor()
        
        # Calculate sky color based on time of day
        if time_factor < 0.5:  # Day to night transition
            day_progress = time_factor * 2  # 0 to 1
            r = int(SKY_BLUE[0] * day_progress + DARK_BLUE[0] * (1 - day_progress))
            g = int(SKY_BLUE[1] * day_progress + DARK_BLUE[1] * (1 - day_progress))
            b = int(SKY_BLUE[2] * day_progress + DARK_BLUE[2] * (1 - day_progress))
        else:  # Night to day transition
            night_progress = (time_factor - 0.5) * 2  # 0 to 1
            r = int(DARK_BLUE[0] * night_progress + SKY_BLUE[0] * (1 - night_progress))
            g = int(DARK_BLUE[1] * night_progress + SKY_BLUE[1] * (1 - night_progress))
            b = int(DARK_BLUE[2] * night_progress + SKY_BLUE[2] * (1 - night_progress))
        
        sky_color = (r, g, b)
        
        # Draw sky
        surface.fill(sky_color)
        
        # Draw stars
        darkness_factor = 1 - time_factor if time_factor < 0.5 else time_factor - 0.5
        for star in self.stars:
            star.draw(surface, darkness_factor)
        
        # Draw sun or moon
        if time_factor < 0.5:  # Day
            # Sun position
            sun_x = self.width * time_factor * 2
            sun_y = self.height * 0.3 - math.sin(time_factor * math.pi) * 150
            pygame.draw.circle(surface, SUN_YELLOW, (int(sun_x), int(sun_y)), 40)
        else:  # Night
            # Moon position
            moon_x = self.width * (time_factor - 0.5) * 2
            moon_y = self.height * 0.3 - math.sin((time_factor - 0.5) * math.pi) * 150
            pygame.draw.circle(surface, MOON_GRAY, (int(moon_x), int(moon_y)), 30)
        
        # Draw mountains with parallax effect
        for i, (x, height, width) in enumerate(self.mountains):
            mountain_color = (100 - i * 10, 100 - i * 10, 100 - i * 10)
            
            # Create mountain polygon
            points = [
                (x, GROUND_HEIGHT),
                (x + width // 2, GROUND_HEIGHT - height),
                (x + width, GROUND_HEIGHT)
            ]
            pygame.draw.polygon(surface, mountain_color, points)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(surface, time_factor)

def main():
    # Create the background
    background = DynamicBackground(WIDTH, HEIGHT)
    
    # Create the ball
    ball = Ball(WIDTH // 3, GROUND_HEIGHT - BALL_RADIUS, BALL_RADIUS)
    
    # Create the scrolling ground
    ground = ScrollingGround(GROUND_HEIGHT, WIDTH, INITIAL_GROUND_SPEED)
    
    # Obstacles
    obstacles = []
    last_obstacle_time = 0
    
    # Game variables
    score = 0
    current_obstacle_speed = INITIAL_OBSTACLE_SPEED
    last_speed_increase = 0
    
    # Game state
    game_active = True
    
    collision_detected = False
    
    # Game loop
    running = True
    last_time = pygame.time.get_ticks()
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    if game_active:
                        ball.jump()
                    else:
                        # Reset game
                        game_active = True
                        obstacles = []
                        score = 0
                        current_obstacle_speed = INITIAL_OBSTACLE_SPEED
                        last_speed_increase = 0
                        ground.set_speed(INITIAL_GROUND_SPEED)
                        ball = Ball(WIDTH // 3, GROUND_HEIGHT - BALL_RADIUS, BALL_RADIUS)
                        collision_detected = False
        
        # Update background
        background.update(dt)
        
        if game_active:
            # Update game objects
            ball.update()
            ground.update()
            
            # Check if it's time to increase speed, but only once per score threshold
            if score > 0 and score % SPEED_INCREASE_INTERVAL == 0 and score != last_speed_increase:
                current_obstacle_speed += SPEED_INCREASE_AMOUNT
                ground.set_speed(INITIAL_GROUND_SPEED + (SPEED_INCREASE_AMOUNT * (score // SPEED_INCREASE_INTERVAL)))
                last_speed_increase = score
            
            # Spawn obstacles with more control over timing
            if current_time - last_obstacle_time > OBSTACLE_SPAWN_RATE + random.randint(0, OBSTACLE_MIN_GAP):
                obstacle_height = random.randint(30, 80)
                # Place obstacles a bit further away to give player time to react as speed increases
                obstacle_x = WIDTH + 50  # Start slightly off-screen
                obstacle = Obstacle(obstacle_x, GROUND_HEIGHT - obstacle_height, 30, obstacle_height, current_obstacle_speed)
                
                # Randomize obstacle color a bit to match time of day
                time_factor = background.get_time_factor()
                if time_factor < 0.5:  # Day
                    color_adjust = int(50 * time_factor)
                    obstacle.color = (BLUE[0], BLUE[1], min(255, BLUE[2] + color_adjust))
                else:  # Night
                    color_adjust = int(50 * (1 - time_factor))
                    obstacle.color = (max(0, BLUE[0] - color_adjust), 
                                    max(0, BLUE[1] - color_adjust), 
                                    max(0, BLUE[2] - color_adjust))
                
                obstacles.append(obstacle)
                last_obstacle_time = current_time
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                
                # Check if ball has passed the obstacle
                if not obstacle.passed and obstacle.x + obstacle.width < ball.x - ball.radius:
                    obstacle.passed = True
                    score += 1
                
                # Remove obstacles that are off-screen
                if obstacle.is_offscreen():
                    obstacles.remove(obstacle)
            
            # Check for collisions
            ball_rect = ball.get_rect()
            for obstacle in obstacles:
                obstacle_rect = obstacle.get_rect()
                if ball_rect.colliderect(obstacle_rect):
                    collision_detected = True
                    game_active = False
                    break
        
        # Draw everything
        # Background first
        background.draw(screen)
        
        # Draw the ground
        ground.draw(screen)
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # Draw the ball
        ball.draw(screen)
        
        # Draw score with a more visible background
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        # Draw a semi-transparent background for the text
        text_bg = pygame.Surface((score_text.get_width() + 10, score_text.get_height() + 10), pygame.SRCALPHA)
        text_bg.fill((255, 255, 255, 180))
        screen.blit(text_bg, (15, 15))
        screen.blit(score_text, (20, 20))
        
        # Draw speed level
        speed_level = score // SPEED_INCREASE_INTERVAL
        if speed_level > 0:
            level_text = font.render(f"Speed Level: {speed_level}", True, BLACK)
            level_bg = pygame.Surface((level_text.get_width() + 10, level_text.get_height() + 10), pygame.SRCALPHA)
            level_bg.fill((255, 255, 255, 180))
            screen.blit(level_bg, (15, 55))
            screen.blit(level_text, (20, 60))
        
        # Draw instructions
        if game_active:
            instruction_text = font.render("Press SPACE to jump", True, BLACK)
            instruction_bg = pygame.Surface((instruction_text.get_width() + 10, instruction_text.get_height() + 10), pygame.SRCALPHA)
            instruction_bg.fill((255, 255, 255, 180))
            screen.blit(instruction_bg, (WIDTH - 255, 15))
            screen.blit(instruction_text, (WIDTH - 250, 20))
        
        # Draw game over message if game is not active
        if not game_active:
            if collision_detected:
                game_over_text = font.render("Game Over! Collision detected. Press SPACE to restart", True, RED)
            else:
                game_over_text = font.render("Game Over! Press SPACE to restart", True, RED)
            
            # Create a nice background for the game over message
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            text_bg = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 180))
            text_bg_rect = text_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
            
            screen.blit(text_bg, text_bg_rect)
            screen.blit(game_over_text, text_rect)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()