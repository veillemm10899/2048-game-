import pygame
import random
import sys
from typing import List, Tuple
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 4
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
PADDING = 10

# Colors
BACKGROUND_COLOR = (250, 248, 239)
GRID_COLOR = (187, 173, 160)
COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

TEXT_COLORS = {
    0: (205, 193, 180),
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242)
}

class Tile:
    def __init__(self, value: int, row: int, col: int):
        self.value = value
        self.row = row
        self.col = col
        self.target_row = row
        self.target_col = col
        self.current_x = col * CELL_SIZE
        self.current_y = row * CELL_SIZE
        self.merged = False
        self.new = True
        self.scale = 0.0

    def update(self, dt: float):
        # Update position animation
        target_x = self.target_col * CELL_SIZE
        target_y = self.target_row * CELL_SIZE
        
        self.current_x += (target_x - self.current_x) * min(dt * 10, 1)
        self.current_y += (target_y - self.current_y) * min(dt * 10, 1)
        
        # Update scale animation for new tiles
        if self.new:
            self.scale = min(1.0, self.scale + dt * 5)
            if self.scale >= 1.0:
                self.new = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        x = self.current_x + PADDING
        y = self.current_y + PADDING
        size = CELL_SIZE - 2 * PADDING
        
        if self.new:
            size *= self.scale
            x += (CELL_SIZE - size) / 2 - PADDING
            y += (CELL_SIZE - size) / 2 - PADDING

        pygame.draw.rect(screen, COLORS[self.value], (x, y, size, size), border_radius=8)
        
        if self.value > 0:
            text = font.render(str(self.value), True, TEXT_COLORS[self.value])
            text_rect = text.get_rect(center=(self.current_x + CELL_SIZE/2,
                                            self.current_y + CELL_SIZE/2))
            screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.score = 0
        self.game_over = False
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) 
                      if self.board[r][c] is None]
        if empty_cells:
            row, col = random.choice(empty_cells)
            value = 2 if random.random() < 0.9 else 4
            self.board[row][col] = Tile(value, row, col)

    def move(self, direction: Tuple[int, int]):
        dr, dc = direction
        moved = False
        
        # Reset merged flags
        for row in self.board:
            for tile in row:
                if tile:
                    tile.merged = False

        # Determine processing order
        row_range = range(GRID_SIZE - 1, -1, -1) if dr > 0 else range(GRID_SIZE)
        col_range = range(GRID_SIZE - 1, -1, -1) if dc > 0 else range(GRID_SIZE)

        for r in row_range:
            for c in col_range:
                if self.board[r][c]:
                    moved |= self.move_tile(r, c, dr, dc)

        if moved:
            self.spawn_tile()
            self.check_game_over()

    def move_tile(self, row: int, col: int, dr: int, dc: int) -> bool:
        tile = self.board[row][col]
        if not tile:
            return False

        new_row, new_col = row + dr, col + dc
        while (0 <= new_row < GRID_SIZE and 
               0 <= new_col < GRID_SIZE):
            
            if self.board[new_row][new_col] is None:
                # Move to empty cell
                self.board[new_row][new_col] = tile
                self.board[row][col] = None
                tile.target_row = new_row
                tile.target_col = new_col
                row, col = new_row, new_col
                new_row, new_col = row + dr, col + dc
                moved = True
            
            elif (self.board[new_row][new_col].value == tile.value and 
                  not self.board[new_row][new_col].merged):
                # Merge with matching tile
                self.board[row][col] = None
                merged_tile = self.board[new_row][new_col]
                merged_tile.value *= 2
                merged_tile.merged = True
                self.score += merged_tile.value
                tile.target_row = new_row
                tile.target_col = new_col
                return True
            
            else:
                break
            
        return row != tile.row or col != tile.col

    def check_game_over(self):
        # Check for possible moves
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.board[r][c] is None:
                    return False
                
                value = self.board[r][c].value
                # Check adjacent cells
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_r, new_c = r + dr, c + dc
                    if (0 <= new_r < GRID_SIZE and 
                        0 <= new_c < GRID_SIZE and 
                        self.board[new_r][new_c] and 
                        self.board[new_r][new_c].value == value):
                        return False
                    
        self.game_over = True
        return True

    def reset(self):
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_over = False
        self.spawn_tile()
        self.spawn_tile()

    def run(self):
        last_time = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move((0, -1))
                        elif event.key == pygame.K_RIGHT:
                            self.move((0, 1))
                        elif event.key == pygame.K_UP:
                            self.move((-1, 0))
                        elif event.key == pygame.K_DOWN:
                            self.move((1, 0))

            # Update
            for row in self.board:
                for tile in row:
                    if tile:
                        tile.update(dt)

            # Draw
            self.screen.fill(BACKGROUND_COLOR)
            
            # Draw grid background
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                  (col * CELL_SIZE + PADDING,
                                   row * CELL_SIZE + PADDING,
                                   CELL_SIZE - 2 * PADDING,
                                   CELL_SIZE - 2 * PADDING),
                                  border_radius=8)

            # Draw tiles
            for row in self.board:
                for tile in row:
                    if tile:
                        tile.draw(self.screen, self.font)

            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, (119, 110, 101))
            self.screen.blit(score_text, (10, 10))

            # Draw game over
            if self.game_over:
                s = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
                s.set_alpha(128)
                s.fill((255, 255, 255))
                self.screen.blit(s, (0, 0))
                
                game_over_text = self.font.render("Game Over!", True, (119, 110, 101))
                restart_text = self.font.render("Press R to restart", True, (119, 110, 101))
                
                game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2 - 30))
                restart_rect = restart_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2 + 30))
                
                self.screen.blit(game_over_text, game_over_rect)
                self.screen.blit(restart_text, restart_rect)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
