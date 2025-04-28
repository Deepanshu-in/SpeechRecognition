import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math
import time
import sys

class Rune:
    def __init__(self, rune_type, vertices, lore_text):
        self.rune_type = rune_type
        self.vertices = vertices
        self.lore_text = lore_text
        self.pulse_intensity = 0.0
        self.pulse_direction = 0.05
        self.last_active_time = 0
        
        # Set color based on rune type
        if rune_type == "infinity":
            self.color = [0.0, 0.3, 1.0]  # Blue
        elif rune_type == "chaos":
            self.color = [0.8, 0.0, 0.8]  # Magenta 
        elif rune_type == "light":
            self.color = [1.0, 0.9, 0.0]  # Yellow
        elif rune_type == "fragmentation":
            self.color = [1.0, 0.5, 0.0]  # Orange
    
    def update_pulse(self):
        self.pulse_intensity += self.pulse_direction
        if self.pulse_intensity >= 1.0 or self.pulse_intensity <= 0.0:
            self.pulse_direction *= -1
        
        # Get current pulsating color
        glow_factor = 0.5 + self.pulse_intensity * 0.5
        return [c * glow_factor for c in self.color]
    
    def activate(self):
        self.last_active_time = time.time()
        self.pulse_intensity = 1.0  # Start at full brightness when activated


