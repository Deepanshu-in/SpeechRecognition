import pygame
import sys
import os
import math
from PIL import Image, ImageDraw
import time

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skipping Rope Game")

# Add to existing game states
COUNTDOWN = 2
# Add to existing colors
YELLOW = (255, 255, 0)


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (76, 187, 23)
BLUE = (135, 206, 235)
SAND = (194, 178, 128)
SUN_COLOR = (255, 204, 0)
SKIN_COLOR = (255, 213, 170)
RED = (255, 0, 0)

# Fonts
font = pygame.font.SysFont('Arial', 36)
game_over_font = pygame.font.SysFont('Arial', 72)
instruction_font = pygame.font.SysFont('Arial', 24)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Game states
PLAYING = 0
GAME_OVER = 1

# Create character sprite with arms and hands
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 100
        self.height = 200
        
        # Main body image
        self.body_image = self.create_body_image()
        
        # Full image with body, arms and hands
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        
        # Arm and hand positioning parameters
        self.arm_length = 60  # Fixed arm length
        self.hand_spacing = 80  # Distance between hands
        self.center_x = self.rect.centerx
        self.base_hand_height = self.rect.centery + 30  # Changed to be at shorts level
        
        # Initialize shoulder and hand positions
        self.left_shoulder = None
        self.right_shoulder = None
        self.left_hand_pos = None
        self.right_hand_pos = None
        self.initial_hands_y = None  # Store initial hand Y position
        
        # Jumping properties - These need to be initialized before calling update_arm_positions
        self.is_jumping = False
        self.jump_height = 20
        self.jump_velocity = 0
        self.gravity = 1
        self.ground_y = y
        self.update_arm_positions(0)  # Initial position
        
        # Update the full image
        self.update_image()
    
    def create_body_image(self):
        # Unchanged - keeping the existing body creation code
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Head dimensions and position
        head_radius = self.width // 8
        head_center_x = self.width // 2
        head_center_y = self.height // 8
        
        # Neck dimensions
        neck_width = head_radius
        neck_height = head_radius * 1.2  # Adjust neck height as needed
        neck_top = head_center_y + head_radius - 5  # Slightly overlap with head
        neck_bottom = neck_top + neck_height
        neck_left = head_center_x - neck_width//3
        neck_right = head_center_x + neck_width//3
        neck_points = [
            (neck_left, neck_top),  # Top left
            (neck_right, neck_top),  # Top right
            (neck_right + 2, neck_bottom),  # Bottom right 
            (neck_left - 2, neck_bottom)   # Bottom left
        ]
        draw.polygon(neck_points, fill=SKIN_COLOR)
        
        # Add neck shading for more depth
        neck_shadow = (
            max(SKIN_COLOR[0] - 20, 0),
            max(SKIN_COLOR[1] - 20, 0),
            max(SKIN_COLOR[2] - 20, 0)
        )
        draw.line([(neck_left, neck_top), (neck_left - 2, neck_bottom)], fill=neck_shadow, width=2)
        tank_top_y = neck_bottom - 5  # Slight overlap with neck
        draw.rectangle([
            (self.width // 3, tank_top_y),
            (2 * self.width // 3, 2 * self.height // 3)
        ], fill=WHITE)
        
        # Add collar/tank top neckline
        collar_points = [
            (self.width // 3, tank_top_y),  # Left top
            (head_center_x - neck_width//2.5, tank_top_y),  # Left inner
            (head_center_x, tank_top_y + 10),  # Center dip
            (head_center_x + neck_width//2.5, tank_top_y),  # Right inner
            (2 * self.width // 3, tank_top_y),  # Right top
        ]
        draw.line(collar_points, fill=(200, 200, 200), width=2)  # Collar detail
        
        # Head
        draw.ellipse([
            (head_center_x - head_radius, head_center_y - head_radius),
            (head_center_x + head_radius, head_center_y + head_radius)
        ], fill=SKIN_COLOR)
        
        # Eyes
        eye_radius = head_radius // 5
        eye_y = head_center_y - 2
        
        # Left eye
        left_eye_x = head_center_x - head_radius//2
        draw.ellipse([
            (left_eye_x - eye_radius, eye_y - eye_radius),
            (left_eye_x + eye_radius, eye_y + eye_radius)
        ], fill=BLACK)
        
        # Right eye
        right_eye_x = head_center_x + head_radius//2
        draw.ellipse([
            (right_eye_x - eye_radius, eye_y - eye_radius),
            (right_eye_x + eye_radius, eye_y + eye_radius)
        ], fill=BLACK)
        
        # Add eyebrows
        eyebrow_y = eye_y - eye_radius - 3
        # Left eyebrow
        draw.line([
            (left_eye_x - eye_radius - 2, eyebrow_y),
            (left_eye_x + eye_radius + 2, eyebrow_y - 2)
        ], fill=BLACK, width=2)
        # Right eyebrow
        draw.line([
            (right_eye_x - eye_radius - 2, eyebrow_y - 2),
            (right_eye_x + eye_radius + 2, eyebrow_y)
        ], fill=BLACK, width=2)
        
        # Smile
        smile_y = head_center_y + head_radius//2
        draw.arc([
            (head_center_x - head_radius//2, smile_y - head_radius//4),
            (head_center_x + head_radius//2, smile_y + head_radius//4)
        ], 0, 180, fill=BLACK, width=2)
        
        draw.rectangle([
            (self.width // 3, 2 * self.height // 3),
            (2 * self.width // 3, 4 * self.height // 5)
        ], fill=(100, 149, 237))
        
        # Legs
        leg_width = self.width // 8
        # Left leg
        draw.rectangle([
            (self.width // 2 - leg_width - 5, 4 * self.height // 5),
            (self.width // 2 - 5, self.height)
        ], fill=SKIN_COLOR)
        # Right leg
        draw.rectangle([
            (self.width // 2 + 5, 4 * self.height // 5),
            (self.width // 2 + leg_width + 5, self.height)
        ], fill=SKIN_COLOR)
        leg_shadow = (
            max(SKIN_COLOR[0] - 20, 0),
            max(SKIN_COLOR[1] - 20, 0),
            max(SKIN_COLOR[2] - 20, 0)
        )
        draw.line([
            (self.width // 2 - leg_width - 3, 4 * self.height // 5),
            (self.width // 2 - leg_width - 3, self.height)
        ], fill=leg_shadow, width=2)
        draw.line([
            (self.width // 2 + leg_width + 3, 4 * self.height // 5),
            (self.width // 2 + leg_width + 3, self.height)
        ], fill=leg_shadow, width=2)
        
        temp_path = "temp_character.png"
        image.save(temp_path)
        pygame_image = pygame.image.load(temp_path)
        os.remove(temp_path)
        
        return pygame_image

    def update_arm_positions(self, rope_phase):
        center_y = self.base_hand_height
        if self.initial_hands_y is None:
            self.initial_hands_y = center_y
        
        hand_offset_x = 5 * math.sin(rope_phase)
        if self.is_jumping:
            hand_offset_y = 0  # No vertical movement during jumps
        else:
            hand_offset_y = 5 * math.cos(rope_phase)  # Limited vertical movement when not jumping
        max_hand_y = self.base_hand_height + 10  # Maximum allowed hand height
        
        # Update hand positions
        self.left_hand_pos = [
            self.center_x - self.hand_spacing/2 + hand_offset_x,
            min(max_hand_y, self.initial_hands_y + hand_offset_y)
        ]
        self.right_hand_pos = [
            self.center_x + self.hand_spacing/2 + hand_offset_x,
            min(max_hand_y, self.initial_hands_y + hand_offset_y)
        ]
        shoulder_spacing = 40  # Narrower than hands for more realistic arm posture
        shoulder_height = self.rect.centery - 50
        
        self.left_shoulder = [
            self.center_x - shoulder_spacing/2,
            shoulder_height
        ]
        self.right_shoulder = [
            self.center_x + shoulder_spacing/2,
            shoulder_height
        ]

    def update_image(self):
        # Clear the image
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.body_image, (0, 0))
        left_shoulder_rel = (
            self.left_shoulder[0] - self.rect.left,
            self.left_shoulder[1] - self.rect.top
        )
        right_shoulder_rel = (
            self.right_shoulder[0] - self.rect.left,
            self.right_shoulder[1] - self.rect.top
        )
        left_hand_rel = (
            self.left_hand_pos[0] - self.rect.left,
            self.left_hand_pos[1] - self.rect.top
        )
        right_hand_rel = (
            self.right_hand_pos[0] - self.rect.left,
            self.right_hand_pos[1] - self.rect.top
        )
        
        # Draw arms with proper thickness
        pygame.draw.line(self.image, SKIN_COLOR, left_shoulder_rel, left_hand_rel, 8)
        pygame.draw.line(self.image, SKIN_COLOR, right_shoulder_rel, right_hand_rel, 8)
        pygame.draw.circle(self.image, SKIN_COLOR, left_shoulder_rel, 6)
        pygame.draw.circle(self.image, SKIN_COLOR, right_shoulder_rel, 6)
        pygame.draw.circle(self.image, SKIN_COLOR, left_hand_rel, 8)
        pygame.draw.circle(self.image, SKIN_COLOR, right_hand_rel, 8)

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = -self.jump_height

    def update(self, rope_phase, rope_height):
        # Update center_x based on current position
        self.center_x = self.rect.centerx
        
        # Update jumping physics
        if self.is_jumping:
            self.rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            
            if self.rect.bottom >= self.ground_y:
                self.rect.bottom = self.ground_y
                self.is_jumping = False
                self.jump_velocity = 0
    
        self.update_arm_positions(rope_phase)
        self.update_image()
        
        return self.rect.bottom

    def get_head_top(self):
        return self.rect.top + self.height // 8 - self.width // 8
        
    def get_feet_position(self):
        # Return the position of the character's feet for rope positioning
        return self.rect.bottom
    
class Rope:
    def __init__(self, character):
        self.character = character
        self.phase = 0
        self.speed = 0.05  # Reduced speed for smoother movement
        self.points = []
        self.rope_width = 3
        self.color = BLACK
        self.handle_radius = 5
        self.rope_angle = 0
        self.rope_state = 0  # 0: above head, 1: moving down, 2: below feet, 3: moving up
        self.rope_velocity = 4  # Reduced velocity for slower movement
        self.rope_position = 0  # Normalized position of the rope 
        self.segment_count = 30  # Number of rope segments
        self.rope_tension = 0.8  # Controls how tight the rope appears 
        self.max_curve_height = 150  # Maximum height of the rope curve
        self.handle_color = (139, 69, 19)  # Brown color for handles
        self.handle_length = 15
        self.points = self.calculate_rope_points()

    def update(self):
        # Update rope state and position
        if self.rope_state == 0:  # Above head, preparing to move down
            self.rope_position = 0
            self.rope_state = 1
        elif self.rope_state == 1:  # Moving down
            self.rope_position += self.rope_velocity / 100
            if self.rope_position >= 1:
                self.rope_position = 1
                self.rope_state = 2
        elif self.rope_state == 2:  # Below feet, preparing to move up
            self.rope_state = 3
        elif self.rope_state == 3:  # Moving up
            self.rope_position -= self.rope_velocity / 100
            if self.rope_position <= 0:
                self.rope_position = 0
                self.rope_state = 0
                
        self.phase += self.speed
        self.points = self.calculate_rope_points()
        if self.rope_state == 1:
            return self.get_rope_position()
        return -1

    def calculate_rope_points(self):
        left_hand = self.character.left_hand_pos
        right_hand = self.character.right_hand_pos
        head_top = self.character.get_head_top()
        feet_bottom = self.character.get_feet_position()  # Use the dedicated method
        below_feet = feet_bottom + 20  # Extend 20 pixels below feet
        points = []
        steps = self.segment_count
        lowest_y = head_top - 50 + self.rope_position * (below_feet - head_top + 100)
        
        for i in range(steps + 1):
            t = i / steps
            base_x = left_hand[0] + (right_hand[0] - left_hand[0]) * t
            base_y = left_hand[1] + (right_hand[1] - left_hand[1]) * t
            
            if self.rope_state == 1 or self.rope_state == 3:
                curve_factor = 4 * self.rope_position * (1 - self.rope_position)
                if 0 < t < 1:
                    # Quadratic curve for smoother rope movement
                    curve_height = self.max_curve_height * curve_factor
                    y_offset = -curve_height * math.sin(math.pi * t)
                    x_offset = 5 * math.sin(self.phase * 2) * math.sin(math.pi * t)
                    
                    base_x += x_offset
                    if self.rope_position >= 0.5 and self.rope_state == 1:
                        base_y = below_feet + y_offset * 0.5  # Reduced curve at lowest point
                    else:
                        base_y = lowest_y + y_offset
                    
                    # Add slight curve even when rope is straight
                    base_y += 5 * math.sin(math.pi * t)
            else:
                # At top or bottom: slight curve
                if 0 < t < 1:
                    if self.rope_state == 2:
                        base_y = below_feet - 5 * math.sin(math.pi * t)
                    else:
                        base_y = lowest_y - 15 * math.sin(math.pi * t)
                    
                    x_offset = 3 * math.sin(self.phase * 2) * math.sin(math.pi * t)
                    base_x += x_offset
            
            points.append((base_x, base_y))
        
        return points

    def get_rope_position(self):
        if not self.points:
            return 0
        middle_point = self.points[len(self.points) // 2]
        return middle_point[1]

    def draw(self, screen):
        if len(self.points) < 2:
            return

        # Draw the main rope
        if len(self.points) > 2:
            for thickness in range(self.rope_width, 0, -1):
                color = (0, 0, 0, 255 * (thickness / self.rope_width))
                pygame.draw.lines(screen, color, False, self.points, thickness)

        # Draw handles at the ends of the rope
        for end_point in [self.points[0], self.points[-1]]:
            pygame.draw.circle(screen, self.handle_color, end_point, self.handle_radius)
            handle_top = (end_point[0], end_point[1] - self.handle_length)
            pygame.draw.line(screen, self.handle_color, end_point, handle_top, 3)
            
            # Draw handle top
            pygame.draw.circle(screen, self.handle_color, handle_top, 4)

        # Add rope texture/detail
        if len(self.points) > 4:
            for i in range(1, len(self.points) - 1, 2):
                pygame.draw.circle(screen, (40, 40, 40), self.points[i], 1)

    def get_rope_height_at_position(self, x_pos):
        if not self.points:
            return 0
            
        # Find the two points that bracket the given x position
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x_pos <= x2:
                if x2 - x1 == 0:
                    return y1
                t = (x_pos - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)
                
        return 0

def draw_background(screen):
    # Sky
    screen.fill(BLUE)
    
    # Sun
    pygame.draw.circle(screen, SUN_COLOR, (WIDTH - 100, 100), 60)
    
    # Sun rays
    for i in range(8):
        angle = i * 45
        start_x = WIDTH - 100 + 60 * math.cos(math.radians(angle))
        start_y = 100 + 60 * math.sin(math.radians(angle))
        end_x = WIDTH - 100 + 90 * math.cos(math.radians(angle))
        end_y = 100 + 90 * math.sin(math.radians(angle))
        pygame.draw.line(screen, SUN_COLOR, (start_x, start_y), (end_x, end_y), 5)
    
    # Ground 
    ground_height = HEIGHT // 4
    ground_rect = pygame.Rect(0, HEIGHT - ground_height, WIDTH, ground_height)
    pygame.draw.rect(screen, GREEN, ground_rect)
    
    # Sand patches
    for i in range(5):
        sand_width = 100 + i * 20
        sand_x = i * 200 % (WIDTH - sand_width)
        sand_y = HEIGHT - ground_height + 10
        pygame.draw.ellipse(screen, SAND, (sand_x, sand_y, sand_width, ground_height // 2))

def check_collision(character_bottom, rope_position, character, is_jumping):
    if rope_position < 0:  # No collision possible when rope moving up
        return False
    
    # Tolerance threshold 
    tolerance = 15
    
    # Get character's feet and middle positions
    feet_pos = character.rect.bottom
    character_middle = character.rect.top + character.height // 2
    
    # If the rope is near the character's feet and they're not jumping
    if not is_jumping and abs(feet_pos - rope_position) < tolerance:
        return True
    
    # If the rope hits the character's body while it's moving down
    if not is_jumping and rope_position > character.rect.top and rope_position < feet_pos:
        return True
    
    return False

def main():
    # Create character
    character = Character(WIDTH // 2, HEIGHT - HEIGHT // 4)
    
    # Create rope
    rope = Rope(character)
    
    # Game variables
    score = 0
    game_state = COUNTDOWN  # Start with countdown
    successful_jumps = 0
    countdown_start = time.time()
    countdown_duration = 3  # 3 seconds countdown
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == PLAYING:
                    character.jump()
                elif event.key == pygame.K_r and game_state == GAME_OVER:
                    # Reset game
                    character = Character(WIDTH // 2, HEIGHT - HEIGHT // 4)
                    rope = Rope(character)
                    score = 0
                    game_state = COUNTDOWN  # Change to countdown state
                    countdown_start = time.time()  # Reset countdown timer
                    successful_jumps = 0
        
        # Update
        if game_state == PLAYING:
            # Update rope and get its position
            rope_position = rope.update()
            
            # Update character and get its bottom position
            character_bottom = character.update(rope.phase, 0)
            
            # Check for collision 
            if check_collision(character_bottom, rope_position, character, character.is_jumping):
                game_state = GAME_OVER
        
            if character.is_jumping and rope.rope_state == 1 and rope_position > character_bottom:
                # Only count once per rope cycle
                if successful_jumps == 0:
                    score += 1
                    successful_jumps = 1
        
            if rope.rope_state == 0:
                successful_jumps = 0
        
        # Draw
        draw_background(screen)
        character.update_image()
        screen.blit(character.image, character.rect)
        rope.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Draw instructions
        instruction = instruction_font.render("Press SPACE to jump", True, BLACK)
        screen.blit(instruction, (WIDTH - 240, 20))
        
        # Handle countdown state
        if game_state == COUNTDOWN:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            # Calculate remaining time
            elapsed_time = time.time() - countdown_start
            remaining_time = max(0, countdown_duration - elapsed_time)
            
            if remaining_time > 0:
                # Draw countdown
                countdown_text = game_over_font.render(str(int(remaining_time + 0.99)), True, YELLOW)
                screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - 50))
                
                # Draw "Get Ready!" text
                ready_text = font.render("Get Ready!", True, WHITE)
                screen.blit(ready_text, (WIDTH // 2 - ready_text.get_width() // 2, HEIGHT // 2 + 50))
            else:
                game_state = PLAYING
        
        # Draw game over screen
        if game_state == GAME_OVER:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            
            # Final score
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 + 20))
            
            # Restart instructions
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 70))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()