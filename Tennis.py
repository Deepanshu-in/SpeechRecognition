import pygame
import math
import random
from pygame import Vector2

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tennis Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)  
RED = (220, 20, 60)    
COURT_GREEN = (53, 94, 59)  
LIGHT_BLUE = (135, 206, 250)  
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
RACKET_HANDLE = (165, 42, 42)  
RACKET_FRAME = (211, 211, 211)  
COURT_COLOR = (53, 94, 59) 
NET_COLOR = (200, 200, 200)
SKY_BLUE = (135, 206, 235)
SUN_COLOR = (255, 215, 0)
CLOUD_COLOR = (255, 255, 255)
BALL_COLOR = (223, 255, 0)  # Tennis ball color

# Game constants
GRAVITY = 0.3
PLAYER_SPEED = 10
BALL_MAX_SPEED = 5
GROUND_HEIGHT = SCREEN_HEIGHT - 40
NET_HEIGHT = 90
WINNING_SCORE = 5

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player_one):
        super().__init__()
        self.is_player_one = is_player_one # Create a simple surface to represent the player
        self.image = pygame.Surface((60, 120), pygame.SRCALPHA)
        self.facing_right = is_player_one
        self.racket_angle = 95 if self.facing_right else 95  # Default angle in degrees
        self.racket_distance = 30  # Distance from shoulder to racket
        self.hit_animation_frames = []
        self.generate_hit_animation()
        self.hitting = False
        self.hit_cooldown = 0
        self.hit_frame = 0
        self.hit_range = 80  # Range within which player can hit ball
        self.draw_player()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.velocity = Vector2(0, 0)
        self.score = 0
        
    def generate_hit_animation(self):
        # Create a series of frames for the hitting animation
        if self.facing_right:
            self.hit_animation_frames = [
                -70,  # Starting position 
                -45,  # Mid backswing
                -20,  # Ready position
                0,    # Forward swing
                20,   # Impact position
                40,   # Follow through
                20,   # Recovery
                0,    # Return
                -20,  # Return to ready
                -45   # Back to default
            ]
        else:
            # For player facing left, mirror the animation
            self.hit_animation_frames = [
                -110,  # Starting position
                -135,  # Mid backswing
                -160,  # Ready position
                -180,  # Forward swing
                -200,  # Impact position
                -220,  # Follow through
                -200,  # Recovery
                -180,  # Return
                -160,  # Return to ready
                -135   # Back to default
            ]
    
    def draw_player(self):
        # Clear the surface
        self.image.fill((0, 0, 0, 0))
        shirt_color = BLACK if self.is_player_one else RED
        pygame.draw.ellipse(self.image, shirt_color, (15, 40, 30, 50))
        shorts_color = WHITE if self.is_player_one else BLUE
        pygame.draw.rect(self.image, shorts_color, (15, 75, 30, 25))
        skin_color = (255, 224, 189)  
        pygame.draw.circle(self.image, skin_color, (30, 30), 15)  # Head
        hair_color = BROWN
        if self.facing_right:
            pygame.draw.arc(self.image, hair_color, (15, 15, 30, 30), math.pi/2, 3*math.pi/2, 5)
            pygame.draw.ellipse(self.image, hair_color, (10, 20, 15, 25))
        else:
            pygame.draw.arc(self.image, hair_color, (15, 15, 30, 30), -math.pi/2, math.pi/2, 5)
            pygame.draw.ellipse(self.image, hair_color, (35, 20, 15, 25))
        eye_x_offset = 5 if self.facing_right else -5
        pygame.draw.circle(self.image, BLACK, (25 + eye_x_offset, 25), 2)
        pygame.draw.circle(self.image, BLACK, (35 + eye_x_offset, 25), 2)
        pygame.draw.circle(self.image, (255, 150, 150), (20, 30), 3)
        pygame.draw.circle(self.image, (255, 150, 150), (40, 30), 3)
        smile_start = 25 if self.facing_right else 30
        pygame.draw.arc(self.image, BLACK, (smile_start, 30, 10, 10), 0, math.pi, 1)
        pygame.draw.rect(self.image, skin_color, (20, 100, 7, 15))
        pygame.draw.rect(self.image, skin_color, (33, 100, 7, 15))
        pygame.draw.ellipse(self.image, BLACK, (15, 115, 12, 5))
        pygame.draw.ellipse(self.image, BLACK, (33, 115, 12, 5))
        
        # Calculate current racket angle 
        current_angle = self.racket_angle
        if self.hitting:
            current_angle = self.hit_animation_frames[self.hit_frame]
        angle_rad = math.radians(current_angle)
        shoulder_x = 40 if self.facing_right else 20
        shoulder_y = 50
        elbow_distance = 15  # Length from shoulder to elbow
        elbow_angle = angle_rad * 0.7  # Elbow bends less than racket angle
        elbow_x = shoulder_x + elbow_distance * math.cos(elbow_angle)
        elbow_y = shoulder_y + elbow_distance * math.sin(elbow_angle)  # Calculate wrist position
        arm_length = 25  # Total arm length
        wrist_x = shoulder_x + arm_length * math.cos(angle_rad)
        wrist_y = shoulder_y + arm_length * math.sin(angle_rad)
        pygame.draw.line(self.image, skin_color, (shoulder_x, shoulder_y), (elbow_x, elbow_y), 5)
        pygame.draw.line(self.image, skin_color, (elbow_x, elbow_y), (wrist_x, wrist_y), 5)
        racket_distance = 15  # Length of racket handle
        racket_head_x = wrist_x + racket_distance * math.cos(angle_rad)
        racket_head_y = wrist_y + racket_distance * math.sin(angle_rad)
        pygame.draw.line(self.image, RACKET_HANDLE, (wrist_x, wrist_y), 
                        (racket_head_x, racket_head_y), 3) # Draw racket handle

        racket_width = 16 # Tennis racket is oval rather than circular
        racket_height = 14
        pygame.draw.ellipse(self.image, RACKET_FRAME, 
                         (racket_head_x - racket_width/2, racket_head_y - racket_height/2, 
                          racket_width, racket_height), 2)
        
        # Draw tennis racket strings
        for i in range(-int(racket_width/2) + 2, int(racket_width/2) - 1, 3):
            pygame.draw.line(self.image, BLACK, 
                            (racket_head_x + i, racket_head_y - racket_height/2 + 2), 
                            (racket_head_x + i, racket_head_y + racket_height/2 - 2), 1)
        
        for i in range(-int(racket_height/2) + 2, int(racket_height/2) - 1, 3):
            pygame.draw.line(self.image, BLACK, 
                            (racket_head_x - racket_width/2 + 2, racket_head_y + i), 
                            (racket_head_x + racket_width/2 - 2, racket_head_y + i), 1)
                
        other_arm_start_x = 20 if self.facing_right else 40
        pygame.draw.line(self.image, skin_color, (other_arm_start_x, 50), 
                         (other_arm_start_x + (10 if self.facing_right else -10), 70), 5)
    
    def update(self, ball):
        if self.hitting:
            if self.hit_cooldown > 0:
                self.hit_cooldown -= 1
                self.hit_frame = min(9, 9 - self.hit_cooldown)
                self.draw_player()  # Redraw player with updated racket position
            else:
                self.hitting = False
                self.hit_frame = 0
                self.draw_player()  # Redraw player in normal pose
                
        if self.hitting and self.hit_frame == 4:  # Hit at impact frame of animation
            if self.can_hit(ball):
                direction_x = 1 if self.is_player_one else -1
                hit_strength = random.uniform(0.8, 1.2)  # Add some randomness to hits
                distance_factor = abs(ball.rect.centerx - self.rect.centerx) / 300 
                upward_velocity = -12 - distance_factor * 4  # Flatter trajectory for tennis               
                ball.velocity = Vector2(direction_x * BALL_MAX_SPEED * hit_strength, upward_velocity)
                ball.last_hit_by = 1 if self.is_player_one else 2
                ball.spin = random.uniform(-0.05, 0.05)
    
    def move(self, dx):
        # Ensure player stays within screen bounds and on their side of the court
        if self.is_player_one:
            new_x = max(50, min(self.rect.x + dx, SCREEN_WIDTH // 2 - 50 - self.rect.width))
        else:
            new_x = max(SCREEN_WIDTH // 2 + 50, min(self.rect.x + dx, SCREEN_WIDTH - 50 - self.rect.width))
        self.rect.x = new_x
    
    def hit(self):
        if self.hit_cooldown == 0:  # Only start a hit if not already hitting
            self.hitting = True
            self.hit_cooldown = 10  # Frames to complete the hit animation
            self.hit_frame = 0
    
    def can_hit(self, ball):  # Check if ball is within hitting range
        distance = Vector2(ball.rect.center) - Vector2(self.rect.midtop)
        return distance.length() < self.hit_range

# Tennis Ball class
class TennisBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.draw_ball()
        self.rect = self.image.get_rect()
        self.reset()
        self.last_hit_by = 0  
        self.spin = 0  # Ball spin effect
        self.hit_net = False  
    
    def draw_ball(self):
        radius = 8
        # Draw the yellow-green base
        pygame.draw.circle(self.image, BALL_COLOR, (10, 10), radius)
        pygame.draw.arc(self.image, WHITE, (2, 2, 16, 16), math.pi/6, 5*math.pi/6, 2) # First curved line
        pygame.draw.arc(self.image, WHITE, (2, 2, 16, 16), 7*math.pi/6, 11*math.pi/6, 2) # Second curved line 
    
    def reset(self, server=None):
        if server is None:
            server = random.choice([1, 2])        
        if server == 1:
            self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
            self.velocity = Vector2(random.uniform(2, 4), -10)
        else:
            self.rect.center = (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
            self.velocity = Vector2(random.uniform(-4, -2), -10)
        self.last_hit_by = server
        self.spin = 0
        self.hit_net = False
    
    def update(self):
        self.velocity.y += GRAVITY  # Apply gravity
        self.velocity.x += self.spin
        self.rect.x += self.velocity.x  # Update position
        self.rect.y += self.velocity.y
        # Bounce off walls with more realistic physics for tennis
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity.x = -self.velocity.x * 0.9
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.velocity.x = -self.velocity.x * 0.9
            
        # Check if ball hits the ground
        if self.rect.bottom >= GROUND_HEIGHT:
            self.rect.bottom = GROUND_HEIGHT
            # Tennis ball bounce
            if abs(self.velocity.y) > 2:  # Only bounce if coming down with enough speed
                self.velocity.y = -self.velocity.y * 0.6
                self.velocity.x *= 0.8  # Reduce horizontal speed on bounce
            else:
                self.velocity = Vector2(0, 0)
                return True  # Signal that the ball hit the ground and stopped
        
        # Check if ball hits the net
        net_rect = pygame.Rect(SCREEN_WIDTH // 2 - 5, GROUND_HEIGHT - NET_HEIGHT, 10, NET_HEIGHT)
        if self.rect.colliderect(net_rect):
            if self.velocity.x > 0:
                self.rect.right = net_rect.left
            else:
                self.rect.left = net_rect.right
            self.velocity.x = -self.velocity.x * 0.3
            self.velocity.y *= 0.7
            self.hit_net = True  # Set flag that ball hit the net
        
        return False  # Ball did not hit the ground and stop

# Cloud class
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        self.image = pygame.Surface((100 * scale, 50 * scale), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(0.2, 0.5)
        
        # Draw cloud
        for i in range(3):
            cloud_x = random.randint(0, int(80 * scale))
            cloud_y = random.randint(0, int(30 * scale))
            cloud_radius = random.randint(int(15 * scale), int(25 * scale))
            pygame.draw.circle(self.image, CLOUD_COLOR, (cloud_x, cloud_y), cloud_radius)
    
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

# Game setup
player1 = Player(SCREEN_WIDTH // 4, GROUND_HEIGHT, True)
player2 = Player(3 * SCREEN_WIDTH // 4, GROUND_HEIGHT, False)
tennis_ball = TennisBall()

# Create clouds
clouds = pygame.sprite.Group()
for i in range(5):
    cloud = Cloud(
        random.randint(0, SCREEN_WIDTH),
        random.randint(20, 150),
        random.uniform(0.5, 1.5)
    )
    clouds.add(cloud)
all_sprites = pygame.sprite.Group()
all_sprites.add(player1, player2, tennis_ball)
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
running = True
game_state = "serving"  # "serving", "playing", "scored", "game_over"
score_delay = 0
serving_player = random.choice([1, 2])
winner = None
point_message = ""  # To display why a point was awarded

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                player1.hit()
            elif event.key == pygame.K_u:
                player2.hit()
            elif event.key == pygame.K_SPACE:
                if game_state == "serving":
                    game_state = "playing"
                    tennis_ball.reset(serving_player)
                elif game_state == "game_over":
                    player1.score = 0
                    player2.score = 0
                    game_state = "serving"
                    serving_player = random.choice([1, 2])
                    winner = None
    
    # Get keys pressed
    keys = pygame.key.get_pressed()
    
    # Player 1 movement 
    if keys[pygame.K_a]:
        player1.move(-PLAYER_SPEED)
    if keys[pygame.K_s]:
        player1.move(PLAYER_SPEED)
    
    # Player 2 movement 
    if keys[pygame.K_k]:
        player2.move(-PLAYER_SPEED)
    if keys[pygame.K_l]:
        player2.move(PLAYER_SPEED)
    
    # Game logic
    if game_state == "playing":
        player1.update(tennis_ball)
        player2.update(tennis_ball)
        hit_ground = tennis_ball.update()
        
        # RULE: Check if ball stays in hitter's court or hits net
        if tennis_ball.last_hit_by == 1:
            # Player 1 hit the ball
            if tennis_ball.hit_net:
                # Ball hit the net after Player 1's hit
                player2.score += 1
                serving_player = 2
                game_state = "scored"
                score_delay = 30
                point_message = "Ball hit the net! Player 2 scores!"
                tennis_ball.hit_net = False  # Reset for next point
            elif hit_ground and tennis_ball.rect.centerx < SCREEN_WIDTH // 2:
                # Ball landed in Player 1's court after they hit it
                player2.score += 1
                serving_player = 2
                game_state = "scored"
                score_delay = 30
                point_message = "Ball stayed in Player 1's court! Player 2 scores!"
            elif hit_ground and tennis_ball.rect.centerx > SCREEN_WIDTH // 2:
                # Ball landed in Player 2's court after Player 1 hit it
                player1.score += 1
                serving_player = 1
                game_state = "scored"
                score_delay = 30
                point_message = "Point for Player 1!"
        
        elif tennis_ball.last_hit_by == 2:
            # Player 2 hit the ball
            if tennis_ball.hit_net:
                # Ball hit the net after Player 2's hit
                player1.score += 1
                serving_player = 1
                game_state = "scored"
                score_delay = 30
                point_message = "Ball hit the net! Player 1 scores!"
                tennis_ball.hit_net = False  # Reset for next point
            elif hit_ground and tennis_ball.rect.centerx > SCREEN_WIDTH // 2:
                # Ball landed in Player 2's court after they hit it
                player1.score += 1
                serving_player = 1
                game_state = "scored"
                score_delay = 30
                point_message = "Ball stayed in Player 2's court! Player 1 scores!"
            elif hit_ground and tennis_ball.rect.centerx < SCREEN_WIDTH // 2:
                # Ball landed in Player 1's court after Player 2 hit it
                player2.score += 1
                serving_player = 2
                game_state = "scored"
                score_delay = 30
                point_message = "Point for Player 2!"
        
        elif hit_ground:
            # No player hit the ball before it hit the ground
            if tennis_ball.rect.centerx < SCREEN_WIDTH // 2:
                # Ball landed in Player 1's court
                player2.score += 1
                serving_player = 2
                game_state = "scored"
                score_delay = 30
                point_message = "Player 1 missed the ball! Player 2 scores!"
            else:
                # Ball landed in Player 2's court
                player1.score += 1
                serving_player = 1
                game_state = "scored"
                score_delay = 30
                point_message = "Player 2 missed the ball! Player 1 scores!"
    
        if player1.score >= WINNING_SCORE: # Check if anyone has won
            game_state = "game_over"
            winner = 1
        elif player2.score >= WINNING_SCORE:
            game_state = "game_over"
            winner = 2
            
    elif game_state == "scored":
        score_delay -= 1
        if score_delay <= 0:
            game_state = "serving"
            
    clouds.update() # Update clouds
    screen.fill(SKY_BLUE) # Draw sky background
    sun_x, sun_y = 650, 80  # Draw blazing sun
    for i in range(12): # Draw sun rays
        angle = i * 30
        ray_length = random.randint(15, 25)
        end_x = sun_x + math.cos(math.radians(angle)) * (35 + ray_length)
        end_y = sun_y + math.sin(math.radians(angle)) * (35 + ray_length)
        pygame.draw.line(screen, SUN_COLOR, (sun_x, sun_y), (end_x, end_y), 3)
    pygame.draw.circle(screen, SUN_COLOR, (sun_x, sun_y), 35)
    clouds.draw(screen)
    
    # Court lines
    pygame.draw.rect(screen, COURT_COLOR, (0, GROUND_HEIGHT - 20, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT + 20))
    pygame.draw.rect(screen, WHITE, (50, GROUND_HEIGHT, SCREEN_WIDTH - 100, 2))
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, GROUND_HEIGHT), (SCREEN_WIDTH // 2, GROUND_HEIGHT - 20), 2)
    service_box_width = (SCREEN_WIDTH // 2 - 50) // 2
    pygame.draw.line(screen, WHITE, (50 + service_box_width, GROUND_HEIGHT), 
                    (50 + service_box_width, GROUND_HEIGHT - 20), 2)
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH - 50 - service_box_width, GROUND_HEIGHT), 
                    (SCREEN_WIDTH - 50 - service_box_width, GROUND_HEIGHT - 20), 2)
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, GROUND_HEIGHT), 
                    (SCREEN_WIDTH // 2, GROUND_HEIGHT + 5), 2)
    
    net_top = GROUND_HEIGHT - NET_HEIGHT
    post_width = 5
    post_height = NET_HEIGHT + 10  # Posts are slightly taller than net
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - post_width // 2, net_top - 10, post_width, post_height))
    net_width = 2
    net_segments = 20
    segment_width = net_width
    points = []
    for i in range(net_segments + 1):
        x = SCREEN_WIDTH // 2 - (net_segments * segment_width) // 2 + i * segment_width 
        curve_height = math.sin(math.pi * i / net_segments) * 5     # Create a slight curve 
        y = net_top - curve_height
        points.append((x, y))
    
    # Draw net top line
    if len(points) > 1:
        pygame.draw.lines(screen, WHITE, False, points, 2)
    
    # Draw vertical net lines
    for i, point in enumerate(points):
        pygame.draw.line(screen, WHITE, point, (point[0], GROUND_HEIGHT), 1)
    
    # Draw horizontal net lines
    for y in range(int(net_top), GROUND_HEIGHT, 5):
        # Find left and right edge of the net at this height
        left_edge = points[0][0]
        right_edge = points[-1][0]
        pygame.draw.line(screen, WHITE, (left_edge, y), (right_edge, y), 1)
    
    all_sprites.draw(screen)  # Draw scores
    score_text = font.render(f"{player1.score} - {player2.score}", True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
    
    # Draw instructions
    if game_state == "serving":
        serve_text = font.render(f"Player {serving_player} to serve. Press SPACE to start.", True, BLACK)
        screen.blit(serve_text, (SCREEN_WIDTH // 2 - serve_text.get_width() // 2, 60))
    elif game_state == "scored":
        point_text = font.render(point_message, True, BLACK) # Display point message
        screen.blit(point_text, (SCREEN_WIDTH // 2 - point_text.get_width() // 2, 60))
    elif game_state == "game_over":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Create a semi-transparent overlay
        overlay.fill((0, 0, 0, 128))  # black with alpha
        screen.blit(overlay, (0, 0)) # Draw game over message
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        winner_text = font.render(f"Player {winner} Wins!", True, WHITE) # Draw winner message
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
        restart_text = font.render("Press SPACE to play again", True, WHITE) # Draw restart instructions
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    # Draw controls help
    controls1 = font.render("Left/right: A/S key, E to hit", True, WHITE)
    controls2 = font.render("Left/right: K/L key, U to hit", True, WHITE)
    screen.blit(controls1, (15, SCREEN_HEIGHT - 30))
    screen.blit(controls2, (SCREEN_WIDTH - controls2.get_width() - 15, SCREEN_HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()