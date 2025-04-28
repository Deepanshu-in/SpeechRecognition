import sys
import math
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPolygon
from PyQt5.QtCore import QPoint


class MarsRoverGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initGame()
        
    def initUI(self):
        self.setWindowTitle("Mars Rover Race")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        # Set up game timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(1000 // 60)
        
        # Set up keyboard handling
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.show()
    
    def initGame(self):
        # Colors
        self.BLACK = QColor(0, 0, 0)
        self.WHITE = QColor(255, 255, 255)
        self.RED = QColor(255, 0, 0)
        self.BLUE = QColor(0, 0, 255)
        self.GRAY = QColor(100, 100, 100)
        self.DARK_GRAY = QColor(50, 50, 50)
        self.LIGHT_GRAY = QColor(180, 180, 180)
        self.MARS_RED = QColor(212, 106, 76)
        self.DARK_MARS_RED = QColor(150, 70, 50)
        self.YELLOW = QColor(255, 255, 0)
        self.GREEN = QColor(34, 139, 34)
        self.PURPLE = QColor(75, 0, 130)
        self.DARK_ORANGE = QColor(180, 60, 10)
        self.GOLD = QColor(255, 215, 0)
        self.ORANGE = QColor(255, 140, 0)
        self.RUST = QColor(183, 65, 14)
        
        # Game state
        self.moving = False
        self.score = 0
        self.fuel = 100
        self.game_over = False
        
        # Car properties
        self.car_scale = 0.6
        self.car_width = int(400 * self.car_scale)
        self.car_height = int(80 * self.car_scale)
        self.car_cabin_height = int(60 * self.car_scale)
        self.wheel_radius = int(40 * self.car_scale)
        self.wheel_rim_radius = int(20 * self.car_scale)
        
        # Car position
        self.car_x = self.width() // 2 - self.car_width // 2
        self.car_pos_x = self.car_x - 25
        self.car_pos_y = 430 - self.wheel_radius - (self.car_height + self.car_cabin_height) * 0.85
        self.car_ground_y = 430
        self.car_angle = 0
        
        # Terrain properties
        self.terrain_speed = 3
        self.terrain_offset = 0
        self.terrain_resolution = 5
        self.current_speed = 0
        
        # Martian crystal properties
        self.crystals = []
        self.crystal_radius = 10
        self.crystal_spawn_chance = 0.05
        self.crystal_animation_offset = 0
        self.crystal_pulse_speed = 0.1
        
        # Fuel canister properties
        self.fuel_tanks = []
        self.fuel_tank_width = 40
        self.fuel_tank_height = 30
        self.fuel_spawn_chance = 0.007
        
        # Star properties
        self.stars = []
        for _ in range(100):
            star_x = random.randint(0, self.width())
            star_y = random.randint(0, self.height() // 2)
            star_size = random.uniform(0.5, 3)
            star_brightness = random.randint(150, 255)
            self.stars.append([star_x, star_y, star_size, star_brightness, random.random() * 6.28])
        
        # Moon properties (Mars has two moons: Phobos and Deimos)
        self.moons = [
            {"x": 650, "y": 70, "radius": 15, "color": QColor(170, 150, 140)},   # Phobos
            {"x": 550, "y": 100, "radius": 10, "color": QColor(160, 140, 130)}   # Deimos
        ]
        
        # Earth properties
        self.earth_angle = 0
        
        # Generate initial terrain
        self.terrain_points = self.generate_terrain(self.terrain_offset)
        
        # Key state
        self.keys_pressed = {}
    
    def generate_terrain(self, offset):
        terrain_points = []
        for x in range(0, self.width() + self.terrain_resolution, self.terrain_resolution):
            # Create a rougher terrain for Mars
            base_height = 430 + 10 * math.sin((x + offset) * 0.01)
            
            # Add more undulations for Mars' craterous terrain
            minor_undulation = 5 * math.sin((x + offset) * 0.05)
            secondary_undulation = 3 * math.sin((x + offset) * 0.08)
            
            y = base_height + minor_undulation + secondary_undulation
            terrain_points.append((x, y))
        return terrain_points
    
    def spawn_crystal(self, offset):
        x = self.width() + offset
        terrain_idx = min(int(x // self.terrain_resolution), len(self.terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(self.terrain_points):
            y = self.terrain_points[terrain_idx][1] - 30
            self.crystals.append([x, y])
    
    def spawn_fuel_tank(self, offset):
        x = self.width() + offset
        terrain_idx = min(int(x // self.terrain_resolution), len(self.terrain_points) - 2)
        if terrain_idx >= 0 and terrain_idx < len(self.terrain_points):
            y = self.terrain_points[terrain_idx][1] - self.fuel_tank_height - 10
            self.fuel_tanks.append([x, y])
    
    def update_game(self):
        # Update terrain offset based on movement
        if not self.game_over:
            self.terrain_offset += self.current_speed
        
        # Generate terrain with current offset
        self.terrain_points = self.generate_terrain(self.terrain_offset)
        
        # Decrease fuel when moving
        if self.moving and not self.game_over:
            self.fuel -= 0.1
            if self.fuel <= 0:
                self.fuel = 0
                self.game_over = True
                self.moving = False
        
        # Randomly spawn crystals
        if self.moving and not self.game_over and random.random() < self.crystal_spawn_chance:
            self.spawn_crystal(random.randint(0, 200))
        
        # Randomly spawn fuel tanks
        if self.moving and not self.game_over and random.random() < self.fuel_spawn_chance:
            self.spawn_fuel_tank(random.randint(0, 200))
        
        # Update animations
        self.crystal_animation_offset += self.crystal_pulse_speed
        self.earth_angle = (self.earth_angle + 0.002) % (2 * math.pi)
        
        # Initialize car position variables if not already set
        if not hasattr(self, 'car_pos_x'):
            self.car_pos_x = 0
        if not hasattr(self, 'car_pos_y'):
            self.car_pos_y = 0
        if not hasattr(self, 'car_ground_y'):
            self.car_ground_y = 430
        if not hasattr(self, 'car_angle'):
            self.car_angle = 0
            
        # Calculate car's position on terrain
        car_center_x = self.car_x + self.car_width / 2
        terrain_idx = min(car_center_x // self.terrain_resolution, len(self.terrain_points) - 2)
        terrain_idx = max(0, int(terrain_idx))  # Ensure positive integer
        
        if terrain_idx >= 0 and terrain_idx < len(self.terrain_points) - 1:
            x1, y1 = self.terrain_points[terrain_idx]
            x2, y2 = self.terrain_points[terrain_idx + 1]
            
            # Linear interpolation to find exact y position
            self.car_ground_y = y1 + (y2 - y1) * ((car_center_x - x1) / (x2 - x1)) if x2 != x1 else y1
            
            # Calculate car angle based on terrain slope
            if x2 != x1:
                slope = (y2 - y1) / (x2 - x1)
                self.car_angle = math.degrees(math.atan(slope))
            else:
                self.car_angle = 0
        else:
            self.car_ground_y = 430
            self.car_angle = 0
            
        # Calculate car's position and center for collision detection
        self.car_pos_x = self.car_x - 25
        self.car_pos_y = self.car_ground_y - self.wheel_radius - (self.car_height + self.car_cabin_height) * 0.85
        
        # Calculate car's true center for collision detection
        car_center_y = self.car_pos_y + (self.car_height + self.car_cabin_height) / 2
        
        # Create a collision rectangle for the car
        car_collision_width = self.car_width * 0.8
        car_collision_height = (self.car_height + self.car_cabin_height) * 0.7
        car_collision_rect = QRect(
            int(car_center_x - car_collision_width/2),
            int(car_center_y - car_collision_height/2),
            int(car_collision_width),
            int(car_collision_height)
        )
        
        # Update crystal positions and check for collection
        i = 0
        while i < len(self.crystals):
            self.crystals[i][0] -= self.current_speed
            
            # Check if car collects crystal
            crystal_rect = QRect(
                int(self.crystals[i][0] - self.crystal_radius),
                int(self.crystals[i][1] - self.crystal_radius),
                self.crystal_radius * 2,
                self.crystal_radius * 2
            )
            
            if car_collision_rect.intersects(crystal_rect):
                self.score += 1
                self.crystals.pop(i)
            # Remove crystals that have gone off screen
            elif self.crystals[i][0] < -2 * self.crystal_radius:
                self.crystals.pop(i)
            else:
                i += 1
        
        # Update fuel tank positions and check for collection
        i = 0
        while i < len(self.fuel_tanks):
            self.fuel_tanks[i][0] -= self.current_speed
            
            # Check if car collects fuel tank
            tank_rect = QRect(
                int(self.fuel_tanks[i][0]),
                int(self.fuel_tanks[i][1]),
                self.fuel_tank_width,
                self.fuel_tank_height
            )
            
            if car_collision_rect.intersects(tank_rect):
                self.fuel = min(100, self.fuel + 30)
                self.fuel_tanks.pop(i)
            elif self.fuel_tanks[i][0] < -self.fuel_tank_width:
                self.fuel_tanks.pop(i)
            else:
                i += 1
        
        # Update speed based on key presses
        if self.moving and not self.game_over:
            if Qt.Key_Right in self.keys_pressed and self.keys_pressed[Qt.Key_Right]:
                self.current_speed = self.terrain_speed * 1.5
            elif Qt.Key_Left in self.keys_pressed and self.keys_pressed[Qt.Key_Left]:
                self.current_speed = -self.terrain_speed / 2
            else:
                self.current_speed = self.terrain_speed
        else:
            self.current_speed = 0
        
        # Trigger repaint
        self.update()
    
    def keyPressEvent(self, event):
        self.keys_pressed[event.key()] = True
        
        if event.key() == Qt.Key_Space and not self.game_over:
            self.moving = not self.moving
        elif event.key() == Qt.Key_R and self.game_over:
            # Reset game
            self.initGame()
    
    def keyReleaseEvent(self, event):
        self.keys_pressed[event.key()] = False
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill the background with dark orange-red for Martian sky
        painter.fillRect(0, 0, self.width(), self.height(), self.DARK_ORANGE)
        
        # Draw stars
        for star_x, star_y, star_size, star_brightness, star_phase in self.stars:
            # Make stars twinkle
            twinkle = math.sin(star_phase * 10 + self.crystal_animation_offset) * 30 + 225
            color = QColor(int(min(star_brightness, twinkle)), 
                          int(min(star_brightness - 30, twinkle - 30)), 
                          int(min(star_brightness - 60, twinkle - 60)))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(star_x), int(star_y), int(star_size), int(star_size))
        
        # Draw moons
        for moon in self.moons:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(moon["color"]))
            painter.drawEllipse(moon["x"] - moon["radius"], moon["y"] - moon["radius"], 
                              moon["radius"] * 2, moon["radius"] * 2)
            
            # Add highlight
            highlight_x = moon["x"] - moon["radius"] * 0.3
            highlight_y = moon["y"] - moon["radius"] * 0.3
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawEllipse(int(highlight_x) - 2, int(highlight_y) - 2, 4, 4)
        
        # Draw Earth
        earth_x = 100
        earth_y = 80
        earth_radius = 8
        painter.setBrush(QBrush(QColor(100, 150, 255)))
        painter.drawEllipse(earth_x - earth_radius, earth_y - earth_radius, 
                          earth_radius * 2, earth_radius * 2)
        
        # Draw Mars surface
        painter.fillRect(0, 450, self.width(), self.height() - 450, self.DARK_MARS_RED)
        
        # Draw terrain
        terrain_polygon = QPolygon()
        for x, y in self.terrain_points:
            terrain_polygon.append(QPoint(int(x), int(y)))
        terrain_polygon.append(QPoint(self.width(), self.height()))
        terrain_polygon.append(QPoint(0, self.height()))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.MARS_RED))
        painter.drawPolygon(terrain_polygon)
        
        # Draw craters
        painter.setPen(QPen(self.DARK_MARS_RED, 1))
        painter.setBrush(Qt.NoBrush)
        for i in range(10):
            crater_x = (i * self.width() // 10 + int(self.terrain_offset // 3)) % self.width()
            crater_y = random.randint(470, self.height() - 10)
            crater_radius = random.randint(5, 15)
            painter.drawEllipse(crater_x - crater_radius, crater_y - crater_radius, 
                              crater_radius * 2, crater_radius * 2)
        
        # Draw crystals
        for crystal_x, crystal_y in self.crystals:
            self.draw_animated_crystal(painter, crystal_x, crystal_y)
        
        # Draw fuel tanks
        for tank_x, tank_y in self.fuel_tanks:
            self.draw_fuel_tank(painter, tank_x, tank_y)
        
        # Draw the Mars rover
        self.draw_rover(painter)
        
        # Draw UI elements
        self.draw_ui(painter)
    
    def draw_animated_crystal(self, painter, x, y):
        # Draw Martian crystal
        glow_size = self.crystal_radius + 2 + math.sin(self.crystal_animation_offset) * 1.5
        
        painter.setPen(QPen(QColor(255, 150, 50, 100), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(int(x - glow_size), int(y - glow_size), int(glow_size * 2), int(glow_size * 2))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 130, 50)))
        painter.drawEllipse(int(x - self.crystal_radius), int(y - self.crystal_radius), 
                          self.crystal_radius * 2, self.crystal_radius * 2)
        
        inner_radius = self.crystal_radius - 2 + math.sin(self.crystal_animation_offset) * 1
        painter.setBrush(QBrush(QColor(255, 160, 90)))
        painter.drawEllipse(int(x - inner_radius), int(y - inner_radius), 
                          int(inner_radius * 2), int(inner_radius * 2))
        
        # Crystal shine effect
        shine_angle = self.crystal_animation_offset * 2 % (2 * math.pi)
        shine_x = x + math.cos(shine_angle) * (self.crystal_radius * 0.5)
        shine_y = y + math.sin(shine_angle) * (self.crystal_radius * 0.5)
        painter.setBrush(QBrush(self.WHITE))
        painter.drawEllipse(int(shine_x - 1), int(shine_y - 1), 2, 2)
    
    def draw_fuel_tank(self, painter, x, y):
        # Mars fuel canister
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.ORANGE))
        painter.drawRoundedRect(int(x), int(y), self.fuel_tank_width, self.fuel_tank_height, 5, 5)
        
        # Metallic edge
        painter.setPen(QPen(self.DARK_GRAY, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(int(x), int(y), self.fuel_tank_width, self.fuel_tank_height, 5, 5)
        
        # Fuel level window
        window_width = self.fuel_tank_width * 0.6
        window_height = self.fuel_tank_height * 0.4
        window_x = x + (self.fuel_tank_width - window_width) / 2
        window_y = y + self.fuel_tank_height * 0.2
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.WHITE))
        painter.drawRoundedRect(int(window_x), int(window_y), int(window_width), int(window_height), 3, 3)
        
        # Fuel level indicator
        fuel_level = window_width * 0.8
        painter.setBrush(QBrush(self.YELLOW))
        painter.drawRect(int(window_x + window_width * 0.1), 
                       int(window_y + window_height * 0.3), 
                       int(fuel_level), 
                       int(window_height * 0.4))
        
        # Cap on top
        cap_width = self.fuel_tank_width * 0.2
        cap_height = self.fuel_tank_height * 0.2
        cap_x = x + self.fuel_tank_width * 0.4
        cap_y = y - cap_height * 0.7
        
        painter.setBrush(QBrush(self.DARK_GRAY))
        painter.drawRoundedRect(int(cap_x), int(cap_y), int(cap_width), int(cap_height), 2, 2)
        
        painter.setPen(QPen(self.LIGHT_GRAY, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(int(cap_x), int(cap_y), int(cap_width), int(cap_height), 2, 2)
        
        # Cap detail
        painter.setPen(QPen(self.BLACK, 1))
        painter.drawLine(int(cap_x + cap_width * 0.2), int(cap_y + cap_height * 0.5),
                       int(cap_x + cap_width * 0.8), int(cap_y + cap_height * 0.5))
    
    def draw_rover(self, painter):
        # Calculate car's position and rotation
        painter.save()
        
        # Translate to car position and rotate
        painter.translate(self.car_pos_x + (self.car_width + 50) / 2, 
                         self.car_pos_y + (self.car_height + self.car_cabin_height + 20) / 2)
        painter.rotate(-self.car_angle)
        painter.translate(-(self.car_width + 50) / 2, -(self.car_height + self.car_cabin_height + 20) / 2)
        
        # Main body
        body_rect = QRect(25, self.car_cabin_height, self.car_width, self.car_height)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.WHITE))
        painter.drawRect(body_rect)
        
        # Top cabin
        cabin_width = self.car_width * 0.5
        cabin_x_offset = (self.car_width - cabin_width) / 2 + 25
        
        cabin_polygon = QPolygon()
        cabin_polygon.append(QPoint(int(cabin_x_offset), self.car_cabin_height))
        cabin_polygon.append(QPoint(int(cabin_x_offset + cabin_width), self.car_cabin_height))
        cabin_polygon.append(QPoint(int(cabin_x_offset + cabin_width * 0.85), 0))
        cabin_polygon.append(QPoint(int(cabin_x_offset + cabin_width * 0.15), 0))
        
        painter.setBrush(QBrush(self.WHITE))
        painter.drawPolygon(cabin_polygon)
        
        # Windows
        window_polygon = QPolygon()
        window_polygon.append(QPoint(int(cabin_x_offset + 5), self.car_cabin_height - 5))
        window_polygon.append(QPoint(int(cabin_x_offset + cabin_width - 5), self.car_cabin_height - 5))
        window_polygon.append(QPoint(int(cabin_x_offset + cabin_width * 0.85 - 5), 5))
        window_polygon.append(QPoint(int(cabin_x_offset + cabin_width * 0.15 + 5), 5))
        
        painter.setBrush(QBrush(QColor(50, 255, 200)))
        painter.drawPolygon(window_polygon)
        
        # Solar panels
        panel_width = cabin_width * 0.7
        panel_height = 5
        panel_x = cabin_x_offset + (cabin_width - panel_width) / 2
        panel_y = self.car_cabin_height / 2 - panel_height
        
        painter.setBrush(QBrush(QColor(50, 50, 200)))
        painter.drawRect(int(panel_x), int(panel_y), int(panel_width), int(panel_height))
        
        # Wheels
        left_wheel_x = 25 + self.wheel_radius
        right_wheel_x = 25 + self.car_width - self.wheel_radius
        wheel_y = self.car_cabin_height + self.car_height
        
        painter.setBrush(QBrush(self.DARK_GRAY))
        painter.drawEllipse(int(left_wheel_x - self.wheel_radius), int(wheel_y - self.wheel_radius),
                          self.wheel_radius * 2, self.wheel_radius * 2)
        painter.drawEllipse(int(right_wheel_x - self.wheel_radius), int(wheel_y - self.wheel_radius),
                          self.wheel_radius * 2, self.wheel_radius * 2)
        
        # Wheel rims
        painter.setBrush(QBrush(self.RUST))
        painter.drawEllipse(int(left_wheel_x - self.wheel_rim_radius), int(wheel_y - self.wheel_rim_radius),
                          self.wheel_rim_radius * 2, self.wheel_rim_radius * 2)
        painter.drawEllipse(int(right_wheel_x - self.wheel_rim_radius), int(wheel_y - self.wheel_rim_radius),
                          self.wheel_rim_radius * 2, self.wheel_rim_radius * 2)
        
        # Headlights
        painter.setBrush(QBrush(self.YELLOW))
        painter.drawRect(25 + self.car_width - 15, self.car_cabin_height + 10, 15, 15)
        
        painter.restore()
    
    def draw_ui(self, painter):
        # Set up fonts
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        
        # Draw score
        painter.setPen(QPen(self.WHITE))
        painter.drawText(20, 30, f"Score: {self.score}")
        
        # Draw fuel meter
        painter.drawText(22, 55, "Fuel")
        painter.setPen(QPen(self.WHITE, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(20, 60, 204, 24)
        
        fuel_width = int(2 * self.fuel)
        if self.fuel < 30:
            painter.setBrush(QBrush(self.RED))
        elif self.fuel < 70:
            painter.setBrush(QBrush(self.YELLOW))
        else:
            painter.setBrush(QBrush(self.GREEN))
        
        painter.setPen(Qt.NoPen)
        painter.drawRect(22, 62, fuel_width, 20)
        
        # Instructions
        instruction_font = QFont()
        instruction_font.setPointSize(10)
        painter.setFont(instruction_font)
        
        if self.game_over:
            font.setPointSize(24)
            painter.setFont(font)
            painter.setPen(QPen(self.RED))
            
            game_over_text = "GAME OVER"
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(game_over_text)
            painter.drawText((self.width() - text_width) // 2, self.height() // 2 - 50, game_over_text)
            
            font.setPointSize(12)
            painter.setFont(font)
            painter.setPen(QPen(self.WHITE))
            
            restart_text = "Press R to restart"
            text_width = metrics.horizontalAdvance(restart_text)
            painter.drawText((self.width() - text_width) // 2, self.height() // 2 + 20, restart_text)
        else:
            painter.setPen(QPen(self.WHITE))
            if self.moving:
                instruction_text = "SPACE to stop | LEFT/RIGHT to change direction"
            else:
                instruction_text = "Press SPACE to start the Mars rover"
            
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(instruction_text)
            painter.drawText(self.width() - text_width - 20, 20, instruction_text)


def main():
    app = QApplication(sys.argv)
    game = MarsRoverGame()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()