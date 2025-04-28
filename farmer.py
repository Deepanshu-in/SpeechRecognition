import pygame
import sys
import random
import math
from enum import Enum
from datetime import datetime, timedelta

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
PLAYER_SPEED = 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
LIGHT_GREEN = (144, 238, 144)
LIGHT_BLUE = (173, 216, 230)

# Game states
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

# Season class
class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3

# Crop stages
class CropStage(Enum):
    EMPTY = 0
    SEEDLING = 1
    GROWING = 2
    MATURE = 3
    RIPE = 4
    DEAD = 5

# Tool types
class ToolType(Enum):
    HOE = 0
    WATERING_CAN = 1
    SEED_BAG = 2
    HARVEST_BASKET = 3

# Crop class
class Crop:
    def __init__(self, name, growth_time, sell_price, seed_price, season):
        self.name = name
        self.growth_time = growth_time  # in days
        self.sell_price = sell_price
        self.seed_price = seed_price
        self.season = season
        self.stage = CropStage.EMPTY
        self.days_growing = 0
        self.watered_today = False
    
    def grow(self):
        if self.watered_today and self.stage != CropStage.RIPE and self.stage != CropStage.DEAD:
            self.days_growing += 1
            growth_percentage = (self.days_growing / self.growth_time) * 100
            
            if growth_percentage <= 25:
                self.stage = CropStage.SEEDLING
            elif growth_percentage <= 50:
                self.stage = CropStage.GROWING
            elif growth_percentage <= 90:
                self.stage = CropStage.MATURE
            else:
                self.stage = CropStage.RIPE
        
        # Reset watered status for the new day
        self.watered_today = False
    
    def water(self):
        self.watered_today = True
    
    def is_harvestable(self):
        return self.stage == CropStage.RIPE
    
    def reset(self):
        self.stage = CropStage.EMPTY
        self.days_growing = 0
        self.watered_today = False

