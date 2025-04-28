import pygame
import sys
import random


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 150, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    WINDSHIELD = (150, 220, 255)
    HEADLIGHT = (255, 255, 200)
    TAILLIGHT = (255, 0, 0)
    MIRROR = (50, 50, 50)
    YELLOW = (255, 255, 0)
    DARK_BLUE = (25, 25, 112)
    OVERLAY = (0, 0, 0, 180)
    
    TRAFFIC_COLORS = [
        (255, 255, 0),
        (0, 255, 255),
        (255, 165, 0),
        (0, 255, 0),
        (255, 0, 255),
        (165, 42, 42),
        (192, 192, 192)
    ]


class RoadSettings:
    def __init__(self, screen_width):
        self.road_width = 400
        self.lane_width = self.road_width / 4
        self.lane_mark_length = 50
        self.lane_gap = 30
        self.road_left = (screen_width - self.road_width) // 2
        self.road_right = self.road_left + self.road_width


class Car:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, surface):
        car_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, car_rect)
        
        pygame.draw.rect(surface, Colors.WINDSHIELD, 
                         (self.x + 10, self.y + self.height - 45, self.width - 20, 30))
        
        pygame.draw.rect(surface, Colors.TAILLIGHT, 
                         (self.x + 10, self.y + self.height - 15, 10, 10))
        pygame.draw.rect(surface, Colors.TAILLIGHT, 
                         (self.x + self.width - 20, self.y + self.height - 15, 10, 10))
        
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x - 5, self.y + 20, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x + self.width, self.y + 20, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x - 5, self.y + self.height - 45, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x + self.width, self.y + self.height - 45, 5, 25))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class PlayerCar(Car):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, Colors.RED)
        self.speed_x = 7
    
    def move_left(self, road_left):
        self.x = max(self.x - self.speed_x, road_left)
    
    def move_right(self, road_right):
        self.x = min(self.x + self.speed_x, road_right - self.width)
    
    def draw(self, surface):
        car_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, car_rect)
        
        pygame.draw.rect(surface, Colors.WINDSHIELD, 
                         (self.x + 10, self.y + 15, self.width - 20, 30))
        
        pygame.draw.rect(surface, Colors.HEADLIGHT, 
                         (self.x + 10, self.y + 5, 10, 10))
        pygame.draw.rect(surface, Colors.HEADLIGHT, 
                         (self.x + self.width - 20, self.y + 5, 10, 10))
        
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x - 5, self.y + 20, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x + self.width, self.y + 20, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x - 5, self.y + self.height - 45, 5, 25))
        pygame.draw.rect(surface, Colors.MIRROR, 
                         (self.x + self.width, self.y + self.height - 45, 5, 25))
        
        return car_rect


class TrafficVehicle:
    def __init__(self, road_settings, vehicle_width, vehicle_height):
        self.lane = random.randint(0, 3)
        self.vehicle_type = self._determine_vehicle_type()
        
        if self.vehicle_type == "truck":
            self.width = vehicle_width * 1.2
            self.height = vehicle_height * 1.5
            self.color = (100, 100, 100)
            self.speed = random.randint(2, 5)
        else:
            self.width = vehicle_width
            self.height = vehicle_height
            self.color = random.choice(Colors.TRAFFIC_COLORS)
            self.speed = random.randint(3, 7)
            
        self.x = (road_settings.road_left + 
             self.lane * road_settings.lane_width + 
             (road_settings.lane_width - self.width) // 2)
        
        self.y = -self.height
    
    def _determine_vehicle_type(self):
        return "truck" if random.random() < 0.3 else "car"
    
    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        vehicle_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, vehicle_rect)
        
        if self.vehicle_type == "truck":
            cab_height = self.height * 0.3
            cab_width = self.width * 0.8
            cab_x = self.x + (self.width - cab_width) // 2
            cab_y = self.y + self.height - cab_height
            
            pygame.draw.rect(surface, (80, 80, 80), 
                            (cab_x, cab_y, cab_width, cab_height))
            
            pygame.draw.rect(surface, Colors.WINDSHIELD, 
                            (cab_x + 10, cab_y + 10, cab_width - 20, cab_height - 20))
            
            pygame.draw.rect(surface, (120, 120, 120),
                            (self.x + 5, self.y + 5, self.width - 10, self.height - cab_height - 10))
        else:
            pygame.draw.rect(surface, Colors.WINDSHIELD, 
                            (self.x + 10, self.y + self.height - 45, self.width - 20, 30))
            
            pygame.draw.rect(surface, Colors.TAILLIGHT, 
                            (self.x + 10, self.y + self.height - 15, 10, 10))
            pygame.draw.rect(surface, Colors.TAILLIGHT, 
                            (self.x + self.width - 20, self.y + self.height - 15, 10, 10))
            
            pygame.draw.rect(surface, Colors.MIRROR, 
                            (self.x - 5, self.y + 20, 5, 25))
            pygame.draw.rect(surface, Colors.MIRROR, 
                            (self.x + self.width, self.y + 20, 5, 25))
            pygame.draw.rect(surface, Colors.MIRROR, 
                            (self.x - 5, self.y + self.height - 45, 5, 25))
            pygame.draw.rect(surface, Colors.MIRROR, 
                            (self.x + self.width, self.y + self.height - 45, 5, 25))


