import pygame
import math
import random
import sys
from PIL import Image, ImageDraw
from pygame.math import Vector2

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Tank Defense")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)  # For laser

# Game variables
clock = pygame.time.Clock()
FPS = 60
game_over = False
score = 0
wave = 1
zombies_killed = 0
zombies_to_next_wave = 10

# Player vehicle settings
player_pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
player_speed = 5
player_angle = 0
player_health = 100

# Create the heavy vehicle image
def create_heavy_vehicle(width=200, height=150, bg_color=(255, 255, 255, 0)):
    # Create a new image with transparent background
    img = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Center of the image
    center_x, center_y = width // 2, height // 2
    
    # Dimensions for heavy vehicle
    body_width = width // 2
    body_height = height // 2
    wheel_radius = min(width, height) // 10  # Bigger wheels for heavy vehicle
    
    # Colors
    body_color = (60, 90, 60)  # Darker green for heavy
    wheel_color = (60, 30, 70)  # Dark purple
    tread_color = (120, 100, 130)  # Light purple
    weapon_color = (99, 12, 12)  # red 
    
    # Draw wheels
    wheel_offset_x = body_width // 3.5
    wheel_offset_y = body_height // 2.1  # Adjusted wheel position
    
    wheel_positions = [
        (center_x - wheel_offset_x, center_y - wheel_offset_y),  # Front left
        (center_x + wheel_offset_x, center_y - wheel_offset_y),  # Front right
        (center_x - wheel_offset_x, center_y + wheel_offset_y),  # Rear left
        (center_x + wheel_offset_x, center_y + wheel_offset_y),  # Rear right
    ]
    
    # Draw treads on each wheel
    for wx, wy in wheel_positions:
        # Draw the wheel
        draw.rectangle((wx - wheel_radius, wy - wheel_radius, 
                      wx + wheel_radius, wy + wheel_radius), 
                     fill=wheel_color)
        
        # Draw treads
        num_treads = 3 # More treads for heavy vehicle
        for j in range(num_treads):
            angle = 2 * math.pi * j / num_treads
            tread_x = wx + int(.5 * wheel_radius * math.cos(angle))
            tread_y = wy + int(.5 * wheel_radius * math.sin(angle))
            tread_size = wheel_radius // 2
            
            draw.ellipse((tread_x - tread_size, tread_y - tread_size,
                          tread_x + tread_size, tread_y + tread_size),
                         fill=tread_color)
    
    # Draw suspension bars
    for wx, wy in wheel_positions:
        side_offset = 5 if wx < center_x else -5
        thickness = 5  # Adjusted thickness for better aesthetics
        
        draw.line((wx + side_offset, wy, 
                  center_x + side_offset * 3, wy), 
                  fill=(0, 0, 10), width=thickness)
    
    # Draw main body outline 
    body_points = [
        (center_x - body_width // 2, center_y),  # Left middle
        (center_x - body_width // 3, center_y - body_height // 2),  # Left front
        (center_x + body_width // 3, center_y - body_height // 2),  # Right front
        (center_x + body_width // 2, center_y),  # Right middle
        (center_x + body_width // 3, center_y + body_height // 2),  # Right back
        (center_x - body_width // 3, center_y + body_height // 2),  # Left back
    ]
    draw.polygon(body_points, fill=body_color, outline=(50, 70, 40), width=3)
    
    # Body details
    draw.line((center_x, center_y - body_height // 2, 
              center_x, center_y + body_height // 2), 
              fill=(50, 70, 40), width=5)
    
    # Cockpit
    cockpit_width = body_width // 3
    cockpit_height = body_height // 3
    draw.polygon([
        (center_x - cockpit_width // 2, center_y - cockpit_height // 2),
        (center_x + cockpit_width // 2, center_y - cockpit_height // 2),
        (center_x + cockpit_width // 3, center_y + cockpit_height // 2),
        (center_x - cockpit_width // 3, center_y + cockpit_height // 2),
    ], fill=(40, 50, 40))
    
    # Highlight panels
    highlight_color = (body_color[0] + 30, body_color[1] + 30, body_color[2] + 30)
    
    left_panel = [
        (center_x - body_width // 2.2, center_y - body_height // 3),
        (center_x - body_width // 3.5, center_y - body_height // 2.2),
        (center_x - body_width // 4, center_y),
        (center_x - body_width // 3.5, center_y + body_height // 2.2),
        (center_x - body_width // 2.2, center_y + body_height // 3),
    ]
    draw.polygon(left_panel, fill=highlight_color)
    
    right_panel = [
        (center_x + body_width // 2.2, center_y - body_height // 3),
        (center_x + body_width // 3.5, center_y - body_height // 2.2),
        (center_x + body_width // 4, center_y),
        (center_x + body_width // 3.5, center_y + body_height // 2.2),
        (center_x + body_width // 2.2, center_y + body_height // 3),
    ]
    draw.polygon(right_panel, fill=highlight_color)
    
    # Draw weapon based on heavy class with upward missiles
    turret_radius = body_width // 7  # Bigger turret for heavy class
    turret_x, turret_y = center_x, center_y - body_height // 4
    
    # Draw turret base
    draw.ellipse((turret_x - turret_radius, turret_y - turret_radius,
                 turret_x + turret_radius, turret_y + turret_radius),
                 fill=weapon_color, outline=(40, 40, 40), width=2)
    
    # Draw weapon turrets 
    horizontal_spacing = turret_radius // 2
    for j in range(3):
        offset_x = (j - 1) * horizontal_spacing
        
        # Draw gun turret
        gun_height = body_height // 1
        gun_width = turret_radius // 2
        
        # Vertical turrets pointing upward
        draw.rectangle((turret_x + offset_x - gun_width // 2, 
                       turret_y - gun_height,
                       turret_x + offset_x + gun_width // 2, 
                       turret_y),
                       fill=weapon_color, outline=(40, 40, 40), width=1)

    # Rear armor plate
    draw.rectangle((center_x - body_width // 4, center_y + body_height // 2,
                   center_x + body_width // 4, center_y + body_height // 2 + body_height // 8),
                   fill=(60, 80, 60), outline=(40, 60, 40), width=2)
                   
    # Exhaust pipes
    pipe_radius = body_height // 20
    draw.rectangle((center_x - body_width // 3, center_y + body_height // 2,
                   center_x - body_width // 3 + pipe_radius, 
                   center_y + body_height // 2 + body_height // 6),
                   fill=(30, 30, 30), outline=(20, 20, 20), width=1)
    draw.rectangle((center_x + body_width // 3 - pipe_radius, center_y + body_height // 2,
                   center_x + body_width // 3, 
                   center_y + body_height // 2 + body_height // 6),
                   fill=(30, 30, 30), outline=(20, 20, 20), width=1)
    return img

def create_tree(width=80, height=150):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw trunk
    trunk_width = width // 4
    pygame.draw.rect(surface, BROWN, (width // 2 - trunk_width // 2, height // 2, trunk_width, height // 2))
    pygame.draw.circle(surface, DARK_GREEN, (width // 2, height // 3), width // 3)
    pygame.draw.circle(surface, DARK_GREEN, (width // 2 - width // 6, height // 4), width // 4)
    pygame.draw.circle(surface, DARK_GREEN, (width // 2 + width // 6, height // 4), width // 4)
    return surface

def create_rock(width=60, height=40):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, GRAY, (0, 0, width, height))
    pygame.draw.ellipse(surface, (GRAY[0] + 20, GRAY[1] + 20, GRAY[2] + 20), 
                      (width // 4, height // 4, width // 3, height // 3))
    
    return surface

# Generate zombie
def create_zombie(width=50, height=70):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Body
    body_color = (100, 150, 100)  # Greenish for zombie
    pygame.draw.ellipse(surface, body_color, (width // 4, height // 3, width // 2, height // 2))
    
    # Head
    head_color = (110, 140, 90)
    pygame.draw.circle(surface, head_color, (width // 2, height // 4), width // 6)
    
    # Arms
    pygame.draw.line(surface, body_color, (width // 3, height // 2), 
                    (width // 6, height * 2 // 3), width // 8)
    pygame.draw.line(surface, body_color, (width * 2 // 3, height // 2), 
                    (width * 5 // 6, height * 2 // 3), width // 8)
    
    # Legs
    pygame.draw.line(surface, body_color, (width * 2 // 5, height * 3 // 4), 
                    (width // 3, height), width // 8)
    pygame.draw.line(surface, body_color, (width * 3 // 5, height * 3 // 4), 
                    (width * 2 // 3, height), width // 8)
    
    # Eyes
    pygame.draw.circle(surface, RED, (width // 2 - width // 10, height // 4 - height // 20), width // 20)
    pygame.draw.circle(surface, RED, (width // 2 + width // 10, height // 4 - height // 20), width // 20)
    
    return surface

# Create game objects
tree = create_tree()
rock = create_rock()
zombie_img = create_zombie()
vehicle_image = pygame.Surface((200, 150), pygame.SRCALPHA)
pil_image = create_heavy_vehicle()
pygame_image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode).convert_alpha()
vehicle_image = pygame_image

# Define different ammo types
ammo_types = {
    "gun": {"color": RED, "damage": 25, "speed": 10, "radius": 5, "key": pygame.K_z},
    "cannon": {"color": BLUE, "damage": 40, "speed": 7, "radius": 8, "key": pygame.K_x},
    "laser": {"color": YELLOW, "damage": 15, "speed": 15, "radius": 3, "key": pygame.K_c}
}

# Game objects
class Player:
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.image = vehicle_image
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.health = 100
        self.cooldowns = {"gun": 0, "cannon": 0, "laser": 0}
        self.cooldown_times = {"gun": 10, "cannon": 30, "laser": 5}
        
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT]:
            self.pos.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.pos.x += self.speed

        self.pos.x = max(self.image.get_width() // 2, min(SCREEN_WIDTH - self.image.get_width() // 2, self.pos.x))
        
        # Update rectangle position
        self.rect.center = self.pos
        
        # Cooldown for shooting
        for ammo_type in self.cooldowns:
            if self.cooldowns[ammo_type] > 0:
                self.cooldowns[ammo_type] -= 1
            
    def shoot(self, ammo_type): 
        if self.cooldowns[ammo_type] <= 0:
            self.cooldowns[ammo_type] = self.cooldown_times[ammo_type]
            if ammo_type == "gun":
                pos = Vector2(self.pos.x, self.pos.y - 30)
                ammo = Ammo(pos, ammo_type)
            elif ammo_type == "cannon":
                pos = Vector2(self.pos.x - 20, self.pos.y - 30)
                ammo = Ammo(pos, ammo_type)
            elif ammo_type == "laser":
                pos = Vector2(self.pos.x + 20, self.pos.y - 30)
                ammo = Ammo(pos, ammo_type)
                
            return ammo
        return None
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Draw health bar
        bar_width = 50
        bar_height = 5
        pygame.draw.rect(surface, RED, (self.pos.x - bar_width // 2, self.pos.y + 40, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, 
                       (self.pos.x - bar_width // 2, self.pos.y + 40, 
                        int(bar_width * (self.health / 100)), bar_height))

class Ammo:
    def __init__(self, pos, ammo_type):
        self.pos = Vector2(pos)
        self.type = ammo_type
        self.speed = ammo_types[ammo_type]["speed"]
        self.damage = ammo_types[ammo_type]["damage"]
        self.radius = ammo_types[ammo_type]["radius"]
        self.color = ammo_types[ammo_type]["color"]
        
    def update(self):
        self.pos.y -= self.speed
        
    def draw(self, surface):
        if self.type == "laser":
            # Draw laser as a line
            pygame.draw.line(surface, self.color, 
                          (int(self.pos.x), int(self.pos.y)), 
                          (int(self.pos.x), int(self.pos.y - 20)), 3)
        elif self.type == "cannon":
            # Draw cannon as a larger circle
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
            pygame.draw.circle(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), 
                            (int(self.pos.x), int(self.pos.y)), self.radius - 2)
        else:
            # Gun - standard bullet
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
    def is_off_screen(self):
        return self.pos.y < 0

class Zombie:
    def __init__(self, pos=None):
        if pos is None:
            # Modified zombie spawning to keep them inward from edges
            border_margin = 100
            spawn_side = random.choice(["left", "top", "right"])
            if spawn_side == "left":
                self.pos = Vector2(border_margin, random.randint(-50, SCREEN_HEIGHT // 4))
            elif spawn_side == "right":
                self.pos = Vector2(SCREEN_WIDTH - border_margin, random.randint(-50, SCREEN_HEIGHT // 4))
            else:  # top
                self.pos = Vector2(random.randint(border_margin, SCREEN_WIDTH - border_margin), -50)
        else:
            self.pos = Vector2(pos)
        
        self.image = zombie_img
        self.rect = self.image.get_rect(center=self.pos)
        self.speed = random.uniform(1, 3)
        self.health = 50
        
    def update(self):
        target_x = SCREEN_WIDTH // 2
        target_y = SCREEN_HEIGHT - 100
        
        # Get direction vector towards player
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        
        # Normalize direction
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
        
        # Move zombie towards player
        self.pos.x += dx * self.speed
        self.pos.y += dy * self.speed
        
        # Update rectangle position
        self.rect.center = self.pos
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Draw health bar
        bar_width = 30
        bar_height = 3
        pygame.draw.rect(surface, RED, (self.pos.x - bar_width // 2, self.pos.y - 30, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, 
                       (self.pos.x - bar_width // 2, self.pos.y - 30, 
                        int(bar_width * (self.health / 50)), bar_height))
        
    def is_off_screen(self):
        return self.pos.y > SCREEN_HEIGHT
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class Environment:
    def __init__(self):
        self.trees = []
        self.rocks = []
        self.tree_img = create_tree()
        self.rock_img = create_rock()
        
        # Generate initial environment objects
        for _ in range(10):
            self.trees.append(Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT // 2)))
            self.rocks.append(Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
    
    def draw(self, surface):
        for pos in self.trees:
            surface.blit(self.tree_img, (pos.x - self.tree_img.get_width() // 2, 
                                        pos.y - self.tree_img.get_height() // 2))
        
        for pos in self.rocks:
            surface.blit(self.rock_img, (pos.x - self.rock_img.get_width() // 2, 
                                        pos.y - self.rock_img.get_height() // 2))

# Game UI elements
def draw_hud(surface, player, score, wave, zombies_killed, zombies_to_next_wave):
    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(score_text, (20, 20))
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    surface.blit(wave_text, (20, 60))
    zombie_text = font.render(f"Zombies: {zombies_killed}/{zombies_to_next_wave}", True, WHITE)
    surface.blit(zombie_text, (20, 100))
    
    # Draw weapon cooldowns
    cooldown_x = SCREEN_WIDTH - 300
    for i, (weapon, data) in enumerate(ammo_types.items()):
        key_name = pygame.key.name(data["key"]).upper()
        cooldown = player.cooldowns[weapon]
        ready = "READY" if cooldown <= 0 else f"WAIT: {cooldown//5 + 1}"
        weapon_text = font.render(f"{weapon.upper()} ({key_name}): {ready}", True, WHITE)
        surface.blit(weapon_text, (cooldown_x, 20 + i * 35))

def draw_game_over(surface):
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, RED)
    restart_text = font_small.render("Press R to Restart", True, WHITE)
    quit_text = font_small.render("Press Q to Quit", True, WHITE)
    
    surface.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    surface.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    surface.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

def main():
    global game_over, score, wave, zombies_killed, zombies_to_next_wave
    player = Player(player_pos)
    environment = Environment()
    zombies = []
    projectiles = []
    spawn_timer = 0
    spawn_delay = 60  # frames between spawns
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        game_over = False
                        score = 0
                        wave = 1
                        zombies_killed = 0
                        zombies_to_next_wave = 10
                        player.health = 100
                        zombies.clear()
                        projectiles.clear()
                    elif event.key == pygame.K_q:
                        running = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            for ammo_type in ammo_types:
                if keys[ammo_types[ammo_type]["key"]]:
                    new_projectile = player.shoot(ammo_type)
                    if new_projectile:
                        projectiles.append(new_projectile)
            
            # Spawn zombies
            spawn_timer += 1
            if spawn_timer >= spawn_delay:
                zombies.append(Zombie())
                spawn_timer = 0
            
            # Update zombies
            for zombie in zombies[:]:
                zombie.update()
                
                # Check collision with player
                if abs(zombie.pos.x - player.pos.x) < 40 and abs(zombie.pos.y - player.pos.y) < 40:
                    player.health -= 1
                    if player.health <= 0:
                        game_over = True
                
                # Remove off-screen zombies
                if zombie.is_off_screen():
                    zombies.remove(zombie)
                    player.health -= 10  # Penalty for letting zombies pass
                    if player.health <= 0:
                        game_over = True
                        
            projectiles_to_remove = []
            zombies_to_remove = []
            
            for i, projectile in enumerate(projectiles):
                projectile.update()
                
                # Check if off-screen
                if projectile.is_off_screen():
                    projectiles_to_remove.append(i)
                    continue
                
                # Check collision with zombies
                for j, zombie in enumerate(zombies):
                    if abs(projectile.pos.x - zombie.pos.x) < 20 and abs(projectile.pos.y - zombie.pos.y) < 20:
                        # Add projectile to removal list
                        if i not in projectiles_to_remove:
                            projectiles_to_remove.append(i)
                        
                        # Apply damage
                        if zombie.take_damage(projectile.damage):
                            # Add zombie to removal list if destroyed
                            zombies_to_remove.append(j)
                            score += 100
                            zombies_killed += 1
                            
                            # Check for wave completion
                            if zombies_killed >= zombies_to_next_wave:
                                wave += 1
                                zombies_killed = 0
                                zombies_to_next_wave = wave * 10
                                spawn_delay = max(20, 60 - wave * 5)  # Increase spawn rate with each wave
                        
                        break
            
            # Remove zombies in reverse order to avoid index issues
            for idx in sorted(zombies_to_remove, reverse=True):
                if 0 <= idx < len(zombies):
                    zombies.pop(idx)
            
            # Remove projectiles in reverse order to avoid index issues
            for idx in sorted(projectiles_to_remove, reverse=True):
                if 0 <= idx < len(projectiles):
                    projectiles.pop(idx)
        
        screen.fill(BLACK)
        environment.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)
        
        for projectile in projectiles:
            projectile.draw(screen)
            
        player.draw(screen)
        draw_hud(screen, player, score, wave, zombies_killed, zombies_to_next_wave)
        if game_over:
            draw_game_over(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()