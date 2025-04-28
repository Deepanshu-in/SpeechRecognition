import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Soldier Combat Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKIN_COLOR = (255, 213, 170)
JACKET_COLOR = (110, 110, 80)  # Olive/khaki color
PANTS_COLOR = (100, 100, 70)  # Slightly darker olive
HAT_COLOR = (70, 60, 50)  # Dark brown
RIFLE_COLOR = (120, 90, 60)  # Brown for rifle
RIFLE_BARREL_COLOR = (80, 80, 80)  # Dark gray for barrel
KNIFE_COLOR = (200, 200, 200)  # Silver for knife
HAIR_COLORS = [
    (50, 30, 25),  # Dark brown
    (120, 80, 40),  # Medium brown
    (240, 200, 120),  # Blonde
    (30, 30, 30),  # Black
    (180, 70, 40)   # Reddish
]

# Enemy uniform color variations
ENEMY_UNIFORM_COLORS = [
    # Jacket color, Pants color
    [(170, 50, 50), (150, 40, 40)],  # Red uniform
    [(50, 80, 170), (40, 70, 150)],  # Blue uniform
    [(80, 120, 40), (70, 110, 30)],  # Green uniform
    [(120, 70, 120), (100, 60, 100)]  # Purple uniform
]

# Colorful bullet colors
BULLET_COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 128, 0),  # Orange
    (128, 0, 255),  # Purple
    (255, 215, 0)  # Gold
]

# Game variables
aim_angle = 0  # In degrees, 0 is horizontal
bullets = []  # List to store active bullets
last_shot_time = 0
shoot_delay = 80  # Milliseconds between shots
player_state = "stand"  # Can be "stand", "crouch", or "jump"
player_jump_height = 0
player_jump_speed = 0
gravity = 0.8
jump_strength = -15

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

