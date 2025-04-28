import pygame
import random
import math

class Star:
    def __init__(self, rect, colour):
        self.rect = rect
        self.colour = colour

    def draw(self, display):
        pygame.draw.rect(display, self.colour, self.rect)


class Starscape:
    def __init__(self, boundary):
        self.amount = 350
        self.boundary = pygame.Rect(boundary)
        self._generate()

    def _generate(self):
        self.stars = []
        for s in range(self.amount):
            x = random.randint(0, self.boundary.width)
            y = random.randint(0, self.boundary.height)
            size = random.choice([2, 2, 2, 2, 3, 4])
            rect = [x, y, size, size]
            colour = (255, 255, 255)
            self.stars.append(Star(rect, colour))

    def draw(self, display):
        for star in self.stars:
            pygame.draw.rect(display, star.colour, star.rect)


class CavePiece:
    def __init__(self, rect, colour):
        self.rect = pygame.Rect(rect)
        self.colour = colour

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)

    def draw(self, display):
        pygame.draw.rect(display, self.colour, self.rect)


class Cave:
    def __init__(self, boundary, size, colour):
        self.boundary = pygame.Rect(boundary)
        self.size = size
        self.scale = [round(self.boundary.width / self.size), round(self.boundary.height / self.size)]
        self.colour = colour
        self.pieces = []
        self.gap_minimum = 10
        self.gap_maximum = self.scale[1] - 2
        self.piece_difference = 1
        
        length = round(self.boundary.width/self.size)
        for square in range(length):
            self.spawn_cave()
            self.move([-self.size, 0])

    def update(self, movement, player):
        self.move(movement)
        self.check_delete()
        self.check_spawn()
        return self.check_wall_hit(player)

    def move(self, movement):
        for wall in self.pieces:
            wall.move(movement[0], movement[1])

    def check_delete(self):
        if not self.boundary.colliderect(self.pieces[0]):
            self.pieces.pop(0)

    def check_spawn(self):
        if self.boundary.colliderect(self.pieces[len(self.pieces)-1]):
            self.spawn_cave()

    def spawn_cave(self):
        if len(self.pieces) == 0:
            x = self.boundary.right
            gap_size = random.randint(self.gap_minimum, self.gap_maximum)
            leftover = self.scale[1] - gap_size
            top = round(leftover) / 2
        else:
            previous_piece = self.pieces[len(self.pieces) - 1]
            x = previous_piece.rect.right
            previous_y = int(previous_piece.rect.y / self.size)
            difference = random.randint(0, self.piece_difference)
            difference = random.choice([difference, -difference])
            top = previous_y + difference
            previous_size = int(previous_piece.rect.height / self.size)
            gap_size = random.randint(previous_size - abs(difference), previous_size + abs(difference))

            if gap_size < self.gap_minimum:
                gap_size = self.gap_minimum
            elif gap_size > self.gap_maximum:
                gap_size = self.gap_maximum

        rect = [x, top * self.size, self.size, self.size*gap_size]
        self.pieces.append(CavePiece(rect, self.colour))

    def check_wall_hit(self, player):
        corners = [False, False, False, False]
        for cave_piece in self.pieces[int(self.scale[0]*0.3):int(self.scale[0]*0.6)]:
            if cave_piece.rect.collidepoint(player.rect.topleft):
                corners[0] = True
            if cave_piece.rect.collidepoint(player.rect.topright):
                corners[1] = True
            if cave_piece.rect.collidepoint(player.rect.bottomleft):
                corners[2] = True
            if cave_piece.rect.collidepoint(player.rect.bottomright):
                corners[3] = True
        if False in corners:
            return True
        return False

    def draw(self, display):
        for wall in self.pieces:
            wall.draw(display)


pygame.font.init()
SCORE_FONT = pygame.font.SysFont('Arial', 36)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 72)

colours = {
    "cave": (255, 255, 255),
    "walls": (5, 5, 30),      
    "player": (220, 220, 220),
    "text": (255, 255, 255),
    "flame": (255, 140, 0),  
}

DISPLAY_SIZE = [1000, 700]
PLAYER_SIZE = [60, 30] 
PLAYER_RECT = [
    round(DISPLAY_SIZE[0]/2 - PLAYER_SIZE[0]/2),
    round(DISPLAY_SIZE[1]/2 - PLAYER_SIZE[1]/2),
    PLAYER_SIZE[0], PLAYER_SIZE[1]]
GRAVITY = -0.01

