import pygame
import sys
import math
import random

# Initialize PyGame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mars Rover Race")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
LIGHT_BLUE = (180, 180, 255)
MARS_RED = (212, 106, 76)
DARK_MARS_RED = (150, 70, 50)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
PURPLE = (75, 0, 130)
DARK_ORANGE = (180, 60, 10)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
RUST = (183, 65, 14)
CYAN = (0, 255, 255)  # For oxygen tanks

def main():
    clock = pygame.time.Clock()
    
    # Game state management
    game_state = "instructions"  # States: "instructions", "playing", "game_over"
    instruction_start_time = pygame.time.get_ticks()
    instruction_duration = 5000  # 5 seconds in milliseconds
    
    # Car properties
    car_scale = 0.6 
    car_width = int(400 * car_scale)
    car_height = int(80 * car_scale)
    car_cabin_height = int(60 * car_scale)
    wheel_radius = int(40 * car_scale)
    wheel_rim_radius = int(20 * car_scale)
    
    # car position 
    car_x = width // 2 - car_width // 2
    
    # Terrain properties
    terrain_speed = 3
    terrain_offset = 0
    terrain_resolution = 5  
    
    # Game state
    moving = False
    score = 0
    fuel = 100
    oxygen = 100  # New oxygen resource
    game_over = False
    game_over_reason = ""  # Track why the game ended
    
    # car position 
    car_x = width // 2 - car_width // 2
    
    # Terrain properties
    terrain_speed = 3
    terrain_offset = 0
    terrain_resolution = 5  
    
    # Game state
    moving = False
    score = 0
    fuel = 100
    oxygen = 100  # New oxygen resource
    game_over = False
    game_over_reason = ""  # Track why the game ended
    
    # Martian crystal properties (replaced coins)
    crystals = []
    crystal_radius = 10
    crystal_spawn_chance = 0.05 
    crystal_animation_offset = 0
    crystal_pulse_speed = 0.1
    
    # Super coin properties
    super_coins = []
    super_coin_radius = 15
    super_coin_spawn_chance = 0.01  # Rarer than regular crystals
    super_coin_animation_offset = 0
    
    # Fuel canister properties
    fuel_tanks = []
    fuel_tank_width = 40
    fuel_tank_height = 30
    fuel_spawn_chance = 0.007
    
    # Oxygen tank properties
    oxygen_tanks = []
    oxygen_tank_width = 35
    oxygen_tank_height = 35
    oxygen_spawn_chance = 0.007
    
    # Star properties
    stars = []
    for _ in range(100):
        star_x = random.randint(0, width)
        star_y = random.randint(0, height // 2)
        star_size = random.uniform(0.5, 3)
        star_brightness = random.randint(150, 255)
        stars.append([star_x, star_y, star_size, star_brightness, random.random() * 6.28])
    
    # Planet/Moon properties (Mars has two moons: Phobos and Deimos)
    moons = [
        {"x": 650, "y": 70, "radius": 15, "color": (170, 150, 140)},   # Phobos
        {"x": 550, "y": 100, "radius": 10, "color": (160, 140, 130)}   # Deimos
    ]
    
    # Earth properties (distant and smaller now)
    earth_angle = 0
    
    # Font setup
    font = pygame.font.SysFont(None, 36)
    game_over_font = pygame.font.SysFont(None, 72)
    instruction_font = pygame.font.SysFont(None, 30)
    title_font = pygame.font.SysFont(None, 60)
    
    # Generate Mars terrain (more rugged)
    def generate_terrain(offset):
        terrain_points = []
        for x in range(0, width + terrain_resolution, terrain_resolution):
            # Create a rougher terrain for Mars
            base_height = 430 + 10 * math.sin((x + offset) * 0.01)
            
            # Add more undulations for Mars' craterous terrain
            minor_undulation = 5 * math.sin((x + offset) * 0.05)
            secondary_undulation = 3 * math.sin((x + offset) * 0.08)
            
            y = base_height + minor_undulation + secondary_undulation
            terrain_points.append((x, y))
        return terrain_points
    
    def spawn_crystal(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - 30  
            crystals.append([x, y])
            
    def spawn_super_coin(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - 30  
            super_coins.append([x, y])
    
    def spawn_fuel_tank(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - fuel_tank_height - 10 
            fuel_tanks.append([x, y])
    
    def spawn_oxygen_tank(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - oxygen_tank_height - 10 
            oxygen_tanks.append([x, y])
    
    def draw_stars():
        for i, (star_x, star_y, star_size, star_brightness, star_phase) in enumerate(stars):
            # Make stars twinkle with a reddish tint for Mars atmosphere
            twinkle = math.sin(pygame.time.get_ticks() * 0.001 + star_phase) * 30 + 225
            color = (min(star_brightness, twinkle), 
                     min(star_brightness - 30, twinkle - 30), 
                     min(star_brightness - 60, twinkle - 60))
            pygame.draw.circle(screen, color, (int(star_x), int(star_y)), star_size)
            
            # Sometimes add a sparkle
            if random.random() < 0.01:
                pygame.draw.line(screen, WHITE, 
                                (star_x - star_size*2, star_y), 
                                (star_x + star_size*2, star_y), 1)
                pygame.draw.line(screen, WHITE, 
                                (star_x, star_y - star_size*2), 
                                (star_x, star_y + star_size*2), 1)
    
    def draw_dust_storm():
        # Randomly show a Martian dust storm
        if random.random() < 0.002:
            storm_x = random.randint(0, width)
            storm_y = random.randint(0, height // 3)
            storm_size = random.randint(30, 80)
            
            # Draw swirling dust particles
            for i in range(20):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(0, storm_size)
                dust_x = storm_x + distance * math.cos(angle)
                dust_y = storm_y + distance * math.sin(angle)
                dust_size = random.randint(1, 3)
                alpha = max(0, 255 - (distance * 255 / storm_size))
                dust_color = (min(212 + random.randint(-20, 20), 255), 
                              min(106 + random.randint(-20, 20), 255), 
                              min(76 + random.randint(-20, 20), 255), 
                              alpha)
                
                # Draw dust particle
                pygame.draw.circle(screen, dust_color, (int(dust_x), int(dust_y)), dust_size)
                
    def draw_instruction_screen():
        # Fill the background with dark orange-red for Martian sky
        screen.fill(DARK_ORANGE)
        
        # Draw stars in background
        draw_stars()
        
        # Draw some Mars terrain at the bottom for aesthetic purposes
        pygame.draw.rect(screen, MARS_RED, (0, 450, width, height - 450))
        
        # Add some crater details to the Mars terrain
        for i in range(10):
            crater_x = (i * width // 10) % width
            crater_y = random.randint(470, height - 10)
            crater_radius = random.randint(5, 15)
            pygame.draw.circle(screen, DARK_MARS_RED, (crater_x, crater_y), crater_radius, 1)
        
        # Title
        title_text = title_font.render("MARS ROVER RACE", True, WHITE)
        title_rect = title_text.get_rect(center=(width//2, 100))
        screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Control your rover across the Martian landscape!",
            "Press SPACE to start/stop moving",
            "Press LEFT/RIGHT to change direction",
            "Collect fuel tanks (orange) to refill your fuel",
            "Collect oxygen tanks (blue) to replenish oxygen",
            "Gather Martian crystals for points",
            "Golden super coins are worth DOUBLE points!",
            "Don't run out of fuel or oxygen!"
        ]
        
        y_position = 180
        for instruction in instructions:
            text = instruction_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(width//2, y_position))
            screen.blit(text, text_rect)
            y_position += 40
        
        # Skip instruction message
        skip_text = instruction_font.render("Press SPACE to start now", True, YELLOW)
        skip_rect = skip_text.get_rect(center=(width//2, height - 100))
        screen.blit(skip_text, skip_rect)
        
        # Time remaining
        time_remaining = max(0, instruction_duration - (pygame.time.get_ticks() - instruction_start_time))
        time_text = instruction_font.render(f"Starting in: {time_remaining // 1000 + 1}s", True, YELLOW)
        time_rect = time_text.get_rect(center=(width//2, height - 60))
        screen.blit(time_text, time_rect)
    
    def draw_fuel_tank(x, y, width, height):
        # Mars fuel canister
        pygame.draw.rect(screen, ORANGE, (int(x), int(y), width, height), 0, 5)
        
        # Metallic edge effect
        pygame.draw.rect(screen, DARK_GRAY, (int(x), int(y), width, height), 2, 5)
        
        # Fuel level window
        window_width = width * 0.6
        window_height = height * 0.4
        window_x = x + (width - window_width) / 2
        window_y = y + height * 0.2
        pygame.draw.rect(screen, WHITE, (int(window_x), int(window_y), int(window_width), int(window_height)), 0, 3)
        
        # Fuel level indicator
        fuel_level = window_width * 0.8
        pygame.draw.rect(screen, YELLOW, (int(window_x + window_width * 0.1), 
                                   int(window_y + window_height * 0.3), 
                                   int(fuel_level), 
                                   int(window_height * 0.4)))
        
        # Cap on top of the tank
        cap_width = width * 0.2
        cap_height = height * 0.2
        cap_x = x + width * 0.4
        cap_y = y - cap_height * 0.7
        pygame.draw.rect(screen, DARK_GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 0, 2)
        pygame.draw.rect(screen, LIGHT_GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 1, 2)
        
        # Cap detail
        pygame.draw.line(screen, BLACK, (int(cap_x + cap_width * 0.2), int(cap_y + cap_height * 0.5)), 
                                       (int(cap_x + cap_width * 0.8), int(cap_y + cap_height * 0.5)), 1)

    def draw_oxygen_tank(x, y, width, height):
        # Mars oxygen tank (blue color scheme)
        pygame.draw.rect(screen, LIGHT_BLUE, (int(x), int(y), width, height), 0, 5)
        
        # Metallic edge effect
        pygame.draw.rect(screen, DARK_GRAY, (int(x), int(y), width, height), 2, 5)
        
        # Oxygen level window
        window_width = width * 0.6
        window_height = height * 0.4
        window_x = x + (width - window_width) / 2
        window_y = y + height * 0.2
        pygame.draw.rect(screen, WHITE, (int(window_x), int(window_y), int(window_width), int(window_height)), 0, 3)
        
        # Oxygen level indicator
        oxygen_level = window_width * 0.8
        pygame.draw.rect(screen, CYAN, (int(window_x + window_width * 0.1), 
                                   int(window_y + window_height * 0.3), 
                                   int(oxygen_level), 
                                   int(window_height * 0.4)))
        
        # Add oxygen symbol (O₂)
        symbol_font = pygame.font.SysFont(None, 20)
        o2_text = symbol_font.render("O₂", True, WHITE)
        symbol_x = x + (width - o2_text.get_width()) // 2
        symbol_y = y + height - 20
        screen.blit(o2_text, (symbol_x, symbol_y))
        
        # Add valve
        valve_size = width * 0.15
        valve_x = x + width // 2 - valve_size // 2
        valve_y = y - valve_size // 2
        pygame.draw.circle(screen, DARK_GRAY, (int(valve_x + valve_size // 2), int(valve_y)), int(valve_size))
        pygame.draw.circle(screen, LIGHT_GRAY, (int(valve_x + valve_size // 2), int(valve_y)), int(valve_size * 0.7))
    
    def draw_animated_crystal(x, y, radius, animation_offset):
        # Draw Martian crystal
        # Outer glow
        glow_size = radius + 2 + math.sin(animation_offset) * 1.5
        pygame.draw.circle(screen, (255, 150, 50, 100), (int(x), int(y)), int(glow_size), 1)
        
        # Crystal shape - reddish/orange for Mars
        pygame.draw.circle(screen, (255, 130, 50), (int(x), int(y)), radius)
        
        # Inner details
        inner_radius = radius - 2 + math.sin(animation_offset) * 1
        pygame.draw.circle(screen, (255, 160, 90), (int(x), int(y)), int(inner_radius))
        
        # Crystal shine effect
        shine_angle = animation_offset * 2 % (2 * math.pi)
        shine_x = x + math.cos(shine_angle) * (radius * 0.5)
        shine_y = y + math.sin(shine_angle) * (radius * 0.5)
        pygame.draw.circle(screen, WHITE, (int(shine_x), int(shine_y)), 2)
        
    def draw_super_coin(x, y, radius, animation_offset):
        # Draw Super Coin (golden with sparkles)
        # Outer glow
        glow_size = radius + 4 + math.sin(animation_offset) * 2.5
        pygame.draw.circle(screen, (255, 215, 0, 150), (int(x), int(y)), int(glow_size), 2)
        
        # Super coin shape - gold color
        pygame.draw.circle(screen, GOLD, (int(x), int(y)), radius)
        
        # Inner details - brighter gold
        inner_radius = radius - 3 + math.sin(animation_offset) * 1.5
        pygame.draw.circle(screen, (255, 223, 100), (int(x), int(y)), int(inner_radius))
        
        # Center star shape
        for i in range(8):  # 8-point star
            angle = i * math.pi / 4 + animation_offset
            inner_pt_x = x + math.cos(angle) * (radius * 0.4)
            inner_pt_y = y + math.sin(angle) * (radius * 0.4)
            outer_pt_x = x + math.cos(angle) * (radius * 0.8)
            outer_pt_y = y + math.sin(angle) * (radius * 0.8)
            pygame.draw.line(screen, WHITE, 
                           (int(inner_pt_x), int(inner_pt_y)), 
                           (int(outer_pt_x), int(outer_pt_y)), 2)
        
        # Multiple shine effects
        for i in range(3):
            shine_angle = (animation_offset * 2 + i * 2) % (2 * math.pi)
            shine_x = x + math.cos(shine_angle) * (radius * 0.6)
            shine_y = y + math.sin(shine_angle) * (radius * 0.6)
            shine_size = 2 + (i % 2)
            pygame.draw.circle(screen, WHITE, (int(shine_x), int(shine_y)), shine_size)
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "instructions":
                        # Skip instructions and start the game
                        game_state = "playing"
                    elif game_state == "playing" and not game_over:
                        # Toggle movement
                        moving = not moving
                elif event.key == pygame.K_r and game_state == "game_over":
                    # Reset game
                    moving = False
                    score = 0
                    fuel = 100
                    oxygen = 100  # Reset oxygen too
                    game_over = False
                    game_state = "playing"
                    game_over_reason = ""
                    crystals = []
                    super_coins = []
                    fuel_tanks = []
                    oxygen_tanks = []
                    
        # Check if instruction timer has expired
        if game_state == "instructions" and pygame.time.get_ticks() - instruction_start_time > instruction_duration:
            game_state = "playing"
            
        # Instruction screen
        if game_state == "instructions":
            draw_instruction_screen()
            pygame.display.flip()
            clock.tick(60)
            continue
                    
        # Get pressed keys for speed control
        keys = pygame.key.get_pressed()
        current_speed = 0
        if moving and game_state == "playing":
            if keys[pygame.K_RIGHT]:
                current_speed = terrain_speed * 1.5
            elif keys[pygame.K_LEFT]:
                current_speed = -terrain_speed / 2  # Reduced backward speed to make it feel more natural
            else:
                current_speed = terrain_speed  
        
        # terrain offset
        if game_state == "playing" and not game_over:
            terrain_offset += current_speed
        
        # Generate terrain with current offset
        terrain_points = generate_terrain(terrain_offset)
        
        # Decrease fuel and oxygen when moving
        if moving and game_state == "playing" and not game_over:
            fuel -= 0.1
            oxygen -= 0.15  # Oxygen depletes slightly faster than fuel
            
            if fuel <= 0:
                fuel = 0
                game_over = True
                moving = False
                game_over_reason = "OUT OF FUEL"
            
            if oxygen <= 0:
                oxygen = 0
                game_over = True
                moving = False
                game_over_reason = "OUT OF OXYGEN"
                
            # Update game state if game over
            if game_over:
                game_state = "game_over"
        
        # Randomly spawn crystals
        if moving and game_state == "playing" and not game_over and random.random() < crystal_spawn_chance:
            spawn_crystal(random.randint(0, 200))
            
        # Randomly spawn super coins (rarer than regular crystals)
        if moving and game_state == "playing" and not game_over and random.random() < super_coin_spawn_chance:
            spawn_super_coin(random.randint(0, 200))
        
        # Randomly spawn fuel tanks
        if moving and game_state == "playing" and not game_over and random.random() < fuel_spawn_chance:
            spawn_fuel_tank(random.randint(0, 200))
            
        # Randomly spawn oxygen tanks
        if moving and game_state == "playing" and not game_over and random.random() < oxygen_spawn_chance:
            spawn_oxygen_tank(random.randint(0, 200))
        
        crystal_animation_offset += crystal_pulse_speed
        earth_angle = (earth_angle + 0.002) % (2 * math.pi)
        
        car_center_x = car_x + car_width / 2
        terrain_idx = min(int(car_center_x / terrain_resolution), len(terrain_points) - 2)
        
        if terrain_idx >= 0 and terrain_idx < len(terrain_points) - 1:
            x1, y1 = terrain_points[terrain_idx]
            x2, y2 = terrain_points[terrain_idx + 1]
            
            # Linear interpolation to find exact y position
            car_ground_y = y1 + (y2 - y1) * ((car_center_x - x1) / (x2 - x1)) if x2 != x1 else y1
            
            # Calculate car angle based on terrain slope
            if x2 != x1:
                slope = (y2 - y1) / (x2 - x1)
                car_angle = math.degrees(math.atan(slope))
            else:
                car_angle = 0
        else:
            car_ground_y = 430  
            car_angle = 0
            
        # Calculate car's position and center for collision detection
        car_pos_x = car_x - 25  
        car_pos_y = car_ground_y - wheel_radius - (car_height + car_cabin_height) * 0.85
        
        # Calculate car's true center for collision detection
        car_center_y = car_pos_y + (car_height + car_cabin_height) / 2
        
        # Create a collision rectangle for the car
        car_collision_width = car_width * 0.8
        car_collision_height = (car_height + car_cabin_height) * 0.7
        car_collision_rect = pygame.Rect(
            car_center_x - car_collision_width/2,
            car_center_y - car_collision_height/2,
            car_collision_width,
            car_collision_height
        )
        
        # Update crystal positions and check for collection
        i = 0
        while i < len(crystals):
            crystals[i][0] -= current_speed
            
            # Check if car collects crystal using collision rect
            crystal_rect = pygame.Rect(
                crystals[i][0] - crystal_radius,
                crystals[i][1] - crystal_radius,
                crystal_radius * 2,
                crystal_radius * 2
            )
            
            if car_collision_rect.colliderect(crystal_rect):
                score += 1
                crystals.pop(i)
            # Remove crystals that have gone off screen
            elif crystals[i][0] < -2 * crystal_radius:
                crystals.pop(i)
            else:
                i += 1
                
        # Update super coin positions and check for collection
        i = 0
        while i < len(super_coins):
            super_coins[i][0] -= current_speed
            
            # Check if car collects super coin using collision rect
            super_coin_rect = pygame.Rect(
                super_coins[i][0] - super_coin_radius,
                super_coins[i][1] - super_coin_radius,
                super_coin_radius * 2,
                super_coin_radius * 2
            )
            
            if car_collision_rect.colliderect(super_coin_rect):
                score += 2  # Double score for super coins
                # Display "+2" text effect
                super_coins.pop(i)
            # Remove super coins that have gone off screen
            elif super_coins[i][0] < -2 * super_coin_radius:
                super_coins.pop(i)
            else:
                i += 1
        
        # Update fuel tank positions and check for collection
        i = 0
        while i < len(fuel_tanks):
            fuel_tanks[i][0] -= current_speed
            
            # Check if car collects fuel tank using collision rect
            tank_rect = pygame.Rect(
                fuel_tanks[i][0],
                fuel_tanks[i][1],
                fuel_tank_width,
                fuel_tank_height
            )
            
            if car_collision_rect.colliderect(tank_rect):
                fuel = min(100, fuel + 30) 
                fuel_tanks.pop(i)
            elif fuel_tanks[i][0] < -fuel_tank_width:
                fuel_tanks.pop(i)
            else:
                i += 1
                
        # Update oxygen tank positions and check for collection
        i = 0
        while i < len(oxygen_tanks):
            oxygen_tanks[i][0] -= current_speed
            
            # Check if car collects oxygen tank using collision rect
            tank_rect = pygame.Rect(
                oxygen_tanks[i][0],
                oxygen_tanks[i][1],
                oxygen_tank_width,
                oxygen_tank_height
            )
            
            if car_collision_rect.colliderect(tank_rect):
                oxygen = min(100, oxygen + 25)  # Fill oxygen
                oxygen_tanks.pop(i)
            elif oxygen_tanks[i][0] < -oxygen_tank_width:
                oxygen_tanks.pop(i)
            else:
                i += 1
        
        # Fill the background with dark orange-red for Martian sky
        screen.fill(DARK_ORANGE)
        
        # Draw stars in background
        draw_stars()
        
        # Draw moons
        for moon in moons:
            pygame.draw.circle(screen, moon["color"], (moon["x"], moon["y"]), moon["radius"])
            # Add a highlight to each moon
            highlight_x = moon["x"] - moon["radius"] * 0.3
            highlight_y = moon["y"] - moon["radius"] * 0.3
            pygame.draw.circle(screen, (255, 255, 255, 150), 
                              (int(highlight_x), int(highlight_y)), 
                              int(moon["radius"] * 0.3))
        
        # Draw Earth as a distant blue dot
        earth_x = 100
        earth_y = 80
        earth_radius = 8
        earth_shine_x = earth_x - earth_radius * 0.3
        earth_shine_y = earth_y - earth_radius * 0.3
        pygame.draw.circle(screen, (100, 150, 255), (earth_x, earth_y), earth_radius)
        pygame.draw.circle(screen, (180, 210, 255), (int(earth_shine_x), int(earth_shine_y)), 2)
        
        # Occasionally draw a dust storm
        draw_dust_storm()
        
        # Draw Mars surface base
        pygame.draw.rect(screen, DARK_MARS_RED, (0, 450, width, height - 450))
        
        # Draw the detailed Mars terrain
        pygame.draw.polygon(screen, MARS_RED, terrain_points + [(width, height), (0, height)])
        
        # Add some crater details to the Mars terrain
        for i in range(10):
            crater_x = (i * width // 10 + terrain_offset // 3) % width
            crater_y = random.randint(470, height - 10)
            crater_radius = random.randint(5, 15)
            pygame.draw.circle(screen, DARK_MARS_RED, (crater_x, crater_y), crater_radius, 1)
        
        for crystal_x, crystal_y in crystals:
            draw_animated_crystal(crystal_x, crystal_y, crystal_radius, crystal_animation_offset)
            
        # Draw super coins
        for super_coin_x, super_coin_y in super_coins:
            draw_super_coin(super_coin_x, super_coin_y, super_coin_radius, crystal_animation_offset)
        
        # Draw fuel tanks
        for tank_x, tank_y in fuel_tanks:
            draw_fuel_tank(tank_x, tank_y, fuel_tank_width, fuel_tank_height)
            
        # Draw oxygen tanks
        for tank_x, tank_y in oxygen_tanks:
            draw_oxygen_tank(tank_x, tank_y, oxygen_tank_width, oxygen_tank_height)
        
        # Create the rover surface for rotation
        car_surface = pygame.Surface((car_width + 50, car_height + car_cabin_height + 20), pygame.SRCALPHA)
        
        # Draw Mars rover on separate surface
        # Main body
        body_rect = (25, car_cabin_height, car_width, car_height)
        pygame.draw.rect(car_surface, WHITE, body_rect)
        
        # Top part
        cabin_width = car_width * 0.5
        cabin_x_offset = (car_width - cabin_width) / 2 + 25
        cabin_points = [
            (cabin_x_offset, car_cabin_height),
            (cabin_x_offset + cabin_width, car_cabin_height),
            (cabin_x_offset + cabin_width * 0.85, 0),
            (cabin_x_offset + cabin_width * 0.15, 0)
        ]
        pygame.draw.polygon(car_surface, WHITE, cabin_points)
        
        # Windows
        window_points = [
            (cabin_x_offset + 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width - 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width * 0.85 - 5, 5),
            (cabin_x_offset + cabin_width * 0.15 + 5, 5)
        ]
        pygame.draw.polygon(car_surface, (50, 255, 200), window_points)
        
        # Solar panels on top
        panel_width = cabin_width * 0.7
        panel_height = 5
        panel_x = cabin_x_offset + (cabin_width - panel_width) / 2
        panel_y = car_cabin_height / 2 - panel_height
        pygame.draw.rect(car_surface, (50, 50, 200), (panel_x, panel_y, panel_width, panel_height))
        
        # Mars rover wheels - bigger for rough terrain
        left_wheel_x = 25 + wheel_radius
        right_wheel_x = 25 + car_width - wheel_radius
        wheel_y = car_cabin_height + car_height
        
        pygame.draw.circle(car_surface, DARK_GRAY, (left_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(car_surface, DARK_GRAY, (right_wheel_x, wheel_y), wheel_radius)
        
        # Wheel rims
        pygame.draw.circle(car_surface, RUST, (left_wheel_x, wheel_y), wheel_rim_radius)
        pygame.draw.circle(car_surface, RUST, (right_wheel_x, wheel_y), wheel_rim_radius)
        
        # Headlights
        pygame.draw.rect(car_surface, YELLOW, (25 + car_width - 15, car_cabin_height + 10, 15, 15))
        
        # Antenna and science equipment
        antenna_x = cabin_x_offset + cabin_width * 0.7
        antenna_y = 0
        antenna_height = 20
        pygame.draw.line(car_surface, DARK_GRAY, (antenna_x, antenna_y), (antenna_x, antenna_y - antenna_height), 2)
        pygame.draw.circle(car_surface, RED, (antenna_x, antenna_y - antenna_height), 3)
        
        # Science camera/sensor
        camera_x = cabin_x_offset + cabin_width * 0.3
        camera_y = 0
        camera_height = 15
        pygame.draw.line(car_surface, DARK_GRAY, (camera_x, camera_y), (camera_x, camera_y - camera_height), 2)
        pygame.draw.rect(car_surface, DARK_GRAY, (camera_x - 5, camera_y - camera_height - 5, 10, 5))
        
        # Rotate the entire rover surface
        rotated_car = pygame.transform.rotate(car_surface, -car_angle)
        
        # Calculate position to place the rotated rover
        rotated_rect = rotated_car.get_rect()
        
        # Draw the rotated rover
        screen.blit(rotated_car, (car_pos_x + (car_width + 50) / 2 - rotated_rect.width / 2, 
                                  car_pos_y + (car_height + car_cabin_height + 20) / 2 - rotated_rect.height / 2))
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 10))
        
        # Draw fuel meter
        pygame.draw.rect(screen, WHITE, (20, 60, 204, 24), 2)
        fuel_width = int(2 * fuel)
        fuel_color = GREEN
        if fuel < 30:
            fuel_color = RED
        elif fuel < 70:
            fuel_color = YELLOW
        pygame.draw.rect(screen, fuel_color, (22, 62, fuel_width, 20))
        
        fuel_text = font.render(f"Fuel", True, WHITE)
        screen.blit(fuel_text, (22, 35))
        
        # Draw oxygen meter
        pygame.draw.rect(screen, WHITE, (20, 120, 204, 24), 2)
        oxygen_width = int(2 * oxygen)
        oxygen_color = GREEN
        if oxygen < 30:
            oxygen_color = RED
        elif oxygen < 70:
            oxygen_color = YELLOW
        pygame.draw.rect(screen, oxygen_color, (22, 122, oxygen_width, 20))
        
        oxygen_text = font.render(f"Oxygen", True, WHITE)
        screen.blit(oxygen_text, (22, 95))
        
        # Instructions
        instruction_font = pygame.font.SysFont(None, 24)
        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            reason_text = font.render(game_over_reason, True, WHITE)
            reason_rect = reason_text.get_rect(center=(width//2, height//2))
            screen.blit(reason_text, reason_rect)
            
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(width//2, height//2 + 50))
            screen.blit(restart_text, restart_rect)
        else:
            if moving:
                instruction_text = instruction_font.render("SPACE to stop | LEFT/RIGHT to change direction", True, WHITE)
            else:
                instruction_text = instruction_font.render("Press SPACE to start the Mars rover", True, WHITE)
            screen.blit(instruction_text, (width - instruction_text.get_width() - 20, 20))
            
            # Show oxygen message when first starting
            if not moving and oxygen == 100 and fuel == 100:
                oxygen_instruction = instruction_font.render("Collect oxygen tanks (blue) to survive!", True, CYAN)
                screen.blit(oxygen_instruction, (width - oxygen_instruction.get_width() - 20, 50))
                
                # Show super coin message
                super_coin_instruction = instruction_font.render("Golden super coins are worth double points!", True, GOLD)
                screen.blit(super_coin_instruction, (width - super_coin_instruction.get_width() - 20, 80))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()