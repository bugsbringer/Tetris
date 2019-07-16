import pygame
import shape
import board
from random import randint


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Tetris")
        self.Window = pygame.display.set_mode((532, 655))
        self.font = pygame.font.SysFont('C:/Windows/Fonts/Consolas.ttf', 32)

        self.board = board.Board(self.Window, 10, 10)
        self.start_pos = self.board.get_cell_coords(4, 1)
        self.preview_pos = self.board.get_cell_coords(12, 3)
        self.speed_pos = self.board.get_cell_coords(11, 5)
        self.linescount_pos = self.board.get_cell_coords(11, 6)
        self.score_pos = self.board.get_cell_coords(11, 7)

        self.fallen = []
        self.speed = 1
        self.linescount = 0
        self.score = 0
        self.current = None
        self.mainloop()

        pygame.quit()

    def mainloop(self):
        self.run = True
        self.play = True
        self.new_shape()
        pygame.time.set_timer(pygame.USEREVENT, 1000 // self.speed)

        while self.run:
            self.event_handler()
            self.draw()

    def draw(self):
        self.Window.fill((40, 44, 52))

        self.board.draw()
        self.projection.draw()
        self.current.draw()

        for item in self.fallen:
            item.draw()

        self.next_shape.draw()

        render = self.font.render(f"Скорость: {self.speed}", 2, (255, 255, 255))
        self.Window.blit(render, self.speed_pos)

        render = self.font.render(f"Линии: {self.linescount}", 2, (255, 255, 255))
        self.Window.blit(render, self.linescount_pos)

        render = self.font.render(f"Очки: {self.score}", 2, (255, 255, 255))
        self.Window.blit(render, self.score_pos)

        pygame.display.update()

    def game_over(self):
        self.play = False

    def new_shape(self):
        if self.current:
            for item in self.current.rects:
                self.fallen.append(item)
        else:
            self.next = randint(0, 6)

        posits = (self.board.get_cell_coords(4, 0), self.board.get_cell_coords(5, 0))
        for item in self.fallen:
            if item.coords in posits:
                self.game_over()

        if self.play:
            self.current = shape.Shape(self.Window, self.start_pos, index=self.next)
            self.next = randint(0, 6)
            self.next_shape = shape.Shape(self.Window, self.preview_pos, index=self.next)

    def falling(self):
        self.current.move(0, 1)
        for rect in self.current.rects:
            if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                self.current.move(0, -1)
                self.dropped()
                break
            if not self.board.area.contains(rect):
                self.current.move(0, -1)
                self.dropped()
                break

    def dropped(self):
        self.score += 40
        self.new_shape()

        rows = {}

        for item in self.fallen:
            rows[item.coords[1]] = rows.setdefault(item.coords[1], 0) + 1

        count = 0
        for key, value in tuple(rows.items())[::-1]:
            if value == board.size[0]:
                count += 1
                for i in range(len(self.fallen) - 1, -1, -1):
                    if self.fallen[i].coords[1] == key:
                        self.fallen.pop(i)
                for i, item in enumerate(self.fallen):
                    if item.coords[1] < key:
                        self.fallen[i].move(0, 1)

        point_per_rows = {
            1: 100,
            2: 300,
            3: 700,
            4: 1500
        }
        if count:
            self.linescount += count
            self.score += point_per_rows[count]

        self.speed = self.score // 8000 + 1

        pygame.time.set_timer(pygame.USEREVENT, 1000 // self.speed)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.USEREVENT and self.play:
                self.falling()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q or event.key == pygame.K_e:

                    if event.key == pygame.K_q:
                        dir = -1
                    else:
                        dir = 1

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

                elif event.key == pygame.K_a:
                    self.current.move(-1, 0)
                    for rect in self.current.rects:

                        if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                            self.current.move(1, 0)
                            break

                        if not self.board.area.contains(rect):
                            self.current.move(1, 0)
                            break

                elif event.key == pygame.K_d:
                    self.current.move(1, 0)
                    for rect in self.current.rects:

                        if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                            self.current.move(-1, 0)
                            break

                        if not self.board.area.contains(rect):
                            self.current.move(-1, 0)
                            break

                elif event.key == pygame.K_SPACE:
                    pygame.time.set_timer(pygame.USEREVENT, 15)

        self.project()

    def project(self):
        pos = self.current.x, self.current.y
        self.projection = shape.Shape(self.Window, pos, projection=True)
        self.projection.shape = self.current.shape
        self.projection.rotation = self.current.rotation

        calculate = True
        while calculate:

            self.projection.move(0, 1)

            for rect in self.projection.rects:
                if rect.rect.collidelist([i.rect for i in self.fallen]) != -1:
                    self.projection.move(0, -1)
                    calculate = False
                    break

                if not self.board.area.contains(rect):
                    self.projection.move(0, -1)
                    calculate = False
                    break


if __name__ == '__main__':
    Game()
