import pygame , sys
import os
import time
import random
import csv
import button

pygame.init()

clock = pygame.time.Clock()
FPS = 60

level = 0 #current level the player is at, currently there is only level 0
ROWS = 500
COLS = 500
TILE_TYPES = 57 #number of placable tiles in level editor
MAX_LEVELS = 1
GRAVITY = 0.75 
SCROLL_THRESH = 200
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 650
TILE_SIZE = SCREEN_HEIGHT //16
screen_scroll = 0
bg_scroll = 0
start_game = False
fight_game = False
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mega Superstar Demon Run XL Supreme El Chappo Xtreme Awesome')

#player activities
moving_left = False
moving_right = False
shoot = False
attack1 = False
attack2 = False


#loads the objects from level editor
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    #img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#loads the images of the buttons that show up in the home page and the restart button
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
fight_img = pygame.image.load('img/fight_btn.png').convert_alpha()

#loads all the other crucial images such as the background and some items
bg_img = pygame.image.load('img/Background/bg.jpg').convert_alpha()
bg2_img = pygame.image.load('img/Background/bg2.jpg').convert_alpha()
bg3_img = pygame.image.load('img/Background/bg3.png').convert_alpha()
bg3_img = pygame.transform.scale(bg3_img, (700,700))
bg5_img = pygame.image.load('img/Background/bg5.jpg').convert_alpha()
arrow_img = pygame.image.load('img/icons/arrow/0.png').convert_alpha()
axe_img = pygame.image.load('img/icons/axe/0.png').convert_alpha()
heal_img = pygame.image.load('img/icons/items/0.png').convert_alpha()
ammo_img = pygame.image.load('img/icons/items/1.png').convert_alpha()
item_boxes = {'Health' : heal_img,
              'Ammo' : ammo_img
}

BG = ('grey')

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def draw_bg():
    screen.fill(BG)
    screen.blit(bg_img, (0 - bg_scroll,0))
#function to restart everything on the level by clearing all data groups
def reset_level():
    enemy1_group.empty()
    enemy2_group.empty()
    enemy3_group.empty()
    arrow_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    lava_group.empty()
    exit_group.empty()
    axe_group.empty()

    data = []
    r = [-1] * COLS
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

