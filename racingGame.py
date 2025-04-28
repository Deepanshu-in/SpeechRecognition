import pygame
import sys
import math
import random

# Initialize PyGame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PyGame Car Design")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
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
    fuel = 100  # Start with full fuel
    game_over = False
    
    # Coin properties
    coins = []
    coin_radius = 10
    coin_spawn_chance = 0.05 
    coin_animation_offset = 0
    coin_pulse_speed = 0.1
    
    # Fuel tank properties
    fuel_tanks = []
    fuel_tank_width = 40
    fuel_tank_height = 30
    fuel_spawn_chance = 0.007  
    
    # Sun animation properties
    sun_rays_angle = 0
    sun_pulse_size = 0
    
    # Font setup
    font = pygame.font.SysFont(None, 36)
    game_over_font = pygame.font.SysFont(None, 72)
    
    # Initial creation of terrain points with smoother hills
    def generate_terrain(offset):
        terrain_points = []
        for x in range(0, width + terrain_resolution, terrain_resolution):
            y = 430 + 15 * math.sin((x + offset) * 0.01)
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
    
    def draw_sun(x, y, base_radius):
        # Dynamic sun size 
        sun_size = base_radius + sun_pulse_size
        
        # Draw the sun's rays
        ray_length = base_radius * 0.4
        for i in range(8):  
            angle = math.radians(i * 45 + sun_rays_angle)
            end_x = x + math.cos(angle) * (sun_size + ray_length)
            end_y = y + math.sin(angle) * (sun_size + ray_length)
            pygame.draw.line(screen, ORANGE, (x, y), (end_x, end_y), 3)
        
        # Draw the main sun circle AFTER the rays
        pygame.draw.circle(screen, YELLOW, (x, y), sun_size)
    
    def draw_fuel_tank(x, y, width, height):
        # Main tank body 
        pygame.draw.rect(screen, DARK_GRAY, (int(x), int(y), width, height), 0, 5)
        
        # Metallic edge effect
        pygame.draw.rect(screen, GRAY, (int(x), int(y), width, height), 2, 5)
        
        # Fuel gauge window
        window_width = width * 0.6
        window_height = height * 0.4
        window_x = x + (width - window_width) / 2
        window_y = y + height * 0.2
        pygame.draw.rect(screen, WHITE, (int(window_x), int(window_y), int(window_width), int(window_height)), 0, 3)
        
        # Fuel level indicator in window
        fuel_level = window_width * 0.8
        pygame.draw.rect(screen, RED, (int(window_x + window_width * 0.1), 
                                       int(window_y + window_height * 0.3), 
                                       int(fuel_level), 
                                       int(window_height * 0.4)))
        
        # Cap on top of the tank
        cap_width = width * 0.2
        cap_height = height * 0.2
        cap_x = x + width * 0.4
        cap_y = y - cap_height * 0.7
        pygame.draw.rect(screen, DARK_GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 0, 2)
        pygame.draw.rect(screen, GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 1, 2)
        
        # Cap detail
        pygame.draw.line(screen, BLACK, (int(cap_x + cap_width * 0.2), int(cap_y + cap_height * 0.5)), 
                                         (int(cap_x + cap_width * 0.8), int(cap_y + cap_height * 0.5)), 1)
    
    def draw_animated_coin(x, y, radius, animation_offset):
        # Draw the outer circle 
        pygame.draw.circle(screen, GOLD, (int(x), int(y)), radius)
        
        # Draw the inner circle - with pulsing animation
        inner_radius = radius - 2 + math.sin(animation_offset) * 1
        pygame.draw.circle(screen, YELLOW, (int(x), int(y)), int(inner_radius))
        
        # Draw $ sign with slight animation
        coin_text = font.render("$", True, BLACK)
        text_y_offset = math.sin(animation_offset * 1.5) * 1
        coin_text_rect = coin_text.get_rect(center=(int(x), int(y + text_y_offset)))
        screen.blit(coin_text, coin_text_rect)
        
        # Add a shine effect 
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
                current_speed = -terrain_speed
            else:
                current_speed = terrain_speed  
        
        # Update terrain offset
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
        sun_rays_angle = (sun_rays_angle + 0.2) % 360
        sun_pulse_size = 2 * math.sin(pygame.time.get_ticks() * 0.001)
        
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
        
        # Fill the background with sky blue
        screen.fill(SKY_BLUE)
        
        # Draw the animated sun
        draw_sun(700, 100, 50)
        
        # Draw terrain
        # Fill the ground
        pygame.draw.rect(screen, BROWN, (0, 450, width, height - 450))
        
        # Draw the grass
        pygame.draw.polygon(screen, GREEN, terrain_points + [(width, height), (0, height)])
        
        # Draw animated coins
        for coin_x, coin_y in coins:
            draw_animated_coin(coin_x, coin_y, coin_radius, coin_animation_offset)
        
        # Draw improved fuel tanks
        for tank_x, tank_y in fuel_tanks:
            draw_fuel_tank(tank_x, tank_y, fuel_tank_width, fuel_tank_height)
        
        # Create the car surface for rotation
        car_surface = pygame.Surface((car_width + 50, car_height + car_cabin_height + 20), pygame.SRCALPHA)
        
        # Draw car on separate surface
        # Main body
        body_rect = (25, car_cabin_height, car_width, car_height)
        pygame.draw.rect(car_surface, RED, body_rect)
        
        # Top part 
        cabin_width = car_width * 0.5
        cabin_x_offset = (car_width - cabin_width) / 2 + 25
        cabin_points = [
            (cabin_x_offset, car_cabin_height),
            (cabin_x_offset + cabin_width, car_cabin_height),
            (cabin_x_offset + cabin_width * 0.85, 0),
            (cabin_x_offset + cabin_width * 0.15, 0)
        ]
        pygame.draw.polygon(car_surface, RED, cabin_points)
        
        # Windows
        window_points = [
            (cabin_x_offset + 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width - 5, car_cabin_height - 5),
            (cabin_x_offset + cabin_width * 0.85 - 5, 5),
            (cabin_x_offset + cabin_width * 0.15 + 5, 5)
        ]
        pygame.draw.polygon(car_surface, BLACK, window_points)
        
        # Wheels
        left_wheel_x = 25 + wheel_radius
        right_wheel_x = 25 + car_width - wheel_radius
        wheel_y = car_cabin_height + car_height
        
        pygame.draw.circle(car_surface, BLACK, (left_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(car_surface, BLACK, (right_wheel_x, wheel_y), wheel_radius)
        
        # Wheel rims
        pygame.draw.circle(car_surface, GRAY, (left_wheel_x, wheel_y), wheel_rim_radius)
        pygame.draw.circle(car_surface, GRAY, (right_wheel_x, wheel_y), wheel_rim_radius)
        
        # Headlights
        pygame.draw.rect(car_surface, YELLOW, (25 + car_width - 10, car_cabin_height + 10, 10, 10))
        
        # Taillight
        pygame.draw.rect(car_surface, RED, (20, car_cabin_height + 10, 5, 10))
        
        # Rotate the entire car surface
        rotated_car = pygame.transform.rotate(car_surface, -car_angle)
        
        # Calculate position to place the rotated car
        rotated_rect = rotated_car.get_rect()
        
        # Draw the rotated car
        screen.blit(rotated_car, (car_pos_x + (car_width + 50) / 2 - rotated_rect.width / 2, 
                                  car_pos_y + (car_height + car_cabin_height + 20) / 2 - rotated_rect.height / 2))
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 10))
        
        # Draw fuel bar
        pygame.draw.rect(screen, BLACK, (20, 60, 204, 24), 2)
        fuel_width = int(2 * fuel)
        fuel_color = GREEN
        if fuel < 30:
            fuel_color = RED
        elif fuel < 70:
            fuel_color = YELLOW
        pygame.draw.rect(screen, fuel_color, (22, 62, fuel_width, 20))
        
        fuel_text = font.render(f"Fuel", True, BLACK)
        screen.blit(fuel_text, (22, 35))
        
        # Instructions
        instruction_font = pygame.font.SysFont(None, 24)
        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            restart_text = font.render("Press R to restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(width//2, height//2 + 20))
            screen.blit(restart_text, restart_rect)
        else:
            if moving:
                instruction_text = instruction_font.render("SPACE to stop | LEFT/RIGHT to move direction", True, BLACK)
            else:
                instruction_text = instruction_font.render("Press SPACE to start the car", True, BLACK)
            screen.blit(instruction_text, (width - instruction_text.get_width() - 20, 20))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()