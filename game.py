import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 4
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
PADDING = 10
ANIMATION_SPEED = 15  # pixels per frame

# Colors
BACKGROUND_COLOR = (250, 248, 239)
GRID_COLOR = (187, 173, 160)

# Load ko image
ko_image = pygame.image.load('pixel_ko.png')

# Text colors
TEXT_COLORS = {
    2: (70, 70, 90),  # Dark text for light tiles
    4: (70, 70, 90),  # Dark text for light tiles
    8: (255, 255, 255),  # White text for dark tiles
    16: (255, 255, 255),
    32: (255, 255, 255),
    64: (255, 255, 255),
    128: (255, 255, 255),
    256: (255, 255, 255),
    512: (255, 255, 255),
    1024: (255, 255, 255),
    2048: (255, 255, 255)
}

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('2048')

class Tile:
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.target_row = row
        self.target_col = col
        self.x = col * CELL_SIZE + PADDING
        self.y = row * CELL_SIZE + PADDING
        self.target_x = self.x
        self.target_y = self.y
        self.merging = False
        self.remove = False

    def move_to(self, row, col):
        self.target_row = row
        self.target_col = col
        self.target_x = col * CELL_SIZE + PADDING
        self.target_y = row * CELL_SIZE + PADDING

    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        if abs(dx) < ANIMATION_SPEED and abs(dy) < ANIMATION_SPEED:
            self.x = self.target_x
            self.y = self.target_y
            self.row = self.target_row
            self.col = self.target_col
            return True
        
        angle = math.atan2(dy, dx)
        self.x += math.cos(angle) * ANIMATION_SPEED
        self.y += math.sin(angle) * ANIMATION_SPEED
        return False

    def draw(self, screen):
        rect_width = CELL_SIZE - 2 * PADDING
        
        # Draw background rectangle
        pygame.draw.rect(screen, GRID_COLOR, 
                        (self.x, self.y, rect_width, rect_width),
                        border_radius=8)
        
        if self.value > 0:
            # Calculate image scale based on value
            scale = min(1.0 + math.log2(self.value) * 0.1, 2.0)
            
            # Calculate image size
            img_size = int(rect_width * scale)
            img = pygame.transform.scale(ko_image, (img_size, img_size))
            
            # Calculate alpha based on value (higher value = more opaque)
            alpha = min(128 + math.log2(self.value) * 20, 255)
            img.set_alpha(int(alpha))
            
            # Center the scaled image
            img_x = self.x + (rect_width - img_size) // 2
            img_y = self.y + (rect_width - img_size) // 2
            screen.blit(img, (img_x, img_y))
            
            # Draw the number
            font_size = 48 if self.value < 1000 else 36
            font = pygame.font.Font(None, font_size)
            text_color = TEXT_COLORS.get(self.value, (255, 255, 255))
            text = font.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=(self.x + rect_width/2,
                                            self.y + rect_width/2))
            screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.tiles = []
        self.score = 0
        self.game_over = False
        self.animating = False
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(GRID_SIZE) 
                      for c in range(GRID_SIZE) if self.grid[r][c] == 0]
        if empty_cells:
            row, col = random.choice(empty_cells)
            value = 2 if random.random() < 0.9 else 4
            self.grid[row][col] = value
            self.tiles.append(Tile(value, row, col))

    def move(self, direction):
        if self.animating:
            return False

        dx, dy = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }[direction]

        moved = False
        new_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        new_tiles = []

        # Sort tiles for correct movement order
        tiles = sorted(self.tiles, 
                      key=lambda t: (t.row if dy else t.col) * 
                      (-1 if direction in ['down', 'right'] else 1))

        for tile in tiles:
            if tile.remove:
                continue

            row, col = tile.row, tile.col
            new_row, new_col = row, col

            # Move tile as far as possible
            while True:
                next_row = new_row + dy
                next_col = new_col + dx
                if not (0 <= next_row < GRID_SIZE and 
                       0 <= next_col < GRID_SIZE):
                    break
                if new_grid[next_row][next_col] == 0:
                    new_row, new_col = next_row, next_col
                    moved = True
                elif (new_grid[next_row][next_col] == tile.value and 
                      not any(t.target_row == next_row and 
                            t.target_col == next_col and 
                            t.merging for t in new_tiles)):
                    new_row, new_col = next_row, next_col
                    tile.merging = True
                    moved = True
                    self.score += tile.value * 2
                    break
                else:
                    break

            if tile.merging:
                # Find tile to merge with
                for other in new_tiles:
                    if (other.target_row == new_row and 
                        other.target_col == new_col):
                        other.value *= 2
                        tile.remove = True
                        break
            else:
                new_grid[new_row][new_col] = tile.value

            tile.move_to(new_row, new_col)
            new_tiles.append(tile)

        if moved:
            self.grid = new_grid
            self.tiles = [t for t in new_tiles if not t.remove]
            self.animating = True
            return True
        return False

    def update(self):
        if self.animating:
            self.animating = False
            for tile in self.tiles:
                if not tile.update():
                    self.animating = True

            if not self.animating:
                for tile in self.tiles:
                    tile.merging = False
                self.add_random_tile()
                if self.is_game_over():
                    self.game_over = True

    def is_game_over(self):
        if any(cell == 0 for row in self.grid for cell in row):
            return False

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                current = self.grid[i][j]
                if (j < GRID_SIZE - 1 and current == self.grid[i][j + 1] or
                    i < GRID_SIZE - 1 and current == self.grid[i + 1][j]):
                    return False
        return True

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        
        # Draw grid background
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                pygame.draw.rect(screen, GRID_COLOR,
                               (col * CELL_SIZE + PADDING,
                                row * CELL_SIZE + PADDING,
                                CELL_SIZE - 2 * PADDING,
                                CELL_SIZE - 2 * PADDING),
                               border_radius=8)

        # Draw tiles
        for tile in self.tiles:
            tile.draw(screen)

        if self.game_over:
            font = pygame.font.Font(None, 72)
            text = font.render("Game Over!", True, (119, 110, 101))
            text_rect = text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
            overlay.fill((238, 228, 218))
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            screen.blit(text, text_rect)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render("Score: {}".format(self.score), True, (119, 110, 101))
        screen.blit(score_text, (10, 10))

def main():
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN and not game.animating:
                if event.key == pygame.K_UP:
                    game.move('up')
                elif event.key == pygame.K_DOWN:
                    game.move('down')
                elif event.key == pygame.K_LEFT:
                    game.move('left')
                elif event.key == pygame.K_RIGHT:
                    game.move('right')

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
