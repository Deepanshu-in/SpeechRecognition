import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("River Boat Obstacle Game")

# Colors
RIVER_BLUE = (65, 105, 225)
BANK_GREEN = (34, 139, 34)
BOAT_BROWN_LIGHT = (205, 133, 63)  # Lighter wood color
BOAT_BROWN_DARK = (139, 69, 19)    # Darker wood color
ROCK_GRAY = (105, 105, 105)
ROCK_DARK = (64, 64, 64)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)

# Rock class
class Rock:
    def __init__(self, river, speed):
        self.river = river
        # Position the rock randomly in the river
        self.x = random.randint(river.left_bank + 30, river.right_bank - 30)
        self.y = -50  # Start above the screen
        self.width = random.randint(20, 40)
        self.height = random.randint(20, 40)
        self.speed = speed
        # Slightly vary rock speed
        self.speed_variation = random.uniform(0.9, 1.1)
    def update(self, accelerate=False):
        # Move rock down with the current
        base_speed = self.speed * self.speed_variation
        if accelerate:
            self.y += base_speed * 2.5
        else:
            self.y += base_speed
    
    def is_off_screen(self):
        return self.y > HEIGHT + 50
        
    def draw(self, surface):
        # Draw rock as irregular polygon
        center_x, center_y = self.x, self.y
        points = []
        
        # Generate points for irregular polygon
        for i in range(8):
            angle = i * (2 * 3.14159 / 8)
            radius = random.uniform(self.width * 0.5, self.width * 0.7)
            x = center_x + radius * pygame.math.Vector2(1, 0).rotate(angle * 180 / 3.14159).x
            y = center_y + radius * pygame.math.Vector2(1, 0).rotate(angle * 180 / 3.14159).y
            points.append((x, y))
        
        # Draw main rock
        pygame.draw.polygon(surface, ROCK_GRAY, points)
        
        # Draw some details on the rock
        for _ in range(3):
            detail_x = center_x + random.randint(-self.width//3, self.width//3)
            detail_y = center_y + random.randint(-self.height//3, self.height//3)
            detail_size = random.randint(2, 5)
            pygame.draw.circle(surface, ROCK_DARK, (int(detail_x), int(detail_y)), detail_size)
        
        # Draw water splash around the rock
        for _ in range(4):
            splash_x = center_x + random.randint(-self.width//2 - 5, self.width//2 + 5)
            splash_y = center_y + random.randint(-self.height//2 - 5, self.height//2 + 5)
            pygame.draw.circle(surface, WHITE, (int(splash_x), int(splash_y)), 2)

    def get_hitbox(self):
        # Return a slightly smaller rectangle for collision detection
        return pygame.Rect(
            self.x - self.width//2 + 5,
            self.y - self.height//2 + 5,
            self.width - 10,
            self.height - 10
        )

# River class
class River:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.river_width = int(width * 0.6)
        self.left_bank = int((width - self.river_width) / 2)
        self.right_bank = self.left_bank + self.river_width
        self.particles = []
        self.generate_particles()
        self.flow_speed = 2.0
        
        # Setup initial rocks
        self.rocks = []
        self.rock_spawn_timer = 0
        self.rock_spawn_interval = 60  # Frames between spawns
        
    def generate_particles(self):
        # Generate initial water particles
        for _ in range(200):
            x = random.randint(self.left_bank + 10, self.right_bank - 10)
            y = random.randint(0, self.height)
            size = random.randint(2, 5)
            self.particles.append([x, y, size])
    
    def spawn_rock(self):
        new_rock = Rock(self, self.flow_speed)
        self.rocks.append(new_rock)
            
    def update(self, accelerate=False):
        # Set flow speed based on acceleration
        speed = self.flow_speed * (2.5 if accelerate else 1.0)
        
        # Update particle positions
        for particle in self.particles:
            # Move particles downward
            particle[1] += speed
            
            # Reset particles that move off-screen
            if particle[1] > self.height:
                particle[1] = 0
                particle[0] = random.randint(self.left_bank + 10, self.right_bank - 10)
                particle[2] = random.randint(2, 5)
        
        # Update rocks
        for rock in self.rocks[:]:
            rock.update(accelerate)
            if rock.is_off_screen():
                self.rocks.remove(rock)
        
        # Spawn new rocks
        self.rock_spawn_timer += 1
        if self.rock_spawn_timer >= self.rock_spawn_interval:
            self.spawn_rock()
            self.rock_spawn_timer = 0
            # Randomly vary next spawn time
            self.rock_spawn_interval = random.randint(50, 120)
    
    def draw(self, surface):
        # Draw river banks (green)
        pygame.draw.rect(surface, BANK_GREEN, (0, 0, self.left_bank, self.height))
        pygame.draw.rect(surface, BANK_GREEN, (self.right_bank, 0, self.width - self.right_bank, self.height))
        
        # Draw river (blue)
        pygame.draw.rect(surface, RIVER_BLUE, (self.left_bank, 0, self.river_width, self.height))
        
        # Draw water particles
        for particle in self.particles:
            x, y, size = particle
            pygame.draw.circle(surface, LIGHT_BLUE, (int(x), int(y)), size)
        
        # Draw rocks
        for rock in self.rocks:
            rock.draw(surface)

class WoodenBoat:
    def __init__(self, river):
        self.river = river
        # Position the boat in the middle of the river
        self.x = WIDTH // 2
        self.y = HEIGHT * 0.8
        self.width = 50
        self.height = 90
        self.speed = 4
        
        # For paddle animation
        self.paddle_angle_left = 0
        self.paddle_angle_right = 0
        self.paddle_direction_left = 1
        self.paddle_direction_right = 1
        
        # Collision detection
        self.hit = False
    
    def update(self, left_pressed, right_pressed):
        # Skip update if boat has been hit
        if self.hit:
            return
            
        # Move boat left or right based on key presses
        if left_pressed:
            self.x -= self.speed
            # Animate left paddle
            self.paddle_angle_left += self.paddle_direction_left * 5
            if abs(self.paddle_angle_left) > 30:
                self.paddle_direction_left *= -1
        else:
            # Reset left paddle position
            if self.paddle_angle_left != 0:
                self.paddle_angle_left = max(-5, min(5, self.paddle_angle_left - self.paddle_direction_left * 3))
                if -5 <= self.paddle_angle_left <= 5:
                    self.paddle_angle_left = 0
                    self.paddle_direction_left = 1
                
        if right_pressed:
            self.x += self.speed
            # Animate right paddle
            self.paddle_angle_right += self.paddle_direction_right * 5
            if abs(self.paddle_angle_right) > 30:
                self.paddle_direction_right *= -1
        else:
            # Reset right paddle position
            if self.paddle_angle_right != 0:
                self.paddle_angle_right = max(-5, min(5, self.paddle_angle_right - self.paddle_direction_right * 3))
                if -5 <= self.paddle_angle_right <= 5:
                    self.paddle_angle_right = 0
                    self.paddle_direction_right = 1
        
        # Keep boat within river boundaries
        min_x = self.river.left_bank + self.width // 2 + 10
        max_x = self.river.right_bank - self.width // 2 - 10
        
        if self.x < min_x:
            self.x = min_x
        if self.x > max_x:
            self.x = max_x
    
    def check_collision(self, rocks):
        if self.hit:
            return True
            
        boat_hitbox = self.get_hitbox()
        for rock in rocks:
            rock_hitbox = rock.get_hitbox()
            if boat_hitbox.colliderect(rock_hitbox):
                self.hit = True
                return True
        return False
    
    def get_hitbox(self):
        # Return a smaller rectangle for collision detection
        return pygame.Rect(
            self.x - self.width//2 + 10,
            self.y - self.height//2 + 15,
            self.width - 20,
            self.height - 25
        )
    
    def draw(self, surface):
        # Boat dimensions
        boat_width = self.width
        boat_height = self.height
        
        # Draw boat hull
        # Start with the hull outline
        boat_points = [
            (self.x - boat_width//2, self.y + boat_height//2 - 10),  # Bottom left
            (self.x - boat_width//2 + 5, self.y - boat_height//2 + 10),  # Top left
            (self.x, self.y - boat_height//2),  # Top middle 
            (self.x + boat_width//2 - 5, self.y - boat_height//2 + 10),  # Top right
            (self.x + boat_width//2, self.y + boat_height//2 - 10),  # Bottom right
            (self.x, self.y + boat_height//2),  # Bottom middle 
        ]
        
        # Use red color if hit, otherwise use normal color
        hull_color = RED if self.hit else BOAT_BROWN_LIGHT
        pygame.draw.polygon(surface, hull_color, boat_points)
        
        # Draw the horizontal slats
        for i in range(1, 5):
            y_pos = self.y - boat_height//2 + (boat_height * i)//5
            left_x = self.x - boat_width//2 + 5 if i == 1 else self.x - boat_width//2 + 3
            right_x = self.x + boat_width//2 - 5 if i == 1 else self.x + boat_width//2 - 3
            
            # Calculate curve for the upper slats
            if i <= 2:
                # More curved at the top, straighter at the bottom
                mid_offset = 15 - i * 5
                mid_x = self.x
                mid_y = y_pos - mid_offset
                
                # Draw curved plank
                pygame.draw.line(surface, BOAT_BROWN_DARK, (left_x, y_pos), (mid_x, mid_y), 2)
                pygame.draw.line(surface, BOAT_BROWN_DARK, (mid_x, mid_y), (right_x, y_pos), 2)
            else:
                # Straight planks for lower part
                pygame.draw.line(surface, BOAT_BROWN_DARK, (left_x, y_pos), (right_x, y_pos), 2)
        
        # Draw the middle support plank
        pygame.draw.line(surface, BOAT_BROWN_DARK, 
                       (self.x, self.y - boat_height//2 + 5), 
                       (self.x, self.y + boat_height//2 - 5), 2)
        
        # Draw bench 
        bench_width = boat_width - 10
        pygame.draw.rect(surface, BOAT_BROWN_DARK, 
                      (self.x - bench_width//2, self.y - 5, bench_width, 10))
        
        # Draw oars/paddles
        self._draw_paddle(surface, "left")
        self._draw_paddle(surface, "right")
        
        # Draw wake effect behind the boat
        for i in range(3):
            offset = 5 + i*5
            pygame.draw.arc(surface, WHITE, 
                           (self.x - 15 - i*5, self.y + boat_height//2 + offset, 
                            30 + i*10, 10), 
                           0, 3.14, 2)
            
    def _draw_paddle(self, surface, side):
        # Don't draw paddles if boat is hit
        if self.hit:
            return
            
        # Paddle dimensions
        paddle_length = 60
        paddle_width = 8
        
        # Position paddle based on side
        if side == "left":
            # Left paddle
            pivot_x = self.x - self.width//2 - 5
            pivot_y = self.y
            angle = self.paddle_angle_left
        else:
            # Right paddle
            pivot_x = self.x + self.width//2 + 5
            pivot_y = self.y
            angle = self.paddle_angle_right
        
        # Calculate paddle position based on angle
        # Convert angle to radians
        angle_rad = angle * 3.14159 / 180
        
        # Handle direction-specific rotation
        if side == "left":
            end_x = pivot_x - paddle_length * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(angle).x
            end_y = pivot_y - paddle_length * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(angle).y
        else:
            end_x = pivot_x + paddle_length * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(angle).x
            end_y = pivot_y - paddle_length * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(angle).y
        
        # Draw the paddle shaft
        pygame.draw.line(surface, BOAT_BROWN_DARK, (pivot_x, pivot_y), (end_x, end_y), 3)
        
        # Draw the paddle blade
        if side == "left":
            blade_x = end_x - 10
            blade_y = end_y
        else:
            blade_x = end_x + 10
            blade_y = end_y
            
        # Simple rectangle blade
        blade_points = [
            (end_x - 5 if side == "left" else end_x + 5, end_y - 10),
            (blade_x, blade_y),
            (end_x - 5 if side == "left" else end_x + 5, end_y + 10)
        ]
        pygame.draw.polygon(surface, BOAT_BROWN_DARK, blade_points)

# Game class to manage game state
class Game:
    def __init__(self):
        self.river = River(WIDTH, HEIGHT)
        self.boat = WoodenBoat(self.river)
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
    
    def update(self, up_pressed, left_pressed, right_pressed):
        if not self.game_over:
            self.river.update(up_pressed)
            self.boat.update(left_pressed, right_pressed)
            
            # Check for collisions
            if self.boat.check_collision(self.river.rocks):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
            
            # Update score
            self.score += 1
    
    def draw(self, surface):
        # Draw river and boat
        self.river.draw(surface)
        self.boat.draw(surface)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        surface.blit(score_text, (10, 10))
        
        # Draw instructions if not game over
        if not self.game_over:
            instructions = [
                "UP ARROW: Move forward",
                "LEFT/RIGHT ARROWS: Move boat sideways",
                "Avoid the rocks!"
            ]
            
            for i, text in enumerate(instructions):
                rendered_text = self.small_font.render(text, True, (0, 0, 0))
                surface.blit(rendered_text, (10, 50 + i*25))
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            surface.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            
            # Score text
            final_score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            surface.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
            
            # High score text
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
            surface.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 40))
            
            # Restart instructions
            restart_text = self.font.render("Press SPACE to play again", True, (255, 255, 255))
            surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
    
    def reset(self):
        self.river = River(WIDTH, HEIGHT)
        self.boat = WoodenBoat(self.river)
        self.game_over = False
        self.score = 0

# Main function
def main():
    # Create game
    game = Game()
    
    # Clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Control flags
    up_pressed = False
    left_pressed = False
    right_pressed = False
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    up_pressed = True
                elif event.key == pygame.K_LEFT:
                    left_pressed = True
                elif event.key == pygame.K_RIGHT:
                    right_pressed = True
                elif event.key == pygame.K_SPACE and game.game_over:
                    game.reset()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up_pressed = False
                elif event.key == pygame.K_LEFT:
                    left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    right_pressed = False
        
        # Update game state
        game.update(up_pressed, left_pressed, right_pressed)
        
        # Draw everything
        screen.fill((200, 230, 255))  # Light sky blue background
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Quit pygame
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()