#defines the character class that is used for both players and enemies, this class will contain all the stats needed although some stats are only needed by player classes and some only by enemy classes
class character(pygame.sprite.Sprite):
    def __init__(self,char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.y = y
        self.x = x
        self.delay_timer = 0
        self.shooting = False
        self.attacking1 = False
        self.attacking2 = False
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.shoot1_cooldown = 0
        self.attack1_cooldown = 0
        self.attack2_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.hurting = False
        self.direction = 1
        self.vel_y = 0
        self.vel_x = 0
        self.in_air = True
        self.jump = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(-0, 0, 500, 500)
        self.vision2 = pygame.Rect(-0, 0, 500, 50)
        self.vision3 = pygame.Rect(-0, 0, 100, 50)
        self.hurtbox1 = pygame.Rect(-0, 0, 150, 20)
        self.hurtbox2 = pygame.Rect(-0, 0, 50, 150)
        self.idling = False
        self.idling_counter = 0
        #used for the animations, the algorithm will load the images and cycle through them depending on the animation type
        animation_types = ['Idle', 'Run', 'Jump', 'Death','Attack','Attack1','Attack2','Hurt']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), (img.get_height() * scale)))
                temp_list.append(img) #3 4:03
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) 
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    #returns x coordinate
    def get_x(self):
        return self.x
    #returns y coordinate
    def get_y(self):
        return self.y
    #updates the class, used to update the animation,check if the character is alive and for the attack cooldowns
    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1 #4 20:00
        if self.shoot1_cooldown > 0:
            self.shoot1_cooldown -=1
        if self.attack1_cooldown > 0:
            self.attack1_cooldown -= 1
        if self.attack2_cooldown > 0:
            self.attack2_cooldown -= 1
        if self.attack1_cooldown > 30:
            pygame.draw.rect(screen, 'yellow', self.hurtbox1, 1)
        if self.attack2_cooldown > 30:
            pygame.draw.rect(screen, 'yellow', self.hurtbox2, 1)
    #move function is to make the character move
    def move(self,moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        # moving left and moving right flips the image if switching direction and moves the character's x coordinate depending on assigned speed
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        # gives the character a vertical velocity upwards while the character is in the ground
        if self.jump == True and self.in_air == False:
            self.vel_y = -18
            self.jump = False
            self.in_air = True
        # gives the character a vertical velocity downwards as gravity
        self.vel_y += GRAVITY
        # adds a vertical speed limit as real gravity would
        if self.vel_y > 10:
            self.vel_y = 10
        # changes y coordinate depending on vertical velocity
        dy += self.vel_y

        #collision detection, ensures that the character does not go through the tiles set by the map by changing the character's x and y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        # level completion detector
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
        
        
        #if self.rect.bottom > SCREEN_HEIGHT:
            #self.health = 0
        # position update and boundary for the player class
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy
        #boundary of the map for the player class
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx 

        return screen_scroll, level_complete
    # move function for flying characters so they are unaffected by gravity, exact same as previous move function aside from gravity exclusion
    def move0g(self,moving_left, moving_right, moving_up, moving_down):
        screen_scroll = 0
        dx = 0
        dy = 0
        
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if moving_up:
            self.vel_y = -self.speed

        if moving_down:
            self.vel_y = self.speed
        
        

        dy += self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx 

        return screen_scroll
    # hurt function will be called when player damage is taken and is used to create an animation and to introduce invulnerability frames after taking damage
    def hurt(self):
        self.update_action(7)
        self.vel_y = -12
        self.vel_y += GRAVITY
        self.vel_x = 12 * self.direction
        self.hurting = True
        print(self.hurting)

    # shoot function for player and will update the player animation and action as well as adding an arrow object to its group granted the player has sufficient ammo and cooldown is finished
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 200
            self.shooting = True
            self.update_action(4)
            new_arrow = arrow(self.rect.centerx + (1 * self.rect.size[0] * self.direction),self.rect.centery,self.direction, 1) #4 10:39
            arrow_group.add(new_arrow)
            self.ammo -=1
    # shoot function for the enemy and will update the enemy animation as well as adding the projectile object to its group
    def shoot1(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 200
            self.shooting = True
            self.update_action(4)
            new_axe = axe(self.rect.centerx + (1 * self.rect.size[0] * self.direction),self.rect.centery,self.direction, 1) #4 10:39
            axe_group.add(new_axe)
            self.ammo -= 1
    # a melee attack for the player that will update the player animation and attack, and if a character is within the attack's hitbox it will take damage
    def attack1(self):
        if self.attack1_cooldown == 0:
            self.attack1_cooldown = 60
            self.attacking1 = True
            self.update_action(5) # animation and action update
            self.hurtbox1.center = (self.rect.centerx + 115 * self.direction, self.rect.centery)
            pygame.draw.rect(screen, 'yellow', self.hurtbox1, 1)
            if self.hurtbox1.colliderect(player.rect): # collision detection with hitbox, reduces hp of targets
                if player.alive:
                    player.health -= 10
            for enemy in enemy1_group:
                if self.hurtbox1.colliderect(enemy.rect):
                    enemy.health -= 40
            for enemy in enemy2_group:
                if self.hurtbox1.colliderect(enemy.rect):
                    enemy.health -= 40
            for enemy in enemy3_group:
                if self.hurtbox1.colliderect(enemy.rect):
                    enemy.health -= 40

    # a second stronger and slower melee attack for the player that deals more damage with a bigger hitbox
    def attack2(self):
        if self.attack2_cooldown == 0:
            self.attack2_cooldown = 100
            self.attacking2 = True
            self.update_action(6)
            self.hurtbox2.center = (self.rect.centerx + 70 * self.direction, self.rect.centery - 80)
            pygame.draw.rect(screen, 'yellow', self.hurtbox2, 1)
            if self.hurtbox2.colliderect(player.rect):
                if player.alive:
                    player.health -= 15
            for enemy in enemy1_group:
                if self.hurtbox2.colliderect(enemy.rect):
                    enemy.health -= 60
            for enemy in enemy2_group:
                if self.hurtbox2.colliderect(enemy.rect):
                    enemy.health -= 60
            for enemy in enemy3_group:
                if self.hurtbox2.colliderect(enemy.rect):
                    enemy.health -= 60
    # defines the ai for one of the enemy classes that is designed to move around and randomly stop to detect any player in its radius(vision), if there is it will update to the attack animation and any player in its radius will take damage, it will also handle collision detection with the tiles and update the animation acordingly
    def ai1(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,100) == 1: #randomly 1/100 chance to perform
                self.update_action(0)
                self.idling = True # puts the character into idle state
                self.idling_counter = 50 
            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                
                else:
                    ai_moving_right = False
                
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left,ai_moving_right) # alternates between left to right
                self.update_action(1)
                self.move_counter += 1

                if self.move_counter > TILE_SIZE * 1: 
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.vision3.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                pygame.draw.rect(screen, 'yellow', self.vision3, 1)
                
                if self.vision3.colliderect(player.rect) and self.shoot1_cooldown == 0: # detects if player is in the character's 'vision'
                    self.update_action(4)
                    if player.alive and player.hurting == False:
                        player.health -= 25
                        player.hurt()  
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll
    # defines the ai another of the enemy classes that is designed to move around and randomly stop to detect any player in its radius(vision), if there is it will attack and call shoot1, it will also handle collision detection with the tiles and update the animation acordingly
    def ai2(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                
                else:
                    ai_moving_right = False
                
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left,ai_moving_right)
                self.update_action(1)
                self.move_counter += 1

                if self.move_counter > TILE_SIZE * 1:
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.vision2.center = (self.rect.centerx + 300 * self.direction, self.rect.centery)
                pygame.draw.rect(screen, 'yellow', self.vision2, 1)
                
                if self.vision2.colliderect(player.rect) and self.shoot1_cooldown == 0:
                    self.update_action(4)
                    if self.shooting == False and self.shoot1_cooldown == 0:
                        self.shoot1()
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll
    # third ai for the flying enemy character however is glitchy and causes crashes
    def ai3(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                
                else:
                    ai_moving_right = False
                
                ai_moving_left = not ai_moving_right
                self.move0g(ai_moving_left,ai_moving_right,False,False)
                self.update_action(1)
                self.move_counter += 1

                if self.move_counter > TILE_SIZE * 3:
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.vision.center = (self.rect.centerx + 0 * self.direction, self.rect.centery)
                pygame.draw.rect(screen, 'yellow', self.vision, 1)
                if self.vision.colliderect(player.rect):
                    self.update_action(0)
                    #qw = player.get_x()
                    #we = player.get_y()
                    #while qw > self.get_x():
                        #self.move0g(True,False,False,False)
                    #while qw < self.get_x():
                        #self.move0g(False,True,False,False)
                    #while we > self.get_y():
                        #self.move0g(False,False,False,True)
                    #while we < self.get_y():
                        #self.move0g(False,False,True,False)#crash
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll
        
    #used for animation updating, it goes through the animation list increasing the index depending on the animation cooldown
    def update_animation(self):
        ANIMATION_COOLDOWN = 40

        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # certain animations aren't supposed to be cycled and supposed to only go through once that are listed here by setting the action to false
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            elif self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) -1
                self.shooting = False
            elif self.action == 5:
                self.frame_index = len(self.animation_list[self.action]) -1
                self.attacking1 = False
            elif self.action == 6:
                self.frame_index = len(self.animation_list[self.action]) -1
                self.attacking2 = False
            elif self.action == 7:
                self.frame_index = len(self.animation_list[self.action]) -1
                self.hurting = False
            else:
                self.frame_index = 0
    # updates the player action if the new action differs from the current action
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    # function used to check if player is alive by checking if hp is above 0 and if player is dead, it renders the player unplayable and plays the death animation
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, 'RED', self.rect, 1)
# class used to store all of the tiles and their locations from the level editor and renders them from the list, depending on the tile number its added to different groups and returns the player
class World():
    def __init__(self):
        self.obstacle_list = []


    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    if tile == 0:
                        img.set_alpha(0)
                    else:
                        img.set_alpha(255)
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                # adds the tiles to their respective groups
                    if tile == 0:
                # For tile 0, we still add it to the obstacle_list, but do not draw it
                        self.obstacle_list.append(tile_data)
                    elif tile >= 1 and tile <= 47:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile >= 48 and tile <= 50:
                        lava = Lava(img, x * TILE_SIZE, y * TILE_SIZE)
                        lava_group.add(lava)
                    elif tile == 51:
                        player = character('player', x * TILE_SIZE, y * TILE_SIZE, 0.3, 6, 3)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 52:
                        enemy = character('enemy1', x * TILE_SIZE, y * TILE_SIZE, 0.7, 4, 1000)
                        enemy1_group.add(enemy)
                    elif tile == 53:
                        enemy = character('enemy2', x * TILE_SIZE, y * TILE_SIZE, 0.7, 1.5, 1000)
                        enemy2_group.add(enemy)
                    elif tile == 54:
                        enemy = character('enemy3', x * TILE_SIZE, y * TILE_SIZE, 0.7, 5, 1000)
                        enemy3_group.add(enemy)
                    elif tile == 55:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 56:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 57:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
    
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
                tile[1][0] += screen_scroll
                screen.blit(tile[0], tile[1])