class Rocket:
    def __init__(self, rect, colour):
        self.rect = pygame.Rect(rect)
        self.vector = [0, 0]
        self.angle = .5
        self.speed = 10
        self.max_speed = 30
        
       
        self.body_color = (220, 220, 220)  
        self.window_color = (173, 216, 230)  
        self.wing_color = (180, 180, 180) 
        self.flame_color = (255, 140, 0)   
        
       
        self.flame_length = 20
        self.flame_width = 15
        self.flame_flicker = 0
        
    def draw(self, display):
        direction = [
            math.sin(self.angle * math.pi),
            math.cos(self.angle * math.pi)
        ]
        
        self.flame_flicker = (self.flame_flicker + 1) % 4
        
        body_width = self.rect.width
        body_height = self.rect.height
        nose_length = body_width * 0.3
        
        nose_tip_x = self.rect.centerx + direction[0] * (body_width/2 + nose_length)
        nose_tip_y = self.rect.centery + direction[1] * (body_width/2 + nose_length)
        
        rear_center_x = self.rect.centerx - direction[0] * body_width/2
        rear_center_y = self.rect.centery - direction[1] * body_width/2
        
        rocket_points = [
            (rear_center_x - direction[0] * body_width * 0.1 - direction[1] * body_height * 0.8,
             rear_center_y - direction[1] * body_width * 0.1 + direction[0] * body_height * 0.8),
            
            (rear_center_x - direction[1] * body_height/2,
             rear_center_y + direction[0] * body_height/2),
            
            (self.rect.centerx - direction[1] * body_height/2,
             self.rect.centery + direction[0] * body_height/2),
            
            (self.rect.centerx + direction[0] * body_width/2 - direction[1] * body_height/3,
             self.rect.centery + direction[1] * body_width/2 + direction[0] * body_height/3),
            
            (nose_tip_x, nose_tip_y),
            
            (self.rect.centerx + direction[0] * body_width/2 + direction[1] * body_height/3,
             self.rect.centery + direction[1] * body_width/2 - direction[0] * body_height/3),
            
            (self.rect.centerx + direction[1] * body_height/2,
             self.rect.centery - direction[0] * body_height/2),
            
            (rear_center_x + direction[1] * body_height/2,
             rear_center_y - direction[0] * body_height/2),
            
            (rear_center_x - direction[0] * body_width * 0.1 + direction[1] * body_height * 0.8,
             rear_center_y - direction[1] * body_width * 0.1 - direction[0] * body_height * 0.8),
        ]
        
        pygame.draw.polygon(display, self.body_color, rocket_points)

        window_size = body_height * 0.5
        window_center_x = self.rect.centerx + direction[0] * body_width * 0.1
        window_center_y = self.rect.centery + direction[1] * body_width * 0.1
        
        window_rect = pygame.Rect(
            window_center_x - window_size/2, 
            window_center_y - window_size/2,
            window_size, window_size
        )
        pygame.draw.ellipse(display, self.window_color, window_rect)
        
        flame_start_x = rear_center_x
        flame_start_y = rear_center_y
        
        flame_length = self.flame_length * (0.8 + random.random() * 0.4)
        
        flame_colors = [(255, 69, 0), (255, 140, 0), (255, 165, 0)]
        
        for i in range(3):
            flame_size = flame_length * (1.0 - i * 0.25)
            flame_width = self.flame_width * (1.0 - i * 0.2)
            
            flame_end_x = flame_start_x - direction[0] * flame_size
            flame_end_y = flame_start_y - direction[1] * flame_size
            
            flame_points = [
                (flame_start_x, flame_start_y),
                (flame_start_x - direction[1] * flame_width/2, flame_start_y + direction[0] * flame_width/2),
                (flame_end_x, flame_end_y),
                (flame_start_x + direction[1] * flame_width/2, flame_start_y - direction[0] * flame_width/2)
            ]
            
            pygame.draw.polygon(display, flame_colors[i], flame_points)
    
    def update(self, objects):
        delta_x = self.speed*math.sin(self.angle * math.pi)
        delta_y = self.speed*math.cos(self.angle * math.pi)
        self.move(0, 0, [])
        return [delta_x, delta_y]

    def apply_gravity(self):
        self.move_clockwise()

    def move_clockwise(self, amount=-0.01):
        self.move_angle(amount)
        self.rollover_angle()

    def move_anticlockwise(self, amount=0.02):
        self.move_angle(amount)
        self.rollover_angle()

    def move_angle(self, amount):
        self.angle += amount

    def rollover_angle(self):
        if self.angle <= 0:
            self.angle = 2
        elif self.angle >= 2:
            self.angle = 0

    def move(self, dx, dy, objects):
        if dx != 0:
            self.move_single_axis(dx, 0, objects)
        if dy != 0:
            self.move_single_axis(0, dy, objects)
        self.apply_gravity()

    def move_single_axis(self, dx, dy, objects):
        self.rect.x += dx
        self.rect.y += dy

        for wall in objects:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                if dx < 0:
                    self.rect.left = wall.rect.right
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                if dy < 0:
                    self.rect.top = wall.rect.bottom
                    
    def increase_speed(self):
        self.speed = min(self.speed + 0.5, self.max_speed)
        return self.speed

class FuelCell:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.colour = (0, 255, 127)  
        self.glow_color = (0, 200, 100)
        self.pulse = 0

    def move(self, movement):
        self.rect = self.rect.move(movement)

    def check_collide(self, player):
        if self.rect.colliderect(player.rect):
            return True
        return False

    def draw(self, display):
        self.pulse = (self.pulse + 0.1) % 6.28
        glow_size = math.sin(self.pulse) * 3 + 5
        
        pygame.draw.circle(display, self.glow_color, self.rect.center, self.rect.width/2 + glow_size)
        
        pygame.draw.circle(display, self.colour, self.rect.center, self.rect.width/2)
        
        inner_rect = pygame.Rect(
            self.rect.centerx - self.rect.width/4,
            self.rect.centery - self.rect.height/4,
            self.rect.width/2,
            self.rect.height/2
        )
        pygame.draw.ellipse(display, (200, 255, 230), inner_rect)

