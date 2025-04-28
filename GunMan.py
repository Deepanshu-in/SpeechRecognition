import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hunter with Rapid-Fire Rifle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKIN_COLOR = (255, 213, 170)
JACKET_COLOR = (110, 110, 80)  # Olive/khaki color
PANTS_COLOR = (100, 100, 70)  # Slightly darker olive
HAT_COLOR = (70, 60, 50)  # Dark brown
RIFLE_COLOR = (120, 90, 60)  # Brown for rifle
RIFLE_BARREL_COLOR = (80, 80, 80)  # Dark gray for barrel

# Rocket colors
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)

# Colorful bullet colors
BULLET_COLORS = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (255, 128, 0),    # Orange
    (128, 0, 255),    # Purple
    (255, 215, 0)     # Gold
]

# Game variables
aim_angle = 0  # In degrees, 0 is horizontal
bullets = []  # List to store active bullets
last_shot_time = 0
shoot_delay = 80  # Milliseconds between shots

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.radius = 4
        self.color = random.choice(BULLET_COLORS)
        self.active = True
        self.trail = []
        self.max_trail_length = 5
    
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if self.x < 0 or self.x > width or self.y < 0 or self.y > height:
            self.active = False
    
    def draw(self, surface):
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / (self.max_trail_length + 1))
            radius = self.radius * (i + 1) / (self.max_trail_length + 1)
            trail_surf = pygame.Surface((int(radius*2), int(radius*2)), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.circle(trail_surf, (r, g, b, alpha), (int(radius), int(radius)), int(radius))
            surface.blit(trail_surf, (int(trail_x - radius), int(trail_y - radius)))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self):
        self.size = random.randint(30, 50)
        self.x = width + self.size
        self.y = random.randint(100, height - 100)
        self.speed = random.uniform(2, 4)
        self.health = 100
        self.active = True
        self.flame_animation = random.uniform(0, 6.28)  # Random starting point for flame animation
    
    def update(self):
        self.x -= self.speed
        self.flame_animation += 0.2
        if self.x + self.size < 0:
            self.active = False

    def draw(self, surface):
        # Instead of drawing a rectangle, draw a rocket pointing left
        self.draw_rocket(surface)
        
        # Draw health bar
        health_width = self.size * (self.health / 100)
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 20, self.size, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 20, health_width, 5))

    def draw_rocket(self, surface):
        # Scale the rocket based on the size
        scale = self.size / 40  # Normalize to make a 40px size = scale 1
        
        # Base point for the rocket (center)
        rocket_x = self.x + self.size / 2
        rocket_y = self.y + self.size / 2
        
        # Body (horizontal rectangle) - pointing left
        body_length = 40 * scale
        body_width = 20 * scale
        
        body_points = [
            (rocket_x, rocket_y - body_width/2),
            (rocket_x, rocket_y + body_width/2),
            (rocket_x - body_length, rocket_y + body_width/2),
            (rocket_x - body_length, rocket_y - body_width/2)
        ]
        pygame.draw.polygon(surface, WHITE, body_points)
        
        # Nose cone (pointing left)
        nose_length = 30 * scale
        nose_points = [
            (rocket_x - body_length, rocket_y - body_width/2),
            (rocket_x - body_length, rocket_y + body_width/2),
            (rocket_x - body_length - nose_length, rocket_y)
        ]
        pygame.draw.polygon(surface, RED, nose_points)
        
        # Window
        window_radius = 7 * scale
        window_x = rocket_x - body_length/2
        window_y = rocket_y
        pygame.draw.circle(surface, LIGHT_BLUE, (int(window_x), int(window_y)), int(window_radius))
        pygame.draw.circle(surface, (200, 200, 200), (int(window_x), int(window_y)), int(window_radius), 2)
        
        # Fins (vertical, since rocket is horizontal)
        fin_size = 20 * scale
        
        top_fin = [
            (rocket_x - body_length * 0.7, rocket_y - body_width/2),
            (rocket_x - body_length * 0.7, rocket_y - body_width/2 - fin_size),
            (rocket_x - body_length * 0.4, rocket_y - body_width/2)
        ]
        
        bottom_fin = [
            (rocket_x - body_length * 0.7, rocket_y + body_width/2),
            (rocket_x - body_length * 0.7, rocket_y + body_width/2 + fin_size),
            (rocket_x - body_length * 0.4, rocket_y + body_width/2)
        ]
        
        pygame.draw.polygon(surface, RED, top_fin)
        pygame.draw.polygon(surface, RED, bottom_fin)
        
        # Flame animation (on the right side, since rocket points left)
        flame_size = (math.sin(self.flame_animation) * 5 + 15) * scale
        
        flame_points = [
            (rocket_x, rocket_y - body_width/3),
            (rocket_x, rocket_y + body_width/3),
            (rocket_x + flame_size, rocket_y)
        ]
        pygame.draw.polygon(surface, ORANGE, flame_points)
        
        inner_flame_points = [
            (rocket_x, rocket_y - body_width/5),
            (rocket_x, rocket_y + body_width/5),
            (rocket_x + flame_size * 0.7, rocket_y)
        ]
        pygame.draw.polygon(surface, YELLOW, inner_flame_points)

    def check_hit(self, bullet_x, bullet_y):
        # Use a simple rectangular hitbox for collision detection
        if (self.x < bullet_x < self.x + self.size and 
            self.y < bullet_y < self.y + self.size):
            self.health -= 25
            if self.health <= 0:
                self.active = False
            return True
        return False

