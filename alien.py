import pygame
import random

# Initialize pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tank Battle")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

# Player tank class
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, is_player=False):
        super().__init__()
        # Create tank surface and draw tank
        self.original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        if is_player:
            # Tank body
            pygame.draw.rect(self.original_image, GREEN, (3, 8, 34, 24), border_radius=3)
            # Tank turret base
            pygame.draw.circle(self.original_image, GREEN, (20, 15), 10)
            # Tank gun
            pygame.draw.rect(self.original_image, GREEN, (15, 0, 10, 25))
            # Tank details - dark green accents
            dark_green = (0, 180, 0)
            # Cannon tip
            pygame.draw.rect(self.original_image, dark_green, (15, 0, 10, 5))
            # Tank hatches
            pygame.draw.circle(self.original_image, dark_green, (20, 15), 5)
            # Tracks
            pygame.draw.rect(self.original_image, BLACK, (0, 5, 5, 30))
            pygame.draw.rect(self.original_image, BLACK, (35, 5, 5, 30))
            # Track details
            for i in range(5, 30, 5):
                pygame.draw.line(self.original_image, GRAY, (0, i), (5, i), 1)
                pygame.draw.line(self.original_image, GRAY, (35, i), (40, i), 1)
        else:  # Enemy tank as simple red rectangle
            # Just a red rectangular structure for enemy tanks
            pygame.draw.rect(self.original_image, RED, (5, 10, 30, 20))  # Simple rectangular body
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(0, -1)  # Facing up initially
        self.speed = 3 if is_player else 1
        self.angle = 0
        self.is_player = is_player
        self.health = 100
        self.reload_time = 0
        self.shoot_delay = 30 if is_player else 90
        
    def update(self, barriers):
        # Store previous position to revert if collision occurs
        prev_pos = self.position.copy()
        
        if self.is_player:
            # Player controls with arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.position += self.direction * self.speed
            if keys[pygame.K_DOWN]:
                self.position -= self.direction * self.speed
            if keys[pygame.K_LEFT]:
                self.angle -= 2
                self.direction.rotate_ip(-2)
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
            if keys[pygame.K_RIGHT]:
                self.angle += 2
                self.direction.rotate_ip(2)
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
            
            # Update reload timer
            if self.reload_time > 0:
                self.reload_time -= 1
        else:
            if random.randint(0, 100) < 3:  # 3% chance to change direction
                self.angle += random.randint(-20, 20)
                self.direction.rotate_ip(self.angle)
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
            
            # Move forward
            if random.randint(0, 100) < 70:  # 70% chance to move
                self.position += self.direction * self.speed
                
            # Update reload timer
            if self.reload_time > 0:
                self.reload_time -= 1
        
        # Update rectangle position
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Check for collisions with barriers
        if pygame.sprite.spritecollideany(self, barriers):
            # Revert position if collision
            self.position = prev_pos
            self.rect.center = (int(self.position.x), int(self.position.y))
            
            # For enemies, change direction when hitting barriers
            if not self.is_player:
                self.angle += random.randint(90, 180)
                self.direction.rotate_ip(self.angle)
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
        
        # Keep tank on screen
        if self.rect.left < 0:
            self.position.x = self.rect.width // 2
        if self.rect.right > screen_width:
            self.position.x = screen_width - self.rect.width // 2
        if self.rect.top < 0:
            self.position.y = self.rect.height // 2
        if self.rect.bottom > screen_height:
            self.position.y = screen_height - self.rect.height // 2
        
        self.rect.center = (int(self.position.x), int(self.position.y))
    
    def shoot(self):
        if self.reload_time <= 0:
            self.reload_time = self.shoot_delay
            # Create bullet starting at the tank's position
            bullet_pos = self.position + self.direction * 30
            return Bullet(bullet_pos.x, bullet_pos.y, self.direction, self.is_player)
        return None

    def draw_health(self, screen):
        # Draw health bar above the tank
        bar_length = 30
        bar_height = 5
        fill = (self.health / 100) * bar_length
        outline_rect = pygame.Rect(self.rect.x + 5, self.rect.y - 10, bar_length, bar_height)
        fill_rect = pygame.Rect(self.rect.x + 5, self.rect.y - 10, fill, bar_height)
        
        # Green health bar for player, red for enemies
        if self.is_player:
            health_color = GREEN
        else:
            health_color = RED
            
        pygame.draw.rect(screen, health_color, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 1)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_player_bullet):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        color = BLUE if is_player_bullet else RED
        pygame.draw.circle(self.image, color, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)
        self.direction = direction.normalize()
        self.speed = 5
        self.is_player_bullet = is_player_bullet
        self.damage = 25
        
    def update(self):
        # Move bullet
        self.position += self.direction * self.speed
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Remove if off screen
        if (self.rect.left < 0 or self.rect.right > screen_width or 
            self.rect.top < 0 or self.rect.bottom > screen_height):
            self.kill()

# Barrier class
class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        # Create simple explosion animation
        for size in range(1, 20, 4):
            img = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(img, RED, (size, size), size)
            self.images.append(img)
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0
        
    def update(self):
        # Progress through explosion animation
        self.counter += 1
        if self.counter >= 4:  # Slow down animation
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)

