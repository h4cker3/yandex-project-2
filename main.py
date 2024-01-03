# This is main file of project
# Last commit: added a improved motion to player
# MAIN TODO: create a good map for testing
import pygame
import sys
import os
import time
from pprint import pprint
from random import choice

FPS = 50

pygame.init()
clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 1000, 500
screen = pygame.display.set_mode(size)

# Константы движения
# TODO: дополнить при выполнении цикла действий ИИ
STEP = 1
M_STOP = 0
M_RIGHT = 1
M_LEFT = 2
M_UP = 3
M_DOWN = 4
M_MOVING = 10 ** 9
M_MOVED = 11 ** 9
MOVES = [[STEP, 0], [-STEP, 0], [0, STEP], [0, -STEP]]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('player.png', -1)
enemy_image = load_image('enemy.png', -1)

tile_width = tile_height = 50

player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
units_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


# TODO: REFACTOR THE CLASSES

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


all_units = []


class Unit(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, base):
        super().__init__(units_group, all_sprites)
        self.image = image
        self.x = pos_x
        self.y = pos_y
        self.eat = base[0]
        self.attr = base[1:]
        self.alive = True
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        all_units.append(self)

    def move_by(self, delta_x, delta_y):
        self.x, self.y = self.x + delta_x, self.y + delta_y
        self.rect = self.rect.move(tile_width * delta_x, tile_height * delta_y)

    def die(self):
        self.alive = False
        all_units.remove(self)
        self.kill()

    def movement(self):
        pass

    def reverse_movement(self):
        pass

    def update(self):
        self.eat -= 1
        if self.eat <= 0:
            self.die()
        self.movement()


class Player(Unit):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_image, [300, 10, 10, 10])


def calculate(matrix, data):
    # TODO: REFACTOR THE AI CALCULATIONS
    return choice(MOVES)


class Enemy(Unit):
    def __init__(self, pos_x, pos_y, matrix=None):
        super().__init__(pos_x, pos_y, enemy_image, [300, 10, 10, 10])
        self.matrix = matrix
        self.last_move = MOVES[0]

    def movement(self):
        data = [[0] * 10]
        # TODO: refactor collecting data
        move = calculate(self.matrix, data)
        # return by move_by
        self.last_move = move
        self.move_by(*move)

    def reverse_movement(self):
        move = self.last_move
        move = -move[0], -move[1]
        self.move_by(*move)


def generate_level(level):
    # TODO: исправить генерацию карты (случайным образом + шум)
    new_player, x, y = None, None, None
    enemies = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'e':
                Tile('empty', x, y)
                enemies.append(Enemy(x, y))
    return new_player, x, y, enemies


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


camera = Camera()


def start_screen():
    intro_text = ["AI EVOLUTION", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
    pygame.init()
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    gameplay = False
    while not gameplay:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                gameplay = True
        pygame.display.flip()
        clock.tick(FPS)


def main_game():
    motion = M_STOP
    level = load_level('map.txt')
    # pprint(level)
    player, level_x, level_y, enemies = generate_level(level)
    while True:
        events = pygame.event.get()
        pressed = False
        for i in events:
            if i.type == pygame.QUIT:
                terminate()
            elif i.type == pygame.KEYDOWN:
                if motion != M_STOP:
                    continue
                if i.key == pygame.K_LEFT:
                    pressed = True
                    motion = M_LEFT
                elif i.key == pygame.K_RIGHT:
                    pressed = True
                    motion = M_RIGHT
                elif i.key == pygame.K_UP:
                    pressed = True
                    motion = M_UP
                elif i.key == pygame.K_DOWN:
                    pressed = True
                    motion = M_DOWN
        screen.fill(pygame.Color("black"))
        if motion == M_LEFT:
            if level[player.x - 1][player.y] != '#':
                player.move_by(-STEP, 0)
            motion = M_MOVING
        elif motion == M_RIGHT:
            if level[player.x + 1][player.y] != '#':
                player.move_by(STEP, 0)
            motion = M_MOVING
        elif motion == M_UP:
            if level[player.x][player.y - 1] != '#':
                player.move_by(0, -STEP)
            motion = M_MOVING
        elif motion == M_DOWN:
            if level[player.x][player.y + 1] != '#':
                player.move_by(0, STEP)
            motion = M_MOVING
        if pressed:
            for unit in all_units:
                unit.update()
                if level[unit.x][unit.y] == '#':
                    unit.reverse_movement()
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
        tiles_group.draw(screen)
        units_group.draw(screen)
        for i in events:
            if i.type == pygame.KEYUP:
                if i.key in [pygame.K_LEFT,
                             pygame.K_RIGHT,
                             pygame.K_UP,
                             pygame.K_DOWN] and motion == M_MOVING:
                    motion = M_STOP
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
main_game()