#item_box = ItemBox('Health',100,300)
#item_box_group.add(item_box)
#item_box = ItemBox('Ammo',100,300)
#item_box_group.add(item_box)

#player = character('player',200,200,0.3,3,3)
#health_bar = HealthBar(10, 10, player.health, player.health)

#enemy1 = character('enemy1',100,250,0.7,0,10000)
#enemy4 = character('enemy1',0,250,0.7,0,10000)
#enemy2 = character('enemy2',200,250,0.7,0,10000)
#enemy3 = character('enemy3',300,250,0.3,1.8,10000)
#enemy1_group.add(enemy1)
#enemy2_group.add(enemy2)
#enemy3_group.add(enemy3)
#enemy1_group.add(enemy4)

# defines the decoration tile types, not to be collided with and moves with the screen
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
# defines the lava tile type, to deal damage to the player if collided with
class Lava(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.spritecollide(player, lava_group, False):
            if player.alive:
                player.health -= 25  

# to be used to enter the next level
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.images.get_height()))

    def update(self):
        self.rect.x += screen_scroll

# defines pickable items, if collided with player, will self destruct and give the player certain attributes
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self,player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 2
            self.kill()
# defines the health bar and draws it at the top right of the screen, if the health goes down or goes up it updates the size of the green bar
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, 'black', (self.x - 2,self.y - 2, 154, 24))
        pygame.draw.rect(screen, 'red', (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, 'green', (self.x, self.y, 150 * ratio, 20))
# defines the projectile for the player when calling shoot1, it defines its collision with tiles(self destruct) and with other characters(take damage) the arrow has its own animation cycle and a speed for the arrow to travel
class arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.speed = 60
        self.images = []
        for num in range(1,4):
            img = pygame.image.load(f'img/icons/arrow/{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]

        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
        self.direction = direction

    def update(self):
        ANIMATION_COOLDOWN = 40 # handles the animation cycle

        self.counter += 1
        if self.counter >= ANIMATION_COOLDOWN: 
            self.counter = 0
            self.frame_index += 1
            self.image = self.images[self.frame_index]
            if self.frame_index >= len(self.images):
                self.frame_index = 0

        self.rect.x += (self.direction * self.speed)  + screen_scroll # kills the projectile if out of bounds of the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for tile in world.obstacle_list: # kills the projectile if it collides with the tile
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, arrow_group, False): # handles the collision of the projectiles(lowers hp of targets)
            if player.alive:
                player.health -= 25
                self.kill()
        for enemy in enemy1_group:
            if pygame.sprite.spritecollide(enemy, arrow_group, False):
                if enemy.alive:
                    enemy.health -= 100
                    self.kill()
        for enemy in enemy2_group:
            if pygame.sprite.spritecollide(enemy, arrow_group, False):
                if enemy.alive:
                    enemy.health -= 100
                    self.kill() 
        for enemy in enemy3_group:
            if pygame.sprite.spritecollide(enemy, arrow_group, False):
                if enemy.alive:
                    enemy.health -= 100
                    self.kill()  
# defines the projectile for enemy2 class in the same way it was defined for player class
class axe(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.speed = 10
        self.images = []
        
        # Load multiple images for the axe animation
        for num in range(1, 4):  # Assuming you have 3 images named 1.png, 2.png, 3.png
            img = pygame.image.load(f'img/icons/axe/{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        
        self.frame_index = 0
        self.image = self.images[self.frame_index]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        self.direction = direction

    def update(self):
        ANIMATION_COOLDOWN = 40

        self.counter += 1
        if self.counter >= ANIMATION_COOLDOWN:
            self.counter = 0
            self.frame_index += 1
            
 
            if self.frame_index >= len(self.images):
                self.frame_index = 0
            
            self.image = self.images[self.frame_index] 


        self.rect.x += (self.direction * self.speed) + screen_scroll
        

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()


        if pygame.sprite.spritecollide(player, axe_group, False):
            if player.alive:
                player.health -= 25
                self.kill()
#draws the buttons on the home page
start_button = button.Button(SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT // 2 - 150, start_img, 1)
fight_button = button.Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 - 150, fight_img, 1)          
exit_button = button.Button(SCREEN_WIDTH // 2 - 380, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2) 
#defines all of the object sprite groups
enemy1_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
enemy3_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
axe_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
axe_group = pygame.sprite.Group()

#item_box = ItemBox('Health',100,300)
#item_box_group.add(item_box)
#item_box = ItemBox('Ammo',100,300)
#item_box_group.add(item_box)

#player = character('player',200,200,0.3,3,3)
#health_bar = HealthBar(10, 10, player.health, player.health)

#enemy1 = character('enemy1',100,250,0.7,0,10000)
#enemy4 = character('enemy1',0,250,0.7,0,10000)
#enemy2 = character('enemy2',200,250,0.7,0,10000)
#enemy3 = character('enemy3',300,250,0.3,1.8,10000)
#enemy1_group.add(enemy1)
#enemy2_group.add(enemy2)
#enemy3_group.add(enemy3)
#enemy1_group.add(enemy4)

# used to define the world by appending the world data list with the data from the csv file obtained from level editor
world_data = []
r = [-1] * COLS
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)


with open(f'level{level}_data.csv', newline = '') as csvfile: # opens the csv file and adds the new line to the list
    reader = csv.reader(csvfile, delimiter =',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
# creates the home page 
    if start_game == False:
        screen.fill('black') # draws the background
        screen.blit(bg2_img, (0,0))
        screen.blit(bg3_img, (470,-50))
        if start_button.draw(screen): # draws the respective buttons
            print("start")
            start_game = True
        if exit_button.draw(screen):
            run = False
        if fight_button.draw(screen):
            fight_game = True

    
    elif start_game == True:
        clock.tick(FPS)

        draw_bg()
        #draw world map
        world.draw()
        health_bar.draw(player.health)
        draw_text(f'{player.ammo}', font, 'white', 10, 35)
        
        player.update() # calls the player update function
        player.draw()
        
        for enemy in enemy1_group: # initialises the enemy character class with its ai and updates it
            enemy.ai1() 
            enemy.update() 
            enemy.draw()

        for enemy in enemy2_group: # initialises the enemy2 character class with its ai and updates it
            enemy.ai2()
            enemy.update()
            enemy.draw()

        for enemy in enemy3_group: # initialises the enemy3 character class with its ai and updates it
            enemy.ai3()
            enemy.update()
            enemy.draw()
        # draws all of the item groups and tiles
        axe_group.update()
        axe_group.draw(screen)
        arrow_group.update()
        arrow_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)
        decoration_group.update()
        decoration_group.draw(screen)
        lava_group.update()
        lava_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)
        # actions of the players, detects if certain actions are being done and if so calls the appropriate function and updates the action
        if player.alive == True:
            if player.shooting == False and player.attacking1 == False and player.attacking2 == False and player.hurting == False:
                if shoot:
                    player.shoot()
                if player.shooting:
                    player.update_action(4)
                elif attack1:
                    player.attack1()
                elif player.attacking1:
                    player.update_action(5)
                elif attack2:
                    player.attack2()
                elif player.attacking2:
                    player.update_action(6)
                elif player.in_air:
                    player.update_action(2)
                elif moving_left or moving_right:
                    player.update_action(1)
                else:
                    player.update_action(0)
                # moves the background depending on the player's movement    
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll * 0.03
                # switches to the next level if the level is complete(player collides with exit) while the levels are still under max levels
                if level_complete:
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS: # ensures level does not overflow
                        with open(f'level{level}_data.csv', newline = '') as csvfile: #opens a new csv file to load
                            reader = csv.reader(csvfile, delimiter =',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
        else: # draws the restart button if the player is dead and if clicked restarts the whole level by rereading the csv file
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter =',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)
    # attempt to make a fighting game
    elif fight_game == True:
        screen.fill('black')
        screen.blit(bg5_img, 0,0)
        print("fight")

    # event handler, controls for the players, when certain keys are placed certain actions will be done by the player
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_h:
                shoot = True
            if event.key == pygame.K_g:
                attack1 = True
            if event.key == pygame.K_t:
                attack2 = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
        # when certain keys aren't being pressed, actions will be reset to false
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_h:
                shoot = False
            if event.key == pygame.K_g:
                attack1 = False
            if event.key == pygame.K_t:
                attack2 = False

    pygame.display.update()