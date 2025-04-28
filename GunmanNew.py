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
SKIN_COLOR = (200, 170, 150)  # Darker skin tone
JACKET_COLOR = (50, 60, 100)  # Navy blue jacket
PANTS_COLOR = (30, 40, 70)    # Dark blue pants
HAT_COLOR = (20, 20, 20)      # Black hat
RIFLE_COLOR = (120, 90, 60)   # Brown for rifle
RIFLE_BARREL_COLOR = (80, 80, 80)  # Dark gray for barrel

# Star colors
STAR_COLORS = [
    (255, 255, 220),  # Warm white
    (220, 220, 255),  # Cool white
    (255, 240, 200),  # Slightly yellow
    (200, 220, 255)   # Slightly blue
]

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

# Stars
stars = []
for _ in range(100):
    stars.append({
        'x': random.randint(0, width),
        'y': random.randint(0, height - 250),  # Keep stars in sky
        'size': random.uniform(0.5, 2.5),
        'twinkle_speed': random.uniform(0.02, 0.1),
        'twinkle_offset': random.uniform(0, 6.28),  # Random phase
        'color': random.choice(STAR_COLORS)
    })

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
        self.rotation = random.uniform(0, 360)  # Random starting rotation
        self.rotation_speed = random.uniform(-2, 2)  # Random rotation speed

    def update(self):
        self.x -= self.speed
        self.rotation += self.rotation_speed
        if self.x + self.size < 0:
            self.active = False

    def draw(self, surface):
        # Draw asteroid
        self.draw_asteroid(surface)
        
        # Draw health bar
        health_width = self.size * (self.health / 100)
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 20, self.size, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 20, health_width, 5))

    def draw_asteroid(self, surface):
        # Scale the asteroid based on the size
        scale = self.size / 40  # Normalize to make a 40px size = scale 1
        
        # Base point for the asteroid (center)
        asteroid_x = self.x + self.size / 2
        asteroid_y = self.y + self.size / 2
        
        # Create a rough, irregular shape for the asteroid
        num_points = 12
        points = []
        for i in range(num_points):
            angle = (360 / num_points) * i
            radius = self.size / 2 * (0.8 + 0.2 * random.random())  # Randomize radius for irregular shape
            x = asteroid_x + radius * math.cos(math.radians(angle + self.rotation))
            y = asteroid_y + radius * math.sin(math.radians(angle + self.rotation))
            points.append((x, y))
        
        # Draw the asteroid
        pygame.draw.polygon(surface, (100, 100, 100), points)  # Gray color for asteroid
        pygame.draw.polygon(surface, (80, 80, 80), points, 2)  # Darker outline
        
        # Add some craters for detail
        for _ in range(3):
            crater_x = asteroid_x + random.uniform(-self.size/3, self.size/3)
            crater_y = asteroid_y + random.uniform(-self.size/3, self.size/3)
            crater_radius = random.uniform(3, 6) * scale
            pygame.draw.circle(surface, (120, 120, 120), (int(crater_x), int(crater_y)), int(crater_radius))
            pygame.draw.circle(surface, (80, 80, 80), (int(crater_x), int(crater_y)), int(crater_radius), 1)

    def check_hit(self, bullet_x, bullet_y):
        # Use a simple circular hitbox for collision detection
        asteroid_center_x = self.x + self.size / 2
        asteroid_center_y = self.y + self.size / 2
        distance = math.sqrt((bullet_x - asteroid_center_x)**2 + (bullet_y - asteroid_center_y)**2)
        if distance < self.size / 2:
            self.health -= 25
            if self.health <= 0:
                self.active = False
            return True
        return False
