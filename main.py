import pygame
import random
import os
import time
import math

pygame.font.init()

BOSS_LEVEL = 1
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
BOSS = pygame.image.load(os.path.join("assets","krbalek_milan.png"))

YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

# laser
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png")) 
KRBOS_LASER = pygame.image.load(os.path.join("assets","laser_krbos.png"))
# Background

BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y < height and self.y >= 0)

    def collision(self, obj):
        return collide(self,obj)



class Ship:
    COOLDOWN = 10

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,window):
        # pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0 :
            self.cool_down_counter += 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER 
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self,vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 100
                        self.lasers.remove(laser)
                        if obj.health <= 0:
                            objs.remove(obj)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x,self.y + self.get_height() + 10,self.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x,self.y + self.get_height() + 10,self.get_width() * self.health /self.max_health, 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP,RED_LASER,1.5),
                "blue": (BLUE_SPACE_SHIP,BLUE_LASER,1),
                "green": (GREEN_SPACE_SHIP,GREEN_LASER,2)
    }

    def __init__(self,x,y,color,health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img, self.enemy_vel = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width()/2 - 5 ,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Boss(Ship):
    def __init__(self,x,y,health = 2000):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img,self.enemy_vel = BOSS,KRBOS_LASER,0.3
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += random.randint(-3,3) + vel
        self.x += random.randint(-3,3)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width()/2 - 5 ,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x,self.y + self.get_height() + 10,self.get_width(), 10))
        pygame.draw.rect(window, (255,0,255), (self.x,self.y + self.get_height() + 10,self.get_width() * self.health /self.max_health, 10))

def collide(obj1,obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x,offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("arialblack", 70)



    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 6

    player = Player(300,600)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # Draw text

        lives_label = main_font.render(f"LIVES: {lives}",1, (255,255,255))
        level_label = main_font.render(f"LEVEL: {level}",1, (255,255,255))
        boss_label = main_font.render(f"BOSS",1, (255,255,255))

        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH - level_label.get_width() -10,10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost and level <= BOSS_LEVEL:
            lost_label = lost_font.render("Game over!!!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2,HEIGHT/2 - lost_label.get_height()/2))

        if level == BOSS_LEVEL:
            WIN.blit(boss_label,(WIDTH/2 - boss_label.get_width()/2,10))

        if level == BOSS_LEVEL + 1:
            win_label = lost_font.render("You Win!!!", 1, (0,255,0))
            WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2,HEIGHT/2 - win_label.get_height()/2))
            
            

        pygame.display.update()

    while run:
        clock.tick(FPS) 
        redraw_window()

        if lives <= 0 or player.health < 0 or level >= BOSS_LEVEL + 1:
            lost = True
            lost_count += 1

        if lost or level >= BOSS_LEVEL + 1:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            if level < BOSS_LEVEL:
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50,WIDTH-100), random.randrange(-1500, -100),random.choice(["red","green","blue"]))
                    enemies.append(enemy)
            if level == BOSS_LEVEL: 
                boss = Boss(WIDTH/2 + 30,0)
                enemies.append(boss)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]  and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            if enemy.enemy_vel == 0.3 and random.randrange(0, FPS) == 1:
                enemy.shoot()
            elif random.randrange(0, 4 * FPS) == 1:
                enemy.shoot()

            enemy.move(enemy.enemy_vel)
            enemy.move_lasers(laser_vel, player)


            if collide(enemy, player) and level < BOSS_LEVEL:
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT and level < BOSS_LEVEL:
                lives -= 1
                enemies.remove(enemy)
            elif collide(enemy, player) and level == BOSS_LEVEL:
                player.health -= 100
            elif enemy.y + enemy.get_height() > HEIGHT and level == BOSS_LEVEL:
                lives -= 5

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:

        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2,300))
        pygame.display.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()