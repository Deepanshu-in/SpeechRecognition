import pygame
import sys
import math
import random

# Initialize PyGame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Lunar Rover Race")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
LIGHT_BLUE = (180, 180, 180)
MOON_GRAY = (220, 220, 230)
DARK_MOON_GRAY = (120, 120, 130)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
PURPLE = (75, 0, 130)
DARK_BLUE = (10, 10, 40)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)

def main():
    clock = pygame.time.Clock()
    
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
    game_over = False
    
    # Coin properties 
    coins = []
    coin_radius = 10
    coin_spawn_chance = 0.05 
    coin_animation_offset = 0
    coin_pulse_speed = 0.1
    
    # Oxygen tank properties
    fuel_tanks = []
    fuel_tank_width = 40
    fuel_tank_height = 30
    fuel_spawn_chance = 0.007  
    
    # Star properties
    stars = []
    for _ in range(100):
        star_x = random.randint(0, width)
        star_y = random.randint(0, height // 2)
        star_size = random.uniform(0.5, 3)
        star_brightness = random.randint(150, 255)
        stars.append([star_x, star_y, star_size, star_brightness, random.random() * 6.28])
    
    # Planet properties
    planets = [
        {"x": 150, "y": 100, "radius": 20, "color": (255, 100, 100)},  # Red planet
        {"x": 650, "y": 50, "radius": 15, "color": (100, 200, 255)},   # Blue planet
        {"x": 300, "y": 150, "radius": 10, "color": (255, 220, 100)}   # Yellow planet
    ]
    
    # Earth properties
    earth_angle = 0
    
    # Font setup
    font = pygame.font.SysFont(None, 36)
    game_over_font = pygame.font.SysFont(None, 72)
    
    # Generate smooth lunar terrain
    def generate_terrain(offset):
        terrain_points = []
        for x in range(0, width + terrain_resolution, terrain_resolution):
            # Create a smoother sine wave with less variation
            base_height = 430 + 8 * math.sin((x + offset) * 0.01)
            
            # Add minor undulations to prevent completely flat surface
            minor_undulation = 2 * math.sin((x + offset) * 0.05)
            
            y = base_height + minor_undulation
            terrain_points.append((x, y))
        return terrain_points
    
    def spawn_coin(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - 30  
            coins.append([x, y])
    
    def spawn_fuel_tank(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - fuel_tank_height - 10 
            fuel_tanks.append([x, y])
    
    def draw_stars():
        for i, (star_x, star_y, star_size, star_brightness, star_phase) in enumerate(stars):
            # Make stars twinkle
            twinkle = math.sin(pygame.time.get_ticks() * 0.001 + star_phase) * 30 + 225
            color = (min(star_brightness, twinkle), min(star_brightness, twinkle), min(255, star_brightness + 20))
            pygame.draw.circle(screen, color, (int(star_x), int(star_y)), star_size)
            
            # Sometimes add a sparkle
            if random.random() < 0.01:
                pygame.draw.line(screen, WHITE, 
                                (star_x - star_size*2, star_y), 
                                (star_x + star_size*2, star_y), 1)
                pygame.draw.line(screen, WHITE, 
                                (star_x, star_y - star_size*2), 
                                (star_x, star_y + star_size*2), 1)
    
    def draw_comet():
        # Randomly show a comet across the sky
        if random.random() < 0.002:
            comet_x = random.randint(0, width)
            comet_y = random.randint(0, height // 3)
            comet_length = random.randint(20, 60)
            comet_angle = random.uniform(0.1, 0.5)
            
            # Draw comet tail
            points = []
            for i in range(comet_length):
                tail_x = comet_x - i * math.cos(comet_angle)
                tail_y = comet_y + i * math.sin(comet_angle)
                tail_width = (comet_length - i) / comet_length * 3
                points.append((tail_x, tail_y))
                
            if len(points) >= 2:
                pygame.draw.lines(screen, (200, 200, 255), False, points, 2)
            
            # Draw comet head
            pygame.draw.circle(screen, WHITE, (int(comet_x), int(comet_y)), 2)
    
    def draw_fuel_tank(x, y, width, height):
        # Oxygen tank
        pygame.draw.rect(screen, BLUE, (int(x), int(y), width, height), 0, 5)
        
        # Metallic edge effect
        pygame.draw.rect(screen, LIGHT_GRAY, (int(x), int(y), width, height), 2, 5)
        
        # Oxygen level window
        window_width = width * 0.6
        window_height = height * 0.4
        window_x = x + (width - window_width) / 2
        window_y = y + height * 0.2
        pygame.draw.rect(screen, WHITE, (int(window_x), int(window_y), int(window_width), int(window_height)), 0, 3)
        
        # Oxygen level indicator
        fuel_level = window_width * 0.8
        pygame.draw.rect(screen, LIGHT_BLUE, (int(window_x + window_width * 0.1), 
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
    
    def draw_animated_coin(x, y, radius, animation_offset):
        # Draw moon crystal
        # Outer glow
        glow_size = radius + 2 + math.sin(animation_offset) * 1.5
        pygame.draw.circle(screen, (150, 150, 255, 100), (int(x), int(y)), int(glow_size), 1)
        
        # Crystal shape
        pygame.draw.circle(screen, (220, 220, 255), (int(x), int(y)), radius)
        
        # Inner details
        inner_radius = radius - 2 + math.sin(animation_offset) * 1
        pygame.draw.circle(screen, (240, 240, 255), (int(x), int(y)), int(inner_radius))
        
        # Crystal shine effect
        shine_angle = animation_offset * 2 % (2 * math.pi)
        shine_x = x + math.cos(shine_angle) * (radius * 0.5)
        shine_y = y + math.sin(shine_angle) * (radius * 0.5)
        pygame.draw.circle(screen, WHITE, (int(shine_x), int(shine_y)), 2)
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    moving = not moving
                elif event.key == pygame.K_r and game_over:
                    # Reset game
                    moving = False
                    score = 0
                    fuel = 100
                    game_over = False
                    coins = []
                    fuel_tanks = []
                    
        # Get pressed keys for speed control
        keys = pygame.key.get_pressed()
        current_speed = 0
        if moving and not game_over:
            if keys[pygame.K_RIGHT]:
                current_speed = terrain_speed * 1.5
            elif keys[pygame.K_LEFT]:
                current_speed = -terrain_speed / 2  # Reduced backward speed to make it feel more natural
            else:
                current_speed = terrain_speed  
        
        # terrain offset
        if not game_over:
            terrain_offset += current_speed
        
        # Generate terrain with current offset
        terrain_points = generate_terrain(terrain_offset)
        
        # Decrease fuel when moving
        if moving and not game_over:
            fuel -= 0.1
            if fuel <= 0:
                fuel = 0
                game_over = True
                moving = False
        
        # Randomly spawn coins
        if moving and not game_over and random.random() < coin_spawn_chance:
            spawn_coin(random.randint(0, 200))
        
        # Randomly spawn fuel tanks
        if moving and not game_over and random.random() < fuel_spawn_chance:
            spawn_fuel_tank(random.randint(0, 200))
        
        coin_animation_offset += coin_pulse_speed
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
        
        # Update coin positions and check for collection
        i = 0
        while i < len(coins):
            coins[i][0] -= current_speed
            
            # Check if car collects coin using collision rect
            coin_rect = pygame.Rect(
                coins[i][0] - coin_radius,
                coins[i][1] - coin_radius,
                coin_radius * 2,
                coin_radius * 2
            )
            
            if car_collision_rect.colliderect(coin_rect):
                score += 1
                coins.pop(i)
            # Remove coins that have gone off screen
            elif coins[i][0] < -2 * coin_radius:
                coins.pop(i)
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
        
        # Fill the background with space black
        screen.fill(BLACK)
        
        # Draw stars in background
        draw_stars()
        
        # Draw planets
        for planet in planets:
            pygame.draw.circle(screen, planet["color"], (planet["x"], planet["y"]), planet["radius"])
            # Add a highlight to each planet
            highlight_x = planet["x"] - planet["radius"] * 0.3
            highlight_y = planet["y"] - planet["radius"] * 0.3
            pygame.draw.circle(screen, (255, 255, 255, 150), 
                              (int(highlight_x), int(highlight_y)), 
                              int(planet["radius"] * 0.3))
        
        # Occasionally draw a comet
        draw_comet()
        
        # Draw moon surface base
        pygame.draw.rect(screen, DARK_GRAY, (0, 450, width, height - 450))
        
        # Draw the detailed lunar terrain
        pygame.draw.polygon(screen, MOON_GRAY, terrain_points + [(width, height), (0, height)])
        
        for coin_x, coin_y in coins:
            draw_animated_coin(coin_x, coin_y, coin_radius, coin_animation_offset)
        
        # Draw oxygen tanks
        for tank_x, tank_y in fuel_tanks:
            draw_fuel_tank(tank_x, tank_y, fuel_tank_width, fuel_tank_height)
        
        # Create the rover surface for rotation
        car_surface = pygame.Surface((car_width + 50, car_height + car_cabin_height + 20), pygame.SRCALPHA)
        
        # Draw lunar rover on separate surface
        # Main body
        body_rect = (25, car_cabin_height, car_width, car_height)
        pygame.draw.rect(car_surface, LIGHT_GRAY, body_rect)
        
        # Top part
        cabin_width = car_width * 0.5
        cabin_x_offset = (car_width - cabin_width) / 2 + 25
        cabin_points = [
            (cabin_x_offset, car_cabin_height),
            (cabin_x_offset + cabin_width, car_cabin_height),
            (cabin_x_offset + cabin_width * 0.85, 0),
            (cabin_x_offset + cabin_width * 0.15, 0)
        ]
        pygame.draw.polygon(car_surface, LIGHT_GRAY, cabin_points)
        
        # Windows
        window_points = [
            (cabin_x_offset + 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width - 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width * 0.85 - 5, 5),
            (cabin_x_offset + cabin_width * 0.15 + 5, 5)
        ]
        pygame.draw.polygon(car_surface, BLUE, window_points)
        
        # Solar panels on top
        panel_width = cabin_width * 0.7
        panel_height = 5
        panel_x = cabin_x_offset + (cabin_width - panel_width) / 2
        panel_y = car_cabin_height / 2 - panel_height
        pygame.draw.rect(car_surface, BLUE, (panel_x, panel_y, panel_width, panel_height))
        
        # Rover wheels
        left_wheel_x = 25 + wheel_radius
        right_wheel_x = 25 + car_width - wheel_radius
        wheel_y = car_cabin_height + car_height
        
        pygame.draw.circle(car_surface, DARK_GRAY, (left_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(car_surface, DARK_GRAY, (right_wheel_x, wheel_y), wheel_radius)
        
        # Wheel rims
        pygame.draw.circle(car_surface, LIGHT_GRAY, (left_wheel_x, wheel_y), wheel_rim_radius)
        pygame.draw.circle(car_surface, LIGHT_GRAY, (right_wheel_x, wheel_y), wheel_rim_radius)
        
        # Headlights
        pygame.draw.rect(car_surface, YELLOW, (25 + car_width - 15, car_cabin_height + 10, 15, 15))
        
        # Antenna
        antenna_x = cabin_x_offset + cabin_width * 0.7
        antenna_y = 0
        antenna_height = 20
        pygame.draw.line(car_surface, DARK_GRAY, (antenna_x, antenna_y), (antenna_x, antenna_y - antenna_height), 2)
        pygame.draw.circle(car_surface, RED, (antenna_x, antenna_y - antenna_height), 3)
        
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
        
        # Draw oxygen meter
        pygame.draw.rect(screen, WHITE, (20, 60, 204, 24), 2)
        fuel_width = int(2 * fuel)
        fuel_color = GREEN
        if fuel < 30:
            fuel_color = RED
        elif fuel < 70:
            fuel_color = YELLOW
        pygame.draw.rect(screen, fuel_color, (22, 62, fuel_width, 20))
        
        oxygen_text = font.render(f"Oxygen", True, WHITE)
        screen.blit(oxygen_text, (22, 35))
        
        # Instructions
        instruction_font = pygame.font.SysFont(None, 24)
        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(width//2, height//2 + 20))
            screen.blit(restart_text, restart_rect)
        else:
            if moving:
                instruction_text = instruction_font.render("SPACE to stop | LEFT/RIGHT to change direction", True, WHITE)
            else:
                instruction_text = instruction_font.render("Press SPACE to start the lunar rover", True, WHITE)
            screen.blit(instruction_text, (width - instruction_text.get_width() - 20, 20))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()