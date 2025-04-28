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

            self.stars.append(
                Star(rect, colour)
            )

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

        # Values are in number of squares.
        self.gap_minimum = 10
        self.gap_maximum = self.scale[1] - 2
        self.piece_difference = 1  # maximum scale amounts the next piece can be different by

        # Initially making cave fill screen to edge
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
            if top == previous_y:
                pass

        rect = [x, top * self.size, self.size, self.size*gap_size]
        self.pieces.append(CavePiece(rect, self.colour))

    def check_wall_hit(self, player):
        corners = [False, False,
                   False, False]
        for cave_piece in self.pieces[int(self.scale[0]*0.3):int(self.scale[0]*0.6)]:
            if cave_piece.rect.collidepoint(player.rect.topleft):
                corners[0] = True
            if cave_piece.rect.collidepoint(player.rect.topright):
                corners[1] = True
            if cave_piece.rect.collidepoint(player.rect.bottomleft):
                corners[2] = True
            if cave_piece.rect.collidepoint(player.rect.bottomright):
                corners[3] = True
        if False in corners:  # no cave piece registered a players corner, must have collided with wall.
            return True
        return False

    def draw(self, display):
        for wall in self.pieces:
            wall.draw(display)


# Font initialization
pygame.font.init()
SCORE_FONT = pygame.font.SysFont('Arial', 36)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 72)

colours = {
    "cave": (0, 0, 0),
    "walls": (135, 206, 235),  # Sky blue for background
    "player": (53, 235, 12),
    "text": (255, 255, 255),  # White color for text
}

DISPLAY_SIZE = [1000, 700]
PLAYER_SIZE = [50, 50]
PLAYER_RECT = [
    round(DISPLAY_SIZE[0]/2 - PLAYER_SIZE[0]/2),
    round(DISPLAY_SIZE[1]/2 - PLAYER_SIZE[1]/2),
    PLAYER_SIZE[0], PLAYER_SIZE[1]]
PLATFORM_HEIGHT = 20
GRAVITY = -0.01

