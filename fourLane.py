import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Avoidance Game")

# Colors
BLACK = (0, 0, 0)       # Road color
WHITE = (255, 255, 255) # Lane marking color
GREEN = (0, 150, 0)     # Background color
RED = (255, 0, 0)       # Player car color
BLUE = (0, 0, 255)      # Game over text

# Car colors for traffic
CAR_COLORS = [
    (255, 255, 0),    # Yellow
    (0, 255, 255),    # Cyan
    (255, 165, 0),    # Orange
    (0, 255, 0),      # Green
    (255, 0, 255),    # Purple
    (165, 42, 42),    # Brown
    (192, 192, 192)   # Silver
]

# Road dimensions
ROAD_WIDTH = 400        # Total width of road
LANE_WIDTH = ROAD_WIDTH / 4  # Width of each lane
LANE_MARKING_LENGTH = 50 # Length of dashed lane markings
LANE_MARKING_GAP = 30    # Gap between dashed markings

# Road positioning
road_left = (WIDTH - ROAD_WIDTH) // 2
road_right = road_left + ROAD_WIDTH

# Car dimensions
CAR_WIDTH = 60
CAR_HEIGHT = 100

# Player car positioning
player_x = road_left + (ROAD_WIDTH - CAR_WIDTH) // 2  # Center car in road
player_y = HEIGHT - CAR_HEIGHT - 50  # Position car near bottom of screen
player_speed_x = 7  # Horizontal movement speed

# Lane markings for scrolling effect
lane_markings = []
for lane in range(1, 4):  # 3 lane dividers
    lane_x = road_left + lane * LANE_WIDTH
    y_offset = 0
    while y_offset < HEIGHT:
        lane_markings.append((lane_x, y_offset, LANE_MARKING_LENGTH))
        y_offset += LANE_MARKING_LENGTH + LANE_MARKING_GAP

# Traffic cars
class TrafficCar:
    def __init__(self):
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.lane = random.randint(0, 3)  # Random lane (0-3)
        self.x = road_left + self.lane * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = -self.height  # Start above the screen
        self.speed = random.randint(3, 7)  # Random speed
        self.color = random.choice(CAR_COLORS)  # Random color

    def update(self, scroll_speed):
        # Move down based on own speed and player scroll speed
        self.y += self.speed + scroll_speed
        
    def draw(self, surface):
        # Draw car body
        car_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, car_rect)
        
        # Draw windshield
        pygame.draw.rect(surface, (150, 220, 255), 
                        (self.x + 10, self.y + self.height - 45, self.width - 20, 30))
        
        # Draw taillights
        pygame.draw.rect(surface, (255, 0, 0), 
                        (self.x + 10, self.y + self.height - 15, 10, 10))
        pygame.draw.rect(surface, (255, 0, 0), 
                        (self.x + self.width - 20, self.y + self.height - 15, 10, 10))
        
        # Draw tires
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x - 5, self.y + 20, 5, 25))
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x + self.width, self.y + 20, 5, 25))
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x - 5, self.y + self.height - 45, 5, 25))
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x + self.width, self.y + self.height - 45, 5, 25))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Game variables
traffic_cars = []
spawn_timer = 0
spawn_delay = 60  # Frames between car spawns (adjust for difficulty)
scroll_speed = 0
max_scroll_speed = 10
acceleration = 0.25
deceleration = 0.1
score = 0
game_over = False

# Main loop
clock = pygame.time.Clock()
running = True

def check_collision(player_rect, traffic_cars):
    for car in traffic_cars:
        if player_rect.colliderect(car.get_rect()):
            return True
    return False

def reset_game():
    global traffic_cars, scroll_speed, score, game_over
    traffic_cars = []
    scroll_speed = 0
    score = 0
    game_over = False

