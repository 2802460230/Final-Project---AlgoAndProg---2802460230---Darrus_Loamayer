import pygame
import button
import csv
import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')


#define game variables
ROWS = 500
MAX_COLS = 500
TILE_SIZE = SCREEN_HEIGHT // 16
TILE_TYPES = 57
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll_up = False
scroll_down = False
scrollh = 0
scrollv = 0
scroll_speed = 1


#load images
bg_img = pygame.image.load('img/background/bg.jpg').convert_alpha()

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
	#img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	if x in [51]:
		img = pygame.transform.scale(img, (int(img.get_width() * 0.3), (img.get_height() * 0.3)))
		if x in [51,52,53,54]:
			img = pygame.transform.scale(img, (int(img.get_width() * 0.7), (img.get_height() * 0.7)))
	
	img_list.append(img)

save_img = pygame.image.load('img/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()


#define colours


#define font
font = pygame.font.SysFont('Futura', 30)

#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)

#create ground
for tile in range(0, MAX_COLS):
	world_data[ROWS - 1][tile] = 0


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#create function for drawing background
def draw_bg():
    screen.fill('black')
    width = bg_img.get_width()
    for x in range(2):
        screen.blit(bg_img, ((x * width)-scrollh * 0.03, 0))

#draw grid
def draw_grid():
    # Vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, 'white', (c * TILE_SIZE - scrollh, -1000 - scrollv), 
                         (c * TILE_SIZE - scrollh, ROWS * TILE_SIZE - scrollv))
    # Horizontal lines

    for c in range(ROWS + 1000):
        pygame.draw.line(screen, 'white', (0, (c - 1000) * TILE_SIZE - scrollv), 
                         (SCREEN_WIDTH, (c - 1000) * TILE_SIZE - scrollv))


#function for drawing the world tiles
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scrollh, y * TILE_SIZE - scrollv))



#create buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
#make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    # Load and scale the image
    image = pygame.transform.scale(img_list[i], (TILE_SIZE, TILE_SIZE))  # Scale the image to TILE_SIZE

    # Create the button with the scaled image
    tile_button = button.Button(SCREEN_WIDTH + (50 * button_col) + 50, 50 * button_row + 50, image, 1)
    button_list.append(tile_button)

    button_col += 1
    if button_col == 5:  # Change this number if you want a different number of buttons per row
        button_row += 1
        button_col = 0


run = True
while run:

	clock.tick(FPS)

	draw_bg()
	draw_grid()
	draw_world()

	draw_text(f'Level: {level}', font, 'white', 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
	draw_text('Press UP or DOWN to change level', font, 'white', 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

	#save and load data
	if save_button.draw(screen):
		#save level data
		with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for row in world_data:
				writer.writerow(row)
		#alternative pickle method
		#pickle_out = open(f'level{level}_data', 'wb')
		#pickle.dump(world_data, pickle_out)
		#pickle_out.close()
	if load_button.draw(screen):
		#load in level data
		#reset scroll back to the start of the level
		scroll = 0
		with open(f'level{level}_data.csv', newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for x, row in enumerate(reader):
				for y, tile in enumerate(row):
					world_data[x][y] = int(tile)
		#alternative pickle method
		#world_data = []
		#pickle_in = open(f'level{level}_data', 'rb')
		#world_data = pickle.load(pickle_in)
				

	#draw tile panel and tiles
	pygame.draw.rect(screen, 'grey', (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

	#choose a tile
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count

	#highlight the selected tile
	pygame.draw.rect(screen, 'white', button_list[current_tile].rect, 3)

	#scroll the map
	if scroll_up == True:
		scrollv -= 5 * scroll_speed
	if scroll_down == True and scrollv < 5000:
		scrollv += 5 * scroll_speed

	if scroll_left == True and scrollh > 0:
		scrollh -= 5 * scroll_speed
	if scroll_right == True and scrollh < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
		scrollh += 5 * scroll_speed

	#add new tiles to the screen
	#get mouse position
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scrollh) // TILE_SIZE
	y = (pos[1] + scrollv) // TILE_SIZE

	#check that the coordinates are within the tile area
	if pos[0]:
		#update tile value
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				scroll_up = True
			if event.key == pygame.K_DOWN:
				scroll_down = True
			if event.key == pygame.K_LEFT:
				scroll_left = True
			if event.key == pygame.K_RIGHT:
				scroll_right = True
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 5
			if event.key == pygame.K_9:
				level += 1
			if event.key == pygame.K_0 and level > 0:
				level -= 1


		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				scroll_left = False
			if event.key == pygame.K_RIGHT:
				scroll_right = False
			if event.key == pygame.K_UP:
				scroll_up = False
			if event.key == pygame.K_DOWN:
				scroll_down = False
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 1


	pygame.display.update()

pygame.quit()

