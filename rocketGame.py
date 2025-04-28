import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 20)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (135, 206, 235)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.twinkle_speed = random.uniform(0.05, 0.2)
        self.brightness = random.uniform(0, math.pi)
    
    def update(self):
        self.brightness += self.twinkle_speed
        if self.brightness > 2 * math.pi:
            self.brightness = 0
    
    def draw(self, screen):
        brightness = abs(math.sin(self.brightness))
        color = (int(255 * brightness), int(255 * brightness), int(255 * brightness))
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

class FireParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(8, 16)
        self.lifetime = random.randint(15, 25)
        self.color = random.choice([RED, ORANGE, YELLOW])
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-3, -1.5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.size = max(0, self.size - 0.2)

    def draw(self, screen):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
class Shield:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40  # Shield width
        self.height = 48  # Shield height (20% taller than width)
        self.speed = 3
        self.color = (0, 128, 255)  # Bright blue
        self.collected = False

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        # Create the shield shape points
        points = [
            (self.x - self.width//2, self.y - self.height//2),  # Top left
            (self.x + self.width//2, self.y - self.height//2),  # Top right
            (self.x + self.width//2, self.y + self.height//3),  # Right middle
            (self.x, self.y + self.height//2),                  # Bottom point
            (self.x - self.width//2, self.y + self.height//3),  # Left middle
        ]

        # Draw main shield body (blue fill)
        pygame.draw.polygon(screen, self.color, points)
        
        # Draw metallic border (darker outline)
        pygame.draw.polygon(screen, (100, 100, 100), points, 3)  # Dark gray border
        
        # Draw shine effect (lighter inner border)
        pygame.draw.polygon(screen, (200, 200, 200), points, 1)  # Light gray inner line
                        
class Asteroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 50
        self.speed = 4
        self.particles = []
        
        self.points = []
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            r = self.radius + random.randint(-15, 15)
            px = r * math.cos(angle)
            py = r * math.sin(angle)
            self.points.append((px, py))
        
        self.angle = 0
        self.rotation_speed = random.uniform(-1, 1)

    def update(self):
        self.y += self.speed
        self.angle += self.rotation_speed
        
        if random.random() < 0.4:
            for _ in range(2):
                offset_x = random.randint(-self.radius//2, self.radius//2)
                self.particles.append(FireParticle(self.x + offset_x, self.y - self.radius))
        
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
        
        transformed_points = []
        for px, py in self.points:
            rotated_x = px * math.cos(self.angle) - py * math.sin(self.angle)
            rotated_y = px * math.sin(self.angle) + py * math.cos(self.angle)
            transformed_points.append((int(self.x + rotated_x), int(self.y + rotated_y)))
        pygame.draw.polygon(screen, BROWN, transformed_points)
        
        for _ in range(6):
            crater_x = self.x + random.randint(-self.radius//2, self.radius//2)
            crater_y = self.y + random.randint(-self.radius//2, self.radius//2)
            crater_size = random.randint(6, 12)
            pygame.draw.circle(screen, (90, 50, 15), (int(crater_x), int(crater_y)), crater_size)

class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.acceleration = 0.5
        self.max_speed = 5
        self.friction = 0.1
        self.flame_animation = 0
        self.lives = 1  # Start with 1 life
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Apply acceleration based on key presses
        if keys[pygame.K_LEFT]:
            self.velocity -= self.acceleration
        if keys[pygame.K_RIGHT]:
            self.velocity += self.acceleration
            
        # Apply friction when no keys are pressed
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            if abs(self.velocity) < self.friction:
                self.velocity = 0
            elif self.velocity > 0:
                self.velocity -= self.friction
            else:
                self.velocity += self.friction
        
        # Limit maximum speed
        self.velocity = max(min(self.velocity, self.max_speed), -self.max_speed)
        
        # Update position
        self.x += self.velocity
        
        # Keep rocket within screen bounds
        self.x = max(40, min(self.x, WIDTH - 40))
        
    def draw(self, screen):
        # Body
        body_points = [
            (self.x - 20, self.y - 60),
            (self.x + 20, self.y - 60),
            (self.x + 20, self.y + 20),
            (self.x - 20, self.y + 20)
        ]
        pygame.draw.polygon(screen, WHITE, body_points)
        
        # Nose cone
        nose_points = [
            (self.x - 20, self.y - 60),
            (self.x + 20, self.y - 60),
            (self.x, self.y - 90)
        ]
        pygame.draw.polygon(screen, RED, nose_points)
        
        # Window
        pygame.draw.circle(screen, LIGHT_BLUE, (int(self.x), self.y - 30), 15)
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), self.y - 30), 15, 2)
        
        # Fins
        left_fin = [
            (self.x - 20, self.y + 20),
            (self.x - 40, self.y + 20),
            (self.x - 20, self.y - 10)
        ]
        right_fin = [
            (self.x + 20, self.y + 20),
            (self.x + 40, self.y + 20),
            (self.x + 20, self.y - 10)
        ]
        pygame.draw.polygon(screen, RED, left_fin)
        pygame.draw.polygon(screen, RED, right_fin)
        
        # Flame animation
        self.flame_animation += 0.2
        flame_size = math.sin(self.flame_animation) * 5 + 20
        
        flame_points = [
            (self.x - 15, self.y + 20),
            (self.x + 15, self.y + 20),
            (self.x, self.y + 20 + flame_size)
        ]
        pygame.draw.polygon(screen, ORANGE, flame_points)
        
        inner_flame_points = [
            (self.x - 8, self.y + 20),
            (self.x + 8, self.y + 20),
            (self.x, self.y + 20 + flame_size * 0.7)
        ]
        pygame.draw.polygon(screen, YELLOW, inner_flame_points)

def create_star_field(num_stars):
    return [Star() for _ in range(num_stars)]
    
def check_collision(rocket, asteroid):
    # Simple circle collision detection
    distance = math.sqrt((rocket.x - asteroid.x)**2 + (rocket.y - asteroid.y)**2)
    return distance < (asteroid.radius + 30)  # 30 is approximate rocket radius
    
def display_score_and_lives(screen, score, lives):
    # Display Score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    score_rect = score_text.get_rect(topleft=(20, 20))
    screen.blit(score_text, score_rect)
    
    # Display Lives
    lives_text = font.render(f'Extra Lives: {lives - 1}', True, WHITE)  # -1 because first life isn't "extra"
    lives_rect = lives_text.get_rect(topleft=(20, 60))
    screen.blit(lives_text, lives_rect)

def check_shield_collision(rocket, shield):
    # Create a rectangular hitbox for both rocket and shield
    rocket_rect = pygame.Rect(rocket.x - 30, rocket.y - 45, 60, 90)  # Approximate rocket size
    shield_rect = pygame.Rect(shield.x - shield.width//2, shield.y - shield.height//2, 
                            shield.width, shield.height)
    
    return rocket_rect.colliderect(shield_rect)

def main():
    clock = pygame.time.Clock()
    asteroid = Asteroid(WIDTH//2, -100)
    rocket = Rocket(WIDTH//2, HEIGHT - 100)
    stars = create_star_field(150)
    shield = None
    shield_spawn_timer = 0
    score = 0
    
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        darkness = y / HEIGHT
        color = (0, 0, int(20 * (1 - darkness)))
        pygame.draw.line(background, color, (0, y), (WIDTH, y))
    
    running = True
    game_over = False
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('GAME OVER', True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    restart_font = pygame.font.Font(None, 36)
    restart_text = restart_font.render('Press SPACE to restart', True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    # Reset game
                    asteroid = Asteroid(WIDTH//2, -100)
                    rocket = Rocket(WIDTH//2, HEIGHT - 100)
                    shield = None
                    shield_spawn_timer = 0
                    score = 0
                    game_over = False

        if not game_over:
            # Update
            rocket.update()
            asteroid.update()
            for star in stars:
                star.update()
            
            # Shield spawning logic
            shield_spawn_timer += 1
            if shield_spawn_timer >= 300 and shield is None:  # Spawn shield every 5 seconds (300 frames)
                shield = Shield(random.randint(50, WIDTH-50), -50)
                shield_spawn_timer = 0

            # Update shield if it exists
            if shield:
                shield.update()
                # Check if rocket collected shield
                if check_shield_collision(rocket, shield):
                    rocket.lives += 1
                    shield = None
                # Remove shield if it goes off screen
                elif shield.y > HEIGHT + 50:
                    shield = None

            # Check for asteroid collision
            if check_collision(rocket, asteroid):
                if rocket.lives > 1:
                    rocket.lives -= 1
                    asteroid = Asteroid(random.randint(100, WIDTH-100), -100)
                else:
                    game_over = True
            
            # Check if asteroid has passed
            if asteroid.y > HEIGHT + 100:
                score += 10
                asteroid = Asteroid(random.randint(100, WIDTH-100), -100)

        # Draw
        screen.blit(background, (0, 0))
        
        for star in stars:
            star.draw(screen)
            
        if shield:
            shield.draw(screen)
            
        asteroid.draw(screen)
        rocket.draw(screen)
        
        if game_over:
            screen.blit(game_over_text, game_over_rect)
            screen.blit(restart_text, restart_rect)
            final_score_text = font.render(f'Final Score: {score}', True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            screen.blit(final_score_text, final_score_rect)
        else:
            display_score_and_lives(screen, score, rocket.lives)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()