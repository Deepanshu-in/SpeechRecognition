import sys
import math
import random
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

# Colors
BLACK = QColor(0, 0, 0)
WHITE = QColor(255, 255, 255)
GREEN = QColor(0, 255, 0)
RED = QColor(255, 0, 0)
BLUE = QColor(0, 0, 255)
BROWN = QColor(139, 69, 19)
GRAY = QColor(128, 128, 128)
DARK_GREEN = QColor(0, 180, 0)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Vector2 class
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def copy(self):
        return Vector2(self.x, self.y)
    
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)
    
    def rotate(self, angle_degrees):
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        self.x = x
        self.y = y
        return self

# Tank class
class Tank:
    def __init__(self, x, y, color, is_player=False):
        self.position = Vector2(x, y)
        self.direction = Vector2(0, -1)  # Facing up initially
        self.speed = 3 if is_player else 1
        self.angle = 0
        self.is_player = is_player
        self.health = 100
        self.reload_time = 0
        self.shoot_delay = 30 if is_player else 90
        self.color = color
        self.width = 40
        self.height = 40
        self.rect = QRectF(x - self.width/2, y - self.height/2, self.width, self.height)
    
    def update(self, barriers, keys_pressed):
        # Store previous position to revert if collision occurs
        prev_pos = self.position.copy()
        
        if self.is_player:
            # Player controls with arrow keys
            if Qt.Key_Up in keys_pressed:
                # Recalculate direction vector based on current angle for forward movement
                forward_dir = Vector2(0, -1).rotate(-self.angle)
                self.position = self.position + forward_dir * self.speed
            if Qt.Key_Down in keys_pressed:
                # Recalculate direction vector based on current angle for backward movement
                forward_dir = Vector2(0, -1).rotate(-self.angle)
                self.position = self.position - forward_dir * self.speed
            if Qt.Key_Left in keys_pressed:
                self.angle += 2
                # Update direction vector after rotation
                self.direction = Vector2(0, -1).rotate(-self.angle)
            if Qt.Key_Right in keys_pressed:
                self.angle -= 2
                # Update direction vector after rotation
                self.direction = Vector2(0, -1).rotate(-self.angle)
            
            # Update reload timer
            if self.reload_time > 0:
                self.reload_time -= 1
        else:
            if random.randint(0, 100) < 3:  # 3% chance to change direction
                angle_change = random.randint(-20, 20)
                self.angle += angle_change
                self.direction.rotate(angle_change)
            
            # Move forward
            if random.randint(0, 100) < 70:  # 70% chance to move
                self.position = self.position + self.direction * self.speed
                
            # Update reload timer
            if self.reload_time > 0:
                self.reload_time -= 1
        
        # Update rectangle position
        self.rect = QRectF(self.position.x - self.width/2, self.position.y - self.height/2, 
                          self.width, self.height)
        
        # Check for collisions with barriers
        for barrier in barriers:
            if self.rect.intersects(barrier.rect):
                # Revert position if collision
                self.position = prev_pos
                self.rect = QRectF(self.position.x - self.width/2, self.position.y - self.height/2, 
                                  self.width, self.height)
                
                # For enemies, change direction when hitting barriers
                if not self.is_player:
                    angle_change = random.randint(90, 180)
                    self.angle += angle_change
                    self.direction.rotate(angle_change)
                break
        
        # Keep tank on screen
        if self.position.x - self.width/2 < 0:
            self.position.x = self.width/2
        if self.position.x + self.width/2 > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - self.width/2
        if self.position.y - self.height/2 < 0:
            self.position.y = self.height/2
        if self.position.y + self.height/2 > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT - self.height/2
        
        self.rect = QRectF(self.position.x - self.width/2, self.position.y - self.height/2, 
                          self.width, self.height)
    
    def shoot(self):
        if self.reload_time <= 0:
            self.reload_time = self.shoot_delay
            # Recalculate the direction vector based on current angle
            # This ensures bullets always go in the direction the tank is facing
            direction = Vector2(0, -1).rotate(-self.angle)
            
            # Create bullet starting at the tank's position + direction
            bullet_pos = self.position + direction * 30
            return Bullet(bullet_pos.x, bullet_pos.y, direction, self.is_player)
        return None

    def draw(self, painter):
        # Save the current painter state
        painter.save()
        
        # Translate and rotate
        painter.translate(self.position.x, self.position.y)
        painter.rotate(-self.angle)
        
        if self.is_player:  # Player tank (green)
            # Tank body
            painter.setBrush(QBrush(GREEN))
            painter.setPen(Qt.NoPen)
            body_rect = QRectF(-17, -12, 34, 24)
            painter.drawRoundedRect(body_rect, 3, 3)
            
            # Tank turret base
            painter.drawEllipse(QPointF(0, -5), 10, 10)
            
            # Tank gun
            gun_rect = QRectF(-5, -25, 10, 25)
            painter.drawRect(gun_rect)
            
            # Tank details dark green accents
            painter.setBrush(QBrush(DARK_GREEN))
            
            # Cannon tip
            painter.drawRect(QRectF(-5, -25, 10, 5))
            
            # Tank hatches
            painter.drawEllipse(QPointF(0, -5), 5, 5)
            
            # Tracks
            painter.setBrush(QBrush(BLACK))
            painter.drawRect(QRectF(-20, -15, 5, 30))
            painter.drawRect(QRectF(15, -15, 5, 30))
            
            # Track details
            painter.setPen(QPen(GRAY, 1))
            for i in range(-15, 15, 5):
                painter.drawLine(QPointF(-20, i), QPointF(-15, i))
                painter.drawLine(QPointF(15, i), QPointF(20, i))
        else:  # Enemy tank (red)
            # Tank body
            painter.setBrush(QBrush(self.color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(-15, -10, 30, 20))  # Tank body
            painter.drawRect(QRectF(-5, -15, 10, 30))   # Tank turret
            
            # Tracks
            painter.setBrush(QBrush(BLACK))
            painter.drawRect(QRectF(-20, -15, 5, 30))   # Left track
            painter.drawRect(QRectF(15, -15, 5, 30))    # Right track
        
        # Restore the painter state
        painter.restore()
        
        # Draw health bar
        self.draw_health(painter)
    
    def draw_health(self, painter):
        # Draw health bar above the tank
        bar_length = 30
        bar_height = 5
        fill = (self.health / 100) * bar_length
        
        # Health bar position
        x = self.position.x - bar_length / 2
        y = self.position.y - self.height / 2 - 10
        
        # Green health bar for player, red for enemies
        health_color = GREEN if self.is_player else RED
        
        # Draw filled part
        painter.setBrush(QBrush(health_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(x, y, fill, bar_height))
        
        # Draw outline
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(WHITE, 1))
        painter.drawRect(QRectF(x, y, bar_length, bar_height))

# Bullet class
class Bullet:
    def __init__(self, x, y, direction, is_player_bullet):
        self.position = Vector2(x, y)
        self.direction = direction.normalize()
        self.speed = 5
        self.is_player_bullet = is_player_bullet
        self.damage = 25
        self.radius = 4
        self.rect = QRectF(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
    
    def update(self):
        # Move bullet
        self.position = self.position + self.direction * self.speed
        self.rect = QRectF(self.position.x - self.radius, self.position.y - self.radius, 
                          self.radius * 2, self.radius * 2)
        
        # Check if bullet is off screen
        if (self.position.x - self.radius < 0 or 
            self.position.x + self.radius > SCREEN_WIDTH or 
            self.position.y - self.radius < 0 or 
            self.position.y + self.radius > SCREEN_HEIGHT):
            return False  # Bullet should be removed
        
        return True  # Bullet is still valid
    
    def draw(self, painter):
        color = BLUE if self.is_player_bullet else RED
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(self.position.x, self.position.y), self.radius, self.radius)

# Barrier class
class Barrier:
    def __init__(self, x, y, width, height):
        self.rect = QRectF(x, y, width, height)
    
    def draw(self, painter):
        painter.setBrush(QBrush(BROWN))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect)

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.max_size = 20
        self.current_size = 1
        self.growth_rate = 4
        self.shrink_rate = 2
        self.growing = True
        self.done = False
    
    def update(self):
        if self.growing:
            self.current_size += self.growth_rate
            if self.current_size >= self.max_size:
                self.growing = False
        else:
            self.current_size -= self.shrink_rate
            if self.current_size <= 0:
                self.done = True
                return False
        
        return True
    
    def draw(self, painter):
        # Create gradient color from yellow to red
        painter.setBrush(QBrush(QColor(255, 100, 0, 200)))  # Orange with transparency
        painter.setPen(QPen(QColor(255, 0, 0), 2))  # Red outline
        
        # Draw the explosion circle
        painter.drawEllipse(QPointF(self.position.x, self.position.y), 
                           self.current_size, self.current_size)
        
        # Inner glow
        painter.setBrush(QBrush(QColor(255, 255, 0, 150)))  # Yellow with transparency
        painter.setPen(Qt.NoPen)
        inner_size = max(2, self.current_size * 0.6)
        painter.drawEllipse(QPointF(self.position.x, self.position.y), 
                           inner_size, inner_size)

