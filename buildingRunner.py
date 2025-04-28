import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
DELTA_TIME = 1/FPS
DEBUG = False 

# Display setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Building Jumper")

# Colors
BACKGROUND = (135, 206, 235)  # Sky blue
CLOUD_COLOR = (255, 255, 255)
COLORS = [
    (255, 150, 200),  # Pink
    (150, 200, 255),  # Light blue
    (200, 255, 150),  # Light green
    (255, 200, 150),  # Light orange
    (200, 150, 255)   # Purple
]
DARK_COLORS = [
    (220, 100, 180),  # Dark pink
    (100, 150, 220),  # Dark blue
    (150, 220, 100),  # Dark green
    (220, 150, 100),  # Dark orange
    (150, 100, 220)   # Dark purple
]
WINDOW_COLOR = (100, 200, 255)
WINDOW_SHINE = (150, 230, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
SUN_COLOR = (255, 215, 0)
BIRD_COLOR = (50, 50, 50)

# Game parameters
GRAVITY = 0.5
JUMP_FORCE = -14
BUILDING_SPEED = 3
PLAYER_SIZE = 30
GROUND_HEIGHT = 50
MAX_GAP = 120
COLLISION_BUFFER = 5
MIN_VELOCITY = 0.1

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.jumping = False
        self.on_ground = False
        self.on_building = None
        self.color = (255, 0, 0)
        self.jump_power = JUMP_FORCE

    def update(self, buildings):
        # Apply gravity
        self.vel_y += GRAVITY
        next_y = self.y + self.vel_y

        # Apply minimum velocity threshold
        if abs(self.vel_y) < MIN_VELOCITY:
            self.vel_y = 0

        # Check if player is on a building
        self.on_ground = False
        self.on_building = None

        for building in buildings:
            # Check if player is within the x-bounds of the building
            if (self.x + self.width > building.x and 
                self.x < building.x + building.width):
                # Check if player is landing on the building
                if (next_y + self.height >= building.y - COLLISION_BUFFER and 
                    self.y + self.height <= building.y + COLLISION_BUFFER):
                    self.on_ground = True
                    self.on_building = building
                    self.y = building.y - self.height
                    self.vel_y = 0
                    break

        # Only update y position if not on a building
        if not self.on_ground:
            self.y = next_y

        # Move with the building if on one
        if self.on_building:
            self.x -= BUILDING_SPEED

        # Keep player within screen bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

        # Check if player has fallen below the screen
        if self.y > HEIGHT:
            return False

        return True

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.jumping = True

    def move_left(self):
        self.x -= 5

    def move_right(self):
        self.x += 5

    def draw(self, surface):
        # Draw collision box if debug mode is on
        if DEBUG:
            pygame.draw.rect(surface, (255, 0, 0), 
                           (self.x, self.y, self.width, self.height), 1)

        # Draw player body
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        # Draw face
        pygame.draw.circle(surface, WHITE, 
                         (int(self.x + self.width*0.3), int(self.y + self.height*0.3)), 
                         int(self.width*0.1))
        pygame.draw.circle(surface, WHITE, 
                         (int(self.x + self.width*0.7), int(self.y + self.height*0.3)), 
                         int(self.width*0.1))
        pygame.draw.circle(surface, BLACK, 
                         (int(self.x + self.width*0.3), int(self.y + self.height*0.3)), 
                         int(self.width*0.05))
        pygame.draw.circle(surface, BLACK, 
                         (int(self.x + self.width*0.7), int(self.y + self.height*0.3)), 
                         int(self.width*0.05))

        # Expression
        if self.jumping:
            # Surprised expression when jumping
            pygame.draw.circle(surface, BLACK, 
                             (int(self.x + self.width*0.5), int(self.y + self.height*0.6)), 
                             int(self.width*0.1))
        else:
            # Smile when not jumping
            pygame.draw.arc(surface, BLACK, 
                          (int(self.x + self.width*0.25), int(self.y + self.height*0.5), 
                           self.width*0.5, self.height*0.3), 0, math.pi, 2)
class Building:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_index = random.randint(0, len(COLORS) - 1)
        self.color = COLORS[self.color_index]
        self.dark_color = DARK_COLORS[self.color_index]
        
    def update(self):
        self.x -= BUILDING_SPEED
        return self.x + self.width > 0
    
    def draw(self, surface):
        # Draw collision box if debug mode is on
        if DEBUG:
            pygame.draw.rect(surface, (0, 255, 0), 
                           (self.x, self.y, self.width, self.height), 1)

        # Main building structure
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Edges/shadows
        pygame.draw.rect(surface, self.dark_color, 
                        (self.x, self.y, self.width, self.height), 3)
        
        # Windows
        window_size = min(self.width, self.height) * 0.15
        max_windows_x = max(1, int(self.width / (window_size * 1.8)))
        max_windows_y = max(1, int(self.height / (window_size * 1.8)))
        
        for i in range(max_windows_x):
            for j in range(max_windows_y):
                window_x = self.x + window_size + i * (window_size * 1.8)
                window_y = self.y + window_size + j * (window_size * 1.8)
                
                if (window_x + window_size < self.x + self.width and 
                    window_y + window_size < self.y + self.height):
                    # Window
                    pygame.draw.rect(surface, WINDOW_COLOR, 
                                   (window_x, window_y, window_size, window_size))
                    
                    # Window shine
                    pygame.draw.polygon(surface, WINDOW_SHINE, [
                        (window_x, window_y),
                        (window_x + window_size*0.4, window_y),
                        (window_x, window_y + window_size*0.4)
                    ])
                    
                    # Window frame
                    pygame.draw.rect(surface, self.dark_color, 
                                   (window_x, window_y, window_size, window_size), 1)
        
        # Gold trim on larger buildings
        if self.height > 100:
            trim_y = self.y + self.height * 0.7
            pygame.draw.rect(surface, GOLD, 
                           (self.x - 5, trim_y, self.width + 10, self.height * 0.03))

class Cloud:
    def __init__(self):
        self.x = random.randint(WIDTH, WIDTH + 500)
        self.y = random.randint(50, 200)
        self.size = random.randint(30, 80)
        self.speed = random.uniform(0.5, 1.5)
        
    def update(self):
        self.x -= self.speed * DELTA_TIME * 60  # Make speed frame-rate independent
        return self.x > -self.size * 3
    
    def draw(self, surface):
        pygame.draw.circle(surface, CLOUD_COLOR, 
                         (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, CLOUD_COLOR, 
                         (int(self.x + self.size * 0.5), int(self.y - self.size * 0.3)), 
                         int(self.size * 0.7))
        pygame.draw.circle(surface, CLOUD_COLOR, 
                         (int(self.x + self.size), int(self.y)), 
                         int(self.size * 0.8))
        pygame.draw.circle(surface, CLOUD_COLOR, 
                         (int(self.x + self.size * 0.5), int(self.y + self.size * 0.3)), 
                         int(self.size * 0.6))

class Bird:
    def __init__(self):
        self.x = random.randint(WIDTH, WIDTH + 300)
        self.y = random.randint(100, 250)
        self.size = random.randint(5, 10)
        self.speed = random.uniform(1.5, 3)
        self.wing_up = False
        self.wing_timer = 0
        
    def update(self):
        self.x -= self.speed * DELTA_TIME * 60
        
        self.wing_timer += 1
        if self.wing_timer >= 10:
            self.wing_up = not self.wing_up
            self.wing_timer = 0
            
        return self.x > -50
    
    def draw(self, surface):
        if self.wing_up:
            pygame.draw.line(surface, BIRD_COLOR, 
                           (self.x, self.y), 
                           (self.x - self.size, self.y - self.size), 2)
            pygame.draw.line(surface, BIRD_COLOR, 
                           (self.x, self.y), 
                           (self.x + self.size, self.y - self.size), 2)
        else:
            pygame.draw.line(surface, BIRD_COLOR, 
                           (self.x, self.y), 
                           (self.x - self.size, self.y + self.size/2), 2)
            pygame.draw.line(surface, BIRD_COLOR, 
                           (self.x, self.y), 
                           (self.x + self.size, self.y + self.size/2), 2)

class Sun:
    def __init__(self):
        self.x = WIDTH - 100
        self.y = 100
        self.radius = 40
        self.rays = 12
        self.ray_length = 20
        self.ray_width = 3
        self.animation_counter = 0
        
    def update(self):
        self.animation_counter += 0.02 * DELTA_TIME * 60
        return True
    
    def draw(self, surface):
        pygame.draw.circle(surface, SUN_COLOR, (self.x, self.y), self.radius)
        
        for i in range(self.rays):
            angle = i * (2 * math.pi / self.rays) + self.animation_counter
            start_x = self.x + (self.radius) * math.cos(angle)
            start_y = self.y + (self.radius) * math.sin(angle)
            end_x = self.x + (self.radius + self.ray_length) * math.cos(angle)
            end_y = self.y + (self.radius + self.ray_length) * math.sin(angle)
            pygame.draw.line(surface, SUN_COLOR, 
                           (start_x, start_y), (end_x, end_y), 
                           self.ray_width)
def calculate_max_jump_distance():
    time_to_peak = abs(JUMP_FORCE) / GRAVITY
    time_of_jump = time_to_peak * 2
    horizontal_distance = BUILDING_SPEED * time_of_jump
    player_movement = 5 * time_of_jump
    return horizontal_distance + player_movement + PLAYER_SIZE + COLLISION_BUFFER

def create_building(buildings):
    last_x = WIDTH
    if buildings:
        last_x = buildings[-1].x + buildings[-1].width
    
    width = random.randint(80, 150)
    height = random.randint(100, 300)
    
    min_gap = 40
    max_jump = calculate_max_jump_distance()
    gap = random.randint(min_gap, min(MAX_GAP, int(max_jump * 0.8)))
    
    # Occasionally make an easier jump
    if random.random() < 0.3:
        gap = random.randint(min_gap, min_gap + 30)
    
    building_y = HEIGHT - height - GROUND_HEIGHT
    return Building(last_x + gap, building_y, width, height)

def show_game_over(surface, score):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    surface.blit(overlay, (0, 0))
    
    font = pygame.font.SysFont(None, 72)
    text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to restart", True, WHITE)
    
    surface.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3 - text.get_height()//2))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - score_text.get_height()//2))
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3 - restart_text.get_height()//2))

def show_score(surface, score):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    shadow_text = font.render(f"Score: {score}", True, BLACK)
    
    # Draw shadow
    surface.blit(shadow_text, (22, 22))
    # Draw text
    surface.blit(text, (20, 20))

def main():
    clock = pygame.time.Clock()
    
    def reset_game():
        player = Player(100, 300)
        
        buildings = []
        first_building = Building(50, HEIGHT - 200 - GROUND_HEIGHT, 200, 200)
        buildings.append(first_building)
        player.on_building = first_building
        player.y = first_building.y - player.height
        
        for _ in range(3):
            buildings.append(create_building(buildings))
        
        clouds = [Cloud() for _ in range(6)]
        birds = [Bird() for _ in range(4)]
        sun = Sun()
        
        return player, buildings, clouds, birds, sun, 0
    
    player, buildings, clouds, birds, sun, score = reset_game()
    game_over = False
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.jump()
                elif event.key == pygame.K_r and game_over:
                    player, buildings, clouds, birds, sun, score = reset_game()
                    game_over = False
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player.move_left()
            if keys[pygame.K_RIGHT]:
                player.move_right()
        
        # Update game state
        sun.update()
        clouds = [cloud for cloud in clouds if cloud.update()]
        birds = [bird for bird in birds if bird.update()]
        
        # Add new background elements
        if random.random() < 0.01 and len(clouds) < 10:
            clouds.append(Cloud())
        if random.random() < 0.005 and len(birds) < 6:
            birds.append(Bird())
        
        if not game_over:
            if not player.update(buildings):
                game_over = True
            
            buildings = [b for b in buildings if b.update()]
            
            if len(buildings) < 5:
                buildings.append(create_building(buildings))
            
            score += 1
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw background elements
        sun.draw(screen)
        for cloud in clouds:
            cloud.draw(screen)
        for bird in birds:
            bird.draw(screen)
        
        # Draw ground
        pygame.draw.rect(screen, (100, 70, 40), 
                        (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        pygame.draw.line(screen, (70, 40, 20), 
                        (0, HEIGHT - GROUND_HEIGHT), 
                        (WIDTH, HEIGHT - GROUND_HEIGHT), 3)
        
        # Draw game elements
        for building in buildings:
            building.draw(screen)
        player.draw(screen)
        
        # Draw UI
        show_score(screen, score)
                
        if game_over:
            show_game_over(screen, score)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()