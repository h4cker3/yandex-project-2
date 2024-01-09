# This is main file of project
# Last commit: Added a beautiful tiles and generation
# MAIN TODO: make a battle mode and AI generation
import random

import pygame
import sys
import os
import time
from pprint import pprint
from random import choice
from numpy import floor
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt

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
# Константы генерации карты
SEED = 4522
amp = 6
period = 16
terrain_width = 100


def generate_landscale(seed=SEED):
    noise = PerlinNoise(octaves=2, seed=seed)
    landscale = [[0 for i in range(terrain_width)] for i in range(terrain_width)]

    for position in range(terrain_width ** 2):
        x = floor(position / terrain_width)
        z = floor(position % terrain_width)
        y = floor(noise([x / period, z / period]) * amp)
        landscale[int(x)][int(z)] = int(y)
    return landscale


def show_map_pic():
    plt.imshow(generate_landscale())
    plt.show()


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
    'empty': load_image('sand.png'),
    'sand': load_image('sand.png'),
    'grass': load_image('grass.png'),
    'rock': load_image('rock.png')
}
player_image = load_image('player.png')
enemies_images = [load_image('enemy1.png'), load_image('enemy2.png'), load_image('enemy3.png')]
orbes_images = [load_image('str_orb.png'), load_image('spd_orb.png'), load_image('mana_orb.png')]
atebles_images = [load_image('eat1.png'), load_image('eat2.png')]

tile_width = tile_height = 50

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
units_group = pygame.sprite.Group()
pickable_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


# TODO: REFACTOR THE CLASSES

class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, font):
        super().__init__()
        self.color = (255, 255, 255)
        self.backcolor = None
        self.pos = (x, y)
        self.width = w
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()

    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface((max(self.width, t_surf.get_width() + 10), t_surf.get_height() + 10),
                                    pygame.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.active:
                self.active = self.rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.render_text()


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
        self.type = choice(range(3))
        super().__init__(pos_x, pos_y, enemies_images[self.type], [300, 10, 10, 10])
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


all_pickables = []


class Pickable(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(pickable_group, all_sprites)
        self.image = image
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        all_pickables.append(self)

    def try_to_pick(self, u: Unit):
        if u.x == self.x and u.y == self.y:
            self.pick(u)

    def pick(self, u: Unit):
        pass

    def die(self):
        all_pickables.remove(self)
        self.kill()


class Orb(Pickable):
    def __init__(self, x, y, type):
        super().__init__(x, y, orbes_images[type])
        self.type = type

    def pick(self, u: Unit):
        u.attr[self.type] += 2
        self.die()


# def generate_level_by_file(level):
#     new_player, x, y = None, None, None
#     enemies = []
#     for y in range(len(level)):
#         for x in range(len(level[y])):
#             if level[y][x] == '.':
#                 Tile('empty', x, y)
#             elif level[y][x] == '#':
#                 Tile('wall', x, y)
#             elif level[y][x] == '@':
#                 Tile('empty', x, y)
#                 new_player = Player(x, y)
#             elif level[y][x] == 'e':
#                 Tile('empty', x, y)
#                 enemies.append(Enemy(x, y))
#     return new_player, x, y, enemies


def generate_level(seed=SEED):
    level = generate_landscale(seed)
    lvl = [['.' for i in range(terrain_width)] for i in range(terrain_width)]
    new_player, x, y = None, None, None
    enemies = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if -1 <= level[y][x] <= 1:
                Tile('sand', x, y)
                lvl[x][y] = '.'
            elif -1 > level[y][x]:
                Tile('rock', x, y)
                lvl[x][y] = '.'
                if level[y][x] < -2:
                    Orb(x, y, choice(range(3)))
            elif level[y][x] > 1:
                Tile('grass', x, y)
                lvl[x][y] = '.'
                enemies.append(Enemy(x, y))
                lvl[x][y] = 'e'
    new_player = Player(x // 2, y // 2)
    return new_player, x, y, enemies, lvl


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
                  "Игра, где тебе предстоить победить ИИ",
                  "Нажми на экран, чтобы начать", ]
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


def new_game():
    intro_text = ["SEED:", "",
                  "seed - уникальный код,",
                  "отвечающий за генерацию уровня",
                  "оставь поле пустым, если не знаешь что это"]
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
    text_box = TextInputBox(78, 57, 30, font)
    text_box_group = pygame.sprite.Group(text_box)
    text_box.active = True
    while True:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                terminate()
        text_box_group.update(event_list)
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
        text_box_group.draw(screen)
        if not text_box.active:
            print(text_box.text)
            return text_box.text
        pygame.display.flip()
        clock.tick(FPS)


def check_coords(level, x, y):
    if 0 <= x < len(level):
        return 0 <= y < len(level[x])
    return False


def draw_menu(player):
    pygame.draw.rect(screen, pygame.color.Color('white'), [0, 0, 1000, 80])
    font = pygame.font.Font(None, 30)
    screen.blit(load_image('eat1.png'), [0, 0])
    stat1 = font.render(str(player.eat), 1, pygame.Color('black'))
    screen.blit(stat1, [10, 55])
    screen.blit(load_image('str_orb.png'), [50, 0])
    stat2 = font.render(str(player.attr[0]), 1, pygame.Color('black'))
    screen.blit(stat2, [62, 55])
    screen.blit(load_image('spd_orb.png'), [100, 0])
    stat3 = font.render(str(player.attr[1]), 1, pygame.Color('black'))
    screen.blit(stat3, [112, 55])
    screen.blit(load_image('mana_orb.png'), [150, 0])
    stat3 = font.render(str(player.attr[2]), 1, pygame.Color('black'))
    screen.blit(stat3, [162, 55])


def main_game(seed=SEED):
    motion = M_STOP
    # level = load_level('map.txt')
    # pprint(level)
    random.seed(seed)
    player, level_x, level_y, enemies, level = generate_level(seed)
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
            if check_coords(level, player.x - 1, player.y) and level[player.x - 1][player.y] != '#':
                player.move_by(-STEP, 0)
            motion = M_MOVING
        elif motion == M_RIGHT:
            if check_coords(level, player.x + 1, player.y) and level[player.x + 1][player.y] != '#':
                player.move_by(STEP, 0)
            motion = M_MOVING
        elif motion == M_UP:
            if check_coords(level, player.x, player.y - 1) and level[player.x][player.y - 1] != '#':
                player.move_by(0, -STEP)
            motion = M_MOVING
        elif motion == M_DOWN:
            if check_coords(level, player.x, player.y + 1) and level[player.x][player.y + 1] != '#':
                player.move_by(0, STEP)
            motion = M_MOVING
        if pressed:
            for unit in all_units:
                unit.update()
                if not check_coords(level, unit.x, unit.y) or level[unit.x][unit.y] == '#':
                    unit.reverse_movement()
                else:
                    for p in all_pickables:
                        p.try_to_pick(unit)
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
        tiles_group.draw(screen)
        units_group.draw(screen)
        pickable_group.draw(screen)
        for i in events:
            if i.type == pygame.KEYUP:
                if i.key in [pygame.K_LEFT,
                             pygame.K_RIGHT,
                             pygame.K_UP,
                             pygame.K_DOWN] and motion == M_MOVING:
                    motion = M_STOP
        draw_menu(player)
        pygame.display.flip()
        clock.tick(FPS)


# pygame.quit()
# show_map_pic()

start_screen()
main_game(int(new_game()))