# Tile class
class Tile:
    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = tile_type  # 'soil', 'water', 'path', etc.
        self.tilled = False
        self.crop = None
    
    def draw(self, screen):
        if self.type == 'soil':
            if self.tilled:
                pygame.draw.rect(screen, GREEN, self.rect)
                # Draw grid lines
                pygame.draw.rect(screen, BLACK, self.rect, 1)
            else:
                pygame.draw.rect(screen, BROWN, self.rect)
                pygame.draw.rect(screen, BLACK, self.rect, 1)
        elif self.type == 'water':
            pygame.draw.rect(screen, BLUE, self.rect)
        elif self.type == 'path':
            pygame.draw.rect(screen, LIGHT_GREEN, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 1)
        
        # Draw crop if it exists
        if self.crop and self.crop.stage != CropStage.EMPTY:
            crop_color = LIGHT_GREEN  # Seedling color
            if self.crop.stage == CropStage.GROWING:
                crop_color = GREEN
            elif self.crop.stage == CropStage.MATURE:
                crop_color = LIGHT_GREEN
            elif self.crop.stage == CropStage.RIPE:
                crop_color = YELLOW
            elif self.crop.stage == CropStage.DEAD:
                crop_color = BROWN
            
            # Draw crop
            crop_rect = pygame.Rect(self.x * TILE_SIZE + 10, self.y * TILE_SIZE + 10, TILE_SIZE - 20, TILE_SIZE - 20)
            pygame.draw.rect(screen, crop_color, crop_rect)
            
            # Draw watered indicator
            if self.crop.watered_today:
                pygame.draw.rect(screen, LIGHT_BLUE, 
                                 (self.x * TILE_SIZE + 5, self.y * TILE_SIZE + 5, 5, 5))

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.energy = 5
        self.max_energy = 5
        self.money = 500
        self.selected_tool = ToolType.HOE
        self.inventory = {
            'carrot_seeds': 5,
            'potato_seeds': 5,
            'tomato_seeds': 5,
            'corn_seeds': 0,
            'cabbage_seeds': 0
        }
        self.harvested_crops = {
            'carrot': 0,
            'potato': 0,
            'tomato': 0,
            'corn': 0,
            'cabbage': 0
        }
    
    def move(self, dx, dy, tiles):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Create a temporary rect for collision detection
        temp_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        
        # Check for collisions with water tiles
        can_move = True
        for tile in tiles:
            if tile.type == 'water' and temp_rect.colliderect(tile.rect):
                can_move = False
                break
        
        # If no collisions, update position
        if can_move:
            if 0 <= new_x <= SCREEN_WIDTH - self.width:
                self.x = new_x
            if 0 <= new_y <= SCREEN_HEIGHT - self.height:
                self.y = new_y
            self.rect.x = self.x
            self.rect.y = self.y
    
    def use_tool(self, tiles):
        if self.energy <= 0:
            return False
        
        # Find the tile that the player is standing on
        for tile in tiles:
            if tile.rect.collidepoint(self.x + self.width // 2, self.y + self.height // 2):
                if tile.type == 'soil':
                    if self.selected_tool == ToolType.HOE and not tile.tilled:
                        tile.tilled = True
                        self.energy -= 1
                        return True
                    elif self.selected_tool == ToolType.WATERING_CAN and tile.tilled and tile.crop:
                        tile.crop.water()
                        self.energy -= 1
                        return True
                    elif self.selected_tool == ToolType.SEED_BAG and tile.tilled and not tile.crop:
                        # Plant seeds based on selected seed type
                        seed_type = input("Enter seed type (carrot, potato, tomato, corn, cabbage): ").lower() + "_seeds"
                        if seed_type in self.inventory and self.inventory[seed_type] > 0:
                            crop_name = seed_type.split('_')[0]
                            if crop_name == 'carrot':
                                tile.crop = Crop('carrot', 3, 20, 10, Season.SPRING)
                            elif crop_name == 'potato':
                                tile.crop = Crop('potato', 4, 25, 15, Season.SPRING)
                            elif crop_name == 'tomato':
                                tile.crop = Crop('tomato', 5, 30, 20, Season.SUMMER)
                            elif crop_name == 'corn':
                                tile.crop = Crop('corn', 6, 40, 25, Season.SUMMER)
                            elif crop_name == 'cabbage':
                                tile.crop = Crop('cabbage', 4, 35, 20, Season.FALL)
                            
                            tile.crop.stage = CropStage.SEEDLING
                            self.inventory[seed_type] -= 1
                            self.energy -= 1
                            return True
                    elif self.selected_tool == ToolType.HARVEST_BASKET and tile.crop and tile.crop.is_harvestable():
                        # Harvest the crop
                        crop_name = tile.crop.name
                        self.harvested_crops[crop_name] += 1
                        self.money += tile.crop.sell_price
                        tile.crop.reset()
                        self.energy -= 1
                        return True
        return False
    
    def draw(self, screen):
        # Draw player
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        
        # Draw energy bar
        energy_bar_width = 100
        energy_bar_height = 20
        energy_percentage = self.energy / self.max_energy
        pygame.draw.rect(screen, BLACK, (10, 10, energy_bar_width + 2, energy_bar_height + 2), 2)
        pygame.draw.rect(screen, RED, (11, 11, int(energy_percentage * energy_bar_width), energy_bar_height))
        
        # Draw selected tool indicator
        tool_names = {
            ToolType.HOE: "Hoe",
            ToolType.WATERING_CAN: "Watering Can",
            ToolType.SEED_BAG: "Seed Bag",
            ToolType.HARVEST_BASKET: "Harvest Basket"
        }
        font = pygame.font.Font(None, 24)
        tool_text = font.render(f"Tool: {tool_names[self.selected_tool]}", True, BLACK)
        screen.blit(tool_text, (10, 40))
        
        # Draw money
        money_text = font.render(f"Money: ${self.money}", True, BLACK)
        screen.blit(money_text, (10, 70))

# Game class
class FarmingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Farming Simulation Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.PLAYING
        self.current_season = Season.SPRING
        self.day = 1
        self.font = pygame.font.Font(None, 36)
        
        # Create farm grid
        self.tiles = []
        for y in range(SCREEN_HEIGHT // TILE_SIZE):
            for x in range(SCREEN_WIDTH // TILE_SIZE):
                # Create water border around the farm
                if (x == 0 or x == (SCREEN_WIDTH // TILE_SIZE) - 1 or 
                    y == 0 or y == (SCREEN_HEIGHT // TILE_SIZE) - 1):
                    self.tiles.append(Tile(x, y, 'water'))
                # Create some path tiles
                elif x % 5 == 0 or y % 5 == 0:
                    self.tiles.append(Tile(x, y, 'path'))
                else:
                    self.tiles.append(Tile(x, y, 'soil'))
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                elif event.key == pygame.K_e:
                    self.player.use_tool(self.tiles)
                elif event.key == pygame.K_1:
                    self.player.selected_tool = ToolType.HOE
                elif event.key == pygame.K_2:
                    self.player.selected_tool = ToolType.WATERING_CAN
                elif event.key == pygame.K_3:
                    self.player.selected_tool = ToolType.SEED_BAG
                elif event.key == pygame.K_4:
                    self.player.selected_tool = ToolType.HARVEST_BASKET
                elif event.key == pygame.K_n:
                    # Skip to next day
                    self.next_day()
    
    def handle_movement(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        self.player.move(dx, dy, self.tiles)
    
    def toggle_pause(self):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
    
    def next_day(self):
        self.day += 1
        
        # Refill player energy
        self.player.energy = self.player.max_energy
        
        # Grow crops
        for tile in self.tiles:
            if tile.crop:
                tile.crop.grow()
        
        # Check for season change (every 30 days)
        if self.day % 30 == 0:
            seasons = list(Season)
            current_index = seasons.index(self.current_season)
            self.current_season = seasons[(current_index + 1) % len(seasons)]
    
    def update(self):
        if self.state == GameState.PLAYING:
            self.handle_movement()
    
    def draw(self):
        # Clear screen
        self.screen.fill(WHITE)
        
        # Draw tiles
        for tile in self.tiles:
            tile.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        season_names = {
            Season.SPRING: "Spring",
            Season.SUMMER: "Summer",
            Season.FALL: "Fall",
            Season.WINTER: "Winter"
        }
        
        season_text = self.font.render(f"Season: {season_names[self.current_season]}", True, BLACK)
        day_text = self.font.render(f"Day: {self.day}", True, BLACK)
        
        self.screen.blit(season_text, (SCREEN_WIDTH - 200, 10))
        self.screen.blit(day_text, (SCREEN_WIDTH - 200, 50))
        
        # Draw pause screen if paused
        if self.state == GameState.PAUSED:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))  # Semi-transparent overlay
            self.screen.blit(s, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
            
            instructions = [
                "Press ESC to resume",
                "Press 1-4 to select tools:",
                "1: Hoe, 2: Watering Can",
                "3: Seed Bag, 4: Harvest Basket",
                "Press N to skip to next day"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_text = pygame.font.Font(None, 24).render(instruction, True, WHITE)
                self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30 + i * 25))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = FarmingGame()
    game.run()