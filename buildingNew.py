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
pygame.display.set_caption("Building Jumper - Night Edition")

# Colors
BACKGROUND = (20, 24, 45)  # Dark night blue
CLOUD_COLOR = (150, 150, 180)  # Darker clouds for night
BUILDING_COLORS = [
    (70, 80, 120),    # Navy blue
    (120, 60, 90),    # Dark magenta
    (80, 100, 110),   # Slate
    (100, 70, 100),   # Dark purple
    (60, 90, 110)     # Steel blue
]
BUILDING_LIGHTS = [
    (130, 160, 210),  # Light blue
    (210, 150, 180),  # Light pink
    (160, 190, 200),  # Light slate
    (180, 150, 190),  # Light purple
    (150, 180, 200)   # Light steel blue
]
WINDOW_COLOR = (250, 240, 170)  # Warm yellow light
WINDOW_SHINE = (255, 250, 200)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
MOON_COLOR = (240, 240, 220)
BIRD_COLOR = (50, 50, 75)
STAR_COLOR = (255, 255, 240)

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
        self.height = PLAYER_SIZE * 1.5  # Make player taller
        self.vel_y = 0
        self.jumping = False
        self.on_ground = False
        self.on_building = None
        self.color = (240, 200, 150)  # Skin tone
        self.jump_power = JUMP_FORCE
        self.arm_angle = 0
        self.leg_angle = 0

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

        # Update limb animation
        if self.jumping or not self.on_ground:
            self.arm_angle = -30  # Arms up when jumping
            self.leg_angle = 15   # Legs spread when jumping
        else:
            # Walking animation when on ground
            self.arm_angle = 20 * math.sin(pygame.time.get_ticks() * 0.01)
            self.leg_angle = 15 * math.sin(pygame.time.get_ticks() * 0.01)

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

        head_radius = self.width // 2
        head_center_x = self.x + self.width // 2
        head_center_y = self.y + head_radius
        
        # Draw head
        pygame.draw.circle(surface, self.color, (head_center_x, head_center_y), head_radius)
        
        # Draw eyes
        eye_offset_x = head_radius * 0.25
        eye_offset_y = head_radius * 0.1
        eye_size = head_radius * 0.2
        
        pygame.draw.circle(surface, WHITE, 
                         (int(head_center_x - eye_offset_x), int(head_center_y - eye_offset_y)), 
                         int(eye_size))
        pygame.draw.circle(surface, WHITE, 
                         (int(head_center_x + eye_offset_x), int(head_center_y - eye_offset_y)), 
                         int(eye_size))
        
        pygame.draw.circle(surface, BLACK, 
                         (int(head_center_x - eye_offset_x), int(head_center_y - eye_offset_y)), 
                         int(eye_size * 0.5))
        pygame.draw.circle(surface, BLACK, 
                         (int(head_center_x + eye_offset_x), int(head_center_y - eye_offset_y)), 
                         int(eye_size * 0.5))
        
        # Expression
        mouth_y = head_center_y + head_radius * 0.2
        if self.jumping:
            # Surprised expression when jumping
            pygame.draw.circle(surface, BLACK, 
                             (int(head_center_x), int(mouth_y)), 
                             int(head_radius * 0.15))
        else:
            pygame.draw.arc(surface, BLACK, 
                          (int(head_center_x - head_radius * 0.3), int(mouth_y - head_radius * 0.1),
                           head_radius * 0.6, head_radius * 0.3), 0, math.pi, 2)