class ObeliskFragment:
    def __init__(self, position, velocity, size, color):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.rotation = [random.uniform(0, 360) for _ in range(3)]
        self.rotation_speed = [random.uniform(-5, 5) for _ in range(3)]
        self.size = size
        self.color = color
        self.lifetime = random.uniform(2.0, 4.0)
        
    def update(self, dt):
        # Apply gravity
        self.velocity[1] -= 9.8 * dt
        
        # Update position
        self.position += self.velocity * dt
        
        # Update rotation
        self.rotation = [r + rs * dt for r, rs in zip(self.rotation, self.rotation_speed)]
        
        # Reduce lifetime
        self.lifetime -= dt
        
        return self.lifetime > 0
        
    def render(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        # Use fragment color with fading based on lifetime
        alpha = min(1.0, self.lifetime)
        glColor4f(self.color[0], self.color[1], self.color[2], alpha)
        
        glScalef(self.size, self.size, self.size)
        self.draw_cube()
        
        glPopMatrix()
    
    def draw_cube(self):
        vertices = [
            [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5]
        ]
        
        faces = [
            [0, 1, 2, 3], [4, 5, 6, 7], [0, 4, 7, 3],
            [1, 5, 6, 2], [0, 1, 5, 4], [3, 2, 6, 7]
        ]
        
        normals = [
            [0, 0, -1], [0, 0, 1], [1, 0, 0],
            [-1, 0, 0], [0, 1, 0], [0, -1, 0]
        ]
        
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3fv(normals[i])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()


class AncientObelisk:
    def __init__(self):
        # Obelisk parameters
        self.height = 5.0
        self.base_width = 1.5
        self.top_width = 0.5
        self.erosion = 0.0  # 0.0 to 1.0
        self.rune_complexity = 0.5  # 0.0 to 1.0
        self.stability = 1.0  # 0.0 to 1.0
        
        # Mouse and rotation controls
        self.rotation = [0, 0, 0]
        self.rotation_speed = [0, 0.5, 0]
        self.auto_rotate = True
        self.last_mouse_pos = None
        
        # Fragments for destruction effect
        self.fragments = []
        
        # Rune lore text
        self.rune_lore = {
            "infinity": "The Infinity Rune connects the obelisk to the cosmic streams of time, allowing glimpses into past and future. Ancient scholars said it was the first rune ever carved.",
            "chaos": "The Chaos Rune harnesses entropic energy, symbolizing both destruction and rebirth. Those who master it can reshape reality itself.",
            "light": "The Light Rune was carved by the first civilization to discover fire. It illuminates hidden truths and burns away deception.",
            "fragmentation": "The Fragmentation Rune represents the division of the once unified ancient knowledge. It serves as both warning and memory of what was lost."
        }
        
        # Active lore text for display
        self.active_lore_text = ""
        self.last_active_rune = None
        
        # Initialize runes and vertices
        self.regenerate_obelisk()

    def regenerate_obelisk(self, regenerate_all=True):
        if regenerate_all:
            # Generate basic obelisk shape (vertices for a pyramid-like structure)
            self.base_vertices = self.generate_base_shape()
        
        # Apply erosion to vertices
        self.vertices = self.apply_erosion(self.base_vertices, self.erosion)
        
        # Generate runes
        if regenerate_all:
            self.generate_runes()
        
        # Calculate normals
        self.calculate_normals()
    
    def generate_base_shape(self):
        # Calculate vertices for a tapered rectangular obelisk
        base_half_width = self.base_width / 2
        top_half_width = self.top_width / 2
        
        # Base rectangle (bottom)
        base = [
            [-base_half_width, 0, -base_half_width],
            [base_half_width, 0, -base_half_width],
            [base_half_width, 0, base_half_width],
            [-base_half_width, 0, base_half_width]
        ]
        
        # Top rectangle
        top = [
            [-top_half_width, self.height, -top_half_width],
            [top_half_width, self.height, -top_half_width],
            [top_half_width, self.height, top_half_width],
            [-top_half_width, self.height, top_half_width]
        ]
        
        # Create full vertex array with additional points along height for detail
        segments = 8
        vertices = []
        
        for i in range(segments + 1):
            t = i / segments
            y = t * self.height
            width_factor = (1 - t) * base_half_width + t * top_half_width
            
            layer = [
                [-width_factor, y, -width_factor],
                [width_factor, y, -width_factor],
                [width_factor, y, width_factor],
                [-width_factor, y, width_factor]
            ]
            
            # Apply small random variation for a more natural look
            if 0 < i < segments:
                for v in layer:
                    v[0] += random.uniform(-0.05, 0.05) * width_factor
                    v[2] += random.uniform(-0.05, 0.05) * width_factor
            
            vertices.append(layer)
        
        # Convert to faces (triangles)
        faces = []
        
        # Connect layers to form the sides
        for i in range(segments):
            for j in range(4):
                j_next = (j + 1) % 4
                
                # First triangle
                faces.append([
                    vertices[i][j],
                    vertices[i + 1][j],
                    vertices[i][j_next]
                ])
                
                # Second triangle
                faces.append([
                    vertices[i + 1][j],
                    vertices[i + 1][j_next],
                    vertices[i][j_next]
                ])
        
        # Add bottom face (base)
        faces.append([vertices[0][0], vertices[0][3], vertices[0][2]])
        faces.append([vertices[0][0], vertices[0][2], vertices[0][1]])
        
        # Add top face
        faces.append([vertices[-1][0], vertices[-1][1], vertices[-1][2]])
        faces.append([vertices[-1][0], vertices[-1][2], vertices[-1][3]])
        
        return np.array(faces, dtype=np.float32)
    
    def apply_erosion(self, base_vertices, erosion_amount):
        vertices = np.copy(base_vertices)
        
        # Apply random displacement to each vertex based on erosion amount
        if erosion_amount > 0:
            for face in vertices:
                for vertex in face:
                    # More erosion at the edges and top
                    distance_from_center = np.sqrt(vertex[0]**2 + vertex[2]**2)
                    height_factor = vertex[1] / self.height
                    
                    # Calculate erosion factor based on position
                    position_factor = distance_from_center * 0.8 + height_factor * 0.2
                    
                    # Apply random displacement
                    max_displacement = 0.1 * erosion_amount * position_factor
                    vertex[0] += random.uniform(-max_displacement, max_displacement)
                    vertex[1] += random.uniform(-max_displacement, max_displacement) * 0.5  # Less vertical erosion
                    vertex[2] += random.uniform(-max_displacement, max_displacement)
        
        return vertices
    
    def calculate_normals(self):
        # Calculate face normals for proper lighting
        self.normals = []
        
        for face in self.vertices:
            v1 = np.array(face[1]) - np.array(face[0])
            v2 = np.array(face[2]) - np.array(face[0])
            normal = np.cross(v1, v2)
            norm = np.linalg.norm(normal)
            
            if norm != 0:
                normal = normal / norm
            
            self.normals.append(normal)
    
    def generate_runes(self):
        # Generate runes based on complexity
        self.runes = []
        
        num_runes = int(5 + self.rune_complexity * 15)
        rune_types = ["infinity", "chaos", "light", "fragmentation"]
        
        for _ in range(num_runes):
            # Select a random face on the side of the obelisk (exclude top and bottom)
            face_idx = random.randint(0, len(self.vertices) - 5)  # Avoid bottom and top faces
            face = self.vertices[face_idx]
            
            # Calculate the center of the face
            center = np.mean(face, axis=0)
            
            # Generate random vertices around the center for the rune
            rune_size = 0.1 + 0.1 * self.rune_complexity
            num_points = 3 + int(self.rune_complexity * 5)
            
            rune_vertices = []
            for _ in range(num_points):
                offset = [
                    random.uniform(-rune_size, rune_size),
                    random.uniform(-rune_size, rune_size),
                    random.uniform(-0.01, 0.01)  # Keep rune close to surface
                ]
                
                # Calculate position relative to face
                vertex = center + offset
                rune_vertices.append(vertex)
            
            # Select random rune type
            rune_type = random.choice(rune_types)
            
            # Create the rune
            rune = Rune(rune_type, rune_vertices, self.rune_lore[rune_type])
            self.runes.append(rune)
    
    def adjust_height(self, amount):
        old_height = self.height
        self.height = max(1.0, min(10.0, self.height + amount))
        
        # Decrease stability if height changes significantly
        if abs(old_height - self.height) > 0.1:
            self.decrease_stability(0.05)
        
        self.regenerate_obelisk()
    
    def adjust_erosion(self, amount):
        old_erosion = self.erosion
        self.erosion = max(0.0, min(1.0, self.erosion + amount))
        
        # Decrease stability if erosion increases
        if self.erosion > old_erosion:
            self.decrease_stability(0.1 * amount)
        
        self.regenerate_obelisk(regenerate_all=False)
    
    def adjust_rune_complexity(self, amount):
        old_complexity = self.rune_complexity
        self.rune_complexity = max(0.0, min(1.0, self.rune_complexity + amount))
        
        # Decrease stability if complexity changes significantly
        if abs(old_complexity - self.rune_complexity) > 0.1:
            self.decrease_stability(0.05)
        
        self.regenerate_obelisk()
    
    def repair(self):
        # Increase stability
        self.stability = min(1.0, self.stability + 0.2)
        
        # Slightly reduce erosion
        self.erosion = max(0.0, self.erosion - 0.1)
        
        self.regenerate_obelisk(regenerate_all=False)
    
    def smooth(self):
        # Reduce erosion
        old_erosion = self.erosion
        self.erosion = max(0.0, self.erosion - 0.15)
        
        # Slightly increase stability
        if old_erosion > self.erosion:
            self.stability = min(1.0, self.stability + 0.05)
        
        self.regenerate_obelisk(regenerate_all=False)
    
    def reset(self):
        # Reset to initial parameters
        self.height = 5.0
        self.base_width = 1.5
        self.top_width = 0.5
        self.erosion = 0.0
        self.rune_complexity = 0.5
        self.stability = 1.0
        self.rotation = [0, 0, 0]
        
        self.regenerate_obelisk()
    
    def decrease_stability(self, amount):
        self.stability = max(0.0, self.stability - amount)
        
        # Check if obelisk should shatter
        if self.stability <= 0:
            self.shatter()
    
    def shatter(self):
        # Create fragments
        self.fragments = []
        
        # Create fragments from each face
        for face in self.vertices:
            center = np.mean(face, axis=0)
            
            # Random size and velocity for each fragment
            size = random.uniform(0.1, 0.3)
            velocity = [
                random.uniform(-2, 2),
                random.uniform(1, 5),  # Upward initial velocity
                random.uniform(-2, 2)
            ]
            
            # Use a stone-like color
            color = [
                random.uniform(0.4, 0.6),
                random.uniform(0.3, 0.5),
                random.uniform(0.2, 0.4),
                1.0
            ]
            
            fragment = ObeliskFragment(center, velocity, size, color)
            self.fragments.append(fragment)
        
        # Create additional fragments for more visual effect
        for _ in range(50):
            position = [
                random.uniform(-self.base_width/2, self.base_width/2),
                random.uniform(0, self.height),
                random.uniform(-self.base_width/2, self.base_width/2)
            ]
            
            velocity = [
                random.uniform(-3, 3),
                random.uniform(1, 5),
                random.uniform(-3, 3)
            ]
            
            size = random.uniform(0.05, 0.2)
            
            # Use a stone-like color with some variation
            color = [
                random.uniform(0.4, 0.6),
                random.uniform(0.3, 0.5),
                random.uniform(0.2, 0.4),
                1.0
            ]
            
            fragment = ObeliskFragment(position, velocity, size, color)
            self.fragments.append(fragment)
        
        # Add fragments for runes with their respective colors
        for rune in self.runes:
            center = np.mean(rune.vertices, axis=0)
            
            velocity = [
                random.uniform(-2, 2),
                random.uniform(1, 5),
                random.uniform(-2, 2)
            ]
            
            # Use rune color
            color = rune.color + [1.0]  # Add alpha
            
            fragment = ObeliskFragment(center, velocity, 0.15, color)
            self.fragments.append(fragment)
        
        # Clear obelisk vertices
        self.vertices = np.array([])
        
        # Reset stability for when we rebuild
        self.stability = 0.5
    
    def rebuild(self):
        # Clear fragments
        self.fragments = []
        
        # Regenerate obelisk with reduced parameters
        self.height = max(3.0, self.height * 0.8)
        self.erosion = min(0.5, self.erosion + 0.2)
        self.regenerate_obelisk()
    
    def update(self, dt):
        # Update rotation if auto-rotate is enabled
        if self.auto_rotate:
            self.rotation[1] += self.rotation_speed[1] * dt
        
        # Update rune pulsating effects
        for rune in self.runes:
            rune.update_pulse()
        
        # Update fragments
        if self.fragments:
            for i in range(len(self.fragments) - 1, -1, -1):
                if not self.fragments[i].update(dt):
                    self.fragments.pop(i)
            
            # Rebuild if all fragments are gone
            if not self.fragments:
                self.rebuild()
        
        # Update active lore text
        current_time = time.time()
        newest_active_time = 0
        newest_active_rune = None
        
        for rune in self.runes:
            if rune.last_active_time > newest_active_time:
                newest_active_time = rune.last_active_time
                newest_active_rune = rune
        
        # Update active lore text if a newer rune was activated
        if newest_active_rune and (newest_active_rune != self.last_active_rune or current_time - newest_active_time < 5.0):
            self.active_lore_text = newest_active_rune.lore_text
            self.last_active_rune = newest_active_rune
    
    def render(self):
        glPushMatrix()
        
        # Apply rotation
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        # Render obelisk if not shattered
        if len(self.vertices) > 0:
            # Set material properties for stone look
            stone_color = [0.6, 0.6, 0.6, 1.0]
            stone_ambient = [0.2, 0.2, 0.2, 1.0]
            stone_specular = [0.3, 0.3, 0.3, 1.0]
            stone_shininess = 20.0
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, stone_ambient)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, stone_color)
            glMaterialfv(GL_FRONT, GL_SPECULAR, stone_specular)
            glMaterialf(GL_FRONT, GL_SHININESS, stone_shininess)
            
            # Draw obelisk faces
            glBegin(GL_TRIANGLES)
            for i, face in enumerate(self.vertices):
                glNormal3fv(self.normals[i])
                for vertex in face:
                    glVertex3fv(vertex)
            glEnd()
            
            # Render runes with glowing effect
            self.render_runes()
        
        # Render fragments if any
        for fragment in self.fragments:
            fragment.render()
        
        glPopMatrix()
    
    def render_runes(self):
        # Enable blending for glow effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)
        
        # Disable lighting temporarily
        glDisable(GL_LIGHTING)
        
        for rune in self.runes:
            # Get pulsating color
            color = rune.update_pulse()
            
            # Check for random activation
            if random.random() < 0.001 * self.rune_complexity:
                rune.activate()
            
            # Draw rune lines
            glLineWidth(2.0)
            glColor4f(color[0], color[1], color[2], 0.8)
            
            glBegin(GL_LINE_LOOP)
            for vertex in rune.vertices:
                glVertex3fv(vertex)
            glEnd()
            
            # Draw rune points
            glPointSize(3.0)
            glBegin(GL_POINTS)
            for vertex in rune.vertices:
                glVertex3fv(vertex)
            glEnd()
        
        # Restore OpenGL state
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
    
    def get_stability_color(self):
        # Return color based on stability (green to yellow to red)
        if self.stability > 0.6:
            return (0, 1, 0)  # Green
        elif self.stability > 0.3:
            return (1, 1, 0)  # Yellow
        else:
            return (1, 0, 0)  # Red


