import pygame
from random import randint

cell_size = 32
size = (10, 20)

shapes = (
    (((-1, 0), (-1, -1), (1, 0)),
     ((0, 1), (0, -1), (1, -1)),
     ((-1, 0), (1, 0), (1, 1)),
     ((0, 1), (-1, 1), (0, -1))),

    (((-1, 0), (1, 0), (1, -1)),
     ((0, 1), (1, 1), (0, -1)),
     ((-1, 0), (-1, 1), (1, 0)),
     ((0, -1), (-1, -1), (0, 1))),

    (((-1, 0), (0, -1), (1, 0)),
     ((0, -1), (1, 0), (0, 1)),
     ((-1, 0), (0, 1), (1, 0)),
     ((0, -1), (-1, 0), (0, 1))),

    (((-1, 0), (0, -1), (1, -1)),
     ((-1, 0), (-1, -1), (0, 1))),

    (((0, -1), (-1, -1), (1, 0)),
     ((1, 0), (1, -1), (0, 1))),

    (((-1, 0), (1, 0), (2, 0)),
     ((0, 2), (0, 1), (0, -1))),

    (((0, -1), (1, 0), (1, -1)), )
)

colors = ('blue', 'green', 'red', 'sky', 'pink', 'purple', 'yellow')
textures = []
for color in colors:
    img = pygame.image.load("textures/" + color + "-min.png")
    textures.append(pygame.transform.scale(img, (cell_size, cell_size)))


class Cell(object):

    def __init__(self, parent, coords):
        self.screen = parent.screen
        self.texture = parent.texture
        self.coords = coords
        self.rect = pygame.rect.Rect(self.coords, (cell_size, cell_size))

    def move(self, dx, dy):
        if dx or dy:
            x, y = self.coords
            if dx:
                x += dx * cell_size
            if dy:
                y += dy * cell_size
            self.coords = x, y
            self.update()

    def update(self):
        self.rect.left, self.rect.top = self.coords

    def draw(self):
        if self.texture:
            self.screen.blit(self.texture, self.coords)
        else:
            pygame.draw.rect(self.screen, (64, 64, 64), self.rect)


class Shape(object):
    rotation = 0

    def __init__(self, screen, pos, index=0, projection=False):
        self.screen = screen
        self.x, self.y = pos
        self.texture = textures[index] if not projection else None
        self.shape = shapes[index]
        self.rects = [Cell(self, pos) for _ in range(4)]
        self.update()

    def rotate(self, dir):
        self.rotation = (self.rotation + dir) % len(self.shape)
        self.update()

    def move(self, dx, dy):
        if dx or dy:
            if dx:
                self.x += dx * cell_size
            if dy:
                self.y += dy * cell_size
            self.update()

    def update(self):
        self.rects[0].coords = self.x, self.y
        self.rects[0].update()
        for i, item in enumerate(self.shape[self.rotation], 1):
            x = self.x + item[0] * cell_size
            y = self.y + item[1] * cell_size
            self.rects[i].coords = x, y
            self.rects[i].update()

    def draw(self):
        for item in self.rects:
            item.draw()


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
        pygame.draw.rect(self.screen, (32, 32, 32), self.area)


