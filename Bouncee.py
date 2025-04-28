import pygame
import sys
import random
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 20
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -12
GROUND_HEIGHT = HEIGHT - 50
INITIAL_GROUND_SPEED = 3
INITIAL_OBSTACLE_SPEED = 5
SPEED_INCREASE_INTERVAL = 5
SPEED_INCREASE_AMOUNT = 0.5
OBSTACLE_SPAWN_RATE = 1500
OBSTACLE_MIN_GAP = 500

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (135, 206, 235)  # Sky blue

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Ball Jump Game")
clock = pygame.time.Clock()

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, num_particles=10):
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'color': color,
                'radius': random.uniform(2, 5),
                'life': 30
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            
            # Slight gravity effect
            particle['dy'] += 0.1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], 
                               (int(particle['x']), int(particle['y'])), 
                               int(particle['radius']))

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_y = 0
        self.on_ground = True
    
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
        else:
            self.on_ground = False
    
    def jump(self, particle_system=None):
        # Only allow jump if the ball is on or near the ground
        if self.on_ground or (GROUND_HEIGHT - (self.y + self.radius) < 5):
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False
            
            # Add particle effect if particle system is provided
            if particle_system:
                particle_system.add_particles(self.x, self.y + self.radius, (255, 100, 0), num_particles=15)
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        # Add a highlight for 3D effect
        pygame.draw.circle(surface, (255, 150, 150), (int(self.x - self.radius/3), int(self.y - self.radius/3)), self.radius//4)
    
    def get_rect(self):
        # Return a rectangle representing the ball's collision box
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), 
                           self.radius * 2, self.radius * 2)

class BackgroundManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clouds = []
        self.generate_clouds()
    
    def generate_clouds(self):
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height // 2)
            size = random.uniform(0.5, 2)
            speed = random.uniform(0.5, 1.5)
            self.clouds.append({
                'x': x, 
                'y': y, 
                'size': size, 
                'speed': speed
            })
    
    def update(self):
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > self.width:
                cloud['x'] = -100
    
    def draw(self, surface):
        # Draw sky
        surface.fill(LIGHT_BLUE)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud_size = int(50 * cloud['size'])
            pygame.draw.circle(surface, WHITE, 
                               (int(cloud['x']), int(cloud['y'])), 
                               cloud_size)
            pygame.draw.circle(surface, WHITE, 
                               (int(cloud['x'] + cloud_size), int(cloud['y'])), 
                               int(cloud_size * 0.8))
            pygame.draw.circle(surface, WHITE, 
                               (int(cloud['x'] - cloud_size), int(cloud['y'])), 
                               int(cloud_size * 0.6))

