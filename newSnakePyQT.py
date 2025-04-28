import sys
import random
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
class Colors:
    BLACK = QColor(0, 0, 0)
    WHITE = QColor(255, 255, 255)
    GREEN = QColor(0, 200, 0)
    RED = QColor(255, 0, 0)
    BACKGROUND = QColor(15, 15, 40)
    SNAKE_BODY = QColor(126, 217, 87)
    SNAKE_SPOTS = QColor(98, 168, 68)
    EYE_WHITE = QColor(255, 255, 255)
    EYE_BLACK = QColor(0, 0, 0)
    OBSTACLE = QColor(128, 0, 128)

class Snake:
    def __init__(self):
        self.reset()
        self.time_counter = 0
        
    def reset(self):
        # Start in the middle of the screen
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT // 2
        self.body = [(self.x, self.y)]
        self.direction = (0, -1)  # Moving up initially
        self.grow_pending = 3  # Start with length 4
        
        # Snake appearance
        self.body_colors = [
            QColor(126, 217, 87),  # SNAKE_BODY
            QColor(116, 207, 77),
            QColor(136, 227, 97)
        ]
        self.spot_color = Colors.SNAKE_SPOTS
        self.eye_color = Colors.EYE_WHITE
        self.pupil_color = Colors.EYE_BLACK
    
    def change_direction(self, dir_x, dir_y):
        # Prevent 180-degree turns
        if (dir_x, dir_y) != (-self.direction[0], -self.direction[1]):
            self.direction = (dir_x, dir_y)
    
    def move(self):
        # Get current head position
        head_x, head_y = self.body[0]
        
        # Calculate new head position
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]
        
        # Insert new head at the beginning of the body list
        self.body.insert(0, (new_x, new_y))
        
        # Check if snake needs to grow
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            # Remove the tail if not growing
            self.body.pop()
        
        # Update time counter for animations
        self.time_counter += 0.1
        
        # Return new head position
        return new_x, new_y
    
    def check_collision(self):
        head_x, head_y = self.body[0]
        
        # Check wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Check self collision
        if (head_x, head_y) in self.body[1:]:
            return True
            
        return False
    
    def grow(self):
        self.grow_pending += 1
    
    def draw(self, painter):
        # Draw each segment of the snake
        for i, (x, y) in enumerate(self.body):
            # Calculate position for the segment
            pos_x = x * GRID_SIZE
            pos_y = y * GRID_SIZE
            
            # Determine segment color - alternate between different shades
            color_index = i % len(self.body_colors)
            segment_color = self.body_colors[color_index]
            
            # Add subtle wave effect to segments
            if i > 0:
                wave_offset = math.sin(self.time_counter + i * 0.3) * 2
                if self.direction[0] == 0:  # Moving vertically
                    pos_x += wave_offset
                else:  # Moving horizontally
                    pos_y += wave_offset
            
            # Calculate segment size
            if i == 0:  # Head
                segment_size = GRID_SIZE
            else:  # Body segments get slightly smaller toward tail
                tail_factor = max(0.7, 1.0 - (i / len(self.body) * 0.3))
                segment_size = int(GRID_SIZE * tail_factor)
            
            # Position adjustment for smaller segments
            pos_adjust = (GRID_SIZE - segment_size) // 2
            pos_x += pos_adjust
            pos_y += pos_adjust
            
            # Set brush for segment
            painter.setBrush(QBrush(segment_color))
            painter.setPen(Qt.NoPen)  # No outline
            
            # Draw segment as rounded rectangle
            painter.drawRoundedRect(int(pos_x), int(pos_y), segment_size, segment_size, 8, 8)
            
            # Add spots to some body segments for variety
            if i > 0 and i % 3 == 0:
                spot_size = segment_size // 3
                spot_x = int(pos_x + segment_size//2 - spot_size//2)
                spot_y = int(pos_y + segment_size//2 - spot_size//2)
                
                painter.setBrush(QBrush(self.spot_color))
                painter.drawRoundedRect(spot_x, spot_y, spot_size, spot_size, 4, 4)
        
        # Draw eyes on the head
        head_x, head_y = self.body[0]
        head_rect = QRect(head_x * GRID_SIZE, head_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        # Calculate eye positions based on direction
        eye_size = GRID_SIZE // 5
        pupil_size = eye_size // 2
        
        # Calculate eye positions based on direction
        if self.direction == (0, -1):  # Up
            left_eye_pos = QPoint(head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = QPoint(head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
        elif self.direction == (0, 1):  # Down
            left_eye_pos = QPoint(head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
            right_eye_pos = QPoint(head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        elif self.direction == (-1, 0):  # Left
            left_eye_pos = QPoint(head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = QPoint(head_x * GRID_SIZE + GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        else:  # Right
            left_eye_pos = QPoint(head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + GRID_SIZE // 3)
            right_eye_pos = QPoint(head_x * GRID_SIZE + 2 * GRID_SIZE // 3, head_y * GRID_SIZE + 2 * GRID_SIZE // 3)
        
        # Draw eyes
        painter.setBrush(QBrush(self.eye_color))
        painter.drawEllipse(left_eye_pos, eye_size, eye_size)
        painter.drawEllipse(right_eye_pos, eye_size, eye_size)
        
        # Draw pupils with slight offset in movement direction
        left_pupil_pos = QPoint(left_eye_pos.x() + self.direction[0] * 2, left_eye_pos.y() + self.direction[1] * 2)
        right_pupil_pos = QPoint(right_eye_pos.x() + self.direction[0] * 2, right_eye_pos.y() + self.direction[1] * 2)
        
        painter.setBrush(QBrush(self.pupil_color))
        painter.drawEllipse(left_pupil_pos, pupil_size, pupil_size)
        painter.drawEllipse(right_pupil_pos, pupil_size, pupil_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse_counter = 0
        self.pulse_direction = 1
        self.pulse_speed = 0.15
        
        # Available colors for food (main color, outline color)
        self.possible_colors = [
            (QColor(255, 215, 0), QColor(184, 134, 11)),   # Gold
            (QColor(50, 205, 50), QColor(34, 139, 34)),    # Green
            (QColor(30, 144, 255), QColor(0, 0, 139)),     # Blue
            (QColor(255, 105, 180), QColor(199, 21, 133)), # Pink
            (QColor(148, 0, 211), QColor(75, 0, 130)),     # Purple
            (QColor(255, 69, 0), QColor(178, 34, 34))      # Red-Orange
        ]
        self.spawn()
    
    def spawn(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
        # Choose a random color pair (main color and outline color)
        self.color, self.outline_color = random.choice(self.possible_colors)
    
    def update(self):
        # Update pulsing effect
        self.pulse_counter += self.pulse_speed * self.pulse_direction
        if self.pulse_counter > 5:
            self.pulse_direction = -1
        elif self.pulse_counter < 0:
            self.pulse_direction = 1
    
    def draw(self, painter):
        # Update pulsing effect
        self.update()
        
        # Calculate position and size
        x, y = self.position
        size_factor = 1.0 + (self.pulse_counter / 25)
        food_size = int(GRID_SIZE * 0.8 * size_factor)
        
        # Draw glow with the food's color but with transparency
        glow_size = int(food_size * 1.5)
        
        # Create glow color based on food color but with alpha
        glow_color = QColor(self.color)
        glow_color.setAlpha(40)  # Set alpha for transparency
        
        # Save current state
        painter.save()
        
        # Set up for drawing glow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_color))
        
        # Draw glow as circle
        glow_x = x * GRID_SIZE + (GRID_SIZE - glow_size) // 2
        glow_y = y * GRID_SIZE + (GRID_SIZE - glow_size) // 2
        painter.drawEllipse(glow_x, glow_y, glow_size, glow_size)
        
        # Draw main food
        rect_x = x * GRID_SIZE + (GRID_SIZE - food_size) // 2
        rect_y = y * GRID_SIZE + (GRID_SIZE - food_size) // 2
        
        # Draw coin
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(rect_x, rect_y, food_size, food_size)
        
        # Draw outline
        painter.setPen(QPen(self.outline_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect_x, rect_y, food_size, food_size)
        
        # Add R text
        font_size = max(10, food_size // 2)
        font = QFont("Arial", font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(Colors.BLACK))
        
        text_rect = QRect(rect_x, rect_y, food_size, food_size)
        painter.drawText(text_rect, Qt.AlignCenter, "R")
        
        # Add shine
        shine_size = max(3, food_size // 6)
        shine_x = rect_x + food_size // 4
        shine_y = rect_y + food_size // 4
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Colors.WHITE))
        painter.drawEllipse(shine_x, shine_y, shine_size, shine_size)
        
        # Restore state
        painter.restore()

class Obstacle:
    def __init__(self):
        self.positions = []
        self.color = Colors.OBSTACLE
    
    def add_obstacle(self, x, y):
        self.positions.append((x, y))
    
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        
        for x, y in self.positions:
            painter.drawRect(
                x * GRID_SIZE, 
                y * GRID_SIZE, 
                GRID_SIZE, 
                GRID_SIZE
            )

def generate_obstacles(level):
    obstacles = Obstacle()
    # More obstacles as level increases
    num_obstacles = min(level * 5, 50)  # Cap at 50 obstacles
    
    # Create obstacles near edges
    for _ in range(num_obstacles):
        side = random.choice(["left", "right"])
        if side == "left":
            x = random.randint(0, GRID_WIDTH // 4)
        else:
            x = random.randint(3 * GRID_WIDTH // 4, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        obstacles.add_obstacle(x, y)
    
    return obstacles

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        self.twinkle_offset = random.randint(0, 100)  # For varied twinkling
    
    def draw(self, painter, time_ms):
        # Simple twinkling effect
        if (self.twinkle_offset + time_ms // 200) % 20 == 0:
            size = self.size + 1
        else:
            size = self.size
            
        color = QColor(self.brightness, self.brightness, self.brightness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self.x - size//2, self.y - size//2, size, size)

class GameWidget(QWidget):
    def __init__(self, parent=None):
        super(GameWidget, self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)  # To receive keyboard events
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize game objects
        self.snake = Snake()
        self.food = Food()
        self.obstacles = generate_obstacles(1)
        
        # Game state variables
        self.score = 0
        self.level = 1
        self.game_over = False
        
        # Create stars for background
        self.stars = [Star() for _ in range(100)]
        
        # Game timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        
        # Make sure food doesn't spawn on obstacles or snake
        self.respawn_food()
        
        # Start the game
        self.speed = 8  # Initial frames per second
        self.timer.start(1000 // self.speed)  # Convert to milliseconds
        
        # Time counter for animations
        self.time_counter = 0
    
    def respawn_food(self):
        while True:
            self.food.spawn()
            if (self.food.position not in self.snake.body and 
                self.food.position not in self.obstacles.positions):
                break
    
    def update_game(self):
        if not self.game_over:
            # Move snake
            self.snake.move()
            
            # Check for food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.score += 10  # Increase score
                
                # Level up every 100 points
                if self.score % 100 == 0:
                    self.level += 1
                    self.obstacles = generate_obstacles(self.level)
                    # Increase speed with level
                    self.speed = min(8 + self.level, 20)  # Cap at 20 fps
                    self.timer.start(1000 // self.speed)  # Update timer
                
                # Respawn food
                self.respawn_food()
            
            # Check for collision with walls, self, or obstacles
            if (self.snake.check_collision() or 
                self.snake.body[0] in self.obstacles.positions):
                self.game_over = True
        
        # Increment time counter for animations
        self.time_counter += 1
        
        # Update the widget
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), Colors.BACKGROUND)
        
        # Draw stars
        for star in self.stars:
            star.draw(painter, self.time_counter * 100)
        
        # Draw game elements
        self.obstacles.draw(painter)
        self.food.draw(painter)
        self.snake.draw(painter)
        
        # Draw score and level
        painter.setPen(QPen(Colors.WHITE))
        font = QFont("Arial", 20)
        painter.setFont(font)
        painter.drawText(10, 30, f"Score: {self.score}")
        painter.drawText(10, 60, f"Level: {self.level}")
        
        # Draw game over screen if needed
        if self.game_over:
            # Create overlay
            overlay = QColor(0, 0, 0, 180)
            painter.fillRect(self.rect(), overlay)
            
            # Draw game over text
            font = QFont("Arial", 36, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QPen(Colors.WHITE))
            
            text_rect = QRect(0, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH, 50)
            painter.drawText(text_rect, Qt.AlignCenter, "GAME OVER")
            
            font = QFont("Arial", 20)
            painter.setFont(font)
            
            score_rect = QRect(0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, 40)
            painter.drawText(score_rect, Qt.AlignCenter, f"Final Score: {self.score}")
            
            restart_rect = QRect(0, SCREEN_HEIGHT // 2 + 80, SCREEN_WIDTH, 40)
            painter.drawText(restart_rect, Qt.AlignCenter, "Press SPACE to restart")
            
            quit_rect = QRect(0, SCREEN_HEIGHT // 2 + 120, SCREEN_WIDTH, 40)
            painter.drawText(quit_rect, Qt.AlignCenter, "Press ESC to quit")
    
    def keyPressEvent(self, event):
        # Direction controls
        if not self.game_over:
            if event.key() == Qt.Key_Up:
                self.snake.change_direction(0, -1)
            elif event.key() == Qt.Key_Down:
                self.snake.change_direction(0, 1)
            elif event.key() == Qt.Key_Left:
                self.snake.change_direction(-1, 0)
            elif event.key() == Qt.Key_Right:
                self.snake.change_direction(1, 0)
        
        # Game controls
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space and self.game_over:
            # Reset game
            self.snake.reset()
            self.score = 0
            self.level = 1
            self.obstacles = generate_obstacles(self.level)
            self.respawn_food()
            self.game_over = False
            self.speed = 8  # Reset speed
            self.timer.start(1000 // self.speed)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("Vertical Snake")
        self.game_widget = GameWidget()
        self.setCentralWidget(self.game_widget)
        
        # Set fixed size for window
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())