class Building:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_index = random.randint(0, len(BUILDING_COLORS) - 1)
        self.color = BUILDING_COLORS[self.color_index]
        self.light_color = BUILDING_LIGHTS[self.color_index]
        self.windows = []
        self.create_windows()
        
    def create_windows(self):
        window_size = min(self.width, self.height) * 0.15
        max_windows_x = max(1, int(self.width / (window_size * 1.8)))
        max_windows_y = max(1, int(self.height / (window_size * 1.8)))
        
        for i in range(max_windows_x):
            for j in range(max_windows_y):
                window_x = self.x + window_size + i * (window_size * 1.8)
                window_y = self.y + window_size + j * (window_size * 1.8)
                
                if (window_x + window_size < self.x + self.width and 
                    window_y + window_size < self.y + self.height):
                    # Randomly decide if window is lit
                    is_lit = random.random() < 0.7
                    self.windows.append((window_x, window_y, window_size, is_lit))
        
    def update(self):
        self.x -= BUILDING_SPEED
        # Update windows positions
        for i in range(len(self.windows)):
            x, y, size, lit = self.windows[i]
            self.windows[i] = (x - BUILDING_SPEED, y, size, lit)
            
            # Occasionally toggle window light
            if random.random() < 0.005:
                self.windows[i] = (x - BUILDING_SPEED, y, size, not lit)
                
        return self.x + self.width > 0
    
    def draw(self, surface):
        # Draw collision box if debug mode is on
        if DEBUG:
            pygame.draw.rect(surface, (0, 255, 0), 
                           (self.x, self.y, self.width, self.height), 1)

        # Main building structure
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Edges/shadows
        pygame.draw.rect(surface, self.light_color, 
                        (self.x, self.y, self.width, self.height), 3)
        
        # Windows
        for window_x, window_y, window_size, is_lit in self.windows:
            if is_lit:
                # Lit window
                pygame.draw.rect(surface, WINDOW_COLOR, 
                               (window_x, window_y, window_size, window_size))
                
                # Window shine
                pygame.draw.polygon(surface, WINDOW_SHINE, [
                    (window_x, window_y),
                    (window_x + window_size*0.4, window_y),
                    (window_x, window_y + window_size*0.4)
                ])
            else:
                # Dark window
                pygame.draw.rect(surface, (40, 40, 60), 
                               (window_x, window_y, window_size, window_size))
            
            # Window frame
            pygame.draw.rect(surface, self.light_color, 
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


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT * 0.7)
        self.size = random.uniform(1, 3)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.offset = random.uniform(0, 2 * math.pi)
        
    def update(self):
        return True
    
    def draw(self, surface):
        # Twinkle effect
        brightness = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.offset)
        color = (int(STAR_COLOR[0] * brightness), 
                 int(STAR_COLOR[1] * brightness), 
                 int(STAR_COLOR[2] * brightness))
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Moon:
    def __init__(self):
        self.x = WIDTH - 100
        self.y = 100
        self.radius = 40
        self.crater_count = 7
        self.craters = []
        
        # Create random craters
        for _ in range(self.crater_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius * 0.7)
            x_offset = distance * math.cos(angle)
            y_offset = distance * math.sin(angle)
            size = random.uniform(3, 8)
            self.craters.append((x_offset, y_offset, size))
        
    def update(self):
        return True
    
    def draw(self, surface):
        # Main moon
        pygame.draw.circle(surface, MOON_COLOR, (self.x, self.y), self.radius)
        
        # Draw moon shadow
        shadow_rect = pygame.Rect(
            self.x - self.radius, 
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        shadow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 100), 
                         (self.radius, self.radius), self.radius)
        shadow_surface.set_alpha(50)
        surface.blit(shadow_surface, (self.x - self.radius, self.y - self.radius))
        
        # Craters
        for x_offset, y_offset, size in self.craters:
            crater_x = self.x + x_offset
            crater_y = self.y + y_offset
            pygame.draw.circle(surface, (200, 200, 190), 
                             (int(crater_x), int(crater_y)), size)
            # Crater shadow
            pygame.draw.circle(surface, (180, 180, 170), 
                             (int(crater_x), int(crater_y)), size, 1)


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
        stars = [Star() for _ in range(40)]
        moon = Moon()
        
        return player, buildings, clouds, birds, stars, moon, 0
    
    player, buildings, clouds, birds, stars, moon, score = reset_game()
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
                    player, buildings, clouds, birds, stars, moon, score = reset_game()
                    game_over = False
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player.move_left()
            if keys[pygame.K_RIGHT]:
                player.move_right()
        
        # Update game state
        moon.update()
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
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw background elements
        moon.draw(screen)
        for cloud in clouds:
            cloud.draw(screen)
        for bird in birds:
            bird.draw(screen)
        
        # Draw ground
        pygame.draw.rect(screen, (40, 30, 60), 
                        (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        pygame.draw.line(screen, (30, 20, 40), 
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