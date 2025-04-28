import pygame, random, math
pygame.init()

# Setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)

class Car:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.max_speed = 5
        self.acceleration = self.max_speed / 30  # 0.5 second me max speed tak pahunchta hai
        self.trail = [(self.x, self.y) for _ in range(5)]
    
    def update(self, target_y):
        # Target ki taraf smooth acceleration
        target_velocity = (target_y - self.y) / 10
        target_velocity = max(min(target_velocity, self.max_speed), -self.max_speed)
        
        if abs(target_velocity - self.velocity) > self.acceleration:
            self.velocity += self.acceleration if target_velocity > self.velocity else -self.acceleration
        else:
            self.velocity = target_velocity
            
        self.y = max(0, min(HEIGHT, self.y + self.velocity))
        
        # Trail update karo
        self.trail.pop(0)
        self.trail.append((self.x, self.y))
    
    def draw(self):
        # Trail ko simple circles se draw kara he 
        for i, (x, y) in enumerate(self.trail):
            radius = i // 2 + 1
            pygame.draw.circle(screen, RED, (int(x), int(y)), radius)
        
        # Car body draw kara he (main rectangle) 
        pygame.draw.rect(screen, RED, (self.x-20, self.y-10, 40, 20))
        
        # Car roof draw kara he (top rectangle) 
        pygame.draw.rect(screen, RED, (self.x-10, self.y-20, 20, 10))
        
        # Windows draw kara he (blue rectangles) 
        pygame.draw.rect(screen, BLUE, (self.x-8, self.y-18, 7, 6))
        pygame.draw.rect(screen, BLUE, (self.x+1, self.y-18, 7, 6))
        
        # Wheels draw kara he (black circles) 
        pygame.draw.circle(screen, BLACK, (int(self.x-10), int(self.y+10)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x+10), int(self.y+10)), 5)
        
        # Taillight draw kara he (yellow rectangle) 
        pygame.draw.rect(screen, YELLOW, (self.x-21, self.y-5, 5, 5))
    
    def get_rect(self):
        return pygame.Rect(self.x-20, self.y-10, 40, 20)

class XObstacle:
    def __init__(self, speed):
        self.x = WIDTH
        self.y = random.randint(50, HEIGHT-50)
        self.speed = speed
        
    def update(self):
        self.x -= self.speed
        
    def draw(self):
        size = 20
        pygame.draw.line(screen, RED, (self.x-size/2, self.y-size/2), 
                        (self.x+size/2, self.y+size/2), 3)
        pygame.draw.line(screen, RED, (self.x-size/2, self.y+size/2), 
                        (self.x+size/2, self.y-size/2), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x-10, self.y-10, 20, 20)

class CircleObstacle:
    def __init__(self, speed):
        self.start_x = WIDTH
        self.x = WIDTH
        self.base_y = random.randint(100, HEIGHT-100)
        self.speed = speed
        self.distance = 0
        
    def update(self):
        self.x -= self.speed
        self.distance += self.speed
        self.y = self.base_y + math.sin(self.distance/100) * 50
        
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 10)
    
    def get_rect(self):
        return pygame.Rect(self.x-10, self.y-10, 20, 20)

# Game variables
car = Car()
obstacles = []
level = 1
score = 0
multiplier = 1.0
frame_count = 0
last_dodge_frame = 0
game_over = False
game_won = False

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN and (game_over or game_won):
            # Game reset karo
            car = Car()
            obstacles = []
            level = 1
            score = 0
            multiplier = 1.0
            frame_count = 0
            last_dodge_frame = 0
            game_over = False
            game_won = False

    screen.fill(SKY_BLUE)
    
    if not game_over and not game_won:
        # Car update karo
        car.update(pygame.mouse.get_pos()[1])
        frame_count += 1

        # Obstacles spawn karo
        spawn_interval = max(30, 120 - (level-1) * 30)
        if frame_count % spawn_interval == 0:
            if level < 6:  # Level 6 se pehle tak hi obstacles spawn honge
                if level < 4:
                    obstacles.append(XObstacle(level))
                else:
                    if len(obstacles) % 2 == 0:
                        obstacles.append(XObstacle(level))
                    else:
                        obstacles.append(CircleObstacle(level))

        # Level progression
        if frame_count % 500 == 0 and level < 6:  # Level 6 tak hi game chalega
            level += 1
            if level >= 6:  # Jaise hi level 6 pe pahunche, game jeet gaye
                game_won = True

        # Obstacles update aur check karo
        for obs in obstacles[:]:
            obs.update()
            obs.draw()
            
            # Collision check kara he idhar 
            if car.get_rect().colliderect(obs.get_rect()):
                game_over = True
                
            # Near miss check kara he idhar 
            if abs(car.x - obs.x) < 5 and abs(car.y - obs.y) < 30:
                score += 50
                last_dodge_frame = frame_count
                multiplier += 0.1
                
            # Off-screen obstacles hatae he 
            if obs.x < -20:
                obstacles.remove(obs)

        # Multiplier update kare he 
        if frame_count - last_dodge_frame > 180:  # 3 seconds
            multiplier = 1.0

        # Score update kari he 
        score += level * multiplier

        # HUD draw kara 
        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f'Score: {int(score)}', True, BLACK), (10, 10))
        screen.blit(font.render(f'Level: {level}', True, BLACK), (10, 50))
        screen.blit(font.render(f'Multiplier: {multiplier:.1f}x', True, BLACK), (10, 90))

    car.draw()

    if game_over or game_won:
        font = pygame.font.Font(None, 74)
        text = font.render('YOU WIN!' if game_won else 'GAME OVER', True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        
        font = pygame.font.Font(None, 36)
        text = font.render(f'Final Score: {int(score)}', True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 50))
        
        text = font.render('Click to Restart', True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 100))

    pygame.display.flip()
    clock.tick(60)