class LaneMarking:
    def __init__(self, x, y, length):
        self.x = x
        self.y = y
        self.length = length
    
    def update(self, scroll_speed, screen_height, total_height):
        new_y = (self.y + scroll_speed) % total_height
        return new_y
    
    def draw(self, surface, screen_height):
        if self.y < screen_height:
            pygame.draw.line(surface, Colors.WHITE, (self.x, self.y), 
                             (self.x, self.y + self.length), 2)


class Road:
    def __init__(self, road_settings, screen_height):
        self.settings = road_settings
        self.screen_height = screen_height
        self.lane_markings = []
        
        self._create_lane_markings()
    
    def _create_lane_markings(self):
        for lane in range(1, 4):
            lane_x = self.settings.road_left + lane * self.settings.lane_width
            y_offset = 0
            
            while y_offset < self.screen_height:
                self.lane_markings.append(
                    LaneMarking(lane_x, y_offset, self.settings.lane_mark_length)
                )
                y_offset += self.settings.lane_mark_length + self.settings.lane_gap
    
    def update(self, scroll_speed):
        new_markings = []
        total_height = self.screen_height + self.settings.lane_mark_length + self.settings.lane_gap
        
        for marking in self.lane_markings:
            new_y = marking.update(scroll_speed, self.screen_height, total_height)
            new_markings.append(LaneMarking(marking.x, new_y, marking.length))
        
        self.lane_markings = new_markings
    
    def draw(self, surface):
        road_rect = pygame.Rect(self.settings.road_left, 0, 
                                self.settings.road_width, self.screen_height)
        pygame.draw.rect(surface, Colors.BLACK, road_rect)
        
        pygame.draw.line(surface, Colors.WHITE, 
                         (self.settings.road_left, 0), 
                         (self.settings.road_left, self.screen_height), 2)
        pygame.draw.line(surface, Colors.WHITE, 
                         (self.settings.road_right, 0), 
                         (self.settings.road_right, self.screen_height), 2)
        
        for marking in self.lane_markings:
            marking.draw(surface, self.screen_height)