# Game level class
class Level:
    def __init__(self, level_num):
        self.barriers = pygame.sprite.Group()
        self.level_num = level_num
        self.create_level()
        
    def create_level(self):
        # Border walls
        wall_thickness = 20
        # Top
        self.barriers.add(Barrier(0, 0, screen_width, wall_thickness))
        # Bottom
        self.barriers.add(Barrier(0, screen_height - wall_thickness, screen_width, wall_thickness))
        # Left
        self.barriers.add(Barrier(0, 0, wall_thickness, screen_height))
        # Right
        self.barriers.add(Barrier(screen_width - wall_thickness, 0, wall_thickness, screen_height))
        
        # Add more barriers based on level
        if self.level_num == 1:
            # Level 1 barriers
            self.barriers.add(Barrier(200, 150, 100, 30))
            self.barriers.add(Barrier(400, 300, 30, 150))
            self.barriers.add(Barrier(100, 450, 200, 30))
        elif self.level_num == 2:
            # Level 2 barriers
            self.barriers.add(Barrier(150, 100, 30, 200))
            self.barriers.add(Barrier(300, 250, 200, 30))
            self.barriers.add(Barrier(600, 150, 30, 300))
            self.barriers.add(Barrier(400, 450, 300, 30))
        elif self.level_num >= 3:
            # Random barriers for levels 3+
            for _ in range(10):
                x = random.randint(50, screen_width - 100)
                y = random.randint(50, screen_height - 100)
                width = random.randint(30, 150)
                height = random.randint(30, 100)
                self.barriers.add(Barrier(x, y, width, height))
        
        return self.barriers

# Game class
class Game:
    def __init__(self):
        self.running = True
        self.game_over = False
        self.level_num = 1
        self.score = 0
        self.lives = 3
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        # Create player tank
        self.player = Tank(screen_width // 2, screen_height - 100, GREEN, is_player=True)
        self.players.add(self.player)
        self.all_sprites.add(self.player)
        
        # Initialize level
        self.level = Level(self.level_num)
        self.barriers = self.level.barriers
        self.all_sprites.add(self.barriers)
        
        # Add enemies
        self.spawn_enemies()
        
        # Set font
        self.font = pygame.font.SysFont('Arial', 26)
        
    def spawn_enemies(self):
        # Clear any existing enemies
        self.enemies.empty()
        
        # Add enemies based on level
        num_enemies = min(2 + self.level_num, 8)  # Max 8 enemies
        
        for i in range(num_enemies):
            # Place enemies away from player and other enemies
            while True:
                x = random.randint(50, screen_width - 50)
                y = random.randint(50, 250)  # Keep enemies on the upper part
                
                # Check if position is good
                temp_tank = Tank(x, y, RED)
                if not pygame.sprite.spritecollideany(temp_tank, self.barriers) and not pygame.sprite.spritecollideany(temp_tank, self.enemies):
                    enemy = Tank(x, y, RED)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
                    break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Player shoot
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                elif event.key == pygame.K_r:
                    # Restart if game over
                    if self.game_over:
                        self.__init__()  # Reinitialize game
    
    def update(self):
        if self.game_over:
            return
            
        # Update all game objects
        self.players.update(self.barriers)
        self.enemies.update(self.barriers)
        self.bullets.update()
        self.explosions.update()
        
        # Enemy shooting (random)
        for enemy in self.enemies:
            if random.randint(0, 100) < 2:  # 2% chance to shoot per frame
                bullet = enemy.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
        
        # Check bullet collisions with tanks
        for bullet in self.bullets:
            # Player bullets hitting enemies
            if bullet.is_player_bullet:
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                for enemy in hit_enemies:
                    enemy.health -= bullet.damage
                    explosion = Explosion(bullet.rect.centerx, bullet.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    bullet.kill()
                    
                    # Check if enemy is destroyed
                    if enemy.health <= 0:
                        self.score += 100
                        explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                        self.explosions.add(explosion)
                        self.all_sprites.add(explosion)
                        enemy.kill()
            
            # Enemy bullets hitting player
            else:
                if pygame.sprite.spritecollide(bullet, self.players, False):
                    self.player.health -= bullet.damage
                    explosion = Explosion(bullet.rect.centerx, bullet.rect.centery)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    bullet.kill()
                    
                    # Check if player is destroyed
                    if self.player.health <= 0:
                        self.lives -= 1
                        explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
                        self.explosions.add(explosion)
                        self.all_sprites.add(explosion)
                        
                        if self.lives <= 0:
                            self.game_over = True
                        else:
                            # Respawn player
                            self.player.health = 100
                            self.player.position.x = screen_width // 2
                            self.player.position.y = screen_height - 100
                            self.player.angle = 0
                            self.player.direction = pygame.math.Vector2(0, -1)
                            self.player.image = self.player.original_image
            
            # Bullets hitting barriers
            if pygame.sprite.spritecollideany(bullet, self.barriers):
                explosion = Explosion(bullet.rect.centerx, bullet.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                bullet.kill()
        
        # Check if all enemies are defeated
        if not self.enemies:
            self.level_num += 1
            self.level = Level(self.level_num)
            self.barriers = self.level.barriers
            self.all_sprites.add(self.barriers)
            self.spawn_enemies()
            # Repair player tank between levels
            self.player.health = 100
    
    def draw(self):
        # Fill screen with background color
        screen.fill(GRAY)
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw health bars for tanks
        self.player.draw_health(screen)
        for enemy in self.enemies:
            enemy.draw_health(screen)
        
        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level_num}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(level_text, (10, 70))
        
        # Draw game over message if game is over
        if self.game_over:
            game_over_font = pygame.font.SysFont('Arial', 64)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
            restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
            
            screen.blit(game_over_text, text_rect)
            screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()

# Main function
def main():
    # Set up the game
    game = Game()
    clock = pygame.time.Clock()
    
    # Game loop
    while game.running:
        # Handle events
        game.handle_events()
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Quit pygame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()