def draw_player_car(x, y):
    # Draw the car body
    car_rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)
    pygame.draw.rect(screen, RED, car_rect)
    
    # Draw windshield
    pygame.draw.rect(screen, (150, 220, 255), 
                    (x + 10, y + 15, CAR_WIDTH - 20, 30))
    
    # Draw headlights
    pygame.draw.rect(screen, (255, 255, 200), 
                    (x + 10, y + 5, 10, 10))
    pygame.draw.rect(screen, (255, 255, 200), 
                    (x + CAR_WIDTH - 20, y + 5, 10, 10))
    
    # Draw tires
    pygame.draw.rect(screen, (50, 50, 50), 
                    (x - 5, y + 20, 5, 25))
    pygame.draw.rect(screen, (50, 50, 50), 
                    (x + CAR_WIDTH, y + 20, 5, 25))
    pygame.draw.rect(screen, (50, 50, 50), 
                    (x - 5, y + CAR_HEIGHT - 45, 5, 25))
    pygame.draw.rect(screen, (50, 50, 50), 
                    (x + CAR_WIDTH, y + CAR_HEIGHT - 45, 5, 25))
    
    return car_rect

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
    
    # Handle key presses if game is not over
    if not game_over:
        keys = pygame.key.get_pressed()
        
        # Vertical movement 
        if keys[pygame.K_UP]:
            scroll_speed = min(scroll_speed + acceleration, max_scroll_speed)
        else:
            scroll_speed = max(scroll_speed - deceleration, 0)
            
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            player_x = max(player_x - player_speed_x, road_left)
        if keys[pygame.K_RIGHT]:
            player_x = min(player_x + player_speed_x, road_right - CAR_WIDTH)
    
    # Fill background with green 
    screen.fill(GREEN)
    
    # Draw the road 
    road_rect = pygame.Rect(road_left, 0, ROAD_WIDTH, HEIGHT)
    pygame.draw.rect(screen, BLACK, road_rect)
    
    # Draw outer edge lines
    pygame.draw.line(screen, WHITE, (road_left, 0), (road_left, HEIGHT), 2)
    pygame.draw.line(screen, WHITE, (road_left + ROAD_WIDTH, 0), (road_left + ROAD_WIDTH, HEIGHT), 2)
    
    # Draw and update lane markings
    new_lane_markings = []
    for marking in lane_markings:
        x, y, length = marking
        # Move marking down based on scroll speed
        new_y = (y + scroll_speed) % (HEIGHT + LANE_MARKING_LENGTH + LANE_MARKING_GAP)
        # Draw marking
        if new_y < HEIGHT:
            pygame.draw.line(screen, WHITE, (x, new_y), (x, new_y + length), 2)
        # Add to new list
        new_lane_markings.append((x, new_y, length))
    lane_markings = new_lane_markings
    
    # Spawn traffic cars
    if not game_over:
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            traffic_cars.append(TrafficCar())
            spawn_timer = 0
            # Decrease spawn delay as score increases 
            spawn_delay = max(20, 60 - score // 500)
    
    # Update and draw traffic cars
    for car in traffic_cars[:]:
        car.update(scroll_speed)
        car.draw(screen)
        # Remove cars that are off screen
        if car.y > HEIGHT:
            traffic_cars.remove(car)
            if not game_over:
                score += 10  # Add points for passing a car
    
    # Draw the player car and get its rectangle for collision detection
    player_rect = draw_player_car(player_x, player_y)
    
    # Check for collisions
    if not game_over and check_collision(player_rect, traffic_cars):
        game_over = True
        scroll_speed = 0
    
    # Update score based on speed
    if not game_over:
        score += int(scroll_speed)
    
    # Display speed and score
    font = pygame.font.SysFont(None, 36)
    speed_text = font.render(f"Speed: {int(scroll_speed * 10)} km/h", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(speed_text, (20, 20))
    screen.blit(score_text, (20, 60))
    
    # Game over screen
    if game_over:
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, BLUE)
        restart_text = font.render("Press R to restart", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        screen.blit(game_over_text, text_rect)
        screen.blit(restart_text, restart_rect)
    
    # Update the display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()