class Game(object):
    def __init__(self, window):
        self.Window = window

        self.board = Board(self.Window, 10, 10)

        self.start_pos = self.board.get_cell_coords(4, 0)
        self.preview_pos = self.board.get_cell_coords(12, 3)
        self.speed_pos = self.board.get_cell_coords(11, 5)
        self.linescount_pos = self.board.get_cell_coords(11, 6)
        self.score_pos = self.board.get_cell_coords(11, 7)

    def mainloop(self):
        self.run = True
        self.start_game()
        while self.run:
            self.event_handler()
            self.draw()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if self.play:
                if event.type == pygame.USEREVENT and self.play:
                    self.falling()

            else:
                pygame.time.set_timer(pygame.USEREVENT, 0)

            if event.type == pygame.KEYDOWN:

                if self.play:
                    if event.key == pygame.K_q or event.key == pygame.K_e:

                        dir = 1 if event.key == pygame.K_e else -1

                        self.current.rotate(dir)

                        shift = [0, 0]
                        form = self.current.shape[self.current.rotation]
                        for i, rect in enumerate(self.current.rects[1:]):

                            if not self.board.area.contains(rect):
                                if abs(form[i][0]) > abs(shift[0]):
                                    shift[0] = -form[i][0]

                                if abs(form[i][1]) > abs(shift[1]):
                                    shift[1] = -form[i][1]

                        self.current.move(shift[0], shift[1])

                        for rect in self.current.rects:
                            if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                                self.current.move(-shift[0], -shift[1])
                                self.current.rotate(-dir)
                                break

                        self.project()

                    elif event.key == pygame.K_a or event.key == pygame.K_d:
                        shift = [-1, 0] if event.key == pygame.K_a else [1, 0]

                        self.current.move(shift[0], shift[1])
                        for rect in self.current.rects:

                            if rect.rect.collidelist([i.rect for i in self.fallen]) != -1 or \
                                    not self.board.area.contains(rect):
                                self.current.move(-shift[0], -shift[1])
                                break

                        self.project()

                    elif event.key == pygame.K_s:
                        self.falling()

                    elif event.key == pygame.K_SPACE:
                        pygame.time.set_timer(pygame.USEREVENT, 12)

                if event.key == pygame.K_r:
                    self.start_game()

    def draw(self):
        self.Window.fill((40, 44, 52))

        self.board.draw()
        self.projection.draw()
        self.current.draw()

        for item in self.fallen:
            item.draw()

        self.next_shape.draw()

        render = main_font.render(f"Скорость: {self.speed}", 2, (255, 255, 255))
        self.Window.blit(render, self.speed_pos)

        render = main_font.render(f"Линии: {self.linescount}", 2, (255, 255, 255))
        self.Window.blit(render, self.linescount_pos)

        render = main_font.render(f"Очки: {self.score}", 2, (255, 255, 255))
        self.Window.blit(render, self.score_pos)

        render = main_font.render(f"R - restart", 2, (255, 255, 255))
        self.Window.blit(render, self.board.get_cell_coords(11, 19))

        pygame.display.update()

    def start_game(self):
        self.fallen = []
        self.speed = 1
        self.linescount = 0
        self.score = 0

        self.next = randint(0, 6)
        self.projection = Shape(self.Window, (0, 0), projection=True)
        self.new_shape()

        pygame.time.set_timer(pygame.USEREVENT, 1000 // self.speed)

        self.play = True

    def game_over(self):
        pygame.time.set_timer(pygame.USEREVENT, 0)
        self.play = False

    def new_shape(self):
        for rect in Shape(self.Window, self.start_pos, index=self.next).rects:
            if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                self.game_over()
                return

        self.current = Shape(self.Window, self.start_pos, index=self.next)
        self.falling()
        self.project()

        self.next = randint(0, 6)
        self.next_shape = Shape(self.Window, self.preview_pos, index=self.next)

    def falling(self):
        self.current.move(0, 1)
        for rect in self.current.rects:

            if rect.rect.collidelist([i.rect for i in self.fallen]) != -1 \
                    or not self.board.area.contains(rect):
                self.current.move(0, -1)
                self.dropped()
                self.new_shape()
                break

    def dropped(self):
        for item in self.current.rects:
            self.fallen.append(item)

        rows = {}

        for item in self.fallen:
            rows[item.coords[1]] = rows.get(item.coords[1], 0) + 1

        sorted_keys = sorted(rows)
        sorted_vals = [rows[key] for key in sorted_keys]

        count = 0
        for key, value in zip(sorted_keys, sorted_vals):
            if value == size[0]:
                count += 1
                for i in reversed(range(len(self.fallen))):
                    if self.fallen[i].coords[1] == key:
                        self.fallen.pop(i)

                for row in reversed(sorted_keys[:sorted_keys.index(key)]):
                    for i, _ in enumerate(self.fallen):
                        if self.fallen[i].coords[1] == row:
                            self.fallen[i].move(0, 1)

        point_per_rows = { 1: 100, 2: 300, 3: 700, 4: 1500 }

        if count:
            self.linescount += count
            self.score += point_per_rows[count]
        else:
            self.score += 40

        self.speed = self.score // 4000 + 1

        if self.speed > 10: self.speed = 10

        pygame.time.set_timer(pygame.USEREVENT, (11 - self.speed) * 100)

    def project(self):
        copyed_vars = ('x', 'y', 'shape', 'rotation')
        for var in copyed_vars:
            setattr(self.projection, var, getattr(self.current, var))

        calculate = True
        while calculate:
            self.projection.move(0, 1)

            for rect in self.projection.rects:
                if rect.rect.collidelist([i.rect for i in self.fallen]) != -1 \
                        or not self.board.area.contains(rect):

                    self.projection.move(0, -1)
                    calculate = False
                    break


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Tetris')
    Window = pygame.display.set_mode((532, 655))
    main_font = pygame.font.SysFont('C:/Windows/Fonts/Consolas.ttf', 32)
    
    Tetris = Game(Window)
    Tetris.mainloop()

    pygame.quit()
