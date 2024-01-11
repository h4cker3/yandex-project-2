# This is main file of project
# Last commit: GUI improved and hardness
# MAIN TODO: make a battle mode and AI generation
import random
import logging
import pygame
import sys
import os
from random import choice
from numpy import floor
import time
import perlin_noise
from perlin_noise import PerlinNoise

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
tile_codes = {
    '.': 1,
    'r': 2,
    'o': 6,
    's': 3,
    'e': 5,
    'g': 4,
    '@': 12
}

BASE_LEVEL = 1

max_matrix = [6.82, 20.10804, 9.8388, 8.53, 36.588145999999995, 5.33, 6.84, 4.29, 9.87, 7.82, 28.241325, 7.37]


# [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 21.432317145200003, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948]
# [37.006794, 478.9033021773, 8.43, 72.54700848, 0.9024834038999999, 6.54, 2.94, 2063.9393489304625, 112.7632091943, 7.82, 6.684135, 3.918629]
# [6.82, 20.10804, 9.8388, 8.53, 36.588145999999995, 5.33, 6.84, 4.29, 9.87, 7.82, 28.241325, 7.37]
# [20.336370000000002, 185.17912549919998, 1.97, 1.671633222, 2.62, 7.4, 44.425445864800004, 8.929404, 2.78, 9.77, 21.22764, 6.49]
# [3.642464, 171.3299742141, 10.7402088365, 9.3, 23.1663422592, 2.72, 2.94, 5.06, 43.300808, 8.95, 12.6812612745, 11.492172]
# [11.524584353579515, 6796.8386980526775, 19.022295, 5346.2012853738925, 60.49509299999999, 73.60691163440032, 2034.9186754245743, 46.794374999999995, 61.24631397040001, 5.51, 663.7396091672757, 320.3145562528]


def generate_landscale(seed=SEED):
    noise = PerlinNoise(octaves=2, seed=seed)
    landscale = [[0 for i in range(terrain_width)] for i in range(terrain_width)]

    for position in range(terrain_width ** 2):
        x = floor(position / terrain_width)
        z = floor(position % terrain_width)
        y = floor(noise([x / period, z / period]) * amp)
        landscale[int(x)][int(z)] = int(y)
    return landscale


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
box_image = load_image('box.png')
fon_image = load_image('new_fon_wr.jpg')
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
    def __init__(self, x, y, w, font: pygame.font.Font, color):
        super().__init__()
        self.color = color
        self.backcolor = None
        self.pos = (x, y)
        self.width = w
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()

    def render_text(self):
        self.font.set_bold(self.active)
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface((max(self.width, t_surf.get_width() + 10), t_surf.get_height() + 10),
                                    pygame.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2*(2 if self.active else 1))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode in '1234567890':
                    self.text += event.unicode
                self.render_text()
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
        try:
            all_units.remove(self)
        except:
            pass
        self.kill()

    def movement(self, level):
        pass

    def reverse_movement(self):
        pass

    def update(self, *args):
        self.eat -= 1
        if self.eat <= 0:
            self.die()
        self.movement(args[0])


class Player(Unit):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_image, [100, 10, 10, 10])


def get_elem_by_coord(lvl, x, y):
    if 0 <= x < len(lvl):
        if 0 <= y < len(lvl[x]):
            return tile_codes[lvl[x][y]]
    return 0


class Enemy(Unit):
    def __init__(self, pos_x, pos_y, matrix=None):
        self.type = choice(range(3))
        attri = [500, 10, 10, 10]
        attri[self.type + 1] += 10 * BASE_LEVEL
        super().__init__(pos_x, pos_y, enemies_images[self.type], attri)
        self.matrix = matrix
        self.last_move = MOVES[0]

    def calculate(self, data):
        max_res = -1
        max_move = MOVES[0]
        for m in MOVES:
            i = MOVES.index(m)
            xn = self.x + m[0] // STEP
            yn = self.y + m[1] // STEP
            elem = get_elem_by_coord(data, xn, yn) * 10
            res = elem * self.matrix[i * 3] + self.matrix[i * 3 + 1] + self.eat * self.matrix[i * 3 + 2]
            if res > max_res and elem != 0:
                max_res = res
                max_move = m
            xn += m[0]
            yn += m[1]
            elem = get_elem_by_coord(data, xn, yn) * 10
            res = elem * self.matrix[i * 3] + self.matrix[i * 3 + 1] + self.eat * self.matrix[i * 3 + 2]
            if res > max_res and elem != 0:
                max_res = res
                max_move = m
        if max_res == -1:
            return [0, 0]
        return max_move

    def movement(self, level):
        data = level[:]
        move = self.calculate(data)
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
            return True
        return False

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


