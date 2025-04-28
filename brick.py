import pygame
import random

# Pygame को इनिशियलाइज़ करें
pygame.init()

# स्क्रीन आयाम
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

# रंग
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# पैडल सेटिंग
paddle_width, paddle_height = 100, 10
paddle_x = (WIDTH - paddle_width) // 2
paddle_y = HEIGHT - 50
paddle_speed = 8

# बॉल सेटिंग
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = random.choice([-4, 4])
ball_speed_y = -4
speed_increase = 0.2  # प्रत्येक ईंट टूटने के बाद गति में वृद्धि

# ईंट सेटिंग
brick_rows, brick_cols = 5, 8
brick_width = WIDTH // brick_cols
brick_height = 30
bricks = [pygame.Rect(col * brick_width, row * brick_height, brick_width - 2, brick_height - 2)
          for row in range(brick_rows) for col in range(brick_cols)]

# जीवन की गिनती
lives = 3
font = pygame.font.Font(None, 36)

def reset_ball():
    """Reset ball position and direction when a life is lost."""
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_speed_x = random.choice([-4, 4])
    ball_speed_y = -4

# गेम लूप
running = True
while running:
    screen.fill(WHITE)
    
    # ईवेंट संभालें
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # पैडल ले जाएँ
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
        paddle_x += paddle_speed
    
    # बॉल ले जाएँ
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    
    # दीवारों से बॉल का टकराव
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
        ball_speed_x *= -1
    if ball_y - ball_radius <= 0:
        ball_speed_y *= -1
    
    # बॉल का पैडल से टकराना
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
    if paddle_rect.collidepoint(ball_x, ball_y + ball_radius):
        ball_speed_y *= -1
        ball_speed_x += random.choice([-1, 1])  # विविधता जोड़ें
    
    # ईंटों से बॉल का टकराना
    for brick in bricks[:]:
        if brick.colliderect(pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, 2 * ball_radius, 2 * ball_radius)):
            bricks.remove(brick)
            ball_speed_y *= -1
            
            # बॉल की गति बढ़ाएँ
            if ball_speed_y > 0:
                ball_speed_y += speed_increase
            else:
                ball_speed_y -= speed_increase
            
            if ball_speed_x > 0:
                ball_speed_x += speed_increase
            else:
                ball_speed_x -= speed_increase
            break
    
    # बॉल पैडल से नीचे गिरती है (एक जीवन खो देती है)
    if ball_y >= HEIGHT:
        lives -= 1
        if lives > 0:
            reset_ball()  # अगर जीवन बचा है तो बॉल को रीसेट करें
        else:
            running = False  # अगर कोई जीवन नहीं बचा है तो गेम समाप्त करें
    
    # तत्वों को ड्रा करें
    pygame.draw.rect(screen, BLUE, paddle_rect)
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)
    for brick in bricks:
        pygame.draw.rect(screen, GREEN, brick)

    # जीवन प्रदर्शित करें
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(lives_text, (10, 10))
    
    pygame.display.flip()
    pygame.time.delay(20)

pygame.quit()