def draw_hunter(surface, x, y, aim_angle):
    # Constrain the aim angle to realistic values (-30 to 30 degrees)
    aim_angle = max(min(aim_angle, 30), -30)
    
    # Calculate positions based on the aim angle
    rifle_length = 120
    
    # Draw legs
    leg_spread = 20
    pygame.draw.rect(surface, PANTS_COLOR, (x - 25, y + 40, 20, 80))  # Left leg
    pygame.draw.rect(surface, PANTS_COLOR, (x + 5, y + 40, 20, 80))  # Right leg
    
    # Draw feet
    pygame.draw.rect(surface, BLACK, (x - 30, y + 120, 25, 10))  # Left foot
    pygame.draw.rect(surface, BLACK, (x + 5, y + 120, 25, 10))  # Right foot
    
    # Draw body (jacket)
    jacket_width = 50
    jacket_height = 80
    pygame.draw.rect(surface, JACKET_COLOR, (x - jacket_width//2, y - 40, jacket_width, jacket_height))
    
    # Draw jacket pocket
    pocket_size = 15
    pygame.draw.rect(surface, JACKET_COLOR, (x - jacket_width//2 + 5, y, pocket_size, pocket_size))
    pygame.draw.line(surface, BLACK, (x - jacket_width//2 + 5, y), (x - jacket_width//2 + 5 + pocket_size, y), 2)
    pygame.draw.line(surface, BLACK, (x - jacket_width//2 + 5, y + pocket_size), 
                    (x - jacket_width//2 + 5 + pocket_size, y + pocket_size), 2)
    
    # Draw head
    head_radius = 15
    head_x = x
    head_y = y - 55
    pygame.draw.circle(surface, SKIN_COLOR, (head_x, head_y), head_radius)
    
    # Draw hat
    hat_width = 35
    hat_height = 12
    brim_height = 6
    pygame.draw.rect(surface, HAT_COLOR, (head_x - hat_width//2, head_y - head_radius - hat_height, hat_width, hat_height))
    pygame.draw.rect(surface, HAT_COLOR, (head_x - hat_width//2 - 5, head_y - head_radius - brim_height, hat_width + 10, brim_height))
    
    # Calculate rifle position based on aim angle
    rifle_pivot_x = x + 15
    rifle_pivot_y = y - 20
    
    # Calculate rifle end position
    rifle_end_x = rifle_pivot_x + rifle_length * math.cos(math.radians(aim_angle))
    rifle_end_y = rifle_pivot_y + rifle_length * math.sin(math.radians(aim_angle))
    
    # Rifle width
    rifle_width = 6
    
    # Calculate perpendicular direction for rifle width
    perp_angle = aim_angle + 90
    dx = rifle_width/2 * math.cos(math.radians(perp_angle))
    dy = rifle_width/2 * math.sin(math.radians(perp_angle))
    
    # Draw rifle as polygon with consistent width
    rifle_points = [
        (rifle_pivot_x + dx, rifle_pivot_y + dy),
        (rifle_pivot_x - dx, rifle_pivot_y - dy),
        (rifle_end_x - dx, rifle_end_y - dy),
        (rifle_end_x + dx, rifle_end_y + dy)
    ]
    pygame.draw.polygon(surface, RIFLE_COLOR, rifle_points)
    
    # Draw rifle stock
    stock_width = 15
    stock_height = 20
    stock_angle = aim_angle + 180  # Opposite direction of barrel
    
    # Calculate stock end position
    stock_end_x = rifle_pivot_x + stock_width * math.cos(math.radians(stock_angle))
    stock_end_y = rifle_pivot_y + stock_width * math.sin(math.radians(stock_angle))
    
    # Calculate perpendicular points for stock
    stock_top_dx = stock_height/2 * math.cos(math.radians(perp_angle))
    stock_top_dy = stock_height/2 * math.sin(math.radians(perp_angle))
    
    # Draw stock as polygon
    stock_points = [
        (rifle_pivot_x + stock_top_dx, rifle_pivot_y + stock_top_dy),
        (rifle_pivot_x - stock_top_dx, rifle_pivot_y - stock_top_dy),
        (stock_end_x - stock_top_dx*1.5, stock_end_y - stock_top_dy*1.5),
        (stock_end_x + stock_top_dx*1.5, stock_end_y + stock_top_dy*1.5)
    ]
    pygame.draw.polygon(surface, RIFLE_COLOR, stock_points)
    
    # Draw rifle sight
    sight_height = 8
    sight_pos_x = rifle_pivot_x + rifle_length * 0.3 * math.cos(math.radians(aim_angle))
    sight_pos_y = rifle_pivot_y + rifle_length * 0.3 * math.sin(math.radians(aim_angle))
    
    pygame.draw.line(surface, BLACK, 
                    (sight_pos_x, sight_pos_y - sight_height//2), 
                    (sight_pos_x, sight_pos_y + sight_height//2), 2)
    
    # Draw arms/hands holding the rifle
    # Front arm/hand (near barrel)
    front_hand_x = rifle_pivot_x + rifle_length * 0.7 * math.cos(math.radians(aim_angle))
    front_hand_y = rifle_pivot_y + rifle_length * 0.7 * math.sin(math.radians(aim_angle))
    
    arm_width = 8
    
    # Draw front arm connecting to body
    pygame.draw.line(surface, JACKET_COLOR, (x - 15, y - 20), (front_hand_x, front_hand_y), arm_width)
    
    # Draw front hand
    pygame.draw.circle(surface, SKIN_COLOR, (int(front_hand_x), int(front_hand_y)), 8)
    
    # Rear arm/hand (at stock)
    rear_hand_x = rifle_pivot_x + 5 * math.cos(math.radians(aim_angle))
    rear_hand_y = rifle_pivot_y + 5 * math.sin(math.radians(aim_angle))
    
    # Draw rear arm
    pygame.draw.line(surface, JACKET_COLOR, (x + 10, y - 10), (rear_hand_x, rear_hand_y), arm_width)
    
    # Draw rear hand
    pygame.draw.circle(surface, SKIN_COLOR, (int(rear_hand_x), int(rear_hand_y)), 8)
    
    # Return barrel end position for bullet spawning
    return rifle_end_x, rifle_end_y, aim_angle

def shoot(x, y, angle):
    global last_shot_time
    current_time = pygame.time.get_ticks()
    if current_time - last_shot_time >= shoot_delay:
        spread_angle = angle + random.uniform(-3, 3)
        bullets.append(Bullet(x, y, spread_angle))
        last_shot_time = current_time
        return True
    return False

def reset_game_state():
    """Reset all game variables to initial state"""
    return {
        'enemies': [],
        'enemy_spawn_timer': 0,
        'score': 0,
        'missed_enemies': 0,
        'game_over': False,
        'bullets': [],
        'muzzle_particles': [],
        'recoil_amount': 0
    }

def create_background():
    background = pygame.Surface((width, height))
    
    # Sky gradient (darker military-style sky)
    for y in range(height):
        gradient = (
            max(20, min(50 - y * 20 // height, 50)),  # Dark blue-grey sky
            max(30, min(60 - y * 20 // height, 60)),
            max(40, min(80 - y * 20 // height, 80))
        )
        pygame.draw.line(background, gradient, (0, y), (width, y))

    # Ground (darker terrain)
    ground_height = height - 150
    pygame.draw.rect(background, (40, 50, 30), (0, ground_height, width, height - ground_height))
    
    # Add fence in the foreground
    fence_y = ground_height + 20
    for x in range(0, width, 30):
        pygame.draw.rect(background, (40, 35, 30), (x, fence_y, 5, 40))
        pygame.draw.rect(background, (45, 40, 35), (x-15, fence_y+10, 30, 5))
    return background

def main():
    global aim_angle, bullets
    
    clock = pygame.time.Clock()
    hunter_x = 100
    hunter_y = height - 150
    
    # Constants
    enemy_spawn_delay = 2000
    max_missed_enemies = 5
    aim_speed = 2
    max_recoil = 3
    recoil_recovery_speed = 0.2
    
    # Background
    background = pygame.Surface((width, height))
    for y in range(height):
        gradient = (50, 100 + y * 50 // height, 200)
        pygame.draw.line(background, gradient, (0, y), (width, y))
    
    # Initial game state
    game_state = reset_game_state()
    
    # Create the detailed background
    background = create_background()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        
        # Handle game over and restart
        if game_state['game_over']:
            game_over_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            game_over_surface.fill((0, 0, 0, 128))
            screen.blit(game_over_surface, (0, 0))
            
            font = pygame.font.SysFont(None, 74)
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            score_text = font.render(f"Final Score: {game_state['score']}", True, WHITE)
            restart_text = font.render("Press SPACE to Restart", True, WHITE)
            
            screen.blit(game_over_text, 
                       (width//2 - game_over_text.get_width()//2, 
                        height//2 - game_over_text.get_height()))
            screen.blit(score_text, 
                       (width//2 - score_text.get_width()//2, 
                        height//2 + score_text.get_height()))
            screen.blit(restart_text, 
                       (width//2 - restart_text.get_width()//2, 
                        height//2 + score_text.get_height() * 2))
            
            pygame.display.flip()
            
            if keys[pygame.K_SPACE]:
                # Reset game state
                game_state = reset_game_state()
                bullets = []  # Reset global bullets
                aim_angle = 0  # Reset global aim angle
            continue
        
        # Regular game logic
        if game_state['recoil_amount'] > 0:
            game_state['recoil_amount'] -= recoil_recovery_speed
            if game_state['recoil_amount'] < 0:
                game_state['recoil_amount'] = 0
        
        applied_aim_angle = aim_angle + game_state['recoil_amount']
        
        if keys[pygame.K_UP]:
            aim_angle = max(aim_angle - aim_speed, -30)
        if keys[pygame.K_DOWN]:
            aim_angle = min(aim_angle + aim_speed, 30)
        
        # Spawn enemies
        if current_time - game_state['enemy_spawn_timer'] > enemy_spawn_delay:
            game_state['enemies'].append(Enemy())
            game_state['enemy_spawn_timer'] = current_time

        # Update enemies
        active_enemies = []
        for enemy in game_state['enemies']:
            enemy.update()
            if enemy.x + enemy.size < 0:
                game_state['missed_enemies'] += 1
                if game_state['missed_enemies'] >= max_missed_enemies:
                    game_state['game_over'] = True
            elif enemy.active:
                active_enemies.append(enemy)
        game_state['enemies'] = active_enemies

        # Warning flash
        if game_state['missed_enemies'] >= max_missed_enemies - 2:
            warning_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            warning_alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 128
            warning_surface.fill((255, 0, 0, warning_alpha))
            screen.blit(warning_surface, (0, 0))

        # Shooting
        barrel_x, barrel_y, gun_angle = draw_hunter(screen, hunter_x, hunter_y, applied_aim_angle)
        if keys[pygame.K_SPACE]:
            if shoot(barrel_x, barrel_y, applied_aim_angle):
                game_state['recoil_amount'] = max_recoil
                
                # Muzzle flash
                for _ in range(10):
                    particle_angle = applied_aim_angle + random.uniform(-30, 30)
                    speed = random.uniform(2, 5)
                    size = random.uniform(2, 4)
                    lifespan = random.randint(5, 10)
                    color = random.choice([(255, 255, 0), (255, 150, 0), (255, 100, 0)])
                    
                    game_state['muzzle_particles'].append({
                        'x': barrel_x,
                        'y': barrel_y,
                        'dx': speed * math.cos(math.radians(particle_angle)),
                        'dy': speed * math.sin(math.radians(particle_angle)),
                        'size': size,
                        'life': lifespan,
                        'color': color
                    })

        # Update bullets and collisions
        active_bullets = []
        for bullet in bullets:
            bullet.update()
            if bullet.active:
                for enemy in game_state['enemies']:
                    if enemy.check_hit(bullet.x, bullet.y):
                        bullet.active = False
                        if not enemy.active:
                            game_state['score'] += 100
                        break
                if bullet.active:
                    active_bullets.append(bullet)
        bullets = active_bullets

        # Drawing
        screen.blit(background, (0, 0))
        
        # Draw enemies
        for enemy in game_state['enemies']:
            enemy.draw(screen)

        # Update and draw particles
        active_particles = []
        for particle in game_state['muzzle_particles']:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            
            if particle['life'] > 0:
                alpha = int(255 * particle['life'] / 10)
                r, g, b = particle['color']
                particle_surf = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (r, g, b, alpha), 
                                 (int(particle['size']), int(particle['size'])), int(particle['size']))
                screen.blit(particle_surf, (int(particle['x'] - particle['size']), 
                                         int(particle['y'] - particle['size'])))
                active_particles.append(particle)
        
        game_state['muzzle_particles'] = active_particles

        # Draw hunter and bullets
        barrel_x, barrel_y, gun_angle = draw_hunter(screen, hunter_x, hunter_y, applied_aim_angle)
        for bullet in bullets:
            bullet.draw(screen)

        # Draw HUD
        font = pygame.font.SysFont(None, 24)
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        bullet_text = font.render(f"Bullets: {len(bullets)}", True, WHITE)
        score_text = font.render(f"Score: {game_state['score']}", True, WHITE)
        lives_text = font.render(f"Lives Remaining: {max_missed_enemies - game_state['missed_enemies']}", True, WHITE)
        
        screen.blit(fps_text, (10, 10))
        screen.blit(bullet_text, (10, 40))
        screen.blit(score_text, (10, 70))
        screen.blit(lives_text, (10, 100))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()