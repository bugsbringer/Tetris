import random
import pygame


class Game:
    def __init__(self, display: pygame.Surface):
        self.display = display
        self.font = pygame.font.Font(pygame.font.match_font('arialbd'), 28)
        self.clock = pygame.time.Clock()
        self.board = Board((10, -32))

        self.paused = False

        self.main_text = {
            'text': '',
            'pos': self.display.get_rect().center,
            'render': self.font.render('', True, (255, 255, 255)),
            'font': pygame.font.Font(pygame.font.match_font('arialbd'), 72)
        }

        self.positions = {
            'current': self.board.cell_pos((5, 0)),
            'preview': self.board.cell_pos((12, 3)),
            'text': {
                'Очки': self.board.cell_pos((11, 6)),
                'Линии': self.board.cell_pos((11, 7)),
                'Скорость': self.board.cell_pos((11, 8)),
                'Линий/мин': self.board.cell_pos((11, 9)),
                'Время': self.board.cell_pos((11, 20))
            }
        }

        self.data = { key: {
                        'prev': 0, 'current': 0, 'render': self.font.render(f"{key}: 0", True, (255, 255, 255))}
                    for key in self.positions['text'].keys()
        }

        self.next_shape = random.choice(shapes)
        self.is_running = False

        self.max_speed_lvl = 10
        self.play_time = 1

        self.fallen_blocks = pygame.sprite.Group()
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def pull_next_shape(self):
        if Shape(self.positions['current'], self.next_shape).collide(self.fallen_blocks):
            self.paused = True
            self.pause(text='Game Over', color=(200, 0, 0))
        else:
            self.cur_shape = Shape(self.positions['current'], self.next_shape)
            self.update_projection()
            self.next_shape = random.choice(shapes)
            self.next_shape_preview = Shape(self.positions['preview'], self.next_shape)

            self.data['Скорость']['current'] = min((self.data['Очки']['current'] // 2500 + 1, self.max_speed_lvl))

            drop_time = int(1000 - (1000 / self.max_speed_lvl * (self.data['Скорость']['current'] - 1)))
            pygame.time.set_timer(pygame.USEREVENT, drop_time)

    def play(self):
        drop_time = int(1000 - (1000 / self.max_speed_lvl * (self.data['Скорость']['current'] - 1)))
        pygame.time.set_timer(pygame.USEREVENT, drop_time)

    def pause(self, text: str = 'Пауза', color: tuple = (255, 255, 255)):
        self.main_text['text'] = text
        self.main_text['render'] = self.main_text['font'].render(text, True, color)
        self.main_text['pos'] = self.main_text['render'].get_rect(center=self.display.get_rect().center)
        pygame.time.set_timer(pygame.USEREVENT, 0)

    def move_down(self):
        self.cur_shape.move(dy=1)
        if self.cur_shape.collide(self.fallen_blocks) or not self.board.contains(self.cur_shape):
            self.cur_shape.move(dy=-1)

            self.fallen_blocks.add(self.cur_shape.sprites())
            self.cur_shape.empty()

            for y in sorted(set(map(lambda x: x.rect.y, self.fallen_blocks))):
                line = tuple(filter(lambda x: x.rect.y == y, self.fallen_blocks))
                if len(line) > 9:
                    [block.kill() for block in line]
                    self.data['Линии']['current'] += 1
                    for block in tuple(filter(lambda x: x.rect.y < y, self.fallen_blocks)):
                        block.move_down()

            lines_count = self.data['Линии']['current'] - self.data['Линии']['prev']

            points_per_rows = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}
            self.data['Очки']['current'] += points_per_rows[lines_count] + 40
            self.pull_next_shape()

    def rotate(self, direction):
        self.cur_shape.rotate90(direction)

        shift = [0, 0]
        for block in self.cur_shape.sprites():
            if not self.board.contains(block):
                if abs(block.dx) > abs(shift[0]):
                    shift[0] = -block.dx
                if abs(block.dy) > abs(shift[1]):
                    shift[1] = -block.dy

        self.cur_shape.move(shift[0], shift[1])

        if self.cur_shape.collide(self.fallen_blocks):
            self.cur_shape.move(-shift[0], -shift[1])
            self.cur_shape.rotate90(-direction)

    def update_projection(self):
        self.cur_shape_projection = self.cur_shape.projection()

        while self.board.contains(self.cur_shape_projection) and \
                not self.cur_shape_projection.collide(self.fallen_blocks):
            self.cur_shape_projection.move(dy=1)
        self.cur_shape_projection.move(dy=-1)

    def mainloop(self):
        self.pull_next_shape()
        self.is_running = True
        while self.is_running:
            self.handle_events()
            if not self.paused:
                self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.is_running = False
                break

            if event.type == pygame.USEREVENT:
                self.move_down()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                    break

                if event.key == pygame.K_a or event.key == pygame.K_d:
                    x_shift = -1 if event.key == pygame.K_a else 1

                    self.cur_shape.move(dx=x_shift)
                    if self.cur_shape.collide(self.fallen_blocks) or not self.board.contains(self.cur_shape):
                        self.cur_shape.move(dx=-x_shift)

                if event.key == pygame.K_q or event.key == pygame.K_e:
                    self.rotate(-1 if event.key == pygame.K_e else 1)

                if event.key == pygame.K_SPACE:
                    pygame.time.set_timer(pygame.USEREVENT, 12)

                if event.key == pygame.K_s:
                    self.move_down()

                if event.key == pygame.K_p:
                    if self.paused:
                        self.play()
                    else:
                        self.pause()

                    self.paused = not self.paused

                self.update_projection()

    def update(self):
        self.next_shape_preview.update()
        self.fallen_blocks.update()
        self.cur_shape_projection.update()
        self.cur_shape.update()

        self.play_time += self.clock.get_time() / 1000

        self.data['Линий/мин']['current'] = round(self.data['Линии']['current'] / self.play_time * 60, 1)
        self.data['Время']['current'] = f'{int(self.play_time // 60)}м' * bool(self.play_time // 60) + \
                                               f' {int(self.play_time % 60)}с'

        for key, value in self.data.items():
            if value['current'] != value['prev']:
                self.data[key]['prev'] = value['current']
                self.data[key]['render'] = self.font.render(f"{key}: {value['current']}", True, (255, 255, 255))

    def draw(self):
        self.display.fill((40, 44, 52))

        self.display.blit(self.board.image, self.board.rect)
        self.next_shape_preview.draw(self.display)
        self.cur_shape_projection.draw(self.display)
        self.fallen_blocks.draw(self.display)
        self.cur_shape.draw(self.display)

        for key, value in self.data.items():
            self.display.blit(value['render'], self.positions['text'][key])

        if self.paused:
            self.display.blit(self.main_text['render'], self.main_text['pos'])

        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Tetris')
    Window = pygame.display.set_mode((530, 650))

    from game_objects import Board, shapes, Shape

    Tetris = Game(Window)
    Tetris.mainloop()

    pygame.quit()