class Food(Pickable):
    def __init__(self, x, y, type):
        super().__init__(x, y, atebles_images[type])
        self.type = type

    def pick(self, u: Unit):
        u.eat += 11 + self.type * 40 - (BASE_LEVEL//3)*5
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
            if -1 <= level[y][x] < 1:
                Tile('sand', x, y)
                lvl[x][y] = 's'
                if level[y][x] == 0 and random.randint(1, 30 - (BASE_LEVEL - 1)*5) == 1:
                    enemies.append(Enemy(x, y, matrix=max_matrix))
            elif -1 > level[y][x]:
                Tile('rock', x, y)
                lvl[x][y] = 'r'
                if level[y][x] < -2 and random.randint(1, BASE_LEVEL + 2) == 1:
                    Orb(x, y, choice(range(3)))
                    lvl[x][y] = 'o'
            elif level[y][x] >= 1:
                Tile('grass', x, y)
                lvl[x][y] = 'g'
                if level[y][x] > 1:
                    Food(x, y, int(random.randrange(5 + BASE_LEVEL) == 5))
                    lvl[x][y] = 'e'
                # enemies.append(Enemy(x, y))
                # lvl[x][y] = 'e'
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
    fon = pygame.transform.scale(fon_image, (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gameplay = True
        pygame.display.flip()
        clock.tick(FPS)


def new_game():
    intro_text = ["SEED:", "",
                  "seed - уникальный код,",
                  "отвечающий за генерацию уровня",
                  "оставь поле пустым, если не знаешь что это",
                  "LVL:", ""
                          "уровень сложности, от 1 до 3 (иначе 1)"]
    fon = pygame.transform.scale(fon_image, (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    font.bold = True
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    text_box = TextInputBox(100, 50, 50, pygame.font.Font(None, 40), pygame.Color('purple'))
    text_box2 = TextInputBox(100, 240, 50, pygame.font.Font(None, 40), pygame.Color('purple'))
    text_box_group = pygame.sprite.Group(text_box, text_box2)
    while True:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                global BASE_LEVEL
                BASE_LEVEL = int(text_box2.text) if int(text_box2.text) in [1, 2, 3] else 1
                print(BASE_LEVEL)
                return text_box.text if text_box.text else SEED
        text_box_group.update(event_list)
        screen.blit(fon, (0, 0))
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('purple'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        text_box_group.draw(screen)
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


def battle(u1: Unit, u2: Unit):
    i = random.randrange(0, 3)
    if u1.attr[i] >= u2.attr[i]:
        u1.eat += u2.eat // (BASE_LEVEL + 1)
        u1.attr[i] += (u1.attr[i] - u2.attr[i] + 4) // (BASE_LEVEL + 1)
        print(i, u1.attr[i])
        u2.die()
    else:
        u2.eat += u1.eat // (BASE_LEVEL + 1)
        u2.attr[i] += (u2.attr[i] - u1.attr[i] + 4) // (BASE_LEVEL + 1)
        u1.die()


def check_nearest(u1: Unit):
    ans = []
    for u2 in all_units:
        m = abs(u1.x - u2.x) + abs(u1.y - u2.y)
        if m <= 1 and u1 != u2:
            ans.append(u2)
    return ans


def menu_battle(u1, u2):
    intro_text = ["БИТВА                        VS", "",
                  f"Вы: Еда: {u1.eat}, Скилы: {', '.join(map(str, u1.attr))}",
                  f"Враг: Еда: {u2.eat}, Скилы: {', '.join(map(str, u2.attr))}",
                  "Нажмите на экран, чтоб начать сражение"]
    font = pygame.font.Font(None, 50)
    text_coord = 50
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))
    surf.set_alpha(220)
    screen.blit(surf, (0, 0))
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    screen.blit(u1.image, (300, 50))
    screen.blit(u2.image, (395, 50))
    gameplay = False
    while not gameplay:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                gameplay = True
        pygame.display.flip()
        clock.tick(FPS)
    battle(u1, u2)
    intro_text[4] = f"Исход битвы: победитель - {'вы' if u1.alive else 'враг'}"
    tiles_group.draw(screen)
    units_group.draw(screen)
    pickable_group.draw(screen)
    draw_menu(u1)
    pygame.display.flip()
    text_coord = 50
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))
    surf.set_alpha(220)
    screen.blit(surf, (0, 0))
    screen.blit(u1.image if u1.alive else box_image, (300, 50))
    screen.blit(u2.image if u2.alive else box_image, (395, 50))
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
            elif event.type == pygame.MOUSEBUTTONDOWN or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                gameplay = True
        pygame.display.flip()
        clock.tick(FPS)


def main_game(seed=SEED):
    all_units.clear()
    all_pickables.clear()
    all_sprites.empty()
    units_group.empty()
    pickable_group.empty()
    tiles_group.empty()
    player_group.empty()
    motion = M_STOP
    # level = load_level('map.txt')
    # pprint(level)
    random.seed(seed)
    player, level_x, level_y, enemies, level = generate_level(seed)
    score = 0
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
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
                level[player.x][player.y] = 's'
                player.move_by(-STEP, 0)
                level[player.x][player.y] = '@'
            motion = M_MOVING
        elif motion == M_RIGHT:
            if check_coords(level, player.x + 1, player.y) and level[player.x + 1][player.y] != '#':
                level[player.x][player.y] = 's'
                player.move_by(STEP, 0)
                level[player.x][player.y] = '@'
            motion = M_MOVING
        elif motion == M_UP:
            if check_coords(level, player.x, player.y - 1) and level[player.x][player.y - 1] != '#':
                level[player.x][player.y] = 's'
                player.move_by(0, -STEP)
                level[player.x][player.y] = '@'
            motion = M_MOVING
        elif motion == M_DOWN:
            if check_coords(level, player.x, player.y + 1) and level[player.x][player.y + 1] != '#':
                level[player.x][player.y] = 's'
                player.move_by(0, STEP)
                level[player.x][player.y] = '@'
            motion = M_MOVING
        if pressed:
            for unit in all_units:
                score += 1
                unit.update(level)
                if not check_coords(level, unit.x, unit.y) or level[unit.x][unit.y] == '#':
                    unit.reverse_movement()
                else:
                    for p in all_pickables:
                        if p.try_to_pick(unit):
                            level[unit.x][unit.y] = '.'
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
        if not player.alive:
            score += sum([(i - 10) * 100 for i in player.attr])
            return score
        for u in check_nearest(player):
            menu_battle(player, u)
            tiles_group.draw(screen)
            units_group.draw(screen)
            pickable_group.draw(screen)
            draw_menu(player)
            pygame.display.flip()
            if not player.alive:
                score += sum([(i - 10) * 100 for i in player.attr])
                return score
        for u1 in all_units:
            if u1 == player:
                continue
            for u2 in check_nearest(u1):
                battle(u1, u2)
        clock.tick(FPS)


def end_game(score):
    intro_text = ["GAME END", "",
                  f"Счет: {score}",
                  "Нажми на экран, чтобы начать новую игру"]
    font = pygame.font.Font(None, 50)
    text_coord = 50
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))
    surf.set_alpha(220)
    screen.blit(surf, (0, 0))
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gameplay = True
        pygame.display.flip()
        clock.tick(FPS)


# pygame.quit()
# show_map_pic()

start_screen()
while True:
    end_game(main_game(int(new_game())))
