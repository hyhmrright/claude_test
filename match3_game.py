#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
消消乐游戏 - Python实现
使用Pygame库实现的简单消消乐游戏
"""

import pygame
import random
import sys
import time

# 初始化pygame
pygame.init()

# 游戏设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 8
TILE_SIZE = 64
MARGIN = 50
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (240, 248, 255)
GRID_COLOR = (200, 200, 200)
COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
    (0, 255, 255),  # 青
]

# 游戏状态
IDLE = 0
SELECTING = 1
SWAPPING = 2
CHECKING = 3
REMOVING = 4
FALLING = 5
REFILLING = 6

class Tile:

    def __init__(self, row, col, color_idx):
        self.row = row
        self.col = col
        self.color_idx = color_idx
        self.x = MARGIN + col * TILE_SIZE
        self.y = MARGIN + row * TILE_SIZE
        self.size = TILE_SIZE - 4  # 留一些间隙
        self.selected = False
        self.removing = False
        self.fall_speed = 0
        self.target_y = self.y

    def update(self):
        if self.y < self.target_y:
            self.y += self.fall_speed
            if self.y >= self.target_y:
                self.y = self.target_y
                return True
        return False

    def draw(self, screen):
        border_width = 4 if self.selected else 2
        if self.removing:
            # 淡出效果
            alpha = max(0, 255 - self.removing * 25)
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(alpha)
            s.fill(COLORS[self.color_idx])
            screen.blit(s, (self.x + 2, self.y + 2))
        else:
            # 绘制普通方块
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size + 4, self.size + 4))
            pygame.draw.rect(screen, COLORS[self.color_idx], (self.x + border_width, self.y + border_width, 
                            self.size - border_width * 2, self.size - border_width * 2))

class Match3Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("消消乐游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.reset_game()

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.state = IDLE
        self.selected_tile = None
        self.score = 0
        self.moves = 30  # 限制移动次数
        self.combo = 0
        self.fill_grid()
        # 确保开始时没有匹配的组合
        while self.check_matches():
            self.refill_grid()

    def fill_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    color_idx = random.randint(0, len(COLORS) - 1)
                    self.grid[row][col] = Tile(row, col, color_idx)

    def refill_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    self.grid[row][col] = Tile(row, col, random.randint(0, len(COLORS) - 1))

    def get_tile_at_pos(self, pos):
        x, y = pos
        if x < MARGIN or y < MARGIN:
            return None
        
        col = (x - MARGIN) // TILE_SIZE
        row = (y - MARGIN) // TILE_SIZE
        
        if col >= GRID_SIZE or row >= GRID_SIZE:
            return None
            
        return self.grid[row][col]

    def swap_tiles(self, tile1, tile2):
        if tile1 and tile2:
            # 检查是否相邻
            if ((abs(tile1.row - tile2.row) == 1 and tile1.col == tile2.col) or
                (abs(tile1.col - tile2.col) == 1 and tile1.row == tile2.row)):
                
                # 交换网格中的位置
                self.grid[tile1.row][tile1.col], self.grid[tile2.row][tile2.col] = \
                    self.grid[tile2.row][tile2.col], self.grid[tile1.row][tile1.col]
                
                # 更新行列信息
                tile1.row, tile2.row = tile2.row, tile1.row
                tile1.col, tile2.col = tile2.col, tile1.col
                
                # 更新目标坐标
                tile1.x, tile1.y = MARGIN + tile1.col * TILE_SIZE, MARGIN + tile1.row * TILE_SIZE
                tile2.x, tile2.y = MARGIN + tile2.col * TILE_SIZE, MARGIN + tile2.row * TILE_SIZE
                
                self.moves -= 1
                return True
        return False

    def check_matches(self):
        matches = []
        
        # 检查水平匹配
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] and self.grid[row][col+1] and self.grid[row][col+2] and
                    self.grid[row][col].color_idx == self.grid[row][col+1].color_idx == self.grid[row][col+2].color_idx):
                    
                    # 寻找连续相同颜色的最大长度
                    length = 3
                    while col + length < GRID_SIZE and self.grid[row][col+length] and \
                          self.grid[row][col].color_idx == self.grid[row][col+length].color_idx:
                        length += 1
                    
                    matches.append([(row, col+i) for i in range(length)])
                    # 跳过已经匹配的方块
                    col += length - 1
                    
        # 检查垂直匹配
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2):
                if (self.grid[row][col] and self.grid[row+1][col] and self.grid[row+2][col] and
                    self.grid[row][col].color_idx == self.grid[row+1][col].color_idx == self.grid[row+2][col].color_idx):
                    
                    # 寻找连续相同颜色的最大长度
                    length = 3
                    while row + length < GRID_SIZE and self.grid[row+length][col] and \
                          self.grid[row][col].color_idx == self.grid[row+length][col].color_idx:
                        length += 1
                    
                    matches.append([(row+i, col) for i in range(length)])
                    # 跳过已经匹配的方块
                    row += length - 1
        
        return matches

    def remove_matches(self, matches):
        if not matches:
            return False
            
        self.combo += 1
        match_count = sum(len(match) for match in matches)
        points = match_count * 10 * self.combo
        self.score += points
        
        # 标记要移除的方块
        for match in matches:
            for row, col in match:
                if self.grid[row][col]:
                    self.grid[row][col].removing = 1
        
        self.state = REMOVING
        return True
        
    def apply_gravity(self):
        falling = False
        
        # 从下往上检查每一格
        for col in range(GRID_SIZE):
            empty_spaces = 0
            
            for row in range(GRID_SIZE-1, -1, -1):
                if self.grid[row][col] is None:
                    empty_spaces += 1
                elif empty_spaces > 0:
                    # 移动方块
                    tile = self.grid[row][col]
                    self.grid[row+empty_spaces][col] = tile
                    self.grid[row][col] = None
                    
                    # 更新方块属性
                    tile.row = row + empty_spaces
                    tile.target_y = MARGIN + tile.row * TILE_SIZE
                    tile.fall_speed = random.randint(5, 15)
                    falling = True
        
        if falling:
            self.state = FALLING
        else:
            self.state = REFILLING
            
        return falling

    def update(self):
        if self.state == REMOVING:
            all_removed = True
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col] and self.grid[row][col].removing:
                        self.grid[row][col].removing += 1
                        if self.grid[row][col].removing > 10:
                            self.grid[row][col] = None
                        else:
                            all_removed = False
            
            if all_removed:
                self.apply_gravity()
                
        elif self.state == FALLING:
            still_falling = False
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col]:
                        if self.grid[row][col].update():
                            still_falling = True
            
            if not still_falling:
                self.state = REFILLING
                
        elif self.state == REFILLING:
            self.fill_grid()
            matches = self.check_matches()
            if matches:
                self.remove_matches(matches)
            else:
                self.combo = 0
                self.state = IDLE
                
        # 检查游戏结束条件
        if self.moves <= 0 and self.state == IDLE:
            # 游戏结束
            self.show_game_over()

    def show_game_over(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # 显示游戏结束文本
        game_over_text = self.font.render("游戏结束!", True, BLACK)
        score_text = self.font.render(f"最终得分: {self.score}", True, BLACK)
        restart_text = self.font.render("按R键重新开始", True, BLACK)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        # 等待用户按R键重新开始
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                        self.reset_game()
            
            self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # 绘制网格背景
        grid_width = GRID_SIZE * TILE_SIZE
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (MARGIN - 5, MARGIN - 5, grid_width + 10, grid_width + 10))
        
        # 绘制所有方块
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(self.screen)
        
        # 绘制分数和剩余移动次数
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        moves_text = self.font.render(f"剩余移动: {self.moves}", True, BLACK)
        combo_text = self.font.render(f"连击: {self.combo}x", True, BLACK)
        
        self.screen.blit(score_text, (MARGIN, 10))
        self.screen.blit(moves_text, (SCREEN_WIDTH - MARGIN - moves_text.get_width(), 10))
        if self.combo > 1:
            self.screen.blit(combo_text, (MARGIN + score_text.get_width() + 50, 10))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == IDLE:
                    # 处理鼠标点击
                    tile = self.get_tile_at_pos(pygame.mouse.get_pos())
                    if tile:
                        if self.selected_tile:
                            if self.selected_tile != tile:
                                if self.swap_tiles(self.selected_tile, tile):
                                    self.state = CHECKING
                                    self.selected_tile.selected = False
                                    self.selected_tile = None
                                    
                                    # 检查是否有匹配
                                    matches = self.check_matches()
                                    if not self.remove_matches(matches):
                                        # 没有匹配，交换回来
                                        self.swap_tiles(self.grid[tile.row][tile.col], self.grid[tile.row][tile.col])
                                        self.moves += 1  # 恢复移动次数
                            else:
                                # 取消选择
                                self.selected_tile.selected = False
                                self.selected_tile = None
                        else:
                            # 选择方块
                            self.selected_tile = tile
                            tile.selected = True
                            
            # 更新游戏逻辑
            if self.state != IDLE:
                self.update()
                
            # 绘制游戏
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Match3Game()
    game.run()
