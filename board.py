import pygame

cell_size = 32
size = (10, 20)

class Board(object):
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x, self.y = x, y
        self.width = size[0] * cell_size
        self.height = size[1] * cell_size
        self.end_pos = (self.x + self.width, self.height + self.y)
        self.area = pygame.rect.Rect(self.x, self.y, self.width, self.height)

    def get_cell_coords(self, x, y):
        x = self.x + x * cell_size
        y = self.y + y * cell_size
        return x, y

    def draw(self):
        pygame.draw.rect(self.screen, (32, 32, 32) , self.area)
