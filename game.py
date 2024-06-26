import os

import pygame
import sys
import csv

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scrolling Platformer")
# Tile dimensions
TILE_SIZE = 40
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Main game loop flag
running = True

DEFAULT_IMAGE_SIZE = (360, 200)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = []
        img = pygame.image.load(os.path.join('images/Base', 'Knight_01__IDLE_000.png')).convert()
        self.images.append(img)
        self.images = pygame.transform.scale(img, DEFAULT_IMAGE_SIZE)
        self.image = self.images
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.change_x = 0
        self.change_y = 0
        self.jump_power = -500  # Pixels per second
        self.gravity = 1500  # Pixels per second^2
        self.on_ground = False

    def update(self, delta_time):
        # Apply gravity
        self.change_y += self.gravity * delta_time

        # Update position
        self.rect.x += self.change_x * delta_time
        self.rect.y += self.change_y * delta_time

        # Prevent player from falling through the bottom
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.change_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.change_y = self.jump_power
            self.on_ground = False

    def go_left(self):
        self.change_x = -300  # Pixels per second

    def go_right(self):
        self.change_x = 300  # Pixels per second

    def stop(self):
        self.change_x = 0


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Level:
    def __init__(self, csv_file):
        self.platform_list = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        # Load level from CSV file
        self.load_level(csv_file)

    def load_level(self, csv_file):
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for y, row in enumerate(reader):
                for x, cell in enumerate(row):
                    if cell == '1':
                        platform = Platform(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        self.platform_list.add(platform)
                        self.all_sprites.add(platform)
                    elif cell == '2':
                        obstacle = Platform(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE,
                                            color=(255, 0, 0))  # Red obstacle
                        self.platform_list.add(obstacle)
                        self.all_sprites.add(obstacle)

    def update(self, delta_time):
        self.all_sprites.update(delta_time)

    def draw(self, screen):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)

    def scroll(self, delta_time):
        # Define scrolling boundaries
        left_boundary = 200
        right_boundary = SCREEN_WIDTH - 200

        # Amount to scroll
        scroll_x = 0

        # Scroll to the right
        if self.player.rect.right >= right_boundary and self.player.change_x > 0:
            scroll_x = self.player.change_x * delta_time

        # Scroll to the left
        elif self.player.rect.left <= left_boundary and self.player.change_x < 0:
            scroll_x = self.player.change_x * delta_time

        # Move all sprites based on scroll_x
        for sprite in self.all_sprites:
            sprite.rect.x -= int(scroll_x)  # Ensure integer movement

        # Adjust player position
        if self.player.rect.left < left_boundary:
            self.player.rect.left = left_boundary
        elif self.player.rect.right > right_boundary:
            self.player.rect.right = right_boundary


# Main game loop
def main():
    global running

    # Initialize Pygame
    pygame.init()

    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scrolling Platformer")

    # Set up the clock for managing the frame rate
    clock = pygame.time.Clock()

    # Load the level from CSV file
    level = Level('level.csv')

    # Get the initial time
    last_time = pygame.time.get_ticks()

    # Set to keep track of pressed keys
    pressed_keys = set()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pressed_keys.add(event.key)
            if event.type == pygame.KEYUP:
                pressed_keys.discard(event.key)

        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time

        # Handle pressed keys
        if pygame.K_LEFT in pressed_keys:
            level.player.go_left()
        elif pygame.K_RIGHT in pressed_keys:
            level.player.go_right()
        else:
            level.player.stop()

        if pygame.K_SPACE in pressed_keys:
            level.player.jump()

        # Update level
        level.update(delta_time)

        # Check for collision between player and platforms
        player_hit_list = pygame.sprite.spritecollide(level.player, level.platform_list, False)
        for platform in player_hit_list:
            if level.player.change_y > 0:  # Falling down
                level.player.rect.bottom = platform.rect.top
                level.player.change_y = 0
                level.player.on_ground = True

        # Scroll level
        level.scroll(delta_time)

        # Draw level
        level.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap the frame rate to 60 FPS
        clock.tick(120)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