# Level class
class Level:
    def __init__(self, level_num):
        self.barriers = []
        self.level_num = level_num
        self.create_level()
    
    def create_level(self):
        # Border walls
        wall_thickness = 20
        # Top
        self.barriers.append(Barrier(0, 0, SCREEN_WIDTH, wall_thickness))
        # Bottom
        self.barriers.append(Barrier(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness))
        # Left
        self.barriers.append(Barrier(0, 0, wall_thickness, SCREEN_HEIGHT))
        # Right
        self.barriers.append(Barrier(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT))
        
        # Add more barriers based on level
        if self.level_num == 1:
            # Level 1 barriers
            self.barriers.append(Barrier(200, 150, 100, 30))
            self.barriers.append(Barrier(400, 300, 30, 150))
            self.barriers.append(Barrier(100, 450, 200, 30))
        elif self.level_num == 2:
            # Level 2 barriers
            self.barriers.append(Barrier(150, 100, 30, 200))
            self.barriers.append(Barrier(300, 250, 200, 30))
            self.barriers.append(Barrier(600, 150, 30, 300))
            self.barriers.append(Barrier(400, 450, 300, 30))
        elif self.level_num >= 3:
            # Random barriers for levels 3+
            for _ in range(10):
                x = random.randint(50, SCREEN_WIDTH - 100)
                y = random.randint(50, SCREEN_HEIGHT - 100)
                width = random.randint(30, 150)
                height = random.randint(30, 100)
                self.barriers.append(Barrier(x, y, width, height))
        
        return self.barriers

