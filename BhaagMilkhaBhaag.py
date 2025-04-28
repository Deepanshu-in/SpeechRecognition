import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
GROUND_Y = SCREEN_HEIGHT - 50
GRAVITY = 1
JUMP_FORCE = -16
SPEED_INCREASE = 0.1
INITIAL_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 69, 0)  # Red-orange for bird head
YELLOW = (255, 255, 0)  # Yellow for bird body
DARK_GRAY = (50, 50, 50)  # For bird wings
GREEN = (34, 139, 34)  # For tree

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bhaag Milkha Bhaag")
clock = pygame.time.Clock()

# Game variables
game_speed = INITIAL_SPEED
score = 0
high_score = 0
game_over = False
obstacles = []
obstacle_timer = 0
# Track passed obstacles for scoring
passed_obstacles = set()

class Character:
    def __init__(self):
        self.x = 80
        self.y = GROUND_Y
        self.normal_width = 40
        self.normal_height = 70
        self.crouch_width = 60
        self.crouch_height = 40
        self.width = self.normal_width
        self.height = self.normal_height
        self.velocity = 0
        self.is_jumping = False
        self.is_crouching = False
        
        # Create character sprites
        self.initialize_sprites()
    
    def initialize_sprites(self):
        # Create a surface for the normal character
        self.normal_sprite = pygame.Surface((self.normal_width, self.normal_height), pygame.SRCALPHA)
        
        # Draw cartoon character (stylized version of the image)
        # Head
        pygame.draw.ellipse(self.normal_sprite, (255, 204, 153), (5, 0, 30, 25))  # Face
        pygame.draw.rect(self.normal_sprite, (139, 69, 19), (5, 0, 30, 10))  # Hair
        pygame.draw.rect(self.normal_sprite, (80, 80, 80), (10, 10, 20, 5))  # Glasses
        pygame.draw.circle(self.normal_sprite, (0, 191, 255), (15, 13), 3)  # Eyes
        pygame.draw.circle(self.normal_sprite, (0, 191, 255), (25, 13), 3)  # Eyes
        pygame.draw.rect(self.normal_sprite, (139, 69, 19), (15, 20, 10, 3))  # Beard
        
        # Body
        pygame.draw.rect(self.normal_sprite, (105, 105, 105), (10, 25, 20, 30))  # Jacket
        pygame.draw.rect(self.normal_sprite, (245, 245, 220), (15, 25, 10, 20))  # Shirt
        pygame.draw.rect(self.normal_sprite, (50, 50, 50), (10, 55, 9, 15))  # Left leg
        pygame.draw.rect(self.normal_sprite, (50, 50, 50), (21, 55, 9, 15))  # Right leg
        pygame.draw.rect(self.normal_sprite, (105, 105, 105), (10, 55 + 15, 9, 5))  # Left shoe
        pygame.draw.rect(self.normal_sprite, (105, 105, 105), (21, 55 + 15, 9, 5))  # Right shoe
        
        # Jump sprite (same as normal but with bent legs)
        self.jump_sprite = pygame.Surface((self.normal_width, self.normal_height), pygame.SRCALPHA)
        # Copy the top part
        self.jump_sprite.blit(self.normal_sprite, (0, 0), (0, 0, self.normal_width, 55))
        # Draw bent legs
        pygame.draw.rect(self.jump_sprite, (50, 50, 50), (7, 55, 9, 10))  # Left leg bent
        pygame.draw.rect(self.jump_sprite, (50, 50, 50), (24, 55, 9, 10))  # Right leg bent
        pygame.draw.rect(self.jump_sprite, (105, 105, 105), (0, 60, 10, 5))  # Left shoe
        pygame.draw.rect(self.jump_sprite, (105, 105, 105), (30, 60, 10, 5))  # Right shoe
        
        # Crouch sprite (shorter and wider)
        self.crouch_sprite = pygame.Surface((self.crouch_width, self.crouch_height), pygame.SRCALPHA)
        # Draw crouched character
        # Head (smaller)
        pygame.draw.ellipse(self.crouch_sprite, (255, 204, 153), (15, 0, 25, 20))  # Face
        pygame.draw.rect(self.crouch_sprite, (139, 69, 19), (15, 0, 25, 8))  # Hair
        pygame.draw.rect(self.crouch_sprite, (80, 80, 80), (18, 8, 18, 4))  # Glasses
        pygame.draw.circle(self.crouch_sprite, (0, 191, 255), (22, 10), 2)  # Eyes
        pygame.draw.circle(self.crouch_sprite, (0, 191, 255), (30, 10), 2)  # Eyes
        
        # Body (wider, lower)
        pygame.draw.rect(self.crouch_sprite, (105, 105, 105), (5, 20, 50, 15))  # Jacket
        pygame.draw.rect(self.crouch_sprite, (245, 245, 220), (20, 20, 20, 10))  # Shirt
        pygame.draw.rect(self.crouch_sprite, (50, 50, 50), (10, 35, 40, 5))  # Legs
        
        # Run animation sprites (two alternating poses)
        self.run_sprites = []
        
        # Run sprite 1 (leg forward)
        run_sprite1 = self.normal_sprite.copy()
        # Clear leg area and redraw
        pygame.draw.rect(run_sprite1, (0, 0, 0, 0), (10, 55, 20, 20), 0)
        pygame.draw.rect(run_sprite1, (50, 50, 50), (10, 55, 9, 15))  # Left leg
        pygame.draw.rect(run_sprite1, (50, 50, 50), (21, 55, 9, 10))  # Right leg (shorter/raised)
        pygame.draw.rect(run_sprite1, (105, 105, 105), (10, 55 + 15, 9, 5))  # Left shoe
        pygame.draw.rect(run_sprite1, (105, 105, 105), (21, 55 + 10, 9, 5))  # Right shoe
        
        # Run sprite 2 (other leg forward)
        run_sprite2 = self.normal_sprite.copy()
        # Clear leg area and redraw
        pygame.draw.rect(run_sprite2, (0, 0, 0, 0), (10, 55, 20, 20), 0)
        pygame.draw.rect(run_sprite2, (50, 50, 50), (10, 55, 9, 10))  # Left leg (shorter/raised)
        pygame.draw.rect(run_sprite2, (50, 50, 50), (21, 55, 9, 15))  # Right leg
        pygame.draw.rect(run_sprite2, (105, 105, 105), (10, 55 + 10, 9, 5))  # Left shoe
        pygame.draw.rect(run_sprite2, (105, 105, 105), (21, 55 + 15, 9, 5))  # Right shoe
        
        self.run_sprites = [run_sprite1, run_sprite2]
        self.current_sprite = 0
        self.animation_speed = 5
        self.animation_counter = 0
    
    def jump(self):
        if not self.is_jumping and not self.is_crouching:
            self.velocity = JUMP_FORCE
            self.is_jumping = True
    
    def crouch(self, is_crouching):
        if not self.is_jumping:
            self.is_crouching = is_crouching
            if is_crouching:
                self.width = self.crouch_width
                self.height = self.crouch_height
            else:
                self.width = self.normal_width
                self.height = self.normal_height
    
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Check ground
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.velocity = 0
            self.is_jumping = False
        
        # Animation
        if not self.is_jumping and not self.is_crouching:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.current_sprite = (self.current_sprite + 1) % len(self.run_sprites)
                self.animation_counter = 0
    
    def draw(self):
        if self.is_jumping:
            screen.blit(self.jump_sprite, (self.x, self.y - self.height))
        elif self.is_crouching:
            screen.blit(self.crouch_sprite, (self.x, self.y - self.height))
        else:
            screen.blit(self.run_sprites[self.current_sprite], (self.x, self.y - self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

class YellowBird:
    def __init__(self, x, is_low=False):
        self.x = x
        self.width = 50
        self.height = 30
        self.is_low = is_low
        # Bird height - lower birds require crouching
        self.y = GROUND_Y - (40 if is_low else 80)
        
        # Wing animation state
        self.wing_position = 0  # 0 to 3 for animation
        self.animation_speed = 4
        self.animation_counter = 0
        
        # Create bird sprites
        self.sprites = self.create_bird_sprites()
    
    def create_bird_sprites(self):
        sprites = []
        
        # Create 4 wing positions for animation
        for wing_pos in range(4):
            sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw yellow body
            pygame.draw.ellipse(sprite, YELLOW, (10, 5, 30, 20))
            
            # Draw red-orange head
            pygame.draw.circle(sprite, RED, (10, 15), 10)
            
            # Draw beak
            pygame.draw.polygon(sprite, BLACK, [(0, 15), (5, 12), (5, 18)])
            
            # Draw eye
            pygame.draw.circle(sprite, BLACK, (8, 12), 2)
            
            # Draw wings based on position
            if wing_pos == 0:  # Wings down
                pygame.draw.ellipse(sprite, DARK_GRAY, (15, 15, 25, 10))
            elif wing_pos == 1:  # Wings mid-down
                pygame.draw.ellipse(sprite, DARK_GRAY, (15, 10, 25, 12))
                pygame.draw.line(sprite, DARK_GRAY, (30, 10), (40, 5), 2)
                pygame.draw.line(sprite, DARK_GRAY, (35, 10), (45, 8), 2)
            elif wing_pos == 2:  # Wings horizontal
                pygame.draw.ellipse(sprite, DARK_GRAY, (15, 8, 20, 8))
                pygame.draw.polygon(sprite, DARK_GRAY, [(25, 8), (45, 0), (45, 15), (25, 15)])
                for i in range(5):
                    pygame.draw.line(sprite, BLACK, (30 + i*3, 4), (30 + i*3, 12), 1)
            else:  # Wings up
                pygame.draw.ellipse(sprite, DARK_GRAY, (15, 5, 15, 8))
                pygame.draw.polygon(sprite, DARK_GRAY, [(22, 5), (40, -10), (45, 5), (30, 12)])
                for i in range(5):
                    pygame.draw.line(sprite, BLACK, (28 + i*3, 2), (25 + i*4, 10), 1)
            
            # Draw tail feathers
            pygame.draw.polygon(sprite, DARK_GRAY, [(35, 10), (50, 5), (50, 15), (35, 15)])
            
            sprites.append(sprite)
        
        return sprites
    
    def update(self, speed):
        self.x -= speed
        
        # Update wing animation
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.wing_position = (self.wing_position + 1) % 4
            self.animation_counter = 0
    
    def draw(self):
        screen.blit(self.sprites[self.wing_position], (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Tree:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(60, 80)
        self.width = 40
        self.y = GROUND_Y - self.height
    
    def update(self, speed):
        self.x -= speed
    
    def draw(self):
        pygame.draw.rect(screen, (139, 69, 19), (self.x + self.width//2 - 5, self.y + 30, 10, self.height - 30))
            
        # Tree foliage (green triangle)
        pygame.draw.polygon(screen, GREEN, [
            (self.x, self.y + 50),
            (self.x + self.width, self.y + 50),
            (self.x + self.width//2, self.y)
        ])
        pygame.draw.polygon(screen, GREEN, [
            (self.x + 5, self.y + 30),
            (self.x + self.width - 5, self.y + 30),
            (self.x + self.width//2, self.y - 10)
        ])
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, x):
        self.x = x
        self.id = id(self)  # Unique identifier for scoring
        
        # Randomly choose between tree and bird
        obstacle_type = random.choice(['tree', 'tree', 'bird'])  # 2/3 chance of tree, 1/3 chance of bird
        
        if obstacle_type == 'tree':
            self.obstacle = Tree(x)
            self.type = 'tree'
        else:  # bird
            is_low = random.choice([True, False])  # 50% chance of low-flying bird
            self.obstacle = YellowBird(x, is_low)
            self.type = 'bird'
            self.is_low = is_low
    
    def update(self):
        self.obstacle.update(game_speed)
        self.x = self.obstacle.x
    
    def draw(self):
        self.obstacle.draw()
    
    def get_rect(self):
        return self.obstacle.get_rect()

def draw_ground():
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)
    
    # Draw some ground details
    for i in range(0, SCREEN_WIDTH, 100):
        pygame.draw.line(screen, GRAY, (i, GROUND_Y + 5), (i + 20, GROUND_Y + 5), 2)

def display_score():
    font = pygame.font.SysFont('Arial', 20)
    score_text = font.render(f'Score: {int(score)}', True, BLACK)
    high_score_text = font.render(f'High Score: {int(high_score)}', True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))

def display_game_title():
    # Display the game title on top of the screen
    font = pygame.font.SysFont('Arial', 28, bold=True)
    title_text = font.render('Bhaag Milkha Bhaag', True, (0, 0, 128))  # Dark blue color
    # Center horizontally at the top
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))

def show_game_over():
    font = pygame.font.SysFont('Arial', 30)
    game_over_text = font.render('GAME OVER', True, BLACK)
    restart_text = font.render('Press SPACE to restart', True, BLACK)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

def reset_game():
    global game_speed, score, game_over, obstacles, obstacle_timer, passed_obstacles
    game_speed = INITIAL_SPEED
    score = 0
    game_over = False
    obstacles = []
    obstacle_timer = 0
    passed_obstacles = set()
    character.y = GROUND_Y
    character.velocity = 0
    character.is_jumping = False
    character.crouch(False)

# Create character
character = Character()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if game_over:
                    reset_game()
                else:
                    character.jump()
            elif event.key == pygame.K_DOWN:
                character.crouch(True)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                character.crouch(False)
    
    # Fill background
    screen.fill(WHITE)
    
    if not game_over:
        # Update character
        character.update()
        
        # Create new obstacles
        obstacle_timer += 1
        if obstacle_timer >= 100 // game_speed * 3:  # Adjust spawn rate with game speed
            obstacles.append(Obstacle(SCREEN_WIDTH))
            obstacle_timer = 0
        
        # Show crouch hint for high-flying birds (not trees)
        should_show_hint = False
        for obstacle in obstacles:
            if (obstacle.type == 'bird' and 
                not obstacle.is_low and  # Only for high birds
                obstacle.x > character.x and obstacle.x < character.x + 200):
                should_show_hint = True
                break
        
        if should_show_hint:
            # Visual indicator to jump for high birds
            font = pygame.font.SysFont('Arial', 20, bold=True)
            hint_text = font.render('PRESS SPACE TO JUMP!', True, (255, 0, 0))  # Red text
            screen.blit(hint_text, (15, 75))
        
        # Show crouch hint for low-flying birds
        should_show_crouch_hint = False
        for obstacle in obstacles:
            if (obstacle.type == 'bird' and 
                obstacle.is_low and  # Only for low birds
                obstacle.x > character.x and obstacle.x < character.x + 200):
                should_show_crouch_hint = True
                break
        
        if should_show_crouch_hint:
            # Visual indicator to crouch for low birds
            font = pygame.font.SysFont('Arial', 20, bold=True)
            hint_text = font.render('PRESS DOWN TO CROUCH!', True, (255, 0, 0))  # Red text
            screen.blit(hint_text, (15, 100))
        
        # Update and check obstacles
        for obstacle in obstacles[:]:
            obstacle.update()
            
            # Calculate obstacle right edge
            obstacle_right = obstacle.x + obstacle.get_rect().width
            
            # Check if player passed an obstacle (score only once per obstacle)
            if obstacle_right < character.x and obstacle.id not in passed_obstacles:
                passed_obstacles.add(obstacle.id)
                score += 10  # Add points for each passed obstacle
            
            # Remove off-screen obstacles
            if obstacle.x + obstacle.get_rect().width < 0:
                obstacles.remove(obstacle)
                continue
            
            # Check collision
            if character.get_rect().colliderect(obstacle.get_rect()):
                game_over = True
                if score > high_score:
                    high_score = score
        
        # Increase game speed gradually
        if score > 0 and score % 100 == 0:
            game_speed += SPEED_INCREASE
    
    # Draw everything
    draw_ground()
    character.draw()
    for obstacle in obstacles:
        obstacle.draw()
    display_score()
    display_game_title()  # Display the game title
    
    if game_over:
        show_game_over()
    
    # Update display
    pygame.display.update()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()