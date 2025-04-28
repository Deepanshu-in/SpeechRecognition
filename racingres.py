"""
A car racing game with collectible coins and fuel tanks.
Player controls a car that can collect coins for score and fuel tanks to refill.
"""

import pygame
import sys
import math
import random

class RacingGame:
    """Main game class handling all game functionality."""
    
    def __init__(self):
        """Initialize game window and resources."""
        # Pygame ko initialize karo
        pygame.init()
        
        # Screen ka size set karo
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Racing Game")
        
        # Rang define karo
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.SKY_BLUE = (135, 206, 235)  # Sky blue background
        self.GREEN = (34, 139, 34)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        
        # Coin ke liye additional rang
        self.COIN_GOLD = (218, 165, 32)  # Metallic gold
        self.COIN_HIGHLIGHT = (255, 215, 0)  # Bright gold highlight
        
        # Fuel tank ke liye additional rang
        self.FUEL_DARK_BROWN = (101, 67, 33)
        self.FUEL_LIGHT_BROWN = (139, 69, 19)
        
        # Clock aur font setup karo
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # Game state variables set karo
        self.car_x = self.width // 2
        self.car_y = 410  # Car ki position road par
        self.terrain_offset = 0
        self.moving = False
        self.score = 0
        self.fuel = 100
        self.game_over = False
        self.coins = []      
        self.fuel_tanks = [] 
        
        # Sun ko screen ke center mein rakhna
        self.sun_x = self.width // 2
        self.sun_y = 100
        self.sun_radius = 50
    
    def draw_detailed_coin(self, surface, x, y):
        """Draw a more detailed and shiny coin."""
        # Coin ka main circle
        pygame.draw.circle(surface, self.COIN_GOLD, (int(x), int(y)), 10)
        
        # Coin ke liye 3D effect
        # Outer highlight
        pygame.draw.circle(surface, self.COIN_HIGHLIGHT, (int(x), int(y)), 8, 2)
        
        # Inner shine effect
        pygame.draw.circle(surface, self.WHITE, (int(x)-3, int(y)-3), 3, 1)
        
        # Coin ke edges par detail
        pygame.draw.circle(surface, self.BLACK, (int(x), int(y)), 10, 1)
    
    def draw_detailed_fuel_tank(self, surface, x, y):
        """Draw a more detailed and textured fuel tank."""
        # Main fuel tank rectangle
        pygame.draw.rect(surface, self.FUEL_LIGHT_BROWN, 
                       (int(x)-15, int(y)-15, 30, 30))
        
        # Fuel tank ke liye texture aur shading
        # Dark border
        pygame.draw.rect(surface, self.FUEL_DARK_BROWN, 
                       (int(x)-15, int(y)-15, 30, 30), 3)
        
        # Fuel tank pe glare effect
        pygame.draw.line(surface, self.WHITE, 
                       (int(x)-10, int(y)-5), 
                       (int(x)+5, int(y)-5), 2)
        
        # Tank pe small details
        pygame.draw.rect(surface, self.BLACK, 
                       (int(x)-2, int(y)-10, 4, 4), 1)
    
    def draw_elements(self):
        """Draw all game elements on the screen."""
        # Sky blue background ko fill karna
        self.screen.fill(self.SKY_BLUE)
        
        # Sun ko draw karna
        pygame.draw.circle(self.screen, self.YELLOW, (self.sun_x, self.sun_y), self.sun_radius)
        
        # Terrain generate aur draw karna
        terrain = self.generate_terrain(self.terrain_offset)
        pygame.draw.polygon(self.screen, self.GREEN,
                          terrain + [(self.width, self.height), (0, self.height)])
        
        # Coins draw karna with new detailed design
        for coin in self.coins:
            self.draw_detailed_coin(self.screen, coin[0], coin[1])
        
        # Fuel tanks draw karna with new detailed design
        for fuel in self.fuel_tanks:
            self.draw_detailed_fuel_tank(self.screen, fuel[0], fuel[1])
        
        # Car draw karna
        # Main body
        pygame.draw.rect(self.screen, self.RED, (self.car_x - 25, self.car_y, 50, 30))
        # Roof
        pygame.draw.rect(self.screen, self.RED, (self.car_x - 20, self.car_y - 15, 40, 15))
        # Windows
        pygame.draw.rect(self.screen, self.BLACK, (self.car_x - 15, self.car_y - 10, 15, 10))
        pygame.draw.rect(self.screen, self.BLACK, (self.car_x + 2, self.car_y - 10, 15, 10))
        # Wheels
        pygame.draw.circle(self.screen, self.BLACK, (self.car_x - 20, self.car_y + 28), 8)
        pygame.draw.circle(self.screen, self.BLACK, (self.car_x + 20, self.car_y + 28), 8)
        # Headlight
        pygame.draw.circle(self.screen, self.YELLOW, (self.car_x + 25, self.car_y + 10), 5)
        
        # Game instructions draw karna
        instructions = [
            "Space: Start/Pause",
            "R: Restart Game"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.BLACK)
            self.screen.blit(text, (self.width - 250, 10 + i * 30))
        
        # Score text draw karna
        score_text = self.font.render(f"Score: {self.score}", True, self.BLACK)
        self.screen.blit(score_text, (20, 10))
        
        # Fuel bar draw karna
        pygame.draw.rect(self.screen, self.WHITE, (20, 50, 200, 20), 2)
        pygame.draw.rect(self.screen, self.GREEN, (22, 52, int(self.fuel * 1.96), 16))
        
        # Game over text draw karna
        if self.game_over:
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, self.RED)
            text_rect = game_over_text.get_rect(center=(self.width//2, self.height//2 - 50))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    def generate_terrain(self, offset):
        """Generate terrain points using sine wave for road bumps."""
        # Terrain points generate karna sine wave ke maddhyam se
        return [(x, 430 + 15 * math.sin((x + offset) * 0.01)) 
                for x in range(0, self.width + 5, 5)]
    
    def handle_events(self):
        """Handle all user input events."""
        # Sabhi game events ko handle karna
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.moving = not self.moving
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
    
    def reset_game(self):
        """Reset all game state variables to initial values."""
        # Game ko initial state mein reset karna
        self.car_x = self.width // 2
        self.terrain_offset = 0
        self.moving = False
        self.score = 0
        self.fuel = 100
        self.game_over = False
        self.coins.clear()
        self.fuel_tanks.clear()
    
    def update_game(self):
        """Update all game objects and check collisions."""
        # Game ke objects ko update karna aur collision check karna
        keys = pygame.key.get_pressed()
        speed = 0
        
        if self.moving and not self.game_over:
            speed = 3 * (1.5 if keys[pygame.K_RIGHT] else 1)
            self.terrain_offset += speed
            self.fuel -= 0.1
            if self.fuel <= 0:
                self.game_over = True
        
        if self.moving and not self.game_over:
            # Coins randomly generate karna
            if random.random() < 0.05:
                self.coins.append([self.width + random.randint(0, 200), random.randint(400, 450)])
            # Fuel tanks randomly generate karna
            if random.random() < 0.01:
                self.fuel_tanks.append([self.width + random.randint(0, 200), random.randint(400, 450)])
        
        # Coins aur fuel tanks ko move karna
        for obj in self.coins + self.fuel_tanks:
            obj[0] -= speed
        
        # Screen se bahar nikle huye coins aur fuel tanks ko hatana
        self.coins = [c for c in self.coins if c[0] > -20]
        self.fuel_tanks = [f for f in self.fuel_tanks if f[0] > -30]
        
        # Car ka rectangle banana
        car_rect = pygame.Rect(self.car_x-25, self.car_y, 50, 30)
        
        # Coins ke liye collision check
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin[0]-10, coin[1]-10, 20, 20)
            if car_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                self.score += 1
        
        # Fuel tanks ke liye collision check
        for fuel in self.fuel_tanks[:]:
            fuel_rect = pygame.Rect(fuel[0]-15, fuel[1]-15, 30, 30)
            if car_rect.colliderect(fuel_rect):
                self.fuel_tanks.remove(fuel)
                self.fuel = 100
    
    def run(self):
        """Main game loop that runs continuously."""
        # Game loop chalana
        while True:
            self.handle_events()
            self.update_game()
            self.draw_elements()
            self.clock.tick(60)

if __name__ == "__main__":
    # Game ko start karna
    game = RacingGame()
    game.run()