import pygame
import random
import math
from PIL import Image, ImageDraw

# Initialize pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Function to create ship designs using PIL
def create_ship_image(width, height, design_type, color_scheme):
    # Create a transparent image
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    if design_type == "player":
        # Player ship - sleek design with thrusters
        primary, secondary, highlight = color_scheme
        
        # Main body
        draw.polygon([(width//2, 0), (width//5, height*2//3), (width*4//5, height*2//3)], fill=primary)
        
        # Cockpit
        draw.ellipse((width*3//8, height//4, width*5//8, height//2), fill=highlight)
        
        # Wings
        draw.polygon([(width//5, height*2//3), (0, height), (width//3, height*2//3)], fill=secondary)
        draw.polygon([(width*4//5, height*2//3), (width, height), (width*2//3, height*2//3)], fill=secondary)
        
        # Thrusters
        draw.rectangle((width*1//3, height*2//3, width*2//5, height), fill=secondary)
        draw.rectangle((width*3//5, height*2//3, width*2//3, height), fill=secondary)
        
        # Thruster flames
        flame_points = [
            (width*3//8, height), (width*3//8, height*9//8), (width*2//5, height),
            (width*5//8, height), (width*5//8, height*9//8), (width*3//5, height)
        ]
        draw.polygon(flame_points, fill=(255, 165, 0, 200))
        
        # Details
        draw.line([(width//2, 0), (width//2, height//4)], fill=highlight, width=2)
        draw.line([(width//3, height//2), (width*2//3, height//2)], fill=highlight, width=1)
        
    elif design_type == "enemy1":
        # Small fast enemy - sharp angles
        primary, secondary, highlight = color_scheme
        
        # Main body
        draw.polygon([(width//2, 0), (0, height*2//3), (width, height*2//3)], fill=primary)
        
        # Bottom part
        draw.polygon([(width//4, height*2//3), (width*3//4, height*2//3), (width//2, height)], fill=secondary)
        
        # Eye/window
        draw.ellipse((width*3//8, height//4, width*5//8, height//2), fill=highlight)
        
        # Details
        draw.line([(width//3, height//2), (width*2//3, height//2)], fill=primary, width=2)
        
    elif design_type == "enemy2":
        # Medium enemy - rounded with spikes
        primary, secondary, highlight = color_scheme
        
        # Main body
        draw.ellipse((width//5, height//5, width*4//5, height*3//4), fill=primary)
        
        # Spikes
        spike_points = [
            (width//5, height//2), (0, height//3),
            (width*4//5, height//2), (width, height//3),
            (width//2, height*3//4), (width//2, height)
        ]
        draw.line(spike_points[0:2], fill=secondary, width=3)
        draw.line(spike_points[2:4], fill=secondary, width=3)
        draw.line(spike_points[4:6], fill=secondary, width=3)
        
        # Central eye
        draw.ellipse((width*2//5, height*2//5, width*3//5, height*3//5), fill=highlight)
        
        # Details
        draw.arc((width//4, height//4, width*3//4, height*2//3), 0, 180, fill=secondary, width=2)
        
    elif design_type == "enemy3":
        # Large enemy - mothership style
        primary, secondary, highlight = color_scheme
        
        # Main saucer body
        draw.ellipse((width//10, height//3, width*9//10, height*2//3), fill=primary)
        
        # Top dome
        draw.ellipse((width//4, height//6, width*3//4, height//2), fill=secondary)
        
        # Bottom structures
        for i in range(3):
            x1 = width * (3 + i*2) // 10
            x2 = width * (4 + i*2) // 10
            y1 = height * 2 // 3
            y2 = height * 9 // 10
            draw.rectangle((x1, y1, x2, y2), fill=secondary)
        
        # Lights/windows
        for i in range(5):
            x = width * (2 + i*1.5) // 10
            y = height // 2
            r = height // 20
            draw.ellipse((x-r, y-r, x+r, y+r), fill=highlight)
        
        # Details
        draw.arc((width//8, height//4, width*7//8, height*3//4), 0, 180, fill=highlight, width=2)
        
    elif design_type == "obstacle":
        # Space rock/asteroid
        primary, secondary, _ = color_scheme
        
        # Irregular polygon for asteroid shape
        points = []
        num_points = 12
        center_x, center_y = width//2, height//2
        min_rad = min(width, height) * 0.3
        max_rad = min(width, height) * 0.45
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            rad = random.uniform(min_rad, max_rad)
            x = center_x + rad * math.cos(angle)
            y = center_y + rad * math.sin(angle)
            points.append((x, y))
        
        draw.polygon(points, fill=primary)
        
        # Crater details
        for _ in range(4):
            crater_x = random.randint(width//4, width*3//4)
            crater_y = random.randint(height//4, height*3//4)
            crater_r = random.randint(width//10, width//6)
            draw.ellipse((crater_x-crater_r, crater_y-crater_r, 
                           crater_x+crater_r, crater_y+crater_r), fill=secondary)
    
    # Convert PIL image to pygame surface
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()

# Create all game images
player_colors = ((30, 144, 255), (15, 82, 186), (173, 216, 230))  # Blue scheme
enemy1_colors = ((220, 20, 60), (139, 0, 0), (255, 200, 200))  # Red scheme
enemy2_colors = ((255, 140, 0), (205, 102, 0), (255, 228, 196))  # Orange scheme
enemy3_colors = ((148, 0, 211), (75, 0, 130), (230, 230, 250))  # Purple scheme
obstacle_colors = ((119, 136, 153), (47, 79, 79), (0, 0, 0))  # Gray scheme

player_img = create_ship_image(64, 64, "player", player_colors)
enemy1_img = create_ship_image(50, 50, "enemy1", enemy1_colors)
enemy2_img = create_ship_image(60, 60, "enemy2", enemy2_colors)
enemy3_img = create_ship_image(70, 70, "enemy3", enemy3_colors)
obstacle_img = create_ship_image(40, 40, "obstacle", obstacle_colors)

# Create projectile images
def create_projectile_image(width, height, proj_type, color):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    if proj_type == "bullet":
        # Simple elongated bullet
        draw.ellipse((0, 0, width, height//4), fill=color)
        draw.rectangle((0, height//8, width, height*7//8), fill=color)
        draw.ellipse((0, height*3//4, width, height), fill=color)
        
        # Add glow effect
        for i in range(3):
            alpha = 150 - i*50
            glow_color = (*color[:3], alpha)
            draw.ellipse((-i, height*2//3-i, width+i, height+i), fill=glow_color)
            
    elif proj_type == "laser":
        # Laser beam with glow
        draw.rectangle((width//3, 0, width*2//3, height), fill=color)
        
        # Core highlight
        highlight = (255, 255, 255, 200)
        draw.rectangle((width*2//5, 0, width*3//5, height), fill=highlight)
        
        # Glow effect
        for i in range(4):
            alpha = 100 - i*25
            glow_color = (*color[:3], alpha)
            draw.rectangle((width//3-i, 0, width*2//3+i, height), fill=glow_color)
            
    elif proj_type == "cannon":
        # Energy ball
        center_x, center_y = width//2, height//2
        radius = min(width, height) // 2
        
        # Gradient layers
        for i in range(radius, 0, -2):
            alpha = 200 if i > radius*2//3 else 150 if i > radius//3 else 255
            current_color = (*color[:3], alpha)
            draw.ellipse((center_x-i, center_y-i, center_x+i, center_y+i), fill=current_color)
        
        # Core highlight
        highlight = (255, 255, 255, 180)
        draw.ellipse((center_x-radius//3, center_y-radius//3, 
                      center_x+radius//3, center_y+radius//3), fill=highlight)
            
    elif proj_type == "enemy":
        # Enemy projectile - sharp and dangerous looking
        center_x, center_y = width//2, height//2
        radius = min(width, height) // 2
        
        # Spiky ball
        for i in range(8):
            angle = 2 * math.pi * i / 8
            x1 = center_x + radius * 0.5 * math.cos(angle)
            y1 = center_y + radius * 0.5 * math.sin(angle)
            x2 = center_x + radius * math.cos(angle)
            y2 = center_y + radius * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        
        # Center
        draw.ellipse((center_x-radius*0.5, center_y-radius*0.5, 
                      center_x+radius*0.5, center_y+radius*0.5), fill=color)
    
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()

# Create projectile images
bullet_img = create_projectile_image(8, 20, "bullet", (220, 220, 255, 255))
laser_img = create_projectile_image(10, 30, "laser", (0, 255, 255, 255))
cannon_img = create_projectile_image(20, 20, "cannon", (255, 255, 0, 255))
enemy_bullet_img = create_projectile_image(12, 12, "enemy", (255, 0, 0, 255))


# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
font = pygame.font.SysFont("arial", 32)
game_over = False

# Weapon class
class Weapon:
    def __init__(self, img, damage, speed, cooldown):
        self.img = img
        self.damage = damage
        self.speed = speed
        self.cooldown = cooldown
        self.last_shot = 0
        self.is_shooting = False 

    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.cooldown

    def shoot(self, current_time):
        self.last_shot = current_time
        return True

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = player_img
        self.speed = 5
        self.health = 100
        self.weapons = [
            Weapon(bullet_img, 15, 5, 150),    # Regular bullet (Z)
            Weapon(laser_img, 20, 12, 400),    # Laser (X)
            Weapon(cannon_img, 25, 3, 800)     # Cannon (C)
        ]
        self.projectiles = []
        self.laser_active = False
        self.laser_beam = None
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        
        # Thruster animation
        self.thruster_frames = []
        for i in range(4):
            thruster = create_ship_image(64, 64, "player", player_colors)
            self.thruster_frames.append(thruster)
        self.thruster_frame = 0
        self.thruster_delay = 5
        self.thruster_counter = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
        
        # Animate thrusters
        self.thruster_counter += 1
        if self.thruster_counter >= self.thruster_delay:
            self.thruster_counter = 0
            self.thruster_frame = (self.thruster_frame + 1) % len(self.thruster_frames)

    def shoot(self, keys):
        current_time = pygame.time.get_ticks()
        
        # Regular bullet (Z) - Triple shot
        if keys[pygame.K_z]:
            if self.weapons[0].can_shoot(current_time):
                self.weapons[0].last_shot = current_time
                # Center bullet
                self.create_projectile(self.weapons[0], 0)
                # Side bullets with reduced spread
                self.create_projectile(self.weapons[0], -10)
                self.create_projectile(self.weapons[0], 10)
                
        # Laser (X) - Continuous beam
        if keys[pygame.K_x]:
            self.laser_active = True
            if self.weapons[1].can_shoot(current_time):
                self.weapons[1].last_shot = current_time
                self.create_laser_beam(self.weapons[1])
        else:
            self.laser_active = False
            self.laser_beam = None
                
        # Cannon (C) - Heavy shot with splash damage
        if keys[pygame.K_c]:
            if self.weapons[2].can_shoot(current_time):
                self.weapons[2].last_shot = current_time
                self.create_cannon_shot(self.weapons[2])

    def create_projectile(self, weapon, offset=0):
        proj_x = self.x + self.width // 2 - weapon.img.get_width() // 2 + offset
        proj_y = self.y - weapon.img.get_height()
        self.projectiles.append({
            'x': proj_x,
            'y': proj_y,
            'img': weapon.img,
            'damage': weapon.damage,
            'speed': weapon.speed,
            'type': 'bullet',
            'offset_x': math.sin(offset * math.pi / 180)
        })

    def create_laser_beam(self, weapon):
        # Create a continuous laser beam from player to top of screen
        beam_width = 4
        beam_x = self.x + self.width // 2 - beam_width // 2
        
        # Create main laser beam
        laser_img = pygame.Surface((beam_width, self.y), pygame.SRCALPHA)
        
        # Create gradient effect for laser
        for i in range(beam_width):
            alpha = 255 if i in [1, 2] else 180
            color = (0, 255, 255, alpha)
            pygame.draw.line(laser_img, color, (i, 0), (i, self.y))
        
        # Create glow effect
        glow_width = 12
        glow_img = pygame.Surface((glow_width, self.y), pygame.SRCALPHA)
        for i in range(glow_width):
            alpha = 128 * (1 - abs(i - glow_width/2) / (glow_width/2))
            color = (0, 255, 255, int(alpha))
            pygame.draw.line(glow_img, color, (i, 0), (i, self.y))
        
        self.laser_beam = {
            'x': beam_x,
            'y': 0,
            'img': laser_img,
            'glow': glow_img,
            'damage': weapon.damage,
            'width': beam_width
        }

    def create_cannon_shot(self, weapon):
        size = 24
        # Create main projectile with gradient
        cannon_img = pygame.Surface((size, size), pygame.SRCALPHA)
        for r in range(size//2, 0, -2):
            alpha = min(255, int(255 * (r / (size/2))))
            color = (255, 255, 0, alpha)
            pygame.draw.circle(cannon_img, color, (size//2, size//2), r)
        
        # Create larger glow effect
        glow_size = 32
        glow_img = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        for r in range(glow_size//2, 0, -2):
            alpha = min(128, int(128 * (r / (glow_size/2))))
            color = (255, 255, 0, alpha)
            pygame.draw.circle(glow_img, color, (glow_size//2, glow_size//2), r)
        
        proj_x = self.x + self.width // 2 - size // 2
        proj_y = self.y - size
        
        self.projectiles.append({
            'x': proj_x,
            'y': proj_y,
            'img': cannon_img,
            'glow': glow_img,
            'damage': weapon.damage,
            'speed': weapon.speed,
            'type': 'cannon',
            'offset_x': 0
        })

    def update_projectiles(self):
        # Update regular projectiles
        for proj in self.projectiles[:]:
            if proj['type'] == 'bullet':
                proj['x'] += proj['offset_x']
                proj['y'] -= proj['speed']
            elif proj['type'] == 'cannon':
                proj['y'] -= proj['speed']
            
            if proj['y'] < -50:
                self.projectiles.remove(proj)
        
        # Update laser beam position if active
        if self.laser_active and self.laser_beam:
            self.laser_beam['x'] = self.x + self.width // 2 - self.laser_beam['width'] // 2

    def draw_projectiles(self, screen):
        # Draw regular projectiles
        for proj in self.projectiles:
            if proj['type'] in ['bullet', 'cannon']:
                if 'glow' in proj:
                    glow_x = proj['x'] - (proj['glow'].get_width() - proj['img'].get_width()) // 2
                    glow_y = proj['y'] - (proj['glow'].get_height() - proj['img'].get_height()) // 2
                    screen.blit(proj['glow'], (glow_x, glow_y))
                screen.blit(proj['img'], (proj['x'], proj['y']))
        
        # Draw laser beam if active
        if self.laser_active and self.laser_beam:
            # Draw glow effect
            glow_x = self.laser_beam['x'] - (self.laser_beam['glow'].get_width() - self.laser_beam['width']) // 2
            screen.blit(self.laser_beam['glow'], (glow_x, 0))
            # Draw main beam
            screen.blit(self.laser_beam['img'], (self.laser_beam['x'], 0))

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        if enemy_type == 1:
            self.img = enemy1_img
            self.speed = 2
            self.health = 20
            self.points = 10
            self.shoot_chance = 0.002
        elif enemy_type == 2:
            self.img = enemy2_img
            self.speed = 3
            self.health = 30
            self.points = 20
            self.shoot_chance = 0.005
        else:  # Type 3
            self.img = enemy3_img
            self.speed = 1.5
            self.health = 50
            self.points = 30
            self.shoot_chance = 0.008
            
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.direction = random.choice([1, -1])
        
    def move(self):
        self.x += self.speed * self.direction
        
        # Change direction if hitting screen edges
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.direction *= -1
            self.y += 20
            
        self.y += 0.2
        
    def should_shoot(self):
        return random.random() < self.shoot_chance
        
    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

# Obstacle class
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = obstacle_img
        self.speed = 2
        self.health = 40
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rotation = 0
        self.rotation_speed = random.uniform(0.5, 2.0) * random.choice([1, -1])
        
    def move(self):
        self.y += self.speed
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Rotate the obstacle
        rotated_img = pygame.transform.rotate(self.img, self.rotation)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        screen.blit(rotated_img, new_rect.topleft)
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

# Star class for background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        self.twinkle_rate = random.uniform(0.01, 0.1)
        self.brightness = random.uniform(0.5, 1.0)
        self.increasing = random.choice([True, False])
        
    def twinkle(self):
        if self.increasing:
            self.brightness += self.twinkle_rate
            if self.brightness >= 1.0:
                self.brightness = 1.0
                self.increasing = False
        else:
            self.brightness -= self.twinkle_rate
            if self.brightness <= 0.3:
                self.brightness = 0.3
                self.increasing = True
                
        # Apply brightness to color
        bright_color = tuple(int(c * self.brightness) for c in self.color)
        return bright_color
        
    def draw(self, screen):
        color = self.twinkle()
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

# Particle effect for explosions
class Explosion:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.particles = []
        self.lifetime = 30
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity = [speed * math.cos(angle), speed * math.sin(angle)]
            size = random.randint(2, 5)
            lifetime = random.randint(20, 30)
            self.particles.append({
                'position': [x, y],
                'velocity': velocity,
                'size': size,
                'color': color,
                'lifetime': lifetime
            })
    
    def update(self):
        self.lifetime -= 1
        for particle in self.particles:
            particle['position'][0] += particle['velocity'][0]
            particle['position'][1] += particle['velocity'][1]
            particle['lifetime'] -= 1
            
    def draw(self, screen):
        for particle in self.particles:
            if particle['lifetime'] > 0:
                alpha = min(255, int(255 * (particle['lifetime'] / 30)))
                color = (*particle['color'][:3], alpha)
                position = (int(particle['position'][0]), int(particle['position'][1]))
                pygame.draw.circle(screen, color, position, particle['size'])
                
    def is_alive(self):
        return self.lifetime > 0

# Create game objects
player = Player(WIDTH // 2 - 32, HEIGHT - 100)
enemies = []
obstacles = []
enemy_projectiles = []
stars = [Star() for _ in range(150)]
explosions = []

# Game functions
def spawn_enemy():
    if len(enemies) < 10 and random.random() < 0.02:
        enemy_type = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, 200)
        enemies.append(Enemy(x, y, enemy_type))
        
def spawn_obstacle():
    if len(obstacles) < 5 and random.random() < 0.01:
        x = random.randint(50, WIDTH - 50)
        y = -50
        obstacles.append(Obstacle(x, y))
        
def enemy_shooting():
    for enemy in enemies:
        if enemy.should_shoot():
            proj_x = enemy.x + enemy.width // 2 - enemy_bullet_img.get_width() // 2
            proj_y = enemy.y + enemy.height
            enemy_projectiles.append({
                'x': proj_x,
                'y': proj_y,
                'img': enemy_bullet_img,
                'speed': 5
            })
            
def update_enemy_projectiles():
    for proj in enemy_projectiles[:]:
        proj['y'] += proj['speed']
        if proj['y'] > HEIGHT:
            enemy_projectiles.remove(proj)
            
def draw_enemy_projectiles(screen):
    for proj in enemy_projectiles:
        screen.blit(proj['img'], (proj['x'], proj['y']))
        
def check_collisions():
    global score, game_over
    
    # Check laser beam collisions first if active
    if player.laser_active and player.laser_beam:
        laser_rect = pygame.Rect(
            player.laser_beam['x'],
            0,
            player.laser_beam['width'],
            player.y
        )
        
        # Check laser collision with enemies
        for enemy in enemies[:]:
            if laser_rect.colliderect(enemy.get_hitbox()):
                if enemy.take_damage(player.weapons[1].damage // 2):  # Reduced damage for balance
                    enemies.remove(enemy)
                    score += enemy.points
                    # Special laser explosion effect
                    explosions.append(Explosion(
                        enemy.x + enemy.width//2,
                        enemy.y + enemy.height//2,
                        enemy.width,
                        (0, 255, 255, 255)  # Cyan color for laser
                    ))
        
        # Check laser collision with obstacles
        for obstacle in obstacles[:]:
            if laser_rect.colliderect(obstacle.get_hitbox()):
                if obstacle.take_damage(player.weapons[1].damage // 3):  # Further reduced damage for obstacles
                    obstacles.remove(obstacle)
                    explosions.append(Explosion(
                        obstacle.x + obstacle.width//2,
                        obstacle.y + obstacle.height//2,
                        obstacle.width,
                        (0, 255, 255, 255)
                    ))
    
    # Regular projectiles hitting enemies
    for proj in player.projectiles[:]:
        proj_rect = pygame.Rect(proj['x'], proj['y'], 
                              proj['img'].get_width(), proj['img'].get_height())
        
        for enemy in enemies[:]:
            if proj_rect.colliderect(enemy.get_hitbox()):
                # Different effects based on projectile type
                if proj['type'] == 'bullet':
                    damage = proj['damage']
                    explosion_size = enemy.width
                    if enemy.take_damage(damage):
                        enemies.remove(enemy)
                        score += enemy.points
                        color = get_enemy_color(enemy.type)
                        explosions.append(Explosion(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2,
                            explosion_size,
                            color
                        ))
                
                elif proj['type'] == 'cannon':
                    # Cannon has splash damage
                    damage = proj['damage']
                    explosion_size = enemy.width * 1.5
                    # Check for nearby enemies for splash damage
                    enemy_pos = pygame.math.Vector2(enemy.x + enemy.width//2, enemy.y + enemy.height//2)
                    for nearby_enemy in enemies[:]:
                        if nearby_enemy != enemy:
                            nearby_pos = pygame.math.Vector2(
                                nearby_enemy.x + nearby_enemy.width//2,
                                nearby_enemy.y + nearby_enemy.height//2
                            )
                            distance = enemy_pos.distance_to(nearby_pos)
                            if distance < 100:  # Splash damage radius
                                splash_damage = int(damage * (1 - distance/100))
                                if nearby_enemy.take_damage(splash_damage):
                                    enemies.remove(nearby_enemy)
                                    score += nearby_enemy.points
                                    explosions.append(Explosion(
                                        nearby_enemy.x + nearby_enemy.width//2,
                                        nearby_enemy.y + nearby_enemy.height//2,
                                        nearby_enemy.width,
                                        (255, 200, 0, 255)
                                    ))
                    
                    if enemy.take_damage(damage):
                        enemies.remove(enemy)
                        score += enemy.points
                        # Large explosion for cannon hit
                        explosions.append(Explosion(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2,
                            explosion_size,
                            (255, 255, 0, 255)
                        ))
                
                if proj in player.projectiles:
                    player.projectiles.remove(proj)
                break
        
        # Check for obstacles
        if proj in player.projectiles:
            for obstacle in obstacles[:]:
                if proj_rect.colliderect(obstacle.get_hitbox()):
                    damage = proj['damage']
                    if proj['type'] == 'cannon':
                        damage *= 1.5  # Cannon does extra damage to obstacles
                    
                    if obstacle.take_damage(damage):
                        obstacles.remove(obstacle)
                        explosion_size = obstacle.width * (1.5 if proj['type'] == 'cannon' else 1)
                        explosions.append(Explosion(
                            obstacle.x + obstacle.width//2,
                            obstacle.y + obstacle.height//2,
                            explosion_size,
                            (100, 100, 100, 255)
                        ))
                    player.projectiles.remove(proj)
                    break
    
    # Enemy projectiles hitting player
    player_rect = player.get_hitbox()
    for proj in enemy_projectiles[:]:
        proj_rect = pygame.Rect(proj['x'], proj['y'], 
                              proj['img'].get_width(), proj['img'].get_height())
        if proj_rect.colliderect(player_rect):
            player.health -= 10
            enemy_projectiles.remove(proj)
            # Shield flash effect could be added here
            explosions.append(Explosion(
                proj['x'],
                proj['y'],
                20,
                (255, 255, 255, 255)
            ))
            
            if player.health <= 0:
                game_over = True
                # Multiple explosions for dramatic effect
                create_player_death_explosion(player)
    
    # Direct collisions
    check_direct_collisions(player_rect)

def get_enemy_color(enemy_type):
    if enemy_type == 1:
        return (255, 0, 0, 255)  # Red
    elif enemy_type == 2:
        return (255, 140, 0, 255)  # Orange
    else:
        return (148, 0, 211, 255)  # Purple

def create_player_death_explosion(player):
    # Create multiple explosions for dramatic effect
    center_x = player.x + player.width//2
    center_y = player.y + player.height//2
    
    # Main explosion
    explosions.append(Explosion(
        center_x,
        center_y,
        player.width * 1.5,
        (30, 144, 255, 255)
    ))
    
    # Secondary explosions
    for _ in range(4):
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        size = random.randint(20, 40)
        explosions.append(Explosion(
            center_x + offset_x,
            center_y + offset_y,
            size,
            (255, 200, 0, 255)
        ))

def check_direct_collisions(player_rect):
    # Handle direct collisions with enemies and obstacles
    for enemy in enemies[:]:
        if player_rect.colliderect(enemy.get_hitbox()):
            handle_collision_with_enemy(enemy)
            
    for obstacle in obstacles[:]:
        if player_rect.colliderect(obstacle.get_hitbox()):
            handle_collision_with_obstacle(obstacle)

def handle_collision_with_enemy(enemy):
    global game_over
    player.health -= 20
    enemies.remove(enemy)
    explosions.append(Explosion(
        enemy.x + enemy.width//2,
        enemy.y + enemy.height//2,
        enemy.width,
        (255, 0, 0, 255)
    ))
    
    if player.health <= 0:
        game_over = True
        create_player_death_explosion(player)

def handle_collision_with_obstacle(obstacle):
    global game_over
    player.health -= 30
    obstacles.remove(obstacle)
    explosions.append(Explosion(
        obstacle.x + obstacle.width//2,
        obstacle.y + obstacle.height//2,
        obstacle.width,
        (100, 100, 100, 255)
    ))
    
    if player.health <= 0:
        game_over = True
        create_player_death_explosion(player)
                
def draw_stars(screen):
    for star in stars:
        star.draw(screen)
        
def update_explosions():
    for explosion in explosions[:]:
        explosion.update()
        if not explosion.is_alive():
            explosions.remove(explosion)
            
def draw_explosions(screen):
    for explosion in explosions:
        explosion.draw(screen)
        
def draw_ui(screen):
    small_font = pygame.font.SysFont("arial", 16)
    
    # Score 
    score_text = small_font.render(f"Score:{score}", True, (255, 255, 255))
    screen.blit(score_text, (5, 5))
    
    # Health bar
    bar_width = 100  
    bar_height = 10 
    
    # Health bar border
    pygame.draw.rect(screen, (100, 100, 100), (5, 25, bar_width + 2, bar_height + 2))
    # Health bar background (red)
    pygame.draw.rect(screen, (255, 0, 0), (6, 26, bar_width, bar_height))
    # Health bar fill (green)
    health_width = int((player.health / 100) * bar_width)
    pygame.draw.rect(screen, (0, 255, 0), (6, 26, health_width, bar_height))
    
    # Small health number
    health_text = small_font.render(f"HP:{player.health}", True, (255, 255, 255))
    screen.blit(health_text, (110, 25))
    
    # Game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        go_font = pygame.font.SysFont("arial", 72)
        go_text = go_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - go_text.get_height()//2))
        
        score_font = pygame.font.SysFont("arial", 48)
        final_score = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 30))
        
        restart_font = pygame.font.SysFont("arial", 32)
        restart_text = restart_font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
        
# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Reset all game variables
            player = Player(WIDTH // 2 - 32, HEIGHT - 100)
            enemies = []
            obstacles = []
            enemy_projectiles = []
            explosions = []
            score = 0
            game_over = False
    
    # Get pressed keys for continuous movement and shooting
    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.shoot(keys)
        
        # Update game objects
        player.update_projectiles()
        for enemy in enemies:
            enemy.move()
        for obstacle in obstacles:
            obstacle.move()
        update_enemy_projectiles()
        update_explosions()
        
        # Remove objects that are out of screen
        enemies = [enemy for enemy in enemies if enemy.y < HEIGHT]
        obstacles = [obstacle for obstacle in obstacles if obstacle.y < HEIGHT]
        
        # Spawn new objects
        spawn_enemy()
        spawn_obstacle()
        enemy_shooting()
        
        # Check for collisions
        check_collisions()
    else:
        # Still update explosions in game over state
        update_explosions()
    
    # Draw everything
    screen.fill((0, 0, 20))  
    draw_stars(screen)
    
    if not game_over:
        player.draw(screen)
        player.draw_projectiles(screen)
    
    for enemy in enemies:
        enemy.draw(screen)
    
    for obstacle in obstacles:
        obstacle.draw(screen)
    
    draw_enemy_projectiles(screen)
    draw_explosions(screen)
    draw_ui(screen)
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()