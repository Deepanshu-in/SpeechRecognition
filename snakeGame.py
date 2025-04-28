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



# Added font initialization
pygame.font.init()
SCORE_FONT = pygame.font.SysFont('Arial', 36)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 72)

colours = {
    "cave": (0, 0, 0),
    "walls": (255, 23, 60),
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
        self.speed = 10  # Initial speed
        self.max_speed = 30  # Maximum speed limit
        # Snake colors
        self.body_color = (126, 217, 87)  # Light green
        self.spot_color = (98, 168, 68)   # Darker green for spots
        self.eye_color = (255, 255, 255)  # White for eyes
        self.pupil_color = (0, 0, 0)      # Black for pupils
        
        self.tail = []
        self.tail_decay = 1
        
        # Store original size for reference
        self.original_width = rect[2]
        self.original_height = rect[3]

    def increase_speed(self):
        # Increase speed when coin is collected, but cap at max_speed
        self.speed = min(self.speed + 0.5, self.max_speed)
        return self.speed

    def draw(self, display):
        # Draw tail segments with spots
        for i, rect in enumerate(self.tail):
            if rect.width > 5 and rect.height > 5:  # Only draw if segment is big enough
                # Draw main body segment
                pygame.draw.ellipse(display, self.body_color, rect)
                
                # Add spots to body segments
                spot_size = min(rect.width, rect.height) // 4
                if i % 2 == 0:  # Add spots to alternate segments
                    spot_x = rect.centerx - spot_size // 2
                    spot_y = rect.centery - spot_size // 2
                    spot_rect = pygame.Rect(spot_x, spot_y, spot_size, spot_size)
                    pygame.draw.ellipse(display, self.spot_color, spot_rect)

        # Draw main head
        pygame.draw.ellipse(display, self.body_color, self.rect)
        
        # Add spots to head
        head_spot_size = self.rect.width // 4
        spot_rect = pygame.Rect(
            self.rect.centerx - head_spot_size // 2,
            self.rect.centery - head_spot_size // 2,
            head_spot_size,
            head_spot_size
        )
        pygame.draw.ellipse(display, self.spot_color, spot_rect)

        # Calculate head direction based on angle
        head_direction = [
            math.sin(self.angle * math.pi),
            math.cos(self.angle * math.pi)
        ]
        
        # Draw eyes
        eye_size = self.rect.width // 5
        eye_offset = self.rect.width // 3
        
        # Calculate eye positions based on head direction
        left_eye_pos = (
            self.rect.centerx - head_direction[1] * eye_offset - head_direction[0] * eye_offset,
            self.rect.centery + head_direction[0] * eye_offset - head_direction[1] * eye_offset
        )
        right_eye_pos = (
            self.rect.centerx - head_direction[1] * eye_offset + head_direction[0] * eye_offset,
            self.rect.centery - head_direction[0] * eye_offset - head_direction[1] * eye_offset
        )
        
        # Draw white part of eyes
        pygame.draw.circle(display, self.eye_color, left_eye_pos, eye_size)
        pygame.draw.circle(display, self.eye_color, right_eye_pos, eye_size)
        
        # Draw pupils
        pupil_size = eye_size // 2
        pygame.draw.circle(display, self.pupil_color, 
                         (left_eye_pos[0], left_eye_pos[1]), pupil_size)
        pygame.draw.circle(display, self.pupil_color, 
                         (right_eye_pos[0], right_eye_pos[1]), pupil_size)

    # Keep all other methods the same
    def update(self, objects):
        delta_x = self.speed*math.sin(self.angle * math.pi)
        delta_y = self.speed*math.cos(self.angle * math.pi)
        self.move(0, 0, [])
        self.update_tail(-delta_x, -delta_y)
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

    def update_tail(self, dx, dy):
        for rect in self.tail:
            rect.move_ip(dx, dy)
            rect.inflate_ip(-self.tail_decay, -self.tail_decay)
            if rect.width <= self.tail_decay or rect.height <= self.tail_decay:
                self.tail.remove(rect)
        self.tail.append(self.rect.copy())
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
        # Draw main coin circle (golden)
        radius = round(self.rect.width/2)
        pygame.draw.circle(display, self.colour, self.rect.center, radius)
        
        # Draw outer ring
        pygame.draw.circle(display, self.outline_color, self.rect.center, radius, 3)
        pygame.draw.circle(display, self.outline_color, self.rect.center, radius-5, 1)
        
        # Calculate center
        center_x, center_y = self.rect.center
        
        # Draw inner circle
        inner_radius = round(radius * 0.85)
        pygame.draw.circle(display, self.outline_color, self.rect.center, inner_radius, 1)
        
        # Draw "$" symbol
        font = pygame.font.SysFont('Arial Bold', round(self.rect.width/2))
        dollar_sign = font.render('$', True, self.text_color)
        dollar_rect = dollar_sign.get_rect(center=(center_x, center_y))
        display.blit(dollar_sign, dollar_rect)
        
        # Draw stars around the edge
        num_stars = 8
        star_distance = radius * 0.7
        for i in range(num_stars):
            angle = i * (2 * math.pi / num_stars)
            star_x = center_x + math.cos(angle) * star_distance
            star_y = center_y + math.sin(angle) * star_distance
            
            # Draw 5-pointed star
            star_size = radius // 8
            points = []
            for j in range(5):
                point_angle = j * (2 * math.pi / 5) - math.pi/2
                point_x = star_x + math.cos(point_angle) * star_size
                point_y = star_y + math.sin(point_angle) * star_size
                points.append((point_x, point_y))
            
            pygame.draw.polygon(display, self.outline_color, points, 1)
        
        # Add shine effect (highlight)
        highlight_pos = (center_x - radius//3, center_y - radius//3)
        highlight_size = (radius//4, radius//4)
        highlight_rect = pygame.Rect(highlight_pos, highlight_size)
        pygame.draw.ellipse(display, self.highlight_color, highlight_rect)

class CoinManager:
    def __init__(self, boundary):
        self.boundary = pygame.Rect(boundary)
        self.coins = []
        self.spawn_chance = 0.02

    def update(self, movement, player, cave):
        score = 0
        speed_increased = False

        for coin in self.coins:
            coin.move(movement)

            if coin.check_collide(player):
                score += 1
                self.delete(coin)
                player.increase_speed()  # Increase speed when coin is collected
                speed_increased = True

            elif self.check_delete(coin):
                self.delete(coin)

        if self.check_spawn():
            self.spawn(cave)

        return score, speed_increased

    def check_spawn(self):
        if random.random() <= self.spawn_chance:
            return True
        return False

    def check_delete(self, coin):
        if not self.boundary.colliderect(coin.rect):
            return True

    def delete(self, coin):
        self.coins.remove(coin)

    def spawn(self, cave):
        current_piece = cave.pieces[len(cave.pieces) - 1]
        x = current_piece.rect.x
        y = random.randint(current_piece.rect.y, current_piece.rect.bottom)

        coin = Coin([x, y, cave.size, cave.size])
        self.coins.append(coin)

    def draw(self, display):
        for coin in self.coins:
            coin.draw(display)

def draw_score_and_speed(display, score, speed):
    score_text = SCORE_FONT.render(f'Score: {score}', True, colours["text"])
    speed_text = SCORE_FONT.render(f'Speed: {speed:.1f}', True, colours["text"])
    display.blit(score_text, (20, 20))
    display.blit(speed_text, (20, 70))  # Display speed below score

def draw_game_over(display, score, speed):
    # Create semi-transparent overlay
    overlay = pygame.Surface(DISPLAY_SIZE)
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    display.blit(overlay, (0, 0))
    
    # Draw "Game Over" text
    game_over_text = GAME_OVER_FONT.render('Game Over', True, colours["text"])
    final_score_text = SCORE_FONT.render(f'Final Score: {score}', True, colours["text"])
    final_speed_text = SCORE_FONT.render(f'Final Speed: {speed:.1f}', True, colours["text"])
    restart_text = SCORE_FONT.render('Press SPACE to restart', True, colours["text"])
    
    # Center the text
    game_over_x = DISPLAY_SIZE[0]/2 - game_over_text.get_width()/2
    game_over_y = DISPLAY_SIZE[1]/2 - game_over_text.get_height()/2 - 80
    
    score_x = DISPLAY_SIZE[0]/2 - final_score_text.get_width()/2
    score_y = game_over_y + game_over_text.get_height() + 20
    
    speed_x = DISPLAY_SIZE[0]/2 - final_speed_text.get_width()/2
    speed_y = score_y + final_score_text.get_height() + 20
    
    restart_x = DISPLAY_SIZE[0]/2 - restart_text.get_width()/2
    restart_y = speed_y + final_speed_text.get_height() + 30
    
    display.blit(game_over_text, (game_over_x, game_over_y))
    display.blit(final_score_text, (score_x, score_y))
    display.blit(final_speed_text, (speed_x, speed_y))
    display.blit(restart_text, (restart_x, restart_y))

def main():
    pygame.init()
    display = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Loot froots")
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
                print("%s - %s - Speed: %.1f" % (distance, score, player.speed))
            if keys[pygame.K_p]:
                pygame.image.save(display, "soar.png")

            # Logic
            movement = player.update([])
            distance += round(movement[0] / 10)

            # Convert to move landscape
            movement[0] = -movement[0]
            movement[1] = -movement[1]

            # Update coins and check if speed increased
            coin_update = coin_manager.update(movement, player, cave)
            score += coin_update[0]
            
            hit = cave.update(movement, player)
            
            if hit:
                game_over = True

        # Drawing
        display.fill(colours["walls"])
        
        cave.draw(display)
        coin_manager.draw(display)
        player.draw(display)
        
        if game_over:
            draw_game_over(display, score, player.speed)
        else:
            draw_score_and_speed(display, score, player.speed)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()