class FuelManager:
    def __init__(self, boundary):
        self.boundary = pygame.Rect(boundary)
        self.cells = []
        self.spawn_chance = 0.02

    def update(self, movement, player, cave):
        score = 0
        speed_increased = False

        for cell in self.cells[:]:
            cell.move(movement)

            if cell.check_collide(player):
                score += 1
                self.delete(cell)
                player.increase_speed()
                speed_increased = True
            elif self.check_delete(cell):
                self.delete(cell)

        if self.check_spawn():
            self.spawn(cave)

        return score, speed_increased

    def check_spawn(self):
        if random.random() <= self.spawn_chance:
            return True
        return False

    def check_delete(self, cell):
        if not self.boundary.colliderect(cell.rect):
            return True

    def delete(self, cell):
        self.cells.remove(cell)

    def spawn(self, cave):
        valid_pieces = []
        for piece in cave.pieces:
            if piece.rect.height > cave.size * 2: 
                valid_pieces.append(piece)
        
        if not valid_pieces:
            return
            
        piece = random.choice(valid_pieces)
        
        margin = cave.size // 3
        min_y = piece.rect.y + margin
        max_y = piece.rect.bottom - margin - cave.size
        
        if min_y >= max_y:
            min_y = piece.rect.y
            max_y = piece.rect.bottom - cave.size
        
        y = random.randint(min_y, max_y)
        
        cell = FuelCell([piece.rect.x, y, cave.size, cave.size])
        self.cells.append(cell)

    def draw(self, display):
        for cell in self.cells:
            cell.draw(display)

def draw_score_and_speed(display, score, speed):
    score_text = SCORE_FONT.render(f'Fuel Cells: {score}', True, colours["text"])
    speed_text = SCORE_FONT.render(f'Speed: {speed:.1f}', True, colours["text"])
    display.blit(score_text, (20, 20))
    display.blit(speed_text, (20, 70))

def draw_game_over(display, score, speed):
    overlay = pygame.Surface(DISPLAY_SIZE)
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    display.blit(overlay, (0, 0))
    
    game_over_text = GAME_OVER_FONT.render('Rocket Crashed!', True, colours["text"])
    final_score_text = SCORE_FONT.render(f'Cells Collected: {score}', True, colours["text"])
    final_speed_text = SCORE_FONT.render(f'Final Speed: {speed:.1f}', True, colours["text"])
    restart_text = SCORE_FONT.render('Press SPACE to restart', True, colours["text"])
    
    game_over_x = DISPLAY_SIZE[0]/2 - game_over_text.get_width()/2
    game_over_y = DISPLAY_SIZE[1]/2 - game_over_text.get_height()/2 - 80
    
    score_x = DISPLAY_SIZE[0]/2 - final_score_text.get_width()/2
    score_y = game_over_y + game_over_text.get_height() + 20
    
    speed_x = DISPLAY_SIZE[0]/2 - final_speed_text.get_width()/2
    speed_y = score_y + final_score_text.get_height() + 20
    
    restart_x = DISPLAY_SIZE[0]/2 - restart_text.get_width()/2
    restart_y = speed_y + final_speed_text.get_height() + 30
    
    display.blit(game_over_text, (game_over_x, game_over_y))
    display.blit(final_score_text, (score_x, score_y))
    display.blit(final_speed_text, (speed_x, speed_y))
    display.blit(restart_text, (restart_x, restart_y))

def main():
    pygame.init()
    display = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Space Explorer")
    clock = pygame.time.Clock()
    FPS = 30

    def reset_game():
        cave = Cave(display.get_rect(), 20, colours["cave"])
        fuel_manager = FuelManager(display.get_rect())
        rocket = Rocket(PLAYER_RECT, colours["player"])
        return cave, fuel_manager, rocket, 0, 0, False

    starscape = Starscape(display.get_rect())
    cave, fuel_manager, rocket, distance, score, game_over = reset_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and game_over:
                    cave, fuel_manager, rocket, distance, score, game_over = reset_game()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_SPACE]:
                rocket.move_anticlockwise()

            movement = rocket.update([])
            distance += round(movement[0] / 10)

            movement[0] = -movement[0]
            movement[1] = -movement[1]

            fuel_update = fuel_manager.update(movement, rocket, cave)
            score += fuel_update[0]
            
            hit = cave.update(movement, rocket)
            
            if hit:
                game_over = True

        display.fill(colours["walls"])
        starscape.draw(display)
        cave.draw(display)
        fuel_manager.draw(display)
        rocket.draw(display)
        
        if game_over:
            draw_game_over(display, score, rocket.speed)
        else:
            draw_score_and_speed(display, score, rocket.speed)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()