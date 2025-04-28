import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from math import sin, cos, pi

# Initialize Pygame and set up an OpenGL display
pygame.init()
width, height = 800, 600  # Window dimensions
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)  # Double-buffered OpenGL context
gluPerspective(45, width/height, 0.1, 50.0)  # Set perspective projection with 45° FOV
glTranslatef(0.0, 0.0, -5)  # Move camera back along Z-axis for initial view
glEnable(GL_DEPTH_TEST)  # Enable depth testing for correct 3D rendering
glEnable(GL_LINE_SMOOTH)  # Smooth lines for better visual quality
glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)  # Use highest quality line smoothing
glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background color to white for better visibility

# Disable lighting to simplify rendering and ensure visibility
glDisable(GL_LIGHTING)
glDisable(GL_LIGHT0)

# Define the Hopf Fibration visualization class
class HopfFibration:
    def __init__(self):
        """Initialize Hopf Fibration parameters."""
        self.t = 0.0  # Animation time parameter
        self.rotation_speed = 0.02  # Speed of fiber rotation
        self.num_fibers = 20  # Number of fibers to render
        self.num_points = 100  # Number of points per fiber
        self.scale = 1.5  # Scaling factor for the visualization
        self.proj_origin = [0.0, 0.0, 0.0, -1.0]  # Stereographic projection origin (4D)
        self.color_mode = 0  # Color mode: 0=θ rainbow, 1=φ rainbow, 2=uniform
        self.show_points = False  # Toggle for displaying points on fibers
        self.show_grid = False  # Toggle for displaying reference grid
        self.exporting = False  # Toggle for exporting frames as images
        self.frame_count = 0  # Frame counter for export
        self.camera_rot_x = 0.0  # Camera pitch (X-axis rotation)
        self.camera_rot_y = 0.0  # Camera yaw (Y-axis rotation)
        self.camera_distance = 5.0  # Distance of camera from origin

    def stereographic_projection(self, x, y, z, w):
        """Convert 4D coordinates to 3D using stereographic projection."""
        ox, oy, oz, ow = self.proj_origin  # Projection origin in 4D space
        dx, dy, dz, dw = x - ox, y - oy, z - oz, w - ow  # Relative coordinates
        denom = 1 + dw  # Denominator for projection calculation
        if abs(denom) < 1e-6:  # Avoid division by zero
            return (0, 0, 0)
        return (dx / denom, dy / denom, dz / denom)  # Return projected 3D coordinates

    def hopf_fiber(self, theta, phi):
        """Generate a single Hopf fiber based on angles theta and phi."""
        points = []
        for t in np.linspace(0, 2 * pi, self.num_points):  # Parameterize fiber over circle
            x = cos(theta) * cos(t)  # 4D coordinates on S3
            y = cos(theta) * sin(t)
            z = sin(theta) * cos(phi + t)
            w = sin(theta) * sin(phi + t)
            proj = self.stereographic_projection(x, y, z, w)  # Project to 3D
            points.append(proj)
        return points

    def hsv_to_rgb(self, h, s=0.8, v=0.9):
        """Convert HSV color to RGB for vibrant rainbow effects."""
        h = h % 1.0  # Normalize hue to [0, 1)
        i = int(h * 6)  # Segment hue into 6 regions
        f = h * 6 - i  # Fractional part of hue
        p = v * (1 - s)  # Precomputed values for RGB conversion
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        # Map hue to RGB based on region
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        return (v, p, q)

    def render(self):
        """Render the Hopf Fibration visualization."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen and depth buffer
        
        # Set up camera transformation
        glLoadIdentity()
        gluPerspective(45, width/height, 0.1, 50.0)  # Reapply perspective
        glTranslatef(0.0, 0.0, -self.camera_distance)  # Position camera
        glRotatef(self.camera_rot_x, 1, 0, 0)  # Apply pitch
        glRotatef(self.camera_rot_y, 0, 1, 0)  # Apply yaw
        glRotatef(self.rotation_speed * 180/pi, 1, 1, 1)  # Animate rotation

        # Render optional reference grid
        if self.show_grid:
            glLineWidth(1.0)
            glColor3f(0.8, 0.8, 0.8)  # Light gray color
            glBegin(GL_LINES)
            for i in np.arange(-2, 3, 1):  # Draw grid lines
                glVertex3f(i, -2, 0); glVertex3f(i, 2, 0)  # Vertical lines
                glVertex3f(-2, i, 0); glVertex3f(2, i, 0)  # Horizontal lines
            glEnd()

        # Render Hopf fibers
        glLineWidth(3.0)  # Thicker lines for visibility
        for i in range(self.num_fibers):
            theta = i * pi / self.num_fibers  # Angle for fiber distribution
            for j in range(self.num_fibers):
                phi = j * 2 * pi / self.num_fibers + self.t  # Animated angle
                fiber = self.hopf_fiber(theta, phi)
                
                # Draw fiber as a colored line strip
                glBegin(GL_LINE_STRIP)
                for k, (x, y, z) in enumerate(fiber):
                    # Select color based on mode
                    if self.color_mode == 0:  # Rainbow by θ
                        rgb = self.hsv_to_rgb(i / self.num_fibers + k / (self.num_points * 2))
                    elif self.color_mode == 1:  # Rainbow by φ
                        rgb = self.hsv_to_rgb(j / self.num_fibers + k / (self.num_points * 2))
                    else:  # Uniform bright magenta
                        rgb = (0.9, 0.2, 0.7)
                    glColor3f(*rgb)
                    glVertex3f(x * self.scale, y * self.scale, z * self.scale)
                glEnd()

                # Optionally draw points along the fiber
                if self.show_points:
                    glPointSize(5.0)
                    glBegin(GL_POINTS)
                    for x, y, z in fiber:
                        glColor3f(*rgb)
                        glVertex3f(x * self.scale, y * self.scale, z * self.scale)
                    glEnd()

        # Export frame as image if enabled
        if self.exporting:
            pygame.image.save(pygame.display.get_surface(), f"frame_{self.frame_count:04d}.png")
            self.frame_count += 1

    def update(self):
        """Update animation state."""
        self.t += self.rotation_speed  # Increment time for animation

# Set up font for rendering text overlays
font = pygame.font.SysFont("Arial", 16)

def draw_text(surface, text, x, y):
    """Render text onto the Pygame surface."""
    text_surface = font.render(text, True, (0, 0, 0))  # Black text for contrast
    surface.blit(text_surface, (x, y))

# Main application loop
hopf = HopfFibration()  # Create Hopf Fibration instance
clock = pygame.time.Clock()  # Control frame rate
running = True  # Main loop control flag
mouse_pressed = False  # Track mouse drag state

# Define user instructions for controls
instructions = [
    "Controls:",
    "W/S: Rotation Speed (+/-0.005)",
    "A/D: Scale (+/-0.1)",
    "F/G: Number of Fibers (+/-5)",
    "P/O: Points per Fiber (+/-10)",
    "C: Cycle Color Mode (0-2)",
    "V: Toggle Points",
    "B: Toggle Grid",
    "E: Toggle Export Frames",
    "X/Y/Z/W + Up/Down: Proj Origin (+/-0.1)",
    "I/K: Camera Pitch (+/-5°)",
    "J/L: Camera Yaw (+/-5°)",
    "U/M: Camera Zoom (+/-0.5)",
    "Mouse Drag: Rotate Camera",
    "Q: Quit"
]

while running:
    for event in pygame.event.get():  # Process all events
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            running = False  # Exit on window close or 'Q' key
        elif event.type == KEYDOWN:
            # Handle keypress controls
            if event.key == K_w:
                hopf.rotation_speed += 0.005  # Increase rotation speed
            elif event.key == K_s:
                hopf.rotation_speed -= 0.005  # Decrease rotation speed
            elif event.key == K_a:
                hopf.scale = max(0.1, hopf.scale - 0.1)  # Decrease scale, enforce minimum
            elif event.key == K_d:
                hopf.scale += 0.1  # Increase scale
            elif event.key == K_f:
                hopf.num_fibers = min(50, hopf.num_fibers + 5)  # Increase fibers, cap at 50
            elif event.key == K_g:
                hopf.num_fibers = max(5, hopf.num_fibers - 5)  # Decrease fibers, min 5
            elif event.key == K_p:
                hopf.num_points = min(200, hopf.num_points + 10)  # More points, cap at 200
            elif event.key == K_o:
                hopf.num_points = max(20, hopf.num_points - 10)  # Fewer points, min 20
            elif event.key == K_c:
                hopf.color_mode = (hopf.color_mode + 1) % 3  # Cycle through color modes
            elif event.key == K_v:
                hopf.show_points = not hopf.show_points  # Toggle points visibility
            elif event.key == K_b:
                hopf.show_grid = not hopf.show_grid  # Toggle grid visibility
            elif event.key == K_e:
                hopf.exporting = not hopf.exporting  # Toggle frame export
                hopf.frame_count = 0 if hopf.exporting else hopf.frame_count  # Reset counter
            elif event.key in (K_UP, K_DOWN):
                mod = 0.1 if event.key == K_UP else -0.1  # Adjustment value
                keys = pygame.key.get_pressed()  # Check modifier keys
                if keys[K_x]:
                    hopf.proj_origin[0] = max(-1, min(1, hopf.proj_origin[0] + mod))  # Adjust X
                elif keys[K_y]:
                    hopf.proj_origin[1] = max(-1, min(1, hopf.proj_origin[1] + mod))  # Adjust Y
                elif keys[K_z]:
                    hopf.proj_origin[2] = max(-1, min(1, hopf.proj_origin[2] + mod))  # Adjust Z
                elif keys[K_w]:
                    hopf.proj_origin[3] = max(-1, min(1, hopf.proj_origin[3] + mod))  # Adjust W
            elif event.key == K_i:
                hopf.camera_rot_x += 5.0  # Pitch up
            elif event.key == K_k:
                hopf.camera_rot_x -= 5.0  # Pitch down
            elif event.key == K_j:
                hopf.camera_rot_y -= 5.0  # Yaw left
            elif event.key == K_l:
                hopf.camera_rot_y += 5.0  # Yaw right
            elif event.key == K_u:
                hopf.camera_distance = max(2.0, hopf.camera_distance - 0.5)  # Zoom in
            elif event.key == K_m:
                hopf.camera_distance = min(10.0, hopf.camera_distance + 0.5)  # Zoom out
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pressed = True  # Start dragging
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                mouse_pressed = False  # Stop dragging
        elif event.type == MOUSEMOTION and mouse_pressed:
            dx, dy = event.rel  # Mouse movement deltas
            hopf.camera_rot_y += dx * 0.5  # Adjust yaw
            hopf.camera_rot_x += dy * 0.5  # Adjust pitch

    hopf.update()  # Update animation state
    hopf.render()  # Render the scene

    # Overlay instructions on the screen
    screen = pygame.display.get_surface()
    for i, line in enumerate(instructions):
        draw_text(screen, line, 10, 10 + i * 20)  # Draw each line of text

    pygame.display.flip()  # Swap buffers to display the frame
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()  # Clean up and exit