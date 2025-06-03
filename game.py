import os
import pygame
import sys
import csv
import random
from pygame import mixer
import time

pygame.init()
mixer.init()
#mixer.music.load('music/song.mp3')
BASE_WIDTH = 1366
BASE_HEIGHT = 768
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BASE_TILE_SIZE = 32
scale_x = SCREEN_WIDTH / BASE_WIDTH
scale_y = SCREEN_HEIGHT / BASE_HEIGHT
font = pygame.font.SysFont("Bauhaus 93", 30)
font1 = pygame.font.SysFont("Jersey 10", 30)
countdown_time = 80
EXTRA=(0,0,0,0)
WHITE = (255, 255, 255)
YELL=(255,255,0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
TRANS = (255,0,0,0)
IMAGE_WIDTH = 60 * scale_x
IMAGE_HEIGHT = 45 * scale_y
RECT_HEIGHT = IMAGE_HEIGHT - (5*scale_y)
RECT_WIDTH = IMAGE_WIDTH - (5*scale_x)
WIDTH_OFFSET = 0
HEIGHT_OFFSET = 3
SHOW_HITBOXES = False
BASE_SPEED = 400
DEFAULT_SPEED=BASE_SPEED*scale_x
buff_spawn_time = 10000  # buff spawns every x seconds
last_buff_spawn = pygame.time.get_ticks()
BUFF_HEIGHT_OFFSET = 40*scale_y
#set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu")


class TransparentButton:
    def __init__(self, x, y, width, height, text, bg_color, text_color, alpha):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text = text
        self.text_color = text_color
        self.alpha = alpha

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((*bg_color, alpha))

    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)
        text_surface = font1.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def splash_screen(images):
    # Set up timing variables
    fade_duration = 1  # duration for fade in and fade out (in seconds)
    total_duration = 2  # total display duration (in seconds)
    clock = pygame.time.Clock()
    
    for image_path in images:
        # Load splash screen image
        splash_image = pygame.image.load(image_path).convert_alpha()
        splash_image = pygame.transform.scale(splash_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create a copy of the image to manipulate its transparency
        splash_surface = splash_image.copy()
        
        # Fade in
        for alpha in range(0, 255, 5):  # Increase alpha from 0 to 255 for fade-in
            splash_surface.set_alpha(alpha)
            screen.blit(splash_surface, (0, 0))
            pygame.display.update()
            clock.tick(60)  # 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        # Hold the splash screen fully visible for some time
        start_time = time.time()
        while time.time() - start_time < total_duration - (2 * fade_duration):
            screen.blit(splash_surface, (0, 0))
            pygame.display.update()
            clock.tick(60)  # 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        # Fade out
        for alpha in range(255, 0, -5):  # Decreas N e alpha from 255 to 0 for fade-out
            splash_surface.set_alpha(alpha)
            screen.blit(splash_surface, (0, 0))
            pygame.display.update()
            clock.tick(60)  # 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

def game(background,Tiles,sigma):
    pygame.display.set_caption("Platform")

    # load background images
    bg_image = pygame.image.load(background).convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # more global variables
    clock = pygame.time.Clock()
    start_ticks = pygame.time.get_ticks()
    TILE_SIZE = int(BASE_TILE_SIZE * min(scale_x, scale_y))

    class Player(pygame.sprite.Sprite):
        def __init__(self, image_folder, keys, platforms):
            super().__init__()
# super is to make the function becomes a parent function, meaning that when we refer to it again in another class
# it will have access and add on to the parent one instead of creating a new one
            self.idle = [
                pygame.transform.scale(
                    pygame.image.load(os.path.join('images', image_folder, f'Idle{i + 1}.png')).convert_alpha(),
                    (IMAGE_WIDTH, IMAGE_HEIGHT)) for i in range(8)
            ]
            # above is the idle animation, we add images to the list 
            self.current_idle = 0 #idle animation index
            self.sprint = [
                pygame.transform.scale(
                    pygame.image.load(os.path.join('images', image_folder, f'walk{i + 1}.png')).convert_alpha(),
                    (IMAGE_WIDTH, IMAGE_HEIGHT)) for i in range(7)
            ]
            # the method is the same for sprint animation also
            self.current_sprint = 0 # the sprint animation index
            self.image = pygame.Surface((RECT_WIDTH, RECT_HEIGHT), pygame.SRCALPHA)#load the image
            self.rect = self.image.get_rect()#get_rect() is to get the coordinates , rect is refer as an image variable with correct position
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) #measure the center if the rect
            self.change_x = DEFAULT_SPEED #rate of horizontal movement, basically default speed of the player
            self.change_y = 0 #rate of vertical movement, same as horizontal, just vertically
            self.jump_power = int((-850)*scale_y) #the lower the jump power, the higher the jump, basically it reduces the gravity to jump higher
            self.gravity = 2000 #gravity
            self.on_ground = False #to check whether the player hit an object
            self.facing_right = True #to check if player is facing right so that we can modify the direction of animation
            self.keys = keys #movement keys
            self.platforms = platforms 
            self.player_image = self.idle[0] # to load the image first for the animation
            self.is_idling = False
            self.is_sprinting = False
            #the two above is to load the animation only when it is true
            self.buffs = [] #this is to hold the buffs the player currently have
            self.speed = DEFAULT_SPEED #this is to make each player have individual speed, e.g player1.speed is a different variable from player2.buff so if 1 have buff we can modify separately

        def idling(self):
            self.is_idling = True
            self.is_sprinting = False

        def update_idle(self, speed):
            self.current_idle += speed # change the index, e.g   index 0, and speed is 0.2 it will increase from 1.0, to 1.2, 1.4, .....  
            if self.current_idle >= len(self.idle):
                self.current_idle = 0 #reset the index if exceeds animation range, because animation basically is just looping images
            self.player_image = self.idle[int(self.current_idle)] #since it's int form, it round down the float, so the lower the speed, we can manage the fps for animation

        def sprinting(self):
            self.is_sprinting = True
            self.is_idling = False

        def update_sprint(self, speed):
            self.current_sprint += speed
            if self.current_sprint >= len(self.sprint):
                self.current_sprint = 0
            self.player_image = self.sprint[int(self.current_sprint)] #same method for sprint animation

        def update(self, delta_time): #redraw the character to update its position
            self.change_y += self.gravity * delta_time
            self.rect.x += self.change_x * delta_time
            self.check_collisions('horizontal')   #prevent from exiting the resolution, to check if it reaches the edges border
            self.rect.y += self.change_y * delta_time 
            self.check_collisions('vertical')#prevent from exiting the screen vertically
            if self.is_sprinting:
                self.update_sprint(0.2) #load animation sprint when moving, and idling when not moving
            elif self.is_idling:
                self.update_idle(0.3)
            self.check_screen_edges() #

            # check whether the player buff is still active
            for buff in self.buffs[:]:
                buff.update()
                if not buff.active:
                    self.remove_buff(buff)

        def check_collisions(self, direction): #check collision with the edge and the platform
            if direction == 'horizontal':
                hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
                for platform in hit_list:
                    if self.change_x > 0:
                        self.rect.right = platform.rect.left
                    elif self.change_x < 0:
                        self.rect.left = platform.rect.right
                    self.change_x = 0
            elif direction == 'vertical':
                hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
                for platform in hit_list:
                    if self.change_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.change_y = 0
                        self.on_ground = True
                    elif self.change_y < 0:
                        self.rect.top = platform.rect.bottom
                        self.change_y = 0
                if len(hit_list) == 0:
                    self.on_ground = False

        def check_screen_edges(self): #initialize the screen edges
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
                self.on_ground = True
                self.change_y = 0

        def draw(self, surface): #just to draw image
            flipped_image = pygame.transform.flip(self.player_image, not self.facing_right, False)
            offset_x = WIDTH_OFFSET if self.facing_right else -WIDTH_OFFSET
            offset_y = HEIGHT_OFFSET
            image_rect = flipped_image.get_rect(center=(self.rect.centerx + offset_x, self.rect.centery - offset_y)) #remodify the coordinates for the flipped image to remain the same place
            surface.blit(flipped_image, image_rect) #draw the images
            if SHOW_HITBOXES: #to show hitboxes when needed, we use it to debug so it doesn't affect the game
                pygame.draw.rect(surface, EXTRA, self.rect, 2)
        def jump(self): 
            if self.on_ground:
                self.change_y = self.jump_power
                self.on_ground = False
                self.is_sprinting = False

        def go_left(self):
            self.change_x = -self.speed
            self.facing_right = False
            self.is_idling = False
            self.sprinting()# sprint animation when moved

        def go_right(self):
            self.change_x = self.speed
            self.facing_right = True
            self.sprinting() #sprint anim
            self.is_idling = False

        def stop(self):
            self.change_x = 0
            self.is_sprinting = False
            self.idling()# idle anim when stop

        def add_buff(self, buff):
            global DEFAULT_SPEED
            #call the function remove buff type
            self.remove_buff_type(buff.buff_type)

            # if picked up a new buffs, the player.buffs list will store that buff and apply the effect to it.
            buff.activate()
            self.buffs.append(buff)
            
            # Apply the effect
            if buff.buff_type == "speed": #speed buff basically increase self speed
                self.speed += buff.effect
                self.jump_power -= buff.effect/3 #increase jump power when you acquire speed buffs, I divide the buff effects by 2 because I don't want to increase the jump power by a lot
            elif buff.buff_type == "inverted": #invert the direction of movement by invert the speed, by timing it by -1
                self.speed *= -1
            elif buff.buff_type == "freeze": #set everything to 0 to freeze the player's movement
                self.speed = 0
                self.jump_power=0

        def remove_buff(self, buff): #def a function to call remove buff effect function and remove overdue buff from the player.buffs list
            self.remove_buff_effect(buff)
            self.buffs.remove(buff)

        def remove_buff_type(self, buff_type): #this function is to prevent stacking buffs
            for buff in self.buffs:
                if buff.buff_type == buff_type: #check whether the new buff has already existed in the list, if has, then replace it with the new one and reset the buff duration
                    self.remove_buff(buff)
                    break

        def remove_buff_effect(self, buff):#to reset to normal conditions when the buffs expired
            global DEFAULT_SPEED #to access the default speed variable outside the udf  
            self.speed = DEFAULT_SPEED
            self.jump_power = -850# reset to default


    class Tag(pygame.sprite.Sprite):
        def __init__(self, player):
            super().__init__()
            self.player = player
            self.image = pygame.image.load(os.path.join('images/Blue_Slime', 'tag arrow.png')).convert_alpha()#load the tag
            TAG_WIDTH = 30#set the width and height
            TAG_HEIGHT = 30
            self.image = pygame.transform.scale(self.image, (TAG_WIDTH, TAG_HEIGHT))#modify its  size depending on the width and height

            self.rect = self.image.get_rect() #get the coordinates
            self.rect.center = (self.player.rect.centerx, self.player.rect.top - 10) #to make it positioned directly above the tagged player

        def update(self, delta_time=None):
            self.rect.center = (self.player.rect.centerx, self.player.rect.top - 10) #to repeatedly update the position of the tag

        def switch_target(self, tagged):
            
            self.player = tagged
             #to make the tag switched when collision between the 2 players happened
            self.update()  # reupdate the tag to the tagged player immediately
    class Buff:
        
        def __init__(self, buff_type, effect, duration):
            self.buff_type = buff_type
            self.effect = effect
            self.duration = duration
            self.active = False
            self.start_time = None

        def activate(self):
            self.active = True
            self.start_time = pygame.time.get_ticks()

        def deactivate(self):
            self.active = False

        def update(self):
            if self.active and pygame.time.get_ticks() - self.start_time > self.duration: #if it is active and (current time - start time > duration of buff): 
                self.deactivate() #deactivate the buffs

    class BuffItem(pygame.sprite.Sprite):
        def __init__(self, buff_type, effect, duration, x, y):
            super().__init__()
            self.buff = Buff(buff_type, effect, duration)
            self.image = pygame.image.load(os.path.join('images/Blue_Slime', 'buff.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40*scale_x,40*scale_y))
            self.rect = self.image.get_rect(topleft=(x, y))

        def apply_to(self, player):
            player.add_buff(self.buff)
    # this function is to generate buffs
    def generate_random_buff(level, buff_types):
        if level.valid_buff_positions:
            x, y = random.choice(level.valid_buff_positions)
            buff_type = random.choice(buff_types)
            new_buff = BuffItem(buff_type, 400, 5000, x, y)  # Adjust effect and duration as needed
            level.buff_items.add(new_buff)
            level.all_sprites.add(new_buff)
            return new_buff
        else:
            print('No')
        return None

    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, width, height, image=None, color=GREEN, one_way=False):
            super().__init__()
            if image:
                self.image = pygame.image.load(image).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            else:
                self.image = pygame.Surface((width, height))
                self.image.fill(color)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.one_way = one_way

        def draw(self, surface):
            surface.blit(self.image, self.rect)
            if SHOW_HITBOXES:
                pygame.draw.rect(surface, RED, self.rect, 2)

    class Level:
        def __init__(self, csv_file):
            # self.platforms = pygame.sprite.Group()
            self.remaining_time = None #initialize the countdown
            self.platform_list = pygame.sprite.Group() 
            self.all_sprites = pygame.sprite.Group() #intialize sprites group
            self.buff_items = pygame.sprite.Group() # initialize the buff list
            self.valid_buff_positions = []  # Store valid buff positions
            self.load_level(csv_file) # load the map file

            self.player1 = Player('Blue_Slime', {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP},
                                  self.platform_list)
            self.player1.rect.center = (100, 300) #this one is to create player 1 and 2 
            self.player2 = Player('Red_Slime', {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w},
                                  self.platform_list)
            self.player1.rect.center = (1000, 300)
            self.all_sprites.add(self.player1, self.player2) # add them to the group
            # adding the tag as attribute of the level class
            self.tag = Tag(self.player1) 
            self.all_sprites.add(self.player1, self.player2, self.tag)#add to the group
            self.timer = 0 #set the delay of switching tag

        def check_player_collision(self, player1, player2):
            return player1.rect.colliderect(player2.rect)#check when ttwo hitboxes collide

        def load_level(self, csv_file):
            tile_images = Tiles
            with open(csv_file, newline='') as file:
                reader = csv.reader(file)
                for y, row in enumerate(reader):
                    for x, cell in enumerate(row):
                        if cell in tile_images:
                            image_path = tile_images[cell]
                            platform = Platform(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, image=image_path)
                            self.platform_list.add(platform)
                            self.all_sprites.add(platform)
                            if cell in ['1']:
                                self.valid_buff_positions.append((x * TILE_SIZE, y * TILE_SIZE - BUFF_HEIGHT_OFFSET))

        def update(self, delta_time):
            self.all_sprites.update(delta_time)
            self.tag.update(delta_time)
            if self.timer == 0: #to switch tage when collision happen
                if self.check_player_collision(self.player1, self.player2):
                    # switch tag function
                    if self.tag.player == self.player1:
                        self.tag.switch_target(self.player2)
                        self.timer = 120
                    else:
                        self.tag.switch_target(self.player1)
                        self.timer = 120
            else:
                self.timer -= 5

        def draw(self, screen):
            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            self.remaining_time = countdown_time - elapsed_seconds
            screen.fill(BLACK)
            timer_text = font.render(f"Time: {self.remaining_time}s", True, WHITE)
            screen.blit(bg_image, (0, 0))
            screen.blit(timer_text, ((SCREEN_WIDTH / 2) - 50, 10))
            self.all_sprites.draw(screen)
            self.platform_list.draw(screen)
            self.player1.draw(screen)
            self.player2.draw(screen)

    def game_loop():
        level = Level(sigma)
        button_width = 650
        button_height = 110
        ble = pygame.image.load(os.path.join('images', 'blewin.png')).convert_alpha()
        re = pygame.image.load(os.path.join('images', 'rewin.png')).convert_alpha()
        sizing = (SCREEN_WIDTH // 2 - button_width // 2 + 5, SCREEN_HEIGHT // 2 - button_height // 2 - 25)
        global running, last_buff_spawn
        #mixer.music.play()
        running = True
        while running:
            delta_time = clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Check if it's time to spawn a new buff
            current_time = pygame.time.get_ticks()
            if current_time - last_buff_spawn > buff_spawn_time:
                new_buff = generate_random_buff(level, ["speed", 'speed', "inverted", "freeze"])
                if new_buff:
                    level.buff_items.add(new_buff)
                    level.all_sprites.add(new_buff)
                last_buff_spawn = current_time

            keys = pygame.key.get_pressed()
            for player in [level.player1, level.player2]:
                if keys[player.keys['left']]:
                    player.go_left()
                elif keys[player.keys['right']]:
                    player.go_right()
                else:
                    player.stop()
                if keys[player.keys['jump']]:
                    player.jump()

            level.update(delta_time)
            level.draw(screen)

            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            countdown = max(0, countdown_time - elapsed_time)
            if countdown == 0:
                running = False
                if level.tag.player == level.player1:
                    screen.blit(ble, (0, 0))
                else:
                    screen.blit(re, (0, 0))
                pygame.display.flip()
                pygame.time.delay(3000)
                exit()

            for player in [level.player1, level.player2]:
                collided_items = pygame.sprite.spritecollide(player, level.buff_items, True)
                for item in collided_items:
                    item.apply_to(player)

            pygame.display.flip()
            clock.tick(60)  


    game_loop()

    pygame.quit()

def exit():
    bg_image = pygame.image.load('images/Background/Restart.png').convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    button_width = 650
    button_height = 110
    button_width1 = 560
    button_height1 = 40
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT // 2 - button_height // 2 - 50
    button_x1 = SCREEN_WIDTH // 2 - button_width // 2 + 50
    button_y1 = SCREEN_HEIGHT // 2 - button_height // 2 - 25
    button_spacing = 150

    start_button = TransparentButton(button_x, button_y, button_width, button_height, "", GREEN, BLACK, 0)
    quit_button = TransparentButton(button_x1, button_y1 + button_spacing, button_width1, button_height1, "", RED,
                                    BLACK, 0)

    buttons = [start_button, quit_button]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))
        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        if button.bg_color == GREEN:
                            options()
                        elif button.bg_color == RED:
                            pygame.quit()
                            sys.exit()

        pygame.display.update()