def draw_hunter(surface, x, y, aim_angle):
    # Constrain the aim angle to realistic values
    aim_angle = max(min(aim_angle, 30), -30)
    
    # Calculate positions based on the aim angle
    rifle_length = 120
    
    # Draw legs - now more tactical looking with boots
    leg_spread = 20
    pygame.draw.rect(surface, PANTS_COLOR, (x - 25, y + 40, 20, 80))  # Left leg
    pygame.draw.rect(surface, PANTS_COLOR, (x + 5, y + 40, 20, 80))  # Right leg
    
    # Draw tactical boots
    pygame.draw.rect(surface, BLACK, (x - 30, y + 120, 25, 15))  # Left boot
    pygame.draw.rect(surface, BLACK, (x + 5, y + 120, 25, 15))  # Right boot
    pygame.draw.rect(surface, (40, 40, 40), (x - 30, y + 120, 25, 8))  # Left boot detail
    pygame.draw.rect(surface, (40, 40, 40), (x + 5, y + 120, 25, 8))  # Right boot detail
    
    # Draw body armor 
    jacket_width = 50
    jacket_height = 80
    pygame.draw.rect(surface, JACKET_COLOR, (x - jacket_width//2, y - 40, jacket_width, jacket_height))
    
    # Draw tactical vest details
    vest_detail_color = (20, 30, 50) 
    pygame.draw.rect(surface, vest_detail_color, (x - jacket_width//2 + 5, y - 30, 40, 10))  # Upper chest strap
    pygame.draw.rect(surface, vest_detail_color, (x - jacket_width//2 + 5, y - 10, 40, 10))  # Middle chest strap
    pygame.draw.rect(surface, vest_detail_color, (x - jacket_width//2 + 5, y + 10, 40, 10))  # Lower chest strap
    
    # Add a tactical pocket
    pygame.draw.rect(surface, (30, 40, 60), (x - jacket_width//2 + 5, y - 35, 15, 20))
    pygame.draw.line(surface, BLACK, (x - jacket_width//2 + 5, y - 25), 
                    (x - jacket_width//2 + 20, y - 25), 2)
    
    # Draw head
    head_radius = 15
    head_x = x
    head_y = y - 55
    pygame.draw.circle(surface, SKIN_COLOR, (head_x, head_y), head_radius)
    
    # Draw tactical helmet instead of hat
    helmet_points = [
        (head_x - head_radius - 3, head_y - head_radius + 5),
        (head_x - head_radius, head_y - head_radius * 1.5),
        (head_x + head_radius, head_y - head_radius * 1.5),
        (head_x + head_radius + 3, head_y - head_radius + 5)
    ]
    pygame.draw.polygon(surface, HAT_COLOR, helmet_points)
    
    # Add night vision goggles on helmet
    pygame.draw.rect(surface, (30, 30, 30), (head_x - 10, head_y - head_radius * 1.4, 20, 5))
    pygame.draw.circle(surface, (20, 100, 20), (head_x, head_y - head_radius * 1.2), 4)  # Green lens
    
    # Face mask
    pygame.draw.rect(surface, (40, 40, 40), (head_x - 10, head_y, 20, 10))
    
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
    stock_height = 25  # Slightly taller stock
    stock_angle = aim_angle + 180  # Opposite direction of barrel
    
    # Calculate stock end position
    stock_end_x = rifle_pivot_x + stock_width * math.cos(math.radians(stock_angle))
    stock_end_y = rifle_pivot_y + stock_width * math.sin(math.radians(stock_angle))
    
    # Calculate perpendicular points for stock
    stock_top_dx = stock_height/2 * math.cos(math.radians(perp_angle))
    stock_top_dy = stock_height/2 * math.sin(math.radians(perp_angle))
    
    # Draw modern tactical stock as polygon
    stock_points = [
        (rifle_pivot_x + stock_top_dx, rifle_pivot_y + stock_top_dy),
        (rifle_pivot_x - stock_top_dx, rifle_pivot_y - stock_top_dy),
        (stock_end_x - stock_top_dx*1.2, stock_end_y - stock_top_dy*1.2),
        (stock_end_x + stock_top_dx*1.2, stock_end_y + stock_top_dy*1.2)
    ]
    pygame.draw.polygon(surface, BLACK, stock_points)  # Black tactical stock
    
    # Draw tactical accessories - scope
    scope_length = 25
    scope_height = 10
    scope_pos_x = rifle_pivot_x + rifle_length * 0.3 * math.cos(math.radians(aim_angle))
    scope_pos_y = rifle_pivot_y + rifle_length * 0.3 * math.sin(math.radians(aim_angle))
    
    # Calculate scope position
    scope_top_dx = scope_height/2 * math.cos(math.radians(perp_angle))
    scope_top_dy = scope_height/2 * math.sin(math.radians(perp_angle))
    
    scope_start_x = scope_pos_x - scope_length/2 * math.cos(math.radians(aim_angle))
    scope_start_y = scope_pos_y - scope_length/2 * math.sin(math.radians(aim_angle))
    scope_end_x = scope_pos_x + scope_length/2 * math.cos(math.radians(aim_angle))
    scope_end_y = scope_pos_y + scope_length/2 * math.sin(math.radians(aim_angle))
    
    scope_points = [
        (scope_start_x + scope_top_dx, scope_start_y + scope_top_dy),
        (scope_start_x - scope_top_dx, scope_start_y - scope_top_dy),
        (scope_end_x - scope_top_dx, scope_end_y - scope_top_dy),
        (scope_end_x + scope_top_dx, scope_end_y + scope_top_dy)
    ]
    pygame.draw.polygon(surface, BLACK, scope_points)
    
    # Scope lens
    lens_pos_x = scope_end_x - 5 * math.cos(math.radians(aim_angle))
    lens_pos_y = scope_end_y - 5 * math.sin(math.radians(aim_angle))
    lens_radius = 3
    pygame.draw.circle(surface, (100, 180, 255), (int(lens_pos_x), int(lens_pos_y)), lens_radius)
    
    # Draw arms/hands holding the rifle
    # Front arm/hand 
    front_hand_x = rifle_pivot_x + rifle_length * 0.6 * math.cos(math.radians(aim_angle))
    front_hand_y = rifle_pivot_y + rifle_length * 0.6 * math.sin(math.radians(aim_angle))
    
    arm_width = 8
    
    # Draw front arm connecting to body - now with tactical gloves
    pygame.draw.line(surface, JACKET_COLOR, (x - 15, y - 20), (front_hand_x, front_hand_y), arm_width)
    
    # Draw front hand with tactical glove
    pygame.draw.circle(surface, BLACK, (int(front_hand_x), int(front_hand_y)), 8)
    
    # Rear arm/hand (at stock)
    rear_hand_x = rifle_pivot_x + 5 * math.cos(math.radians(aim_angle))
    rear_hand_y = rifle_pivot_y + 5 * math.sin(math.radians(aim_angle))
    
    # Draw rear arm
    pygame.draw.line(surface, JACKET_COLOR, (x + 10, y - 10), (rear_hand_x, rear_hand_y), arm_width)
    
    # Draw rear hand with tactical glove
    pygame.draw.circle(surface, BLACK, (int(rear_hand_x), int(rear_hand_y)), 8)
    
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
    
    # Night sky gradient 
    for y in range(height):
        gradient = (
            max(5, min(15 - y * 10 // height, 20)),  # Very dark blue-grey sky
            max(10, min(20 - y * 10 // height, 25)),
            max(30, min(40 - y * 10 // height, 50))
        )
        pygame.draw.line(background, gradient, (0, y), (width, y))

    # Ground 
    ground_height = height - 150
    pygame.draw.rect(background, (20, 30, 15), (0, ground_height, width, height - ground_height))
    
    # Add fence in the foreground
    fence_y = ground_height + 20
    for x in range(0, width, 30):
        pygame.draw.rect(background, (30, 25, 20), (x, fence_y, 5, 40))
        pygame.draw.rect(background, (35, 30, 25), (x-15, fence_y+10, 30, 5))
    return background

def draw_moon(surface):
    moon_radius = 50
    moon_x = width - 100  # Position the moon on the right side of the screen
    moon_y = 100  # Position the moon near the top of the screen
    
    # Draw the base of the moon
    pygame.draw.circle(surface, (200, 200, 200), (moon_x, moon_y), moon_radius)
    
    # Draw craters on the moon
    craters = [
        {'x': moon_x - 30, 'y': moon_y - 20, 'radius': 10},
        {'x': moon_x + 20, 'y': moon_y + 10, 'radius': 8},
        {'x': moon_x - 10, 'y': moon_y + 30, 'radius': 12},
        {'x': moon_x + 25, 'y': moon_y - 15, 'radius': 6},
    ]
    
    for crater in craters:
        pygame.draw.circle(surface, (180, 180, 180), (crater['x'], crater['y']), crater['radius'])
        pygame.draw.circle(surface, (160, 160, 160), (crater['x'], crater['y']), crater['radius'], 1)

def draw_stars(surface, time):
    for star in stars:
        # Calculate twinkle effect
        twinkle = abs(math.sin(time * star['twinkle_speed'] + star['twinkle_offset']))
        size = star['size'] * (0.7 + 0.5 * twinkle)
        
        # Brighten color based on twinkle
        base_r, base_g, base_b = star['color']
        brightness = 0.7 + 0.3 * twinkle
        color = (
            min(255, int(base_r * brightness)),
            min(255, int(base_g * brightness)),
            min(255, int(base_b * brightness))
        )
        
        # Draw the star
        pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), size)

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
        
        # Draw twinkling stars
        draw_stars(screen, current_time / 1000)
        
        # Draw the moon
        draw_moon(screen)
        
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