class Obstacle:
    def __init__(self, x, y, width, height, speed):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.speed = speed
        self.passed = False
        self.pattern_offset = random.uniform(0, 10)
        
        # Grey color palette for thorny obstacles
        self.base_color = (100, 100, 100)  # Dark grey
        self.highlight_color = (150, 150, 150)  # Lighter grey
        
        # Generate thorn positions
        self.thorns = self.generate_thorns()
    
    def generate_thorns(self):
        thorns = []
        num_thorns = int(self.width // 10)  # Number of thorns based on width
        for i in range(num_thorns):
            # Randomize thorn position and size
            x_pos = self.width * (i / num_thorns)
            thorn_height = random.uniform(5, 15)
            thorn_width = random.uniform(3, 7)
            direction = random.choice([-1, 1])  # Alternate thorn direction
            thorns.append({
                'x': x_pos,
                'height': thorn_height,
                'width': thorn_width,
                'direction': direction
            })
        return thorns
    
    def update(self):
        # Update position as float for smoother movement
        self.x -= self.speed
        # Subtle movement effect
        self.pattern_offset += 0.1
    
    def draw(self, surface):
        # Draw main obstacle body
        obstacle_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        pygame.draw.rect(surface, self.base_color, obstacle_rect)
        
        # Draw thorns
        for thorn in self.thorns:
            # Create thorn polygon
            thorn_points = [
                (int(self.x + thorn['x']), int(self.y)),
                (int(self.x + thorn['x'] - thorn['width']/2 * thorn['direction']), 
                 int(self.y - thorn['height'])),
                (int(self.x + thorn['x'] + thorn['width']/2 * thorn['direction']), 
                 int(self.y))
            ]
            pygame.draw.polygon(surface, self.highlight_color, thorn_points)
        
        # Add some texture
        for i in range(5):
            line_y = int(self.y + i * (self.height / 5))
            pygame.draw.line(surface, self.highlight_color, 
                             (int(self.x), line_y), 
                             (int(self.x + self.width), line_y), 
                             1)
    
    def get_rect(self):
        # Use integer coordinates for collision detection
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width < 0

class ScrollingGround:
    def __init__(self, ground_height, width, speed):
        self.ground_height = ground_height
        self.width = width
        self.speed = speed
        self.segment_width = 100
        self.offset = 0.0
    
    def update(self):
        # Update the offset for scrolling using float for smoother movement
        self.offset = (self.offset + self.speed) % self.segment_width
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def draw(self, surface):
        # Draw the main ground area
        pygame.draw.rect(surface, GREEN, (0, self.ground_height, self.width, HEIGHT - self.ground_height))
        
        # Draw the darker segments for scrolling effect
        segment_offset = int(self.offset)
        for x in range(-segment_offset, self.width, self.segment_width):
            pygame.draw.rect(surface, DARK_GREEN, (x, self.ground_height, self.segment_width // 2, 10))

def reset_game():
    """Reset all game state to initial conditions"""
    ball = Ball(WIDTH // 3, GROUND_HEIGHT - BALL_RADIUS, BALL_RADIUS)
    ground = ScrollingGround(GROUND_HEIGHT, WIDTH, INITIAL_GROUND_SPEED)
    particle_system = ParticleSystem()
    background_manager = BackgroundManager(WIDTH, HEIGHT)
    
    return {
        'ball': ball,
        'ground': ground,
        'particle_system': particle_system,
        'background_manager': background_manager,
        'obstacles': [],
        'score': 0,
        'current_obstacle_speed': INITIAL_OBSTACLE_SPEED,
        'last_speed_increase': 0,
        'game_active': True,
        'collision_detected': False,
        'last_obstacle_time': 0
    }

def main():
    # Initialize game state
    game_state = reset_game()
    
    # Game loop
    running = True
    try:
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        if game_state['game_active']:
                            game_state['ball'].jump(game_state['particle_system'])
                        else:
                            # Reset game
                            game_state = reset_game()
            
            if game_state['game_active']:
                # Update game objects
                game_state['ball'].update()
                game_state['ground'].update()
                game_state['background_manager'].update()
                game_state['particle_system'].update()
                
                # Check if it's time to increase speed
                if (game_state['score'] > 0 and 
                    game_state['score'] % SPEED_INCREASE_INTERVAL == 0 and 
                    game_state['score'] != game_state['last_speed_increase']):
                    game_state['current_obstacle_speed'] += SPEED_INCREASE_AMOUNT
                    game_state['ground'].set_speed(
                        INITIAL_GROUND_SPEED + 
                        (SPEED_INCREASE_AMOUNT * (game_state['score'] // SPEED_INCREASE_INTERVAL))
                    )
                    game_state['last_speed_increase'] = game_state['score']
                
                # Spawn obstacles
                if (current_time - game_state['last_obstacle_time'] > 
                    max(100, OBSTACLE_SPAWN_RATE + random.randint(0, OBSTACLE_MIN_GAP))):
                    obstacle_height = random.randint(30, 80)
                    obstacle_x = WIDTH + 50
                    obstacle = Obstacle(
                        obstacle_x, 
                        GROUND_HEIGHT - obstacle_height, 
                        30, 
                        obstacle_height, 
                        game_state['current_obstacle_speed']
                    )
                    game_state['obstacles'].append(obstacle)
                    game_state['last_obstacle_time'] = current_time
                
                # Update and manage obstacles
                for obstacle in game_state['obstacles'][:]:
                    obstacle.update()
                    
                    # Check if ball has passed the obstacle
                    if (not obstacle.passed and 
                        obstacle.x + obstacle.width < game_state['ball'].x - game_state['ball'].radius):
                        obstacle.passed = True
                        game_state['score'] += 1
                    
                    # Remove obstacles that are off-screen
                    if obstacle.is_offscreen():
                        game_state['obstacles'].remove(obstacle)
                
                # Check for collisions
                ball_rect = game_state['ball'].get_rect()
                for obstacle in game_state['obstacles']:
                    obstacle_rect = obstacle.get_rect()
                    if ball_rect.colliderect(obstacle_rect):
                        game_state['collision_detected'] = True
                        game_state['game_active'] = False
                        break
            
            # Draw everything
            game_state['background_manager'].draw(screen)
            game_state['ground'].draw(screen)
            
            # Draw obstacles
            for obstacle in game_state['obstacles']:
                obstacle.draw(screen)
            
            # Draw particles
            game_state['particle_system'].draw(screen)
            
            # Draw the ball
            game_state['ball'].draw(screen)
            
            # Draw score and other UI elements
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {game_state['score']}", True, BLACK)
            screen.blit(score_text, (20, 20))
            
            # Draw speed level (starting from 1)
            speed_level = max(1, game_state['score'] // SPEED_INCREASE_INTERVAL + 1)
            level_text = font.render(f"Speed Level: {speed_level}", True, BLACK)
            screen.blit(level_text, (20, 60))
            
            # Draw current obstacle speed
            speed_info = font.render(f"Obstacle Speed: {game_state['current_obstacle_speed']:.1f}", True, BLACK)
            screen.blit(speed_info, (20, 100))
            
            # Draw instructions
            if game_state['game_active']:
                instruction_text = font.render("Press SPACE to jump", True, BLACK)
                screen.blit(instruction_text, (WIDTH - 250, 20))
            
            # Draw game over screen
            if not game_state['game_active']:
                # Create a semi-transparent overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Semi-transparent black
                screen.blit(overlay, (0, 0))

                # Game over text
                font_large = pygame.font.SysFont(None, 72)
                font_medium = pygame.font.SysFont(None, 48)
                font_small = pygame.font.SysFont(None, 36)

                # Game Over title
                game_over_text = font_large.render("Game Over", True, WHITE)
                game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
                screen.blit(game_over_text, game_over_rect)

                # Score display
                score_text = font_medium.render(f"Your Score: {game_state['score']}", True, WHITE)
                score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(score_text, score_rect)

                # Restart instruction
                restart_text = font_small.render("Press SPACE button to restart", True, WHITE)
                restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
                screen.blit(restart_text, restart_rect)
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(FPS)
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()