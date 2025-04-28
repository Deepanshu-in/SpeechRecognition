import pygame
import random
import sys

class Constants:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    
    BLUE = (65, 105, 225)
    GREEN = (34, 139, 34)
    BROWN_LIGHT = (205, 133, 63)
    DARK_BROWN = (139, 69, 19)
    ROCK_COLOR = (105, 105, 105)
    DARK_ROCK = (64, 64, 64)
    WHITE = (255, 255, 255)
    LIGHT_BLUE = (173, 216, 230)
    RED = (255, 0, 0)
    SKY_BLUE = (200, 230, 255)
    BLACK = (0, 0, 0)
    
    RIVER_WIDTH_RATIO = 0.6
    SCROLL_SPEED_BASE = 2.0
    BOAT_SPEED = 4
    FPS = 60


class Particle:
    def __init__(self, left_bank: int, right_bank: int, height: int):
        self.x = random.randint(left_bank + 10, right_bank - 10)
        self.y = random.randint(0, height)
        self.size = random.randint(2, 5)
    
    def update(self, speed: float, height: int):
        self.y += speed
        
        if self.y > height:
            self.y = 0
            self.size = random.randint(2, 5)
    
    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Rock:
    def __init__(self, left_bank: int, right_bank: int, base_speed: float):
        self.x = random.randint(left_bank + 30, right_bank - 30)
        self.y = -50
        self.width = random.randint(20, 40)
        self.height = random.randint(20, 40)
        self.speed = base_speed
        self.velocity_multiplier = random.uniform(0.9, 1.1)
        self.hitbox = pygame.Rect(
            self.x - self.width//2 + 5,
            self.y - self.height//2 + 5,
            self.width - 10,
            self.height - 10
        )
    
    def update(self, speed_multiplier: float):
        self.y += self.speed * self.velocity_multiplier * speed_multiplier
        self.hitbox.x = self.x - self.width//2 + 5
        self.hitbox.y = self.y - self.height//2 + 5
    
    def is_off_screen(self, height: int) -> bool:
        return self.y > height + 50
    
    def draw(self, surface):
        points = []
        for i in range(8):
            angle = i * (2 * 3.14159 / 8)
            radius = random.uniform(self.width * 0.5, self.width * 0.7)
            point_x = self.x + radius * pygame.math.Vector2(1, 0).rotate(angle * 180 / 3.14159).x
            point_y = self.y + radius * pygame.math.Vector2(1, 0).rotate(angle * 180 / 3.14159).y
            points.append((point_x, point_y))
        
        pygame.draw.polygon(surface, Constants.ROCK_COLOR, points)
        
        for _ in range(3):
            detail_x = self.x + random.randint(-self.width//3, self.width//3)
            detail_y = self.y + random.randint(-self.height//3, self.height//3)
            detail_size = random.randint(2, 5)
            pygame.draw.circle(surface, Constants.DARK_ROCK, (int(detail_x), int(detail_y)), detail_size)
        
        for _ in range(4):
            highlight_x = self.x + random.randint(-self.width//2 - 5, self.width//2 + 5)
            highlight_y = self.y + random.randint(-self.height//2 - 5, self.height//2 + 5)
            pygame.draw.circle(surface, Constants.WHITE, (int(highlight_x), int(highlight_y)), 2)


class Log:
    def __init__(self, left_bank: int, right_bank: int, base_speed: float):
        self.x = random.randint(left_bank + 30, right_bank - 30)
        self.y = -50
        self.width = random.randint(80, 120)
        self.height = random.randint(20, 30)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-0.5, 0.5)
        self.speed = base_speed
        self.velocity_multiplier = random.uniform(0.8, 1.0)
        self.sideways_speed = random.uniform(-0.5, 0.5)
        self.hitbox = pygame.Rect(
            self.x - self.width//2 + 5,
            self.y - self.height//2 + 5,
            self.width - 10,
            self.height - 10
        )
    
    def update(self, speed_multiplier: float, left_bank: int, right_bank: int):
        self.y += self.speed * self.velocity_multiplier * speed_multiplier
        self.x += self.sideways_speed * speed_multiplier
        self.rotation += self.rotation_speed
        
        if self.x < left_bank + self.width//2:
            self.x = left_bank + self.width//2
            self.sideways_speed = abs(self.sideways_speed)
        elif self.x > right_bank - self.width//2:
            self.x = right_bank - self.width//2
            self.sideways_speed = -abs(self.sideways_speed)
            
        self.hitbox.x = self.x - self.width//2 + 5
        self.hitbox.y = self.y - self.height//2 + 5
    
    def is_off_screen(self, height: int) -> bool:
        return self.y > height + 50
    
    def draw(self, surface):
        log_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        pygame.draw.ellipse(log_surface, Constants.DARK_BROWN, (0, 0, self.width, self.height))
        
        for i in range(3, self.width - 3, 10):
            pygame.draw.line(log_surface, (self.darken_color(Constants.DARK_BROWN, 20)), 
                           (i, 5), (i, self.height - 5), 2)
        
        for i in range(3):
            knot_x = random.randint(self.width//4, 3*self.width//4)
            knot_y = random.randint(self.height//4, 3*self.height//4)
            knot_size = random.randint(3, 6)
            pygame.draw.circle(log_surface, self.darken_color(Constants.DARK_BROWN, 30), 
                             (knot_x, knot_y), knot_size)
            pygame.draw.circle(log_surface, Constants.BLACK, (knot_x, knot_y), knot_size - 2)
        
        rotated_log = pygame.transform.rotate(log_surface, self.rotation)
        new_rect = rotated_log.get_rect(center=(self.x, self.y))
        surface.blit(rotated_log, new_rect.topleft)
    
    def darken_color(self, color, amount):
        r = max(0, color[0] - amount)
        g = max(0, color[1] - amount)
        b = max(0, color[2] - amount)
        return (r, g, b)


class EnemyBoat:
    def __init__(self, left_bank: int, right_bank: int, base_speed: float):
        self.width = 40
        self.height = 70
        self.x = random.randint(left_bank + self.width, right_bank - self.width)
        self.y = -self.height
        self.speed = base_speed
        self.velocity_multiplier = random.uniform(0.7, 0.9)
        self.horizontal_speed = random.choice([-1, 1]) * random.uniform(1.0, 2.0)
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(120, 240)
        self.hitbox = pygame.Rect(
            self.x - self.width//2 + 8,
            self.y - self.height//2 + 10,
            self.width - 16,
            self.height - 20
        )
        self.color = random.choice([
            (139, 69, 19),   
            (160, 82, 45),    
            (165, 42, 42),   
            (128, 0, 0),      
            (220, 20, 60)   
        ])
    
    def update(self, speed_multiplier: float, left_bank: int, right_bank: int):
        self.y += self.speed * self.velocity_multiplier * speed_multiplier
        self.x += self.horizontal_speed
        
        self.direction_change_timer += 1
        if self.direction_change_timer >= self.direction_change_interval:
            self.horizontal_speed *= -1
            self.direction_change_timer = 0
            self.direction_change_interval = random.randint(60, 180)
        
        if self.x < left_bank + self.width//2 + 10:
            self.x = left_bank + self.width//2 + 10
            self.horizontal_speed = abs(self.horizontal_speed)
        elif self.x > right_bank - self.width//2 - 10:
            self.x = right_bank - self.width//2 - 10
            self.horizontal_speed = -abs(self.horizontal_speed)
            
        self.hitbox.x = self.x - self.width//2 + 8
        self.hitbox.y = self.y - self.height//2 + 10
    
    def is_off_screen(self, height: int) -> bool:
        return self.y > height + self.height
    
    def draw(self, surface):
        boat_points = [
            (self.x - self.width//2, self.y + self.height//2 - 10),
            (self.x - self.width//2 + 5, self.y - self.height//2 + 10),
            (self.x, self.y - self.height//2),
            (self.x + self.width//2 - 5, self.y - self.height//2 + 10),
            (self.x + self.width//2, self.y + self.height//2 - 10),
            (self.x, self.y + self.height//2),
        ]
        
        pygame.draw.polygon(surface, self.color, boat_points)
        
        for i in range(1, 5):
            beam_y = self.y - self.height//2 + (self.height * i)//5
            left_x = self.x - self.width//2 + 5 if i == 1 else self.x - self.width//2 + 3
            right_x = self.x + self.width//2 - 5 if i == 1 else self.x + self.width//2 - 3
            
            if i <= 2:
                mid_offset = 12 - i * 4
                mid_x = self.x
                mid_y = beam_y - mid_offset
                
                pygame.draw.line(surface, Constants.DARK_BROWN, (left_x, beam_y), (mid_x, mid_y), 2)
                pygame.draw.line(surface, Constants.DARK_BROWN, (mid_x, mid_y), (right_x, beam_y), 2)
            else:
                pygame.draw.line(surface, Constants.DARK_BROWN, (left_x, beam_y), (right_x, beam_y), 2)
        
        pygame.draw.line(surface, Constants.DARK_BROWN, 
                       (self.x, self.y - self.height//2 + 5), 
                       (self.x, self.y + self.height//2 - 5), 2)
        
        bench_width = self.width - 10
        pygame.draw.rect(surface, Constants.DARK_BROWN, 
                       (self.x - bench_width//2, self.y - 5, bench_width, 10))
        
        for i in range(2):
            offset = 5 + i*5
            pygame.draw.arc(surface, Constants.WHITE, 
                           (self.x - 12 - i*4, self.y + self.height//2 + offset, 
                            24 + i*8, 8), 
                           0, 3.14, 2)


class Boat:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 50
        self.height = 90
        self.x = screen_width // 2
        self.y = screen_height * 0.8
        self.speed = Constants.BOAT_SPEED
        
        self.left_angle = 0
        self.right_angle = 0
        self.left_direction = 1
        self.right_direction = 1
        
        self.hit = False
        
        self.update_hitbox()
    
    def update_hitbox(self):
        self.hitbox = pygame.Rect(
            self.x - self.width//2 + 10,
            self.y - self.height//2 + 15,
            self.width - 20,
            self.height - 25
        )
    
    def move_left(self):
        if self.hit:
            return
            
        self.x -= self.speed
        self.left_angle += self.left_direction * 5
        
        if abs(self.left_angle) > 30:
            self.left_direction *= -1
    
    def move_right(self):
        if self.hit:
            return
            
        self.x += self.speed
        self.right_angle += self.right_direction * 5
        
        if abs(self.right_angle) > 30:
            self.right_direction *= -1
    
    def update_paddle_resting(self, is_left: bool):
        if is_left:
            if self.left_angle != 0:
                self.left_angle = max(-5, min(5, self.left_angle - self.left_direction * 3))
                if -5 <= self.left_angle <= 5:
                    self.left_angle = 0
                    self.left_direction = 1
        else:
            if self.right_angle != 0:
                self.right_angle = max(-5, min(5, self.right_angle - self.right_direction * 3))
                if -5 <= self.right_angle <= 5:
                    self.right_angle = 0
                    self.right_direction = 1
    
    def check_boundary(self, left_limit: int, right_limit: int):
        min_x = left_limit + self.width // 2 + 10
        max_x = right_limit - self.width // 2 - 10
        
        if self.x < min_x:
            self.x = min_x
        if self.x > max_x:
            self.x = max_x
    
    def update(self, left_pressed: bool, right_pressed: bool, left_bank: int, right_bank: int):
        if not self.hit:
            if left_pressed:
                self.move_left()
            else:
                self.update_paddle_resting(True)
                
            if right_pressed:
                self.move_right()
            else:
                self.update_paddle_resting(False)
            
            self.check_boundary(left_bank, right_bank)
        
        self.update_hitbox()
    
    def check_collision(self, obstacles) -> bool:
        if self.hit:
            return True
            
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle.hitbox):
                self.hit = True
                return True
        
        return False
    
    def reset(self, screen_width: int, screen_height: int):
        self.x = screen_width // 2
        self.y = screen_height * 0.8
        self.hit = False
        self.left_angle = 0
        self.right_angle = 0
        self.left_direction = 1
        self.right_direction = 1
        self.update_hitbox()
    
    def draw_paddle(self, surface, is_left: bool):
        if self.hit:
            return
            
        paddle_length = 60
        
        if is_left:
            paddle_x = self.x - self.width//2 - 5
            paddle_y = self.y
            angle = self.left_angle
        else:
            paddle_x = self.x + self.width//2 + 5
            paddle_y = self.y
            angle = self.right_angle
        
        if is_left:
            end_x = paddle_x - paddle_length * pygame.math.Vector2(1, 0).rotate(angle).x
            end_y = paddle_y - paddle_length * pygame.math.Vector2(1, 0).rotate(angle).y
        else:
            end_x = paddle_x + paddle_length * pygame.math.Vector2(1, 0).rotate(angle).x
            end_y = paddle_y - paddle_length * pygame.math.Vector2(1, 0).rotate(angle).y
        
        pygame.draw.line(surface, Constants.DARK_BROWN, (paddle_x, paddle_y), (end_x, end_y), 3)
        
        if is_left:
            blade_x = end_x - 10
            blade_y = end_y
        else:
            blade_x = end_x + 10
            blade_y = end_y
            
        blade_points = [
            (end_x - 5 if is_left else end_x + 5, end_y - 10),
            (blade_x, blade_y),
            (end_x - 5 if is_left else end_x + 5, end_y + 10)
        ]
        pygame.draw.polygon(surface, Constants.DARK_BROWN, blade_points)
    
    def draw(self, surface):
        boat_points = [
            (self.x - self.width//2, self.y + self.height//2 - 10),
            (self.x - self.width//2 + 5, self.y - self.height//2 + 10),
            (self.x, self.y - self.height//2),
            (self.x + self.width//2 - 5, self.y - self.height//2 + 10),
            (self.x + self.width//2, self.y + self.height//2 - 10),
            (self.x, self.y + self.height//2),
        ]
        
        color = Constants.RED if self.hit else Constants.BROWN_LIGHT
        pygame.draw.polygon(surface, color, boat_points)
        
        for i in range(1, 5):
            beam_y = self.y - self.height//2 + (self.height * i)//5
            left_x = self.x - self.width//2 + 5 if i == 1 else self.x - self.width//2 + 3
            right_x = self.x + self.width//2 - 5 if i == 1 else self.x + self.width//2 - 3
            
            if i <= 2:
                mid_offset = 15 - i * 5
                mid_x = self.x
                mid_y = beam_y - mid_offset
                
                pygame.draw.line(surface, Constants.DARK_BROWN, (left_x, beam_y), (mid_x, mid_y), 2)
                pygame.draw.line(surface, Constants.DARK_BROWN, (mid_x, mid_y), (right_x, beam_y), 2)
            else:
                pygame.draw.line(surface, Constants.DARK_BROWN, (left_x, beam_y), (right_x, beam_y), 2)
        
        pygame.draw.line(surface, Constants.DARK_BROWN, 
                       (self.x, self.y - self.height//2 + 5), 
                       (self.x, self.y + self.height//2 - 5), 2)
        
        bench_width = self.width - 10
        pygame.draw.rect(surface, Constants.DARK_BROWN, 
                      (self.x - bench_width//2, self.y - 5, bench_width, 10))
        
        self.draw_paddle(surface, True)
        self.draw_paddle(surface, False)
        
        for i in range(3):
            offset = 5 + i*5
            pygame.draw.arc(surface, Constants.WHITE, 
                           (self.x - 15 - i*5, self.y + self.height//2 + offset, 
                            30 + i*10, 10), 
                           0, 3.14, 2)


class River:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.river_width = int(screen_width * Constants.RIVER_WIDTH_RATIO)
        self.left_bank = int((screen_width - self.river_width) / 2)
        self.right_bank = self.left_bank + self.river_width
        
        self.particles = []
        for _ in range(200):
            particle = Particle(self.left_bank, self.right_bank, screen_height)
            self.particles.append(particle)
    
    def update(self, scroll_speed: float):
        for particle in self.particles:
            particle.update(scroll_speed, self.screen_height)
            if particle.y == 0:
                particle.x = random.randint(self.left_bank + 10, self.right_bank - 10)
    
    def draw(self, surface):
        surface.fill(Constants.SKY_BLUE)
        
        pygame.draw.rect(surface, Constants.GREEN, (0, 0, self.left_bank, self.screen_height))
        pygame.draw.rect(surface, Constants.GREEN, (self.right_bank, 0, 
                                                  self.screen_width - self.right_bank, 
                                                  self.screen_height))
        
        pygame.draw.rect(surface, Constants.BLUE, 
                       (self.left_bank, 0, self.river_width, self.screen_height))
        
        for particle in self.particles:
            particle.draw(surface, Constants.LIGHT_BLUE)


class ObstacleManager:
    def __init__(self, left_bank: int, right_bank: int, base_speed: float):
        self.left_bank = left_bank
        self.right_bank = right_bank
        self.base_speed = base_speed
        self.rocks = []
        self.logs = []
        self.enemy_boats = []
        self.rock_timer = 0
        self.log_timer = 0
        self.enemy_boat_timer = 0
        self.rock_spawn_interval = 60
        self.log_spawn_interval = 180
        self.enemy_boat_spawn_interval = 300
    
    def update(self, speed_multiplier: float, screen_height: int):
        for rock in self.rocks[:]:
            rock.update(speed_multiplier)
            if rock.is_off_screen(screen_height):
                self.rocks.remove(rock)
        
        for log in self.logs[:]:
            log.update(speed_multiplier, self.left_bank, self.right_bank)
            if log.is_off_screen(screen_height):
                self.logs.remove(log)
                
        for enemy_boat in self.enemy_boats[:]:
            enemy_boat.update(speed_multiplier, self.left_bank, self.right_bank)
            if enemy_boat.is_off_screen(screen_height):
                self.enemy_boats.remove(enemy_boat)
        
        self.rock_timer += 1
        if self.rock_timer >= self.rock_spawn_interval:
            new_rock = Rock(self.left_bank, self.right_bank, self.base_speed)
            self.rocks.append(new_rock)
            self.rock_timer = 0
            self.rock_spawn_interval = random.randint(50, 120)
            
        self.log_timer += 1
        if self.log_timer >= self.log_spawn_interval:
            new_log = Log(self.left_bank, self.right_bank, self.base_speed)
            self.logs.append(new_log)
            self.log_timer = 0
            self.log_spawn_interval = random.randint(150, 250)
            
        self.enemy_boat_timer += 1
        if self.enemy_boat_timer >= self.enemy_boat_spawn_interval:
            new_enemy_boat = EnemyBoat(self.left_bank, self.right_bank, self.base_speed)
            self.enemy_boats.append(new_enemy_boat)
            self.enemy_boat_timer = 0
            self.enemy_boat_spawn_interval = random.randint(250, 400)
    
    def get_all_obstacles(self):
        return self.rocks + self.logs + self.enemy_boats
    
    def draw(self, surface):
        for rock in self.rocks:
            rock.draw(surface)
            
        for log in self.logs:
            log.draw(surface)
            
        for enemy_boat in self.enemy_boats:
            enemy_boat.draw(surface)
    
    def reset(self):
        self.rocks = []
        self.logs = []
        self.enemy_boats = []
        self.rock_timer = 0
        self.log_timer = 0
        self.enemy_boat_timer = 0
        self.rock_spawn_interval = 60
        self.log_spawn_interval = 180
        self.enemy_boat_spawn_interval = 300


class GameUI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.main_font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 24)
    
    def draw_score(self, surface, score: int):
        score_text = self.main_font.render(f"Score: {score}", True, Constants.BLACK)
        surface.blit(score_text, (10, 10))
    
    def draw_instructions(self, surface):
        instructions = [
            "UP ARROW: Move forward",
            "LEFT/RIGHT ARROWS: Move boat sideways",
            "SPACE: Pause/Resume game",
            "Avoid rocks, logs, and other boats!"
        ]
        
        for i, text in enumerate(instructions):
            rendered_text = self.small_font.render(text, True, Constants.BLACK)
            surface.blit(rendered_text, (10, 50 + i*25))
    
    def draw_pause_screen(self, surface):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        pause_text = self.main_font.render("GAME PAUSED", True, Constants.WHITE)
        surface.blit(pause_text, 
                   (self.screen_width//2 - pause_text.get_width()//2, 
                    self.screen_height//2 - 25))
        
        resume_text = self.main_font.render("Press SPACE to resume", True, Constants.WHITE)
        surface.blit(resume_text, 
                   (self.screen_width//2 - resume_text.get_width()//2, 
                    self.screen_height//2 + 25))
                    
    def draw_intro_screen(self, surface, time_remaining):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title_text = self.title_font.render("RIVER BOAT OBSTACLE GAME", True, Constants.WHITE)
        surface.blit(title_text, 
                   (self.screen_width//2 - title_text.get_width()//2, 
                    self.screen_height//6))
                    
        instructions = [
            "Use ARROW KEYS to control your boat:",
            "- UP ARROW: Move forward faster",
            "- LEFT/RIGHT ARROWS: Move boat sideways",
            "",
            "Obstacles to avoid:",
            "- Rocks: Stationary obstacles",
            "- Logs: Rotating wooden logs that drift sideways",
            "- Enemy Boats: Colored boats that move unpredictably",
            "",
            "Press SPACE during gameplay to pause the game",
            "",
            f"Game starts in {time_remaining} seconds...",
            "Press SPACE to start immediately"
        ]
        
        for i, text in enumerate(instructions):
            rendered_text = self.main_font.render(text, True, Constants.WHITE)
            surface.blit(rendered_text, 
                       (self.screen_width//2 - rendered_text.get_width()//2, 
                        self.screen_height//3 + i*36))
    
    def draw_game_over(self, surface, score: int, high_score: int):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        game_over_text = self.main_font.render("GAME OVER", True, Constants.RED)
        surface.blit(game_over_text, 
                   (self.screen_width//2 - game_over_text.get_width()//2, 
                    self.screen_height//2 - 50))
        
        score_text = self.main_font.render(f"Score: {score}", True, Constants.WHITE)
        surface.blit(score_text, 
                   (self.screen_width//2 - score_text.get_width()//2, 
                    self.screen_height//2))
        
        high_score_text = self.main_font.render(f"High Score: {high_score}", True, Constants.WHITE)
        surface.blit(high_score_text, 
                   (self.screen_width//2 - high_score_text.get_width()//2, 
                    self.screen_height//2 + 40))
        
        restart_text = self.main_font.render("Press SPACE to play again", True, Constants.WHITE)
        surface.blit(restart_text, 
                   (self.screen_width//2 - restart_text.get_width()//2, 
                    self.screen_height//2 + 100))


class RiverBoatGame:
    def __init__(self):
        pygame.init()
        
        self.screen_width = Constants.SCREEN_WIDTH
        self.screen_height = Constants.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("River Boat Obstacle Game")
        
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.paused = False
        self.showing_intro = True
        self.intro_timer = 5 * Constants.FPS 
        
        self.river = River(self.screen_width, self.screen_height)
        self.boat = Boat(self.screen_width, self.screen_height)
        self.obstacle_manager = ObstacleManager(
            self.river.left_bank, 
            self.river.right_bank, 
            Constants.SCROLL_SPEED_BASE
        )
        self.ui = GameUI(self.screen_width, self.screen_height)
        
        self.up_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.up_pressed = True
                elif event.key == pygame.K_LEFT:
                    self.left_pressed = True
                elif event.key == pygame.K_RIGHT:
                    self.right_pressed = True
                elif event.key == pygame.K_SPACE:
                    if self.showing_intro:
                        self.showing_intro = False
                    elif self.game_over:
                        self.reset_game()
                    else:
                        self.paused = not self.paused
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.up_pressed = False
                elif event.key == pygame.K_LEFT:
                    self.left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    self.right_pressed = False
    
    def update(self):
        if self.showing_intro:
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.showing_intro = False
                
        elif not self.game_over and not self.paused:
            scroll_speed_multiplier = 2.5 if self.up_pressed else 1.0
            scroll_speed = Constants.SCROLL_SPEED_BASE * scroll_speed_multiplier
            
            self.river.update(scroll_speed)
            self.boat.update(
                self.left_pressed, 
                self.right_pressed, 
                self.river.left_bank, 
                self.river.right_bank
            )
            self.obstacle_manager.update(scroll_speed_multiplier, self.screen_height)
            
            if self.boat.check_collision(self.obstacle_manager.get_all_obstacles()):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
            
            self.score += 1
    
    def draw(self):
        self.river.draw(self.screen)
        self.obstacle_manager.draw(self.screen)
        self.boat.draw(self.screen)
        
        self.ui.draw_score(self.screen, self.score)
        
        if self.showing_intro:
            seconds_remaining = self.intro_timer // Constants.FPS + 1
            self.ui.draw_intro_screen(self.screen, seconds_remaining)
        elif not self.game_over:
            self.ui.draw_instructions(self.screen)
            if self.paused:
                self.ui.draw_pause_screen(self.screen)
        else:
            self.ui.draw_game_over(self.screen, self.score, self.high_score)
        
        pygame.display.flip()
    
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.boat.reset(self.screen_width, self.screen_height)
        self.obstacle_manager.reset()
        self.showing_intro = True
        self.intro_timer = 5 * Constants.FPS
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Constants.FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = RiverBoatGame()
    game.run()