import pygame
import sys
import math
import random

# Initialize PyGame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Death Race")

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
DARK_SKY_BLUE = (25, 25, 112)  # Night sky color
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
TEAL = (0, 128, 128)
BLOOD_RED = (150, 0, 0)
NIGHT_GREEN = (20, 80, 20)  # Darker green for night
NIGHT_BROWN = (80, 40, 10)  # Darker brown for night

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
    
    # Day-night cycle properties
    day_night_timer = 0
    cycle_duration = 60 * 60
    is_night = False
    transition_duration = 5 * 60  # 5 seconds transition
    night_alpha = 0  # For smooth transition
    
    # Torch light properties
    torch_radius = 200
    torch_flicker = 0
    
    # Zombie properties
    zombies = []
    zombie_width = 40
    zombie_height = 60
    zombie_spawn_chance = 0.05
    zombie_colors = [DARK_GREEN, PURPLE, TEAL, GRAY, GOLD]
    
    # Blood effect properties
    blood_splats = []
    blood_duration = 60
    
    # Fuel tank properties
    fuel_tanks = []
    fuel_tank_width = 40
    fuel_tank_height = 30
    fuel_spawn_chance = 0.007  
    
    # Sun/Moon animation properties
    celestial_rays_angle = 0
    celestial_pulse_size = 0
    
    # Stars for night sky
    stars = []
    for _ in range(100):
        stars.append((random.randint(0, width), random.randint(0, height//2), random.random() * 2 + 1))
    
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
    
    def spawn_zombie(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - zombie_height  
            color = random.choice(zombie_colors)
            zombies.append([x, y, color])
    
    def spawn_fuel_tank(offset):
        x = width + offset
        terrain_idx = min(int(x / terrain_resolution), len(terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(terrain_points):
            y = terrain_points[terrain_idx][1] - fuel_tank_height - 10 
            fuel_tanks.append([x, y])
    
    def draw_sun(x, y, base_radius):
        # Dynamic sun size 
        sun_size = base_radius + celestial_pulse_size
        
        # Draw the sun's rays
        ray_length = base_radius * 0.4
        for i in range(8):  
            angle = math.radians(i * 45 + celestial_rays_angle)
            end_x = x + math.cos(angle) * (sun_size + ray_length)
            end_y = y + math.sin(angle) * (sun_size + ray_length)
            pygame.draw.line(screen, ORANGE, (x, y), (end_x, end_y), 3)
        
        # Draw the main sun circle AFTER the rays
        pygame.draw.circle(screen, YELLOW, (x, y), sun_size)
    
    def draw_moon(x, y, base_radius):
        # Main moon
        moon_size = base_radius + celestial_pulse_size * 0.5
        pygame.draw.circle(screen, WHITE, (x, y), moon_size)
        
        # Craters
        pygame.draw.circle(screen, GRAY, (x - moon_size//3, y - moon_size//4), moon_size//5)
        pygame.draw.circle(screen, GRAY, (x + moon_size//4, y + moon_size//3), moon_size//6)
        pygame.draw.circle(screen, GRAY, (x + moon_size//2, y - moon_size//5), moon_size//8)
    
    
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
        
        cap_width = width * 0.2
        cap_height = height * 0.2
        cap_x = x + width * 0.4
        cap_y = y - cap_height * 0.7
        pygame.draw.rect(screen, DARK_GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 0, 2)
        pygame.draw.rect(screen, GRAY, (int(cap_x), int(cap_y), int(cap_width), int(cap_height)), 1, 2)
        
        # Cap detail
        pygame.draw.line(screen, BLACK, (int(cap_x + cap_width * 0.2), int(cap_y + cap_height * 0.5)), 
                                         (int(cap_x + cap_width * 0.8), int(cap_y + cap_height * 0.5)), 1)
    
    def draw_zombie(x, y, width, height, color):
        # Main zombie body
        pygame.draw.rect(screen, color, (int(x), int(y + height/3), width, height*2/3))
        
        # Zombie head
        pygame.draw.circle(screen, color, (int(x + width/2), int(y + height/4)), int(width/2))
        
        # Zombie eyes
        eye_radius = width/6
        pygame.draw.circle(screen, YELLOW, (int(x + width/3), int(y + height/4)), int(eye_radius))
        pygame.draw.circle(screen, YELLOW, (int(x + width*2/3), int(y + height/4)), int(eye_radius))
        
        # Zombie pupils
        pupil_radius = eye_radius/2
        pygame.draw.circle(screen, BLACK, (int(x + width/3), int(y + height/4)), int(pupil_radius))
        pygame.draw.circle(screen, BLACK, (int(x + width*2/3), int(y + height/4)), int(pupil_radius))
        
        # Zombie mouth
        pygame.draw.rect(screen, BLACK, (int(x + width/4), int(y + height/2), int(width/2), int(height/8)))
        
        # Zombie teeth
        pygame.draw.rect(screen, WHITE, (int(x + width/3), int(y + height/2), int(width/8), int(height/12)))
        pygame.draw.rect(screen, WHITE, (int(x + width/2), int(y + height/2), int(width/8), int(height/12)))
        
        # Zombie arms
        pygame.draw.rect(screen, color, (int(x - width/4), int(y + height/2), int(width/4), int(height/8)))
        pygame.draw.rect(screen, color, (int(x + width), int(y + height/2), int(width/4), int(height/8)))
        
        # Zombie legs
        pygame.draw.rect(screen, DARK_GRAY, (int(x + width/4), int(y + height), int(width/6), int(height/3)))
        pygame.draw.rect(screen, DARK_GRAY, (int(x + width*3/5), int(y + height), int(width/6), int(height/3)))
    
    def create_blood_splat(x, y):
        num_particles = random.randint(10, 20)
        for _ in range(num_particles):
            # Random position near collision
            splat_x = x + random.randint(-20, 20)
            splat_y = y + random.randint(-20, 20)
            # Random size
            size = random.randint(3, 10)
            # Random velocity
            vel_x = random.uniform(-2, 2)
            vel_y = random.uniform(-3, 0)
            # Add to blood splats list [x, y, size, vel_x, vel_y, life]
            blood_splats.append([splat_x, splat_y, size, vel_x, vel_y, blood_duration])
    
    def update_blood_splats():
        for splat in blood_splats:
            # Update position based on velocity
            splat[0] += splat[3]
            splat[1] += splat[4]
            # Add gravity
            splat[4] += 0.1
            # Decrease life
            splat[5] -= 1
    
    def draw_blood_splats():
        for i in reversed(range(len(blood_splats))):
            splat = blood_splats[i]
            if splat[5] <= 0:
                blood_splats.pop(i)
            else:
                # Calculate alpha based on remaining life
                alpha = int(255 * (splat[5] / blood_duration))
                # Create a surface for the blood splat with alpha
                blood_surface = pygame.Surface((splat[2]*2, splat[2]*2), pygame.SRCALPHA)
                # Draw the blood splat on the surface
                pygame.draw.circle(blood_surface, (BLOOD_RED[0], BLOOD_RED[1], BLOOD_RED[2], alpha), 
                                   (splat[2], splat[2]), splat[2])
                # Blit the surface to the screen
                screen.blit(blood_surface, (int(splat[0] - splat[2]), int(splat[1] - splat[2])))
    
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
                    zombies = []
                    fuel_tanks = []
                    blood_splats = []
                    
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
        
        # Update day-night cycle
        if not game_over:
            day_night_timer = (day_night_timer + 1) % cycle_duration
            
            # Check if day or night should change
            if day_night_timer == 0:
                is_night = False
            elif day_night_timer == cycle_duration // 2:
                is_night = True
            
            # Handle transition
            if is_night:
                if day_night_timer < cycle_duration // 2 + transition_duration:
                    # Transitioning to night
                    night_alpha = min(255, night_alpha + 255 / transition_duration)
                else:
                    night_alpha = 255
            else:
                if day_night_timer > cycle_duration - transition_duration:
                    # Transitioning to day
                    night_alpha = max(0, night_alpha - 255 / transition_duration)
                else:
                    night_alpha = 0
        
        # Update torch flicker
        torch_flicker = 5 * math.sin(pygame.time.get_ticks() * 0.01)
                    
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
        
        # Randomly spawn zombies
        if moving and not game_over and random.random() < zombie_spawn_chance:
            spawn_zombie(random.randint(0, 200))
        
        # Randomly spawn fuel tanks 
        if moving and not game_over and random.random() < fuel_spawn_chance:
            spawn_fuel_tank(random.randint(0, 200))
        
        celestial_rays_angle = (celestial_rays_angle + 0.2) % 360
        celestial_pulse_size = 2 * math.sin(pygame.time.get_ticks() * 0.001)
        
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
        
        # Update zombie positions and check for collisions
        i = 0
        while i < len(zombies):
            zombies[i][0] -= current_speed
            
            # Check if car hits zombie using collision rect
            zombie_rect = pygame.Rect(
                zombies[i][0],
                zombies[i][1],
                zombie_width,
                zombie_height
            )
            
            if car_collision_rect.colliderect(zombie_rect):
                score += 1
                # Create blood effect at collision point
                create_blood_splat(zombies[i][0] + zombie_width/2, zombies[i][1] + zombie_height/2)
                zombies.pop(i)
            # Remove zombies that have gone off screen
            elif zombies[i][0] < -zombie_width:
                zombies.pop(i)
            else:
                i += 1
        
        # Update blood splats
        update_blood_splats()
        
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
                
        # Determine sky color based on day/night
        if is_night:
            sky_color = DARK_SKY_BLUE
            terrain_color = NIGHT_GREEN
            ground_color = NIGHT_BROWN
        else:
            sky_color = SKY_BLUE
            terrain_color = GREEN
            ground_color = BROWN
        
        # Fill the background with sky color
        screen.fill(sky_color)
        
        # Draw stars if night
        if night_alpha > 0:
            star_alpha = min(255, night_alpha + 50)  # Stars appear slightly before full night
            for star_x, star_y, star_size in stars:
                # Twinkle effect
                actual_size = star_size * (0.8 + 0.4 * math.sin(pygame.time.get_ticks() * 0.001 + star_x * star_y * 0.01))
                
                # Create star surface with alpha
                star_surface = pygame.Surface((int(actual_size * 2), int(actual_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(star_surface, (255, 255, 255, star_alpha), 
                                  (int(actual_size), int(actual_size)), actual_size)
                screen.blit(star_surface, (star_x - actual_size, star_y - actual_size))
        
        # Draw sun or moon based on time
        if is_night:
            draw_moon(700, 100, 40)
        else:
            draw_sun(700, 100, 50)
        
        # Draw terrain
        pygame.draw.rect(screen, ground_color, (0, 450, width, height - 450))
        
        # Draw the grass
        pygame.draw.polygon(screen, terrain_color, terrain_points + [(width, height), (0, height)])
        
        # Draw zombies
        for zombie_x, zombie_y, zombie_color in zombies:
            draw_zombie(zombie_x, zombie_y, zombie_width, zombie_height, zombie_color)
        
        # Draw blood splats
        draw_blood_splats()
        
        # Draw improved fuel tanks
        for tank_x, tank_y in fuel_tanks:
            draw_fuel_tank(tank_x, tank_y, fuel_tank_width, fuel_tank_height)
        
        car_surface = pygame.Surface((car_width + 50, car_height + car_cabin_height + 20), pygame.SRCALPHA)
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
        car_draw_x = car_pos_x + (car_width + 50) / 2 - rotated_rect.width / 2
        car_draw_y = car_pos_y + (car_height + car_cabin_height + 20) / 2 - rotated_rect.height / 2
        screen.blit(rotated_car, (car_draw_x, car_draw_y))
        
        # Draw torch light at night
        if night_alpha > 0:
            torch_x = car_center_x + math.cos(math.radians(-car_angle)) * 100
            torch_y = car_center_y + math.sin(math.radians(-car_angle)) * 100
        
        # Apply night overlay if transitioning or night
        if night_alpha > 0:
            dark_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 30, night_alpha // 2))  # Bluish tint
            screen.blit(dark_overlay, (0, 0))
        
        # Draw score
        score_text = font.render(f"Zombies: {score}", True, WHITE if night_alpha > 150 else BLACK)
        screen.blit(score_text, (20, 10))
        
        # Draw fuel bar
        pygame.draw.rect(screen, WHITE if night_alpha > 150 else BLACK, (20, 60, 204, 24), 2)
        fuel_width = int(2 * fuel)
        fuel_color = GREEN
        if fuel < 30:
            fuel_color = RED
        elif fuel < 70:
            fuel_color = YELLOW
        pygame.draw.rect(screen, fuel_color, (22, 62, fuel_width, 20))
        
        fuel_text = font.render(f"Fuel", True, WHITE if night_alpha > 150 else BLACK)
        screen.blit(fuel_text, (22, 35))
        
        # Draw day/night indicator
        time_text = font.render("Day" if not is_night else "Night", True, WHITE if night_alpha > 150 else BLACK)
        screen.blit(time_text, (width - 100, 60))
        
        # Instructions
        instruction_font = pygame.font.SysFont(None, 24)
        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            restart_text = font.render("Press R to restart", True, WHITE if night_alpha > 150 else BLACK)
            restart_rect = restart_text.get_rect(center=(width//2, height//2 + 20))
            screen.blit(restart_text, restart_rect)
        else:
            if moving:
                instruction_text = instruction_font.render("SPACE to stop | LEFT/RIGHT to move direction", True, WHITE if night_alpha > 150 else BLACK)
            else:
                instruction_text = instruction_font.render("Press SPACE to start the car", True, WHITE if night_alpha > 150 else BLACK)
            screen.blit(instruction_text, (width - instruction_text.get_width() - 20, 20))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()