class GameEngine:
    def __init__(self):
        pygame.init()
        
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Car Avoidance Game")
        
        self.car_width = 60
        self.car_height = 100
        self.road_settings = RoadSettings(self.screen_width)
        
        player_x = (self.road_settings.road_left + 
                     (self.road_settings.road_width - self.car_width) // 2)
        player_y = self.screen_height - self.car_height - 50
        self.player = PlayerCar(player_x, player_y, self.car_width, self.car_height)
        
        self.road = Road(self.road_settings, self.screen_height)
        
        self.traffic_cars = []
        
        self.reset_game()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.show_instructions = True
        self.instruction_start_time = pygame.time.get_ticks()
        self.instruction_duration = 5000
        
        self.sample_car = TrafficVehicle(self.road_settings, self.car_width, self.car_height)
        self.sample_car.vehicle_type = "car"
        self.sample_car.x = 200
        self.sample_car.y = 320
        
        self.sample_truck = TrafficVehicle(self.road_settings, self.car_width, self.car_height)
        self.sample_truck.vehicle_type = "truck"
        self.sample_truck.x = 500
        self.sample_truck.y = 320
    
    def reset_game(self):
        self.traffic_cars = []
        self.scroll_speed = 0
        self.max_scroll_speed = 10
        self.acceleration = 0.25
        self.deceleration = 0.1
        self.score = 0
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.game_over = False
        self.show_instructions = True
        self.instruction_start_time = pygame.time.get_ticks()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_SPACE and self.show_instructions:
                    self.show_instructions = False
    
    def handle_player_input(self):
        if not self.game_over and not self.show_instructions:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_UP]:
                self.scroll_speed = min(self.scroll_speed + self.acceleration, 
                                         self.max_scroll_speed)
            else:
                self.scroll_speed = max(self.scroll_speed - self.deceleration, 0)
            
            if keys[pygame.K_LEFT]:
                self.player.move_left(self.road_settings.road_left)
            if keys[pygame.K_RIGHT]:
                self.player.move_right(self.road_settings.road_right)
    
    def update_traffic(self):
        if not self.game_over and not self.show_instructions:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.traffic_cars.append(
                    TrafficVehicle(self.road_settings, self.car_width, self.car_height)
                )
                self.spawn_timer = 0
                self.spawn_delay = max(20, 60 - self.score // 500)
        
        for vehicle in self.traffic_cars[:]:
            vehicle.update(self.scroll_speed)
            
            if vehicle.y > self.screen_height:
                self.traffic_cars.remove(vehicle)
                if not self.game_over and not self.show_instructions:
                    if vehicle.vehicle_type == "truck":
                        self.score += 25
                    else:
                        self.score += 10
    
    def check_collisions(self):
        if not self.game_over and not self.show_instructions:
            player_rect = self.player.get_rect()
            
            for car in self.traffic_cars:
                if player_rect.colliderect(car.get_rect()):
                    self.game_over = True
                    self.scroll_speed = 0
                    return True
        
        return False
    
    def update_score(self):
        if not self.game_over and not self.show_instructions:
            self.score += int(self.scroll_speed)
    
    def check_instruction_timeout(self):
        if self.show_instructions:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.instruction_start_time
            
            if elapsed_time >= self.instruction_duration:
                self.show_instructions = False
    
    def update(self):
        self.handle_events()
        self.check_instruction_timeout()
        
        if not self.show_instructions:
            self.handle_player_input()
            self.road.update(self.scroll_speed)
            self.update_traffic()
            self.check_collisions()
            self.update_score()
    
    def render_instructions(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        self.screen.blit(overlay, (0, 0))
        
        title_font = pygame.font.SysFont(None, 80)
        instruction_font = pygame.font.SysFont(None, 32)
        countdown_font = pygame.font.SysFont(None, 48)
        
        title_text = title_font.render("CAR AVOIDANCE", True, Colors.YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        
        instruction1 = instruction_font.render("Controls: Use left/right keys to move your car", True, Colors.WHITE)
        instruction2 = instruction_font.render("Press Up key to accelerate", True, Colors.WHITE)
        instruction3 = instruction_font.render("Vehicle Types:", True, Colors.WHITE)
        instruction4 = instruction_font.render("- Regular Cars: 10 points", True, Colors.WHITE)
        instruction5 = instruction_font.render("- Trucks (Larger vehicles): 25 points", True, Colors.WHITE)
        
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.instruction_start_time
        remaining_time = max(0, self.instruction_duration - elapsed_time)
        remaining_seconds = int(remaining_time / 1000) + 1
        
        skip_text = instruction_font.render("Press SPACE to skip", True, Colors.YELLOW)
        countdown_text = countdown_font.render(f"{remaining_seconds}", True, Colors.WHITE)
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(instruction1, (self.screen_width // 2 - instruction1.get_width() // 2, 160))
        self.screen.blit(instruction2, (self.screen_width // 2 - instruction2.get_width() // 2, 200))
        self.screen.blit(instruction3, (self.screen_width // 2 - instruction3.get_width() // 2, 260))
        self.screen.blit(instruction4, (self.screen_width // 2 - instruction4.get_width() // 2, 300))
        self.screen.blit(instruction5, (self.screen_width // 2 - instruction5.get_width() // 2, 340))
        
        self.screen.blit(skip_text, (self.screen_width // 2 - skip_text.get_width() // 2, 500))
        self.screen.blit(countdown_text, (self.screen_width // 2 - countdown_text.get_width() // 2, 440))
    
    def render(self):
        self.screen.fill(Colors.GREEN)
        self.road.draw(self.screen)
        
        for car in self.traffic_cars:
            car.draw(self.screen)
        
        self.player.draw(self.screen)
        
        self.render_ui()
        
        if self.show_instructions:
            self.render_instructions()
        
        pygame.display.flip()
    
    def render_ui(self):
        font = pygame.font.SysFont(None, 36)
        
        speed_text = font.render(f"Speed: {int(self.scroll_speed * 10)} km/h", 
                                  True, Colors.WHITE)
        score_text = font.render(f"Score: {self.score}", True, Colors.WHITE)
        self.screen.blit(speed_text, (20, 20))
        self.screen.blit(score_text, (20, 60))
        
        if self.game_over and not self.show_instructions:
            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, Colors.BLUE)
            restart_text = font.render("Press R to restart", True, Colors.WHITE)
            
            text_rect = game_over_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 50)
            )
            restart_rect = restart_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 50)
            )
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()