class EnemySoldier:
    def __init__(self):
        self.size = random.randint(70, 90)  # Overall size scale
        self.x = width + 50
        self.y = height - 150  # Place on ground
        self.base_y = height - 150  # Base ground level position
        self.speed = random.uniform(1.5, 3)
        self.health = 100
        self.active = True
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.attack_cooldown = 0
        self.attack_range = 100  # Distance at which soldier will attack
        self.attack_damage = 20  # Damage dealt to player
        self.attacking = False
        self.state = random.choice(["stand", "jump"])
        self.jump_height = 0
        self.jump_speed = 0
        self.state_change_timer = random.randint(60, 180)
        self.uniform_colors = random.choice(ENEMY_UNIFORM_COLORS)
        self.jacket_color = self.uniform_colors[0]
        self.pants_color = self.uniform_colors[1]
        self.hair_color = random.choice(HAIR_COLORS)

    def update(self, player_x, player_y):
        # Update state change timer
        self.state_change_timer -= 1
        if self.state_change_timer <= 0:
            self.state = random.choice(["stand", "jump"])
            if self.state == "jump" and self.jump_height == 0:
                self.jump_speed = jump_strength * 0.7  
            self.state_change_timer = random.randint(60, 180) 
        
        # Handle jumping physics if jumping
        if self.state == "jump":
            self.jump_height -= self.jump_speed
            self.jump_speed += gravity * 0.8  # Slightly less gravity effect
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jump_speed = 0
                self.state = "stand"
                self.state_change_timer = random.randint(30, 90)  # Shorter timer after landing
        
        # Move forward
        move_speed = self.speed
        self.x -= move_speed
        self.animation_frame += self.animation_speed * (move_speed / self.speed)  # Animation speed based on movement
        self.y = self.base_y - self.jump_height
        
        # Check if in attack range of player
        distance_to_player = abs(self.x - player_x)
        if distance_to_player < self.attack_range:
            self.attacking = True
            if self.attack_cooldown <= 0:
                # Attack the player
                self.attack_cooldown = 60  # Attack every 60 frames (about 1 second)
                return True  # Signal that player is being attacked
            self.attack_cooldown -= 1
        else:
            self.attacking = False
        
        if self.x + self.size < 0:
            self.active = False
            
        return False 

    def draw(self, surface):
        # Draw enemy soldier with knife
        self.draw_soldier(surface)
        
        # Draw health bar
        health_width = self.size * (self.health / 100)
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 20, self.size, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 20, health_width, 5))
        
        # Draw state indicator (optional)
        font = pygame.font.SysFont(None, 16)
        state_text = font.render(self.state, True, WHITE)
        surface.blit(state_text, (self.x + self.size//2 - state_text.get_width()//2, self.y - 30))

    def draw_soldier(self, surface):
        scale = self.size / 80  
        leg_offset = math.sin(self.animation_frame) * 10 * scale
        
        # Draw legs
        leg_spread = 20 * scale
        leg_height = 80 * scale
        pygame.draw.rect(surface, self.pants_color, 
                        (self.x - 25*scale + leg_offset, self.y - 40*scale, 20*scale, leg_height))  # Left leg
        pygame.draw.rect(surface, self.pants_color, 
                        (self.x + 5*scale - leg_offset, self.y - 40*scale, 20*scale, leg_height))  # Right leg
        pygame.draw.rect(surface, BLACK, 
                        (self.x - 30*scale + leg_offset, self.y - 40*scale + leg_height, 25*scale, 10*scale))  # Left foot
        pygame.draw.rect(surface, BLACK, 
                        (self.x + 5*scale - leg_offset, self.y - 40*scale + leg_height, 25*scale, 10*scale))  # Right foot
        jacket_width = 50 * scale
        jacket_height = 80 * scale
        pygame.draw.rect(surface, self.jacket_color, 
                        (self.x - jacket_width//2, self.y - 120*scale, jacket_width, jacket_height))
        head_radius = 15 * scale
        head_x = self.x
        head_y = self.y - 135*scale
        pygame.draw.circle(surface, SKIN_COLOR, (int(head_x), int(head_y)), int(head_radius))
        
        # Draw hair (new)
        hair_height = 8 * scale
        pygame.draw.rect(surface, self.hair_color, 
                        (head_x - head_radius, head_y - head_radius - hair_height/2, head_radius*2, hair_height))
        eye_size = 4 * scale
        eye_spacing = 8 * scale
        # eye
        pygame.draw.circle(surface, BLACK, (int(head_x - eye_spacing), int(head_y - 3*scale)), int(eye_size))
        pygame.draw.line(surface, BLACK, 
                        (head_x - eye_spacing - eye_size, head_y - 6*scale), 
                        (head_x - eye_spacing + eye_size, head_y - 8*scale), 
                        int(2*scale))
        pygame.draw.circle(surface, BLACK, (int(head_x + eye_spacing), int(head_y - 3*scale)), int(eye_size))
        pygame.draw.line(surface, BLACK, 
                        (head_x + eye_spacing - eye_size, head_y - 8*scale), 
                        (head_x + eye_spacing + eye_size, head_y - 6*scale),
                        int(2*scale))
        hat_width = 35 * scale
        hat_height = 12 * scale
        pygame.draw.rect(surface, BLACK, 
                        (head_x - hat_width//2, head_y - head_radius - hat_height, hat_width, hat_height))
        arm_length = 50 * scale
        arm_width = 10 * scale
        knife_length = 30 * scale
        
        if self.attacking:
            # Attacking animation - arm forward with knife
            pygame.draw.rect(surface, self.jacket_color, 
                            (self.x - jacket_width//2 - arm_length, self.y - 100*scale, arm_length, arm_width))
            pygame.draw.rect(surface, KNIFE_COLOR, 
                             (self.x - jacket_width//2 - arm_length - knife_length, 
                              self.y - 100*scale, knife_length, 5*scale))
            pygame.draw.rect(surface, BLACK, 
                             (self.x - jacket_width//2 - arm_length, 
                              self.y - 100*scale - 2*scale, 10*scale, 10*scale))
        else:
            arm_swing = math.sin(self.animation_frame) * 10 * scale
            pygame.draw.rect(surface, self.jacket_color, 
                            (self.x - jacket_width//2 - arm_length//2, 
                             self.y - 100*scale + arm_swing, arm_length//2, arm_width))
            pygame.draw.rect(surface, KNIFE_COLOR, 
                             (self.x - jacket_width//2 - arm_length//2, 
                              self.y - 90*scale + arm_swing, knife_length//2, 5*scale))

    def check_hit(self, bullet_x, bullet_y):
        hitbox_width = self.size
        hitbox_height = 150 * (self.size / 80)
        hitbox_y = self.y - hitbox_height
        
        if (self.x < bullet_x < self.x + hitbox_width and 
            hitbox_y < bullet_y < self.y):
            self.health -= 25
            if self.health <= 0:
                self.active = False
            return True
        return False

def draw_hunter(surface, x, y, aim_angle, player_state, player_jump_height):
    player_hair_color = HAIR_COLORS[0]  # Using the first color as default for player
    
    player_y = y
    if player_state == "crouch":
        player_y = y + 30  # Lower position when crouching
    elif player_state == "jump":
        player_y = y - player_jump_height  # Higher during jump
        
    aim_angle = max(min(aim_angle, 30), -30)
    rifle_length = 120
    scale = 1.0
    if player_state == "crouch":
        scale = 0.8  # Smaller when crouching

    # Draw legs
    leg_spread = 20 * scale
    if player_state == "crouch":
        pygame.draw.rect(surface, PANTS_COLOR, (x - 25, player_y, 20, 60*scale))  # Left leg
        pygame.draw.rect(surface, PANTS_COLOR, (x + 5, player_y, 20, 60*scale))  # Right leg
    else:
        pygame.draw.rect(surface, PANTS_COLOR, (x - 25, player_y + 40, 20, 80*scale))  # Left leg
        pygame.draw.rect(surface, PANTS_COLOR, (x + 5, player_y + 40, 20, 80*scale))  # Right leg
    if player_state == "crouch":
        pygame.draw.rect(surface, BLACK, (x - 30, player_y + 60*scale, 25, 10))  # Left foot
        pygame.draw.rect(surface, BLACK, (x + 5, player_y + 60*scale, 25, 10))  # Right foot
    else:
        pygame.draw.rect(surface, BLACK, (x - 30, player_y + 120*scale, 25, 10))  # Left foot
        pygame.draw.rect(surface, BLACK, (x + 5, player_y + 120*scale, 25, 10))  # Right foot

    # Draw body (jacket)
    jacket_width = 50 * scale
    jacket_height = 80 * scale
    pygame.draw.rect(surface, JACKET_COLOR, (x - jacket_width//2, player_y - 40, jacket_width, jacket_height))
    pocket_size = 15 * scale
    pygame.draw.rect(surface, JACKET_COLOR, (x - jacket_width//2 + 5, player_y, pocket_size, pocket_size))
    pygame.draw.line(surface, BLACK, (x - jacket_width//2 + 5, player_y), (x - jacket_width//2 + 5 + pocket_size, player_y), 2)
    pygame.draw.line(surface, BLACK, (x - jacket_width//2 + 5, player_y + pocket_size), 
                    (x - jacket_width//2 + 5 + pocket_size, player_y + pocket_size), 2)

    # Draw head
    head_radius = 15 * scale
    head_x = x
    head_y = player_y - 55
    pygame.draw.circle(surface, SKIN_COLOR, (head_x, head_y), head_radius)
    hair_height = 8 * scale
    pygame.draw.rect(surface, player_hair_color, 
                    (head_x - head_radius, head_y - head_radius - hair_height/2, head_radius*2, hair_height))
    eye_size = 4 * scale
    eye_spacing = 8 * scale
    # eye
    pygame.draw.circle(surface, BLACK, (int(head_x - eye_spacing), int(head_y - 3*scale)), int(eye_size))
    pygame.draw.line(surface, BLACK, 
                    (head_x - eye_spacing - eye_size, head_y - 6*scale), 
                    (head_x - eye_spacing + eye_size, head_y - 8*scale), 
                    int(2*scale))
    pygame.draw.circle(surface, BLACK, (int(head_x + eye_spacing), int(head_y - 3*scale)), int(eye_size))
    pygame.draw.line(surface, BLACK, 
                    (head_x + eye_spacing - eye_size, head_y - 8*scale), 
                    (head_x + eye_spacing + eye_size, head_y - 6*scale),
                    int(2*scale))

    # Draw hat
    hat_width = 35 * scale
    hat_height = 12 * scale
    brim_height = 6 * scale
    pygame.draw.rect(surface, HAT_COLOR, (head_x - hat_width//2, head_y - head_radius - hat_height, hat_width, hat_height))
    pygame.draw.rect(surface, HAT_COLOR, (head_x - hat_width//2 - 5, head_y - head_radius - brim_height, hat_width + 10, brim_height))
    rifle_pivot_x = x + 15
    rifle_pivot_y = player_y - 20
    rifle_end_x = rifle_pivot_x + rifle_length * math.cos(math.radians(aim_angle))
    rifle_end_y = rifle_pivot_y + rifle_length * math.sin(math.radians(aim_angle))
    rifle_width = 6
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
    stock_angle = aim_angle + 180 
    stock_end_x = rifle_pivot_x + stock_width * math.cos(math.radians(stock_angle))
    stock_end_y = rifle_pivot_y + stock_width * math.sin(math.radians(stock_angle))
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
    front_hand_x = rifle_pivot_x + rifle_length * 0.7 * math.cos(math.radians(aim_angle))
    front_hand_y = rifle_pivot_y + rifle_length * 0.7 * math.sin(math.radians(aim_angle))
    arm_width = 8
    pygame.draw.line(surface, JACKET_COLOR, (x - 15, player_y - 20), (front_hand_x, front_hand_y), arm_width)
    pygame.draw.circle(surface, SKIN_COLOR, (int(front_hand_x), int(front_hand_y)), 8)
    rear_hand_x = rifle_pivot_x + 5 * math.cos(math.radians(aim_angle))
    rear_hand_y = rifle_pivot_y + 5 * math.sin(math.radians(aim_angle))
    pygame.draw.line(surface, JACKET_COLOR, (x + 10, player_y - 10), (rear_hand_x, rear_hand_y), arm_width)
    pygame.draw.circle(surface, SKIN_COLOR, (int(rear_hand_x), int(rear_hand_y)), 8)
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
    return {
        'enemies': [],
        'enemy_spawn_timer': 0,
        'score': 0,
        'player_health': 100,
        'game_over': False,
        'bullets': [],
        'muzzle_particles': [],
        'recoil_amount': 0,
        'max_enemies': 8,  # New parameter: maximum number of active enemies
        'difficulty_level': 1,  # Tracks game progression
        'enemy_spawn_delay': 2000  # Initial spawn delay (will decrease as game progresses)
    }

def create_background():
    background = pygame.Surface((width, height))
    for y in range(height):
        gradient = (
            max(20, min(50 - y * 20 // height, 50)),
            max(30, min(60 - y * 20 // height, 60)),
            max(40, min(80 - y * 20 // height, 80))
        )
        pygame.draw.line(background, gradient, (0, y), (width, y))
    ground_height = height - 150
    pygame.draw.rect(background, (40, 50, 30), (0, ground_height, width, height - ground_height))

    # Add fence in the foreground
    fence_y = ground_height + 20
    for x in range(0, width, 30):
        pygame.draw.rect(background, (40, 35, 30), (x, fence_y, 5, 40))
        pygame.draw.rect(background, (45, 40, 35), (x-15, fence_y+10, 30, 5))
    return background

def main():
    global aim_angle, bullets, player_state, player_jump_height, player_jump_speed

    clock = pygame.time.Clock()
    hunter_x = 100
    hunter_y = height - 150

    # Constants
    aim_speed = 2
    max_recoil = 3
    recoil_recovery_speed = 0.2

    # Background
    background = create_background()

    # Initial game state
    game_state = reset_game_state()

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
                player_state = "stand"  # Reset player state
                player_jump_height = 0
                player_jump_speed = 0
            continue
        
        # Regular game logic
        if game_state['recoil_amount'] > 0:
            game_state['recoil_amount'] -= recoil_recovery_speed
            if game_state['recoil_amount'] < 0:
                game_state['recoil_amount'] = 0
        
        applied_aim_angle = aim_angle + game_state['recoil_amount']
        
        # Player movement and actions
        if keys[pygame.K_UP]:
            if player_state == "stand" and player_jump_height == 0:
                player_state = "jump"
                player_jump_speed = jump_strength
        elif keys[pygame.K_DOWN]:
            if player_state != "jump":
                player_state = "crouch"
        else:
            if player_state == "crouch":
                player_state = "stand"
                
        # Handle jumping physics
        if player_state == "jump":
            player_jump_height -= player_jump_speed
            player_jump_speed += gravity
            
            # Return to standing state when jump is complete
            if player_jump_height <= 0:
                player_jump_height = 0
                player_jump_speed = 0
                player_state = "stand"
        
        # Aiming control is separate from movement
        if keys[pygame.K_LEFT]:
            aim_angle = max(aim_angle - aim_speed, -30)
        if keys[pygame.K_RIGHT]:
            aim_angle = min(aim_angle + aim_speed, 30)
        
        # Firing with F key
        if keys[pygame.K_f]:
            barrel_x, barrel_y, gun_angle = draw_hunter(screen, hunter_x, hunter_y, applied_aim_angle, player_state, player_jump_height)
            if shoot(barrel_x, barrel_y, applied_aim_angle):
                game_state['recoil_amount'] = max_recoil
                
                # Muzzle flash
                for _ in range(10):
                    particle_angle = applied_aim_angle + random.uniform(-30, 30)
                    speed = random.uniform(2, 5)
                    size = random.uniform(2, 4)
                    lifespan = random.particle_angle = applied_aim_angle + random.uniform(-30, 30)
                    speed = random.uniform(2, 5)
                    size = random.uniform(2, 4)
                    lifespan = random.randint(5, 15)
                    game_state['muzzle_particles'].append({
                        'x': barrel_x,
                        'y': barrel_y,
                        'dx': math.cos(math.radians(particle_angle)) * speed,
                        'dy': math.sin(math.radians(particle_angle)) * speed,
                        'size': size,
                        'life': lifespan,
                        'color': random.choice([(255, 200, 50), (255, 150, 0), (255, 100, 0)])
                    })
        
        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if not bullet.active:
                bullets.remove(bullet)
        
        # Update muzzle particles
        for particle in game_state['muzzle_particles'][:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                game_state['muzzle_particles'].remove(particle)
        
        # Enemy spawning and updating
        game_state['enemy_spawn_timer'] += clock.get_time()
        if game_state['enemy_spawn_timer'] >= game_state['enemy_spawn_delay'] and len(game_state['enemies']) < game_state['max_enemies']:
            game_state['enemies'].append(EnemySoldier())
            game_state['enemy_spawn_timer'] = 0
            
            # Gradually increase difficulty
            if len(game_state['enemies']) % 5 == 0:
                game_state['difficulty_level'] += 1
                game_state['enemy_spawn_delay'] = max(500, 2000 - game_state['difficulty_level'] * 200)
                game_state['max_enemies'] = min(15, 8 + game_state['difficulty_level'])
        
        # Update enemies
        for enemy in game_state['enemies'][:]:
            if enemy.update(hunter_x, hunter_y - player_jump_height if player_state == "jump" else hunter_y):
                # Enemy attacks player
                game_state['player_health'] -= enemy.attack_damage
                if game_state['player_health'] <= 0:
                    game_state['game_over'] = True
            
            # Check bullet collisions
            for bullet in bullets[:]:
                if enemy.check_hit(bullet.x, bullet.y):
                    bullets.remove(bullet)
                    if not enemy.active:
                        game_state['score'] += 100 * game_state['difficulty_level']
            
            if not enemy.active:
                game_state['enemies'].remove(enemy)
        
        # Drawing
        screen.blit(background, (0, 0))
        
        # Draw ground line
        pygame.draw.line(screen, (30, 40, 20), (0, height - 150), (width, height - 150), 2)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        
        # Draw muzzle particles
        for particle in game_state['muzzle_particles']:
            alpha = int(255 * particle['life'] / 15)
            particle_surf = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
            r, g, b = particle['color']
            pygame.draw.circle(particle_surf, (r, g, b, alpha), 
                              (int(particle['size']), int(particle['size'])), 
                              int(particle['size']))
            screen.blit(particle_surf, 
                        (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
        
        # Draw enemies
        for enemy in game_state['enemies']:
            enemy.draw(screen)
        
        # Draw player
        barrel_x, barrel_y, _ = draw_hunter(screen, hunter_x, hunter_y, applied_aim_angle, player_state, player_jump_height)
        
        # Draw HUD
        # Health bar
        health_width = 200 * (game_state['player_health'] / 100)
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, health_width, 20))
        
        # Score display
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {game_state['score']}", True, WHITE)
        screen.blit(score_text, (width - score_text.get_width() - 20, 20))
        
        # Level display
        level_text = font.render(f"Level: {game_state['difficulty_level']}", True, WHITE)
        screen.blit(level_text, (width - level_text.get_width() - 20, 60))
        
        # Controls guide
        control_font = pygame.font.SysFont(None, 24)
        controls = [
            "LEFT/RIGHT: Aim",
            "UP: Jump",
            "DOWN: Crouch",
            "F: Fire weapon"
        ]
        for i, control in enumerate(controls):
            control_text = control_font.render(control, True, WHITE)
            screen.blit(control_text, (20, height - 120 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()