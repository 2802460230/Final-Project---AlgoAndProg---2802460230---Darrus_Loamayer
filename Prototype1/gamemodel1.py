import pygame , sys
import os
import time
import random
import csv

pygame.init()

clock = pygame.time.Clock()
FPS = 60

level = 0
ROWS = 500
COLS = 500
TILE_TYPES = 57

GRAVITY = 0.75

SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 650
TILE_SIZE = SCREEN_HEIGHT //16

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mega Superstar Demon Run XL Supreme El Chappo Xtreme Awesome')

moving_left = False
moving_right = False
shoot = False

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    #img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

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


class character(pygame.sprite.Sprite):
    def __init__(self,char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.delay_timer = 0
        self.shooting = False
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.in_air = True
        self.jump = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        self.move_counter = 0
        self.vision = pygame.Rect(-0, 0, 500, 500)
        self.idling = False
        self.idling_counter = 0

        animation_types = ['Idle', 'Run', 'Jump', 'Death','Attack']
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

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1 #4 20:00

    def move(self,moving_left, moving_right):
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

        if self.jump == True and self.in_air == False:
            self.vel_y = -18
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
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

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 200
            self.shooting = True
            self.update_action(4)
            new_arrow = arrow(self.rect.centerx + (1 * self.rect.size[0] * self.direction),self.rect.centery,self.direction, 1) #4 10:39
            arrow_group.add(new_arrow)
            self.ammo -=1


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,2000) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
                if self.vision.colliderect(player.rect):
                    self.update_action(0)
                    #attack not yet intitialised
            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                
                else:
                    ai_moving_right = False
                
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left,ai_moving_right)
                self.update_action(1)
                self.move_counter += 1

                self.vision.center = (self.rect.centerx + 0 * self.direction, self.rect.centery)
                pygame.draw.rect(screen, 'yellow', self.vision, 1)

                if self.move_counter > TILE_SIZE * 20:
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.idling_counter -=1
                if self.idling_counter <= 0:
                    self.idling = False

    def update_animation(self):
        ANIMATION_COOLDOWN = 40

        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            elif self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) -1
                self.shooting = False
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, 'RED', self.rect, 1)

class World():
    def __init__(self):
        self.obstacle_list = []


    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile == 0:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 1 and tile <= 47:
                        decoration = Decoration(img,x * TILE_SIZE,y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile >= 48 and tile <= 50:
                        lava = Lava(img,x * TILE_SIZE,y * TILE_SIZE)
                        lava_group.add(lava)
                    elif tile == 51:
                        player = character('player',x * TILE_SIZE,y * TILE_SIZE,0.3,3,3)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 52:
                        enemy = character('enemy1', x * TILE_SIZE, y * TILE_SIZE,0.7,0,10000)
                        enemy1_group.add(enemy)
                    elif tile == 53:
                        enemy = character('enemy2', x * TILE_SIZE, y * TILE_SIZE,0.7,0,10000)
                        enemy1_group.add(enemy)
                    elif tile == 54:
                        enemy = character('enemy3', x * TILE_SIZE, y * TILE_SIZE,0.7,0,10000)
                        enemy1_group.add(enemy)
                    elif tile == 55:
                        item_box = ItemBox('Health',x * TILE_SIZE,y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 56:
                        item_box = ItemBox('Ammo',x * TILE_SIZE,y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 57:
                        exit = Exit(img,x * TILE_SIZE,y * TILE_SIZE)
                        exit_group.add(exit)
        
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
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

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.images.get_height()))

class Lava(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.images.get_height()))

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.images.get_height()))


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self,player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 2
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.heath = health
        
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, 'black', (self.x - 2,self.y - 2, 154, 24))
        pygame.draw.rect(screen, 'red', (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, 'green', (self.x, self.y, 150 * ratio, 20))

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
        ANIMATION_COOLDOWN = 40

        self.counter += 1
        if self.counter >= ANIMATION_COOLDOWN:
            self.counter = 0
            self.frame_index += 1
            self.image = self.images[self.frame_index]
            if self.frame_index >= len(self.images):
                self.frame_index = 0

        self.rect.x += (self.direction * self.speed) 
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        if pygame.sprite.spritecollide(player, arrow_group, False):
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

class Axe(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.vel_y = 7
        self.image = axe_img
        self.image = arrow_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

enemy1_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
enemy3_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
axe_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

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

world_data = []
r = [-1] * COLS
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f'level{level}_data.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter =',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)

    draw_bg()
	#draw world map
    world.draw()
    health_bar.draw(player.health)
    draw_text(f'{player.ammo}', font, 'white', 10, 35)
    
    player.update()
    player.draw()

    for enemy in enemy1_group:
        enemy.update()
        enemy.draw()

    for enemy in enemy2_group:
        enemy.update()
        enemy.draw()

    for enemy in enemy3_group:
        enemy.ai()
        enemy.update()
        enemy.draw()
    
    
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

    if player.alive == True and player.shooting == False:
        if shoot:
            player.shoot()
        if player.shooting:
            player.update_action(4)
        elif player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)
        player.move(moving_left, moving_right)

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
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_h:
                shoot = False

    pygame.display.update()