def options():
    bg_image = pygame.image.load('images/Background/skibidi.png').convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    button_width = 383
    button_height = 200
    button_x = SCREEN_WIDTH // 2 - button_width // 2-10
    button_y = SCREEN_HEIGHT // 2 - button_height // 2+100
    button_x1 = SCREEN_WIDTH // 2 - button_width // 2-455
    button_y1 = SCREEN_HEIGHT // 2 - button_height // 2-50
    button_x2 = SCREEN_WIDTH // 2 - button_width // 2+450
    button_y2 = SCREEN_HEIGHT // 2 - button_height // 2-50
    button_spacing = 150
    running = True
    Map1 = TransparentButton(button_x, button_y, button_width, button_height, "", GREEN, BLACK, 0)
    Map2 = TransparentButton(button_x1, button_y1 + button_spacing, button_width, button_height, "", RED, BLACK,0)
    Map3 = TransparentButton(button_x2, button_y2 + button_spacing, button_width, button_height, "", YELL, BLACK,0)
    buttons=[Map1,Map2,Map3]
    while running:
        screen.blit(bg_image, (0, 0))
        for button in buttons:
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        if button.bg_color==GREEN:
                            game('images/Background/bg10.png',{'1': 'images/Tiles/Tile_02.png',
                                                               '2': 'images/Tiles/Tile_12.png',
                                                               '3': 'images/Tiles/Tile_13.png',
                                                               '4': 'images/Tiles/Tile_11.png',
                                                               '5': 'images/Tiles/Tile_03.png',
                                                               '6': 'images/Tiles/Tile_01.png'},'Level.csv')                   
                        elif button.bg_color==RED:
                            game('images/Background/bg6.png',{'1': 'images/Tiles/tile51.png',
                                                              '2': 'images/Tiles/tile52.png',
                                                              '3': 'images/Tiles/tile53.png',
                                                              '4': 'images/Tiles/tile54.png',
                                                              '5': 'images/Tiles/tile65.png',
                                                              '6': 'images/Tiles/tile68.png'},'Level1.csv')
                        else:
                            game('images/Background/bg9.png',{'1': 'images/Tiles/IndustrialTile_05.png',
                                                              '2': 'images/Tiles/IndustrialTile_21.png',
                                                              '3': 'images/Tiles/IndustrialTile_15.png',
                                                              '4': 'images/Tiles/IndustrialTile_13.png',
                                                              '5': 'images/Tiles/IndustrialTile_06.png',
                                                              '6': 'images/Tiles/IndustrialTile_04.png'},'Level3.csv')
                
        pygame.display.update()
    
def main_menu():
    bg_image = pygame.image.load('images/Background/START.png').convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    button_width = 650
    button_height = 95
    button_width1 = 560
    button_height1 = 40
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT // 2 - button_height // 2
    button_x1 = SCREEN_WIDTH // 2 - button_width // 2 +50
    button_y1 = SCREEN_HEIGHT // 2 - button_height // 2 
    button_spacing = 150
    
    start_button = TransparentButton(button_x, button_y, button_width, button_height, "", GREEN, BLACK, 0)
    quit_button = TransparentButton(button_x1, button_y1 + button_spacing, button_width1, button_height1, "", RED, BLACK,0)
    
    buttons = [start_button, quit_button]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))
        for button in buttons:
            button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        if button.bg_color==GREEN:
                            options()                       
                        elif button.bg_color==RED:
                            pygame.quit()
                            sys.exit()
        
        pygame.display.update()

splash_screen(['splashscreen/idk..png', 'splashscreen/ultitag.png'])
main_menu()