class ObeliskSimulator:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set window size and title
        self.window_size = [800, 600]
        self.display = pygame.display.set_mode(self.window_size, DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("Ancient Obelisk Simulator")
        
        # Initialize OpenGL
        self.init_opengl()
        
        # Create obelisk
        self.obelisk = AncientObelisk()
        
        # Camera position
        self.camera_distance = 10.0
        
        # Font for UI
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Running state
        self.running = True
        self.clock = pygame.time.Clock()
    
    def init_opengl(self):
        # Initialize OpenGL settings
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Set up lighting
        light_position = [5.0, 10.0, 5.0, 1.0]
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    def resize_window(self, width, height):
        # Update window size
        self.window_size = [width, height]
        pygame.display.set_mode(self.window_size, DOUBLEBUF | OPENGL | RESIZABLE)
        
        # Update OpenGL viewport
        glViewport(0, 0, width, height)
    
    def update_projection(self):
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.window_size[0] / self.window_size[1]), 0.1, 50.0)
        
        # Set up modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, self.obelisk.height / 2, self.camera_distance,  # Camera position
                  0, self.obelisk.height / 2, 0,                    # Look at point
                  0, 1, 0)                                          # Up vector
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == VIDEORESIZE:
                self.resize_window(event.w, event.h)
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.obelisk.auto_rotate = not self.obelisk.auto_rotate
                    self.obelisk.last_mouse_pos = pygame.mouse.get_pos()
            
            elif event.type == MOUSEMOTION:
                if not self.obelisk.auto_rotate and pygame.mouse.get_pressed()[0]:  # Left button pressed
                    if self.obelisk.last_mouse_pos:
                        x, y = pygame.mouse.get_pos()
                        dx = x - self.obelisk.last_mouse_pos[0]
                        dy = y - self.obelisk.last_mouse_pos[1]
                        
                        # Adjust rotation based on mouse movement
                        self.obelisk.rotation[1] += dx * 0.5
                        self.obelisk.rotation[0] += dy * 0.5
                        
                        self.obelisk.last_mouse_pos = (x, y)
            
            elif event.type == KEYDOWN:
                # Handle height adjustments
                if event.key == K_h:
                    self.obelisk.adjust_height(0.5)
                elif event.key == K_j:
                    self.obelisk.adjust_height(-0.5)
                
                # Handle erosion adjustments
                elif event.key == K_e:
                    self.obelisk.adjust_erosion(0.1)
                elif event.key == K_r:
                    self.obelisk.adjust_erosion(-0.1)
                
                # Handle rune complexity adjustments
                elif event.key == K_t:
                    self.obelisk.adjust_rune_complexity(0.1)
                elif event.key == K_y:
                    self.obelisk.adjust_rune_complexity(-0.1)
                
                # Handle repair, smooth, and reset
                elif event.key == K_w:
                    self.obelisk.repair()
                elif event.key == K_s:
                    self.obelisk.smooth()
                elif event.key == K_q:
                    self.obelisk.reset()
                
                # Trigger a random rune
                elif event.key == K_SPACE:
                    if self.obelisk.runes:
                        random.choice(self.obelisk.runes).activate()
                
                # Force shatter (for testing)
                elif event.key == K_x:
                    self.obelisk.stability = 0
                    self.obelisk.shatter()
                
                # Zoom controls
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    self.camera_distance = max(5.0, self.camera_distance - 1.0)
                elif event.key == K_MINUS:
                    self.camera_distance = min(20.0, self.camera_distance + 1.0)
                
                # Exit
                elif event.key == K_ESCAPE:
                    self.running = False
    
    def render_ui(self):
        # Save OpenGL state
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Switch to 2D rendering for UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window_size[0], self.window_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Create UI surface
        ui_surface = pygame.Surface(self.window_size, pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 0))
        
        # Render position information
        position_text = f"Height: {self.obelisk.height:.1f} | Erosion: {self.obelisk.erosion:.2f} | Rune Complexity: {self.obelisk.rune_complexity:.2f}"
        position_surf = self.font.render(position_text, True, (255, 255, 255))
        ui_surface.blit(position_surf, (10, 10))
        
        # Render stability information
        # Render stability information
        stability_text = f"Stability: {self.obelisk.stability:.2f}"
        stability_color = self.obelisk.get_stability_color()
        stability_surf = self.font.render(stability_text, True, (int(stability_color[0]*255), int(stability_color[1]*255), int(stability_color[2]*255)))
        ui_surface.blit(stability_surf, (10, 40))
        
        # Render warning if stability is low
        if self.obelisk.stability < 0.3:
            warning_text = "WARNING: Obelisk stability critically low!"
            warning_surf = self.font.render(warning_text, True, (255, 0, 0))
            ui_surface.blit(warning_surf, (self.window_size[0] // 2 - warning_surf.get_width() // 2, 70))
        
        # Render controls information
        controls_text = [
            "Controls:",
            "H/J - Increase/Decrease Height",
            "E/R - Increase/Decrease Erosion",
            "T/Y - Increase/Decrease Rune Complexity",
            "W - Repair | S - Smooth | Q - Reset",
            "Space - Activate Random Rune",
            "Left Click - Toggle Auto-rotation",
            "+/- - Zoom In/Out",
            "ESC - Exit"
        ]
        
        for i, text in enumerate(controls_text):
            text_surf = self.font.render(text, True, (200, 200, 200))
            ui_surface.blit(text_surf, (10, self.window_size[1] - 180 + i * 20))
        
        # Render active rune lore
        if self.obelisk.active_lore_text:
            # Create a semi-transparent background
            lore_background = pygame.Surface((self.window_size[0] - 40, 60), pygame.SRCALPHA)
            lore_background.fill((0, 0, 0, 180))
            ui_surface.blit(lore_background, (20, self.window_size[1] - 220))
            
            # Render lore title
            if self.obelisk.last_active_rune:
                lore_title = f"{self.obelisk.last_active_rune.rune_type.capitalize()} Rune:"
                title_surf = self.font.render(lore_title, True, self.obelisk.last_active_rune.color)
                ui_surface.blit(title_surf, (30, self.window_size[1] - 215))
            
            # Wrap and render lore text
            wrapped_text = self.wrap_text(self.obelisk.active_lore_text, self.font, self.window_size[0] - 60)
            for i, line in enumerate(wrapped_text):
                line_surf = self.font.render(line, True, (255, 255, 255))
                ui_surface.blit(line_surf, (30, self.window_size[1] - 195 + i * 20))
        
        # Convert pygame surface to OpenGL texture
        data = pygame.image.tostring(ui_surface, "RGBA", True)
        width, height = ui_surface.get_size()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw UI texture
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)
        
        # Restore OpenGL state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
    
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def run(self):
        while self.running:
            # Handle events
            self.handle_events()
            
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0
            
            # Update obelisk
            self.obelisk.update(dt)
            
            # Update projection matrix
            self.update_projection()
            
            # Clear screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Render obelisk
            self.obelisk.render()
            
            # Render UI
            self.render_ui()
            
            # Swap buffers
            pygame.display.flip()


def main():
    try:
        simulator = ObeliskSimulator()
        simulator.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()