class Player:
    def __init__(self, rect, colour):
        self.rect = pygame.Rect(rect)
        self.vector = [0, 0]
        self.angle = .5
        self.speed = 10
        
        # Bird colors
        self.body_color = (144, 238, 144)  # Yellow
        self.wing_color = (0, 198, 252)  # Blue
        self.beak_color = (255, 69, 0)   # Red-Orange
        self.eye_color = (255, 255, 255)  # White
        self.pupil_color = (0, 0, 0)     # Black
        
        # Original size for reference
        self.original_width = rect[2]
        self.original_height = rect[3]
        
        # Animation variables
        self.flap_angle = 0
        self.flap_speed = 0.2

    def draw(self, display):
        # Draw bird body (circle)
        pygame.draw.circle(display, self.body_color, self.rect.center, self.rect.width // 2)
        
        # Draw tail
        tail_color = (0, 198, 252)  # Blue
        tail_points = [
            (self.rect.centerx - self.rect.width * 0.4, self.rect.centery),  # Base of tail
            (self.rect.centerx - self.rect.width * 0.8, self.rect.centery - self.rect.height * 0.3),  # Top point
            (self.rect.centerx - self.rect.width * 0.9, self.rect.centery),  # Middle point
            (self.rect.centerx - self.rect.width * 0.8, self.rect.centery + self.rect.height * 0.3),  # Bottom point
        ]
        pygame.draw.polygon(display, tail_color, tail_points)
        
        # Add tail details/feathers
        tail_detail_color = (255, 165, 0)  # Orange color for tail details
        tail_details = [
            [(self.rect.centerx - self.rect.width * 0.5, self.rect.centery),
             (self.rect.centerx - self.rect.width * 0.7, self.rect.centery - self.rect.height * 0.2),
             (self.rect.centerx - self.rect.width * 0.6, self.rect.centery)],
            
            [(self.rect.centerx - self.rect.width * 0.5, self.rect.centery),
             (self.rect.centerx - self.rect.width * 0.7, self.rect.centery + self.rect.height * 0.2),
             (self.rect.centerx - self.rect.width * 0.6, self.rect.centery)]
        ]
        for detail in tail_details:
            pygame.draw.polygon(display, tail_detail_color, detail)
        
        # Calculate wing position based on flap animation
        wing_angle = math.sin(self.flap_angle) * 0.5
        self.flap_angle += self.flap_speed
        
        # Draw wing
        wing_points = [
            (self.rect.centerx, self.rect.centery),
            (self.rect.centerx - self.rect.width * 0.6, 
             self.rect.centery - self.rect.height * 0.3 * math.sin(wing_angle + 1)),
            (self.rect.centerx - self.rect.width * 0.5, 
             self.rect.centery - self.rect.height * 0.5 * math.sin(wing_angle + 0.5)),
            (self.rect.centerx - self.rect.width * 0.2, 
             self.rect.centery - self.rect.height * 0.3 * math.sin(wing_angle))
        ]
        pygame.draw.polygon(display, self.wing_color, wing_points)
        
        # Draw beak
        beak_points = [
            (self.rect.centerx + self.rect.width * 0.4, self.rect.centery),
            (self.rect.centerx + self.rect.width * 0.7, self.rect.centery - self.rect.height * 0.1),
            (self.rect.centerx + self.rect.width * 0.7, self.rect.centery + self.rect.height * 0.1)
        ]
        pygame.draw.polygon(display, self.beak_color, beak_points)
        
        # Draw eye
        eye_pos = (self.rect.centerx + self.rect.width * 0.2, self.rect.centery - self.rect.height * 0.1)
        eye_size = self.rect.width // 6
        pygame.draw.circle(display, self.eye_color, eye_pos, eye_size)
        
        # Draw pupil
        pupil_pos = (eye_pos[0] + eye_size * 0.2, eye_pos[1])
        pupil_size = eye_size // 2
        pygame.draw.circle(display, self.pupil_color, pupil_pos, pupil_size)

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

class Coin:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.colour = (218, 165, 32)      # Golden color
        self.outline_color = (184, 134, 11)  # Darker gold for details
        self.text_color = (139, 69, 19)   # Darker color for text
        self.highlight_color = (255, 215, 0)  # Bright gold for highlights

    def move(self, movement):
        self.rect = self.rect.move(movement)

    def check_collide(self, player):
        if self.rect.colliderect(player.rect):
            return True
        return False

    def draw(self, display):
        # Draw main coin circle
        pygame.draw.circle(display, self.colour, self.rect.center, self.rect.width // 1)
        
        # Draw outline
        pygame.draw.circle(display, self.outline_color, self.rect.center, self.rect.width // 2, 2)
        
        # Draw highlight (small circle in upper-left quadrant)
        highlight_pos = (self.rect.centerx - self.rect.width // 4, 
                        self.rect.centery - self.rect.height // 4)
        pygame.draw.circle(display, self.highlight_color, highlight_pos, self.rect.width // 6)
        
class Diamond:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.colour = (0, 191, 255)      # Deep sky blue
        self.outline_color = (135, 206, 235)  # Sky blue
        self.highlight_color = (255, 255, 255)  # White

    def move(self, movement):
        self.rect = self.rect.move(movement)

    def check_collide(self, player):
        if self.rect.colliderect(player.rect):
            return True
        return False

    def draw(self, display):
        # Calculate diamond points
        center_x, center_y = self.rect.center
        width, height = self.rect.width, self.rect.height
        
        diamond_points = [
            (center_x, center_y - height//1),  # top
            (center_x + width//1, center_y),   # right
            (center_x, center_y + height//1),  # bottom
            (center_x - width//1, center_y)    # left
        ]
        
        # Draw main diamond
        pygame.draw.polygon(display, self.colour, diamond_points)
        # Draw outline
        pygame.draw.polygon(display, self.outline_color, diamond_points, 2)
        
        # Draw highlight
        highlight_points = [
            (center_x - width//4, center_y - height//4),
            (center_x, center_y - height//3),
            (center_x + width//4, center_y - height//4)
        ]
        pygame.draw.polygon(display, self.highlight_color, highlight_points)

class CoinManager:
    def __init__(self, boundary):
        self.boundary = pygame.Rect(boundary)
        self.coins = []
        self.diamonds = []
        self.spawn_chance = 0.02
        self.diamond_spawn_chance = 0.01  # Lower chance for diamonds

    def update(self, movement, player, cave):
        score = 0

        # Update coins
        for coin in self.coins[:]:  # Use slice copy to safely remove while iterating
            coin.move(movement)
            if coin.check_collide(player):
                score += 10  # Changed coin score to 10
                self.coins.remove(coin)
            elif not self.boundary.colliderect(coin.rect):
                self.coins.remove(coin)

        # Update diamonds
        for diamond in self.diamonds[:]:  # Use slice copy to safely remove while iterating
            diamond.move(movement)
            if diamond.check_collide(player):
                score += 20  # Diamond score is 20
                self.diamonds.remove(diamond)
            elif not self.boundary.colliderect(diamond.rect):
                self.diamonds.remove(diamond)

        # Spawn new items
        if random.random() <= self.spawn_chance:
            self.spawn_coin(cave)
        if random.random() <= self.diamond_spawn_chance:
            self.spawn_diamond(cave)

        return score

    def spawn_coin(self, cave):
        current_piece = cave.pieces[len(cave.pieces) - 1]
        x = current_piece.rect.x
        y = random.randint(current_piece.rect.y, current_piece.rect.bottom)
        coin = Coin([x, y, cave.size, cave.size])
        self.coins.append(coin)

    def spawn_diamond(self, cave):
        current_piece = cave.pieces[len(cave.pieces) - 1]
        x = current_piece.rect.x
        y = random.randint(current_piece.rect.y, current_piece.rect.bottom)
        diamond = Diamond([x, y, cave.size, cave.size])
        self.diamonds.append(diamond)

    def draw(self, display):
        for coin in self.coins:
            coin.draw(display)
        for diamond in self.diamonds:
            diamond.draw(display)
            
def draw_score(display, score):
    score_text = SCORE_FONT.render(f'Score: {score}', True, colours["text"])
    display.blit(score_text, (20, 20))

def draw_game_over(display, score):
    # Create semi-transparent overlay
    overlay = pygame.Surface(DISPLAY_SIZE)
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    display.blit(overlay, (0, 0))
    
    # Draw "Game Over" text
    game_over_text = GAME_OVER_FONT.render('Game Over', True, colours["text"])
    final_score_text = SCORE_FONT.render(f'Final Score: {score}', True, colours["text"])
    restart_text = SCORE_FONT.render('Press SPACE to restart', True, colours["text"])
    
    # Center the text
    game_over_x = DISPLAY_SIZE[0]/2 - game_over_text.get_width()/2
    game_over_y = DISPLAY_SIZE[1]/2 - game_over_text.get_height()/2 - 50
    
    score_x = DISPLAY_SIZE[0]/2 - final_score_text.get_width()/2
    score_y = game_over_y + game_over_text.get_height() + 20
    
    restart_x = DISPLAY_SIZE[0]/2 - restart_text.get_width()/2
    restart_y = score_y + final_score_text.get_height() + 20
    
    display.blit(game_over_text, (game_over_x, game_over_y))
    display.blit(final_score_text, (score_x, score_y))
    display.blit(restart_text, (restart_x, restart_y))

def main():
    pygame.init()
    display = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    FPS = 30

    def reset_game():
        cave = Cave(display.get_rect(), 20, colours["cave"])
        coin_manager = CoinManager(display.get_rect())
        player = Player(PLAYER_RECT, colours["player"])
        return cave, coin_manager, player, 0, 0, False

    cave, coin_manager, player, distance, score, game_over = reset_game()

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and game_over:
                    cave, coin_manager, player, distance, score, game_over = reset_game()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_SPACE]:
                player.move_anticlockwise()
            if keys[pygame.K_s]:
                print("%s - %s" % (distance, score))
            if keys[pygame.K_p]:
                pygame.image.save(display, "flappy.png")

            # Logic
            movement = player.update([])
            distance += round(movement[0] / 10)

            # Convert to move landscape
            movement[0] = -movement[0]
            movement[1] = -movement[1]

            score += coin_manager.update(movement, player, cave)
            hit = cave.update(movement, player)
            
            if hit:
                game_over = True

        # Drawing
        display.fill(colours["walls"])
        
        cave.draw(display)
        coin_manager.draw(display)
        player.draw(display)
        
        if game_over:
            draw_game_over(display, score)
        else:
            draw_score(display, score)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()