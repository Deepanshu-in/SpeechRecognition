import pygame
import random
import sys

def main():
    pygame.init()
    
    W, HEIGHT = 800, 600
    screen = pygame.display.set_mode((W, HEIGHT))
    pygame.display.set_caption("River Boat Obstacle Game")
    
    BLUE = (65, 105, 225)
    green = (34, 139, 34)
    brownLight = (205, 133, 63)
    dark_brown = (139, 69, 19)
    ROCK_COLOR = (105, 105, 105)
    darkrock = (64, 64, 64)
    white = (255, 255, 255)
    lightblue = (173, 216, 230)
    r = (255, 0, 0)
    
    GameOver = False
    SCORE = 0
    HiScore = 0
    FONT = pygame.font.SysFont(None, 36)
    smallfont = pygame.font.SysFont(None, 24)
    
    riv_width = int(W * 0.6)
    L_bank = int((W - riv_width) / 2)
    R = L_bank + riv_width
    p = []
    spd = 2.0
    rx = []
    timer = 0
    interval = 60
    
    X = W // 2
    y = HEIGHT * 0.8
    width = 50
    h = 90
    speed = 4
    langle = 0
    rangle = 0
    ldir = 1
    rdir = 1
    hit = False
    
    for _ in range(200):
        X_ = random.randint(L_bank + 10, R - 10)
        Y = random.randint(0, HEIGHT)
        sz = random.randint(2, 5)
        p.append([X_, Y, sz])
    
    UP = False
    left = False
    RIGHT = False
    
    klock = pygame.time.Clock()
    
    def RESET():
        nonlocal GameOver, SCORE, X, y, hit, rx, timer
        GameOver = False
        SCORE = 0
        X = W // 2
        y = HEIGHT * 0.8
        hit = False
        rx = []
        timer = 0
        
        nonlocal langle, rangle, ldir, rdir
        langle = 0
        rangle = 0
        ldir = 1
        rdir = 1
    
    def DRAWROCK(scr, x, y, w, h):
        pts = []
        
        for i in range(8):
            a = i * (2 * 3.14159 / 8)
            r = random.uniform(w * 0.5, w * 0.7)
            xx = x + r * pygame.math.Vector2(1, 0).rotate(a * 180 / 3.14159).x
            yy = y + r * pygame.math.Vector2(1, 0).rotate(a * 180 / 3.14159).y
            pts.append((xx, yy))
        
        pygame.draw.polygon(scr, ROCK_COLOR, pts)
        
        for _ in range(3):
            dx = x + random.randint(-w//3, w//3)
            dy = y + random.randint(-h//3, h//3)
            d_sz = random.randint(2, 5)
            pygame.draw.circle(scr, darkrock, (int(dx), int(dy)), d_sz)
        
        for _ in range(4):
            sx = x + random.randint(-w//2 - 5, w//2 + 5)
            sy = y + random.randint(-h//2 - 5, h//2 + 5)
            pygame.draw.circle(scr, white, (int(sx), int(sy)), 2)
    
    def drawBoat(surf):
        b_pts = [
            (X - width//2, y + h//2 - 10),
            (X - width//2 + 5, y - h//2 + 10),
            (X, y - h//2),
            (X + width//2 - 5, y - h//2 + 10),
            (X + width//2, y + h//2 - 10),
            (X, y + h//2),
        ]
        
        COLOR = r if hit else brownLight
        pygame.draw.polygon(surf, COLOR, b_pts)
        
        for i in range(1, 5):
            YY = y - h//2 + (h * i)//5
            LEFT = X - width//2 + 5 if i == 1 else X - width//2 + 3
            rt = X + width//2 - 5 if i == 1 else X + width//2 - 3
            
            if i <= 2:
                MIDOFFSET = 15 - i * 5
                MID = X
                yMID = YY - MIDOFFSET
                
                pygame.draw.line(surf, dark_brown, (LEFT, YY), (MID, yMID), 2)
                pygame.draw.line(surf, dark_brown, (MID, yMID), (rt, YY), 2)
            else:
                pygame.draw.line(surf, dark_brown, (LEFT, YY), (rt, YY), 2)
        
        pygame.draw.line(surf, dark_brown, 
                       (X, y - h//2 + 5), 
                       (X, y + h//2 - 5), 2)
        
        BENCH = width - 10
        pygame.draw.rect(surf, dark_brown, 
                      (X - BENCH//2, y - 5, BENCH, 10))
        
        PADDLE("left", surf)
        PADDLE("right", surf)
        
        for i in range(3):
            o = 5 + i*5
            pygame.draw.arc(surf, white, 
                           (X - 15 - i*5, y + h//2 + o, 
                            30 + i*10, 10), 
                           0, 3.14, 2)
    
    def PADDLE(s, surf):
        if hit:
            return
            
        L = 60
        
        if s == "left":
            p_x = X - width//2 - 5
            p_y = y
            a = langle
        else:
            p_x = X + width//2 + 5
            p_y = y
            a = rangle
        
        if s == "left":
            E_X = p_x - L * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(a).x
            E_Y = p_y - L * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(a).y
        else:
            E_X = p_x + L * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(a).x
            E_Y = p_y - L * pygame.math.Vector2(pygame.math.Vector2(1, 0)).rotate(a).y
        
        pygame.draw.line(surf, dark_brown, (p_x, p_y), (E_X, E_Y), 3)
        
        if s == "left":
            BX = E_X - 10
            BY = E_Y
        else:
            BX = E_X + 10
            BY = E_Y
            
        b_pts = [
            (E_X - 5 if s == "left" else E_X + 5, E_Y - 10),
            (BX, BY),
            (E_X - 5 if s == "left" else E_X + 5, E_Y + 10)
        ]
        pygame.draw.polygon(surf, dark_brown, b_pts)
    
    def CHECK():
        nonlocal hit, GameOver, HiScore
        
        if hit:
            return True
            
        bHitbox = pygame.Rect(
            X - width//2 + 10,
            y - h//2 + 15,
            width - 20,
            h - 25
        )
        
        for r in rx:
            rHitbox = pygame.Rect(
                r["xx"] - r["w"]//2 + 5,
                r["yy"] - r["H"]//2 + 5,
                r["w"] - 10,
                r["H"] - 10
            )
            
            if bHitbox.colliderect(rHitbox):
                hit = True
                GameOver = True
                if SCORE > HiScore:
                    HiScore = SCORE
                return True
        
        return False
    
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    UP = True
                elif e.key == pygame.K_LEFT:
                    left = True
                elif e.key == pygame.K_RIGHT:
                    RIGHT = True
                elif e.key == pygame.K_SPACE and GameOver:
                    RESET()
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_UP:
                    UP = False
                elif e.key == pygame.K_LEFT:
                    left = False
                elif e.key == pygame.K_RIGHT:
                    RIGHT = False
        
        if not GameOver:
            if not hit:
                if left:
                    X -= speed
                    langle += ldir * 5
                    if abs(langle) > 30:
                        ldir *= -1
                else:
                    if langle != 0:
                        langle = max(-5, min(5, langle - ldir * 3))
                        if -5 <= langle <= 5:
                            langle = 0
                            ldir = 1
                        
                if RIGHT:
                    X += speed
                    rangle += rdir * 5
                    if abs(rangle) > 30:
                        rdir *= -1
                else:
                    if rangle != 0:
                        rangle = max(-5, min(5, rangle - rdir * 3))
                        if -5 <= rangle <= 5:
                            rangle = 0
                            rdir = 1
                
                min_X = L_bank + width // 2 + 10
                maxX = R - width // 2 - 10
                
                if X < min_X:
                    X = min_X
                if X > maxX:
                    X = maxX
            
            s = spd * (2.5 if UP else 1.0)
            
            for P in p:
                P[1] += s
                
                if P[1] > HEIGHT:
                    P[1] = 0
                    P[0] = random.randint(L_bank + 10, R - 10)
                    P[2] = random.randint(2, 5)
            
            for rock in rx[:]:
                rock["yy"] += rock["SPD"] * rock["V"] * (2.5 if UP else 1.0)
                if rock["yy"] > HEIGHT + 50:
                    rx.remove(rock)
            
            timer += 1
            if timer >= interval:
                newRock = {
                    "xx": random.randint(L_bank + 30, R - 30),
                    "yy": -50,
                    "w": random.randint(20, 40),
                    "H": random.randint(20, 40),
                    "SPD": spd,
                    "V": random.uniform(0.9, 1.1)
                }
                rx.append(newRock)
                timer = 0
                interval = random.randint(50, 120)
            
            CHECK()
            
            SCORE += 1
        
        screen.fill((200, 230, 255))
        
        pygame.draw.rect(screen, green, (0, 0, L_bank, HEIGHT))
        pygame.draw.rect(screen, green, (R, 0, W - R, HEIGHT))
        
        pygame.draw.rect(screen, BLUE, (L_bank, 0, riv_width, HEIGHT))
        
        for PP in p:
            x, y_, size = PP
            pygame.draw.circle(screen, lightblue, (int(x), int(y_)), size)
        
        for rock in rx:
            DRAWROCK(screen, rock["xx"], rock["yy"], rock["w"], rock["H"])
        
        drawBoat(screen)
        
        score_text = FONT.render(f"Score: {SCORE}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        
        if not GameOver:
            INS = [
                "UP ARROW: Move forward",
                "LEFT/RIGHT ARROWS: Move boat sideways",
                "Avoid the rocks!"
            ]
            
            for i, txt in enumerate(INS):
                rendered_text = smallfont.render(txt, True, (0, 0, 0))
                screen.blit(rendered_text, (10, 50 + i*25))
        
        if GameOver:
            overlay = pygame.Surface((W, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            GOtext = FONT.render("GAME OVER", True, (255, 0, 0))
            screen.blit(GOtext, (W//2 - GOtext.get_width()//2, HEIGHT//2 - 50))
            
            scoreTxt = FONT.render(f"Score: {SCORE}", True, (255, 255, 255))
            screen.blit(scoreTxt, (W//2 - scoreTxt.get_width()//2, HEIGHT//2))
            
            hiScoreTxt = FONT.render(f"High Score: {HiScore}", True, (255, 255, 255))
            screen.blit(hiScoreTxt, (W//2 - hiScoreTxt.get_width()//2, HEIGHT//2 + 40))
            
            restartTxt = FONT.render("Press SPACE to play again", True, (255, 255, 255))
            screen.blit(restartTxt, (W//2 - restartTxt.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
        
        klock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()