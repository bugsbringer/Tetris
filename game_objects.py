from __future__ import annotations
import pygame


class Shape(pygame.sprite.Group):
    def __init__(self, coords: tuple = (0, 0), shape_type: str = 'O'):
        super().__init__()
        self.type = shape_type
        self.texture = textures[self.type]
        self.coords = coords
        self.add([Block(pos, self) for pos in models[self.type]])

        self.update()

    def move(self, dx: int = 0, dy: int = 0):
        x, y = self.coords
        self.coords = x + dx * block_size[0], y + dy * block_size[1]
        self.update()

    def rotate90(self, direction: int):
        if self.type != 'O':
            for block in self.sprites():
                block.rotate90(direction)

        self.update()

    def projection(self) -> Shape:
        new_shape = Shape(self.coords, self.type)
        new_shape.texture = textures['projection']

        for block, origin_block in zip(new_shape.sprites(), self.sprites()):
            block.image = new_shape.texture
            block.rect = block.image.get_rect()
            block.dx, block.dy = origin_block.dx, origin_block.dy

        return new_shape

    def collide(self, group: [pygame.sprite.Group, Shape]) -> bool:
        return pygame.sprite.groupcollide(self, group, False, False)


class Block(pygame.sprite.Sprite):
    def __init__(self, delta_pos: tuple, group: Shape):
        super().__init__(group)
        self.shape = group

        self.dx, self.dy = delta_pos
        self.image = self.shape.texture
        self.rect = self.image.get_rect()

    def update(self):
        if any([type(item) is Shape for item in self.groups()]):
            self.rect.x = self.shape.coords[0] + block_size[0] * self.dx
            self.rect.y = self.shape.coords[1] + block_size[1] * self.dy

    def move_down(self):
        self.rect.y = self.rect.y + block_size[1]

    def rotate90(self, direction: int):
        self.dx, self.dy = (self.dy, -self.dx) if direction == 1 else (-self.dy, self.dx)


class Board(pygame.sprite.Sprite):
    def __init__(self, pos: tuple):
        super().__init__()
        self.size = block_size[0] * 10, block_size[1] * 21
        self.image = pygame.Surface(self.size).convert()
        self.image.fill((32, 32, 32))
        self.rect = self.image.get_rect(x=pos[0], y=pos[1])

    def cell_pos(self, cell: tuple) -> tuple:
        return self.rect.x + cell[0] * block_size[0], self.rect.y + cell[1] * block_size[0]

    def contains(self, item: [Shape, Block]) -> bool:
        if type(item) is Shape:
            return len(pygame.sprite.spritecollide(self, item, False)) == 4
        elif type(item) is Block:
            return pygame.sprite.collide_rect(self, item)


shapes = ('L', 'J', 'T', 'Z', 'S', 'I', 'O')
block_size = (32, 32)

models = {
    'L': ((0, 0), (-1, 0), (1, 0), (1, 1)),
    'J': ((0, 0), (-1, 1), (-1, 0), (1, 0)),
    'T': ((0, 0), (-1, 0), (0, 1), (1, 0)),
    'Z': ((0, 0), (-1, 1), (0, 1), (1, 0)),
    'S': ((0, 0), (-1, 0), (0, 1), (1, 1)),
    'I': ((0, 0), (-1, 0), (1, 0), (2, 0)),
    'O': ((0, 0), (0, 1), (1, 0), (1, 1))
}

textures = {'projection': pygame.Surface(block_size).convert()}
textures['projection'].fill((64, 64, 64))
for shape, color in zip(shapes, ('red', 'purple', 'blue', 'green', 'pink', 'sky', 'yellow')):
    image = pygame.image.load(f"textures/{color}-min.png")
    textures[shape] = pygame.transform.scale(image, block_size).convert()