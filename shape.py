import pygame
import board

shapes = (
            (   ((-1, 0), (-1, -1), (1, 0)),
                ((0, 1), (0, -1), (1, -1)),
                ((-1, 0), (1, 0), (1, 1)),
                ((0, 1), (-1, 1), (0, -1))  ),

            (   ((-1, 0), (1, 0), (1, -1)),
                ((0, 1), (1, 1), (0, -1)),
                ((-1, 0), (-1, 1), (1, 0)),
                ((0, -1), (-1, -1), (0, 1)) ),

            (   ((-1, 0), (0, -1), (1, 0)),
                ((0, -1), (1, 0), (0, 1)),
                ((-1, 0), (0, 1), (1, 0)),
                ((0, -1), (-1, 0), (0, 1))  ),

            (   ((-1, 0), (0, -1), (1, -1)),
                ((-1, 0), (-1, -1), (0, 1)) ),

            (   ((0, -1), (-1, -1), (1, 0)),
                ((1, 0), (1, -1), (0, 1))   ),

            (   ((-1, 0), (1, 0), (2, 0)),
                ((0, 2), (0, 1), (0, -1))    ),

            (   ((0, -1), (1, 0), (1, -1)), )    )

blocks = (
        pygame.transform.smoothscale(pygame.image.load("blocks/blue.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/green.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/red.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/sky.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/pink.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/purple.png"), (board.cell_size, board.cell_size)),
        pygame.transform.smoothscale(pygame.image.load("blocks/yellow.png"), (board.cell_size, board.cell_size)),
)

class Cell(object):

    def __init__(self, parent, coords):
        self.parent = parent
        self.coords = coords
        self.rect = pygame.rect.Rect((self.coords), (board.cell_size, board.cell_size))

    def move(self, dx, dy):
        if dx or dy:
            x, y = self.coords
            if dx: x += dx * board.cell_size
            if dy: y += dy * board.cell_size
            self.coords = x, y
            self.update()

    def update(self):
        self.rect.left, self.rect.top = self.coords

    def draw(self):
        if not self.parent.projection:
            self.parent.screen.blit(self.parent.texture, self.coords)
        else:
            pygame.draw.rect(self.parent.screen, (64, 64, 64), self.rect)


class Shape(object):
    rotation = 0
    size = board.cell_size

    def __init__(self, screen, pos, index=0, projection=False):
        self.screen = screen
        self.x, self.y = pos
        self.projection = projection
        self.texture = blocks[index]
        self.shape = shapes[index]
        self.rects = [Cell(self, pos) for _ in range(4)]
        self.update()

    def rotate(self, dir):
        self.rotation = (self.rotation + dir) % len(self.shape)
        self.update()

    def move(self, dx, dy):
        if dx or dy:
            if dx: self.x += dx * self.size
            if dy: self.y += dy * self.size
            self.update()

    def update(self):
        self.rects[0].coords = self.x, self.y
        self.rects[0].update()
        for i, item in enumerate(self.shape[self.rotation], 1):
            x = self.x + item[0] * self.size
            y = self.y + item[1] * self.size
            self.rects[i].coords = (x, y)
            self.rects[i].update()

    def draw(self):
        for item in self.rects:
            item.draw()