# Game Window class
class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Game state
        self.running = True
        self.game_over = False
        self.level_num = 1
        self.score = 0
        self.lives = 3
        
        # Game objects
        self.player = None
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.barriers = []
        
        # Keys currently pressed
        self.keys_pressed = set()
        
        # Set up the game window
        self.setWindowTitle("Tank Battle")
        self.setGeometry(100, 100, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize game
        self.init_game()
        
        # Set up timer for game loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)  # ~60 FPS
    
    def init_game(self):
        # Create player tank
        self.player = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, GREEN, is_player=True)
        
        # Initialize level
        self.level = Level(self.level_num)
        self.barriers = self.level.barriers
        
        # Add enemies
        self.spawn_enemies()
    
    def spawn_enemies(self):
        # Clear any existing enemies
        self.enemies = []
        
        # Add enemies based on level
        num_enemies = min(2 + self.level_num, 8)  # Max 8 enemies
        
        for i in range(num_enemies):
            # Place enemies away from player and other enemies
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, 250)  # Keep enemies on the upper part
                
                # Check if position is good (away from barriers and other enemies)
                valid_position = True
                temp_tank = Tank(x, y, RED)
                
                # Check collision with barriers
                for barrier in self.barriers:
                    if temp_tank.rect.intersects(barrier.rect):
                        valid_position = False
                        break
                
                # Check collision with other enemies
                for enemy in self.enemies:
                    if temp_tank.rect.intersects(enemy.rect):
                        valid_position = False
                        break
                
                if valid_position:
                    enemy = Tank(x, y, RED)
                    self.enemies.append(enemy)
                    break
    
    def keyPressEvent(self, event):
        key = event.key()
        self.keys_pressed.add(key)
        
        # Handle shooting
        if key == Qt.Key_Space and not event.isAutoRepeat():
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)
        
        # Handle restart
        if key == Qt.Key_R and self.game_over:
            self.restart_game()
        
        # Handle escape to quit
        if key == Qt.Key_Escape:
            self.close()
    
    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat() and event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
    
    def restart_game(self):
        self.game_over = False
        self.level_num = 1
        self.score = 0
        self.lives = 3
        self.bullets = []
        self.explosions = []
        self.init_game()
    
    def game_loop(self):
        if not self.game_over:
            self.update_game()
        self.update()  # Trigger paintEvent
    
    def update_game(self):
        # Update player
        self.player.update(self.barriers, self.keys_pressed)
        
        # Update enemies
        for enemy in self.enemies[:]:  # Use a copy of the list for safe iteration
            enemy.update(self.barriers, set())  # Empty set for keys
            
            # Enemy shooting (random)
            if random.randint(0, 100) < 2:  # 2% chance to shoot per frame
                bullet = enemy.shoot()
                if bullet:
                    self.bullets.append(bullet)
        
        # Update bullets and check collisions
        for bullet in self.bullets[:]:  # Use a copy of the list for safe iteration
            if not bullet.update():  # Bullet is off-screen
                self.bullets.remove(bullet)
                continue
            
            # Check collisions with barriers
            bullet_hit_barrier = False
            for barrier in self.barriers:
                if bullet.rect.intersects(barrier.rect):
                    self.explosions.append(Explosion(bullet.position.x, bullet.position.y))
                    if bullet in self.bullets:  # Check if bullet hasn't been removed yet
                        self.bullets.remove(bullet)
                    bullet_hit_barrier = True
                    break
            
            if bullet_hit_barrier:
                continue
            
            # Player bullets hitting enemies
            if bullet.is_player_bullet:
                for enemy in self.enemies[:]:  # Use a copy of the list for safe iteration
                    if bullet.rect.intersects(enemy.rect):
                        enemy.health -= bullet.damage
                        self.explosions.append(Explosion(bullet.position.x, bullet.position.y))
                        if bullet in self.bullets:  # Check if bullet hasn't been removed yet
                            self.bullets.remove(bullet)
                        
                        # Check if enemy is destroyed
                        if enemy.health <= 0:
                            self.score += 100
                            self.explosions.append(Explosion(enemy.position.x, enemy.position.y))
                            self.enemies.remove(enemy)
                        break
            
            # Enemy bullets hitting player
            else:
                if bullet.rect.intersects(self.player.rect):
                    self.player.health -= bullet.damage
                    self.explosions.append(Explosion(bullet.position.x, bullet.position.y))
                    if bullet in self.bullets:  # Check if bullet hasn't been removed yet
                        self.bullets.remove(bullet)
                    
                    # Check if player is destroyed
                    if self.player.health <= 0:
                        self.lives -= 1
                        self.explosions.append(Explosion(self.player.position.x, self.player.position.y))
                        
                        if self.lives <= 0:
                            self.game_over = True
                        else:
                            # Respawn player
                            self.player.health = 100
                            self.player.position.x = SCREEN_WIDTH // 2
                            self.player.position.y = SCREEN_HEIGHT - 100
                            self.player.angle = 0
                            self.player.direction = Vector2(0, -1)
        
        # Update explosions
        for explosion in self.explosions[:]:  # Use a copy of the list for safe iteration
            if not explosion.update():  # Explosion animation is done
                self.explosions.remove(explosion)
        
        # Check if all enemies are defeated
        if not self.enemies:
            self.level_num += 1
            self.level = Level(self.level_num)
            self.barriers = self.level.barriers
            self.spawn_enemies()
            # Repair player tank between levels
            self.player.health = 100
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), GRAY)
        
        # Draw barriers
        for barrier in self.barriers:
            barrier.draw(painter)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(painter)
        
        # Draw player and enemies
        self.player.draw(painter)
        for enemy in self.enemies:
            enemy.draw(painter)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(painter)
        
        # Draw HUD (score, lives, level)
        painter.setPen(QPen(WHITE))
        painter.setFont(QFont('Arial', 12))
        
        painter.drawText(10, 20, f"Score: {self.score}")
        painter.drawText(10, 40, f"Lives: {self.lives}")
        painter.drawText(10, 60, f"Level: {self.level_num}")
        
        # Draw game over message if game is over
        if self.game_over:
            painter.setPen(QPen(RED))
            painter.setFont(QFont('Arial', 32, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, "GAME OVER")
            
            painter.setPen(QPen(WHITE))
            painter.setFont(QFont('Arial', 16))
            painter.drawText(QRectF(0, SCREEN_HEIGHT/2 + 40, SCREEN_WIDTH, 30), 
                             Qt.AlignCenter, "Press R to restart")

# Main function
def main():
    app = QApplication(sys.argv)
    game = GameWindow()
    game.show()
    sys.exit(app.exec_())

# Run the game
if __name__ == "__main__":
    main()