"""
Welcome to a fun spaceship game called UFOs VS. U, where you are aimed to attack as many enemy ships as possible and 
prevent them from touching the bottom of the screen (Earth), to avoid losing. 
Sunny Zhang January 25th, 2021
""" 
import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UFOs VS. U")

# Upload images needed for the game
# Player's player
PURPLE_SPACE_SHIP = pygame.image.load(os.path.join("images", "pixel_ship_purple.png"))
# Enemy's players
RED_SPACE_SHIP = pygame.image.load(os.path.join("images", "pixel_ship_red.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("images", "pixel_ship_blue.png"))
GREY_SPACE_SHIP = pygame.image.load(os.path.join("images", "pixel_ship_grey.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("images", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("images", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("images", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("images", "pixel_laser_yellow.png"))

# Background Image
SPACE_GROUND = pygame.transform.scale(pygame.image.load(os.path.join("images", "background-space.png")), (WIDTH, HEIGHT))

# Name characters

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img 
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, object):
        return collide(self, object)


class Ship:
    MANAGECOOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        # Lasers are slowed dwon
        self.cool_down_counter = 0  

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def laser_movement(self, velocity, object):
        self.cooldown()
        for laser in self.lasers: # Each laser that we shot
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.MANAGECOOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:   # Make sure cool down counter starts at 0
            laser = Laser(self.x, self.y, self.laser_img) # Then, create new laser
            self.lasers.append(laser)  # Add to lasers list
            self.cool_down_counter = 1 # Start counting up

    def get_height(self):
        return self.ship_img.get_height()

    def get_width(self):
        return self.ship_img.get_width()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PURPLE_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def laser_movement(self, velocity, objects):
        self.cooldown()
        for laser in self.lasers: # Each laser that we shot
            laser.move(velocity) #Move the laser
            if laser.off_screen(HEIGHT): # If off the screen, 
                self.lasers.remove(laser) # Remove it
            else:
                for object in objects: # If not off the screen, for each object in the object list
                    if laser.collision (object): # If laser collides with object
                        objects.remove(object) # Remove it  
                        if laser in self.lasers:                        
                            self.lasers.remove(laser)
    
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health /self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "grey": (GREY_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    
    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, velocity):
        self.y += velocity # Enemy ships only move down

def collide (object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 4
    main_font = pygame.font.SysFont("impact", 50)
    lost_font = pygame.font.SysFont("impact", 30)
    enemies = []
    wave_length = 5 # Batch of enemies move down the screen
    # Enemy's velocity
    enemy_velocity = 1
    # Object's velocity 
    player_velocity = 5 
    # Laser's velocity
    laser_velocity = 5

    player = Player(300, 650)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    # Background illustration
    def redraw_window():
        WIN.blit(SPACE_GROUND, (0,0))
        # Take background image and draw at (0,0), filling entire screen 
        # Draw text

        lives_word = main_font.render(f"Lives: {lives}", 1, (166,90,252))
        level_word = main_font.render(f"Level: {level}", 1, (166,90,252))

        WIN.blit(lives_word, (10,10))
        WIN.blit(level_word, (590,10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You lost:( Please wait.", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <=0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else: 
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                # Enemy ship spawns down at differnt coordinates
                enemy = Enemy(random.randrange(50, 650), random.randrange(-1600, -110), random.choice(["red", "blue", "grey"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

         # Check 60 times / sec to see if key is being pressed
         # Checking for left, right, up, down keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: 
            player.x -= player_velocity
        if keys[pygame.K_RIGHT]: 
            player.x += player_velocity
        if keys[pygame.K_UP]: 
            player.y -= player_velocity
        if keys[pygame.K_DOWN]: 
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_RETURN]:
            quit()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.laser_movement(laser_velocity, player)
            if random.randrange(0, 120) == 1: # Enemy shoots lasers at random
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy) # Remove this object from the enemies list

        player.laser_movement(-laser_velocity, enemies) # Check if player hit enemies

def main_menu():
    title_font = pygame.font.SysFont("impact", 22)
    second_line = pygame.font.SysFont("impact", 20)    
    third_line = pygame.font.SysFont("impact", 22)
    fourth_line = pygame.font.SysFont("impact", 22)
    fifth_line = pygame.font.SysFont("impact", 22)
    last_line = pygame.font.SysFont("impact", 21)

    run = True
    while run:
        WIN.blit(SPACE_GROUND,(0,0))
        title_label = title_font.render("Welcome to Sunny Zhang's game, 'UFOs VS. U!' Completed by: January 25th, 2021.", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 300))
        second_label = second_line.render("Avoid contact with enemies, press space bar to shoot, so you don't get hit to increase levels!", 1, (255,255,255))
        WIN.blit(second_label, (WIDTH/2 - second_label.get_width()/2, 350))
        third_label = third_line.render("The more enemy and player contacts, the shorter your health.", 1, (255,255,255))
        WIN.blit(third_label, (WIDTH/2 - third_label.get_width()/2, 400))
        fourth_label = fourth_line.render("Don't let the enemies get to the bottom of the screen, or else you'll lose a life.", 1, (255,255,255))
        WIN.blit(fourth_label, (WIDTH/2 - fourth_label.get_width()/2, 450))
        fifth_label = fifth_line.render("Use arrow keys to play!", 1, (255,255,255))
        WIN.blit(fifth_label, (WIDTH/2 - fifth_label.get_width()/2, 500))
        last_label = last_line.render("Click mouse to play. Exit to quit the game NOW, or press enter to exit DURING the game.", 1, (255,255,255))
        WIN.blit(last_label, (WIDTH/2 - last_label.get_width()/2, 600))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
