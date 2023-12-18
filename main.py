# This is main file of project
# Last commit: added a collision with blocks
# MAIN TODO: create a good map for testing
import pygame
import sys
import os
import time
from pprint import pprint

FPS = 50

pygame.init()
clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 1500, 500
screen = pygame.display.set_mode(size)

# Константы движения
# TODO: дополнить при выполнении цикла действий ИИ
STEP = 1
M_STOP = 0
M_RIGHT = 1
M_LEFT = 2
M_UP = 3
M_DOWN = 4


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

tile_width = tile_height = 50

player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def move_to(self, delta_x, delta_y):
        self.x, self.y = self.x + delta_x, self.y + delta_y
        self.rect = self.rect.move(tile_width * delta_x, tile_height * delta_y)


def generate_level(level):
    # TODO: исправить генерацию карты (случайным образом + шум)
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


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
    player, level_x, level_y = generate_level(level)
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                terminate()
            elif i.type == pygame.KEYDOWN:
                if i.key == pygame.K_LEFT:
                    motion = M_LEFT
                elif i.key == pygame.K_RIGHT:
                    motion = M_RIGHT
                elif i.key == pygame.K_UP:
                    motion = M_UP
                elif i.key == pygame.K_DOWN:
                    motion = M_DOWN
            elif i.type == pygame.KEYUP:
                if i.key in [pygame.K_LEFT,
                             pygame.K_RIGHT,
                             pygame.K_UP,
                             pygame.K_DOWN]:
                    motion = M_STOP
        screen.fill(pygame.Color("black"))
        if motion == M_LEFT:
            if level[player.x - 1][player.y] != '#':
                player.move_to(-STEP, 0)
        elif motion == M_RIGHT:
            if level[player.x + 1][player.y] != '#':
                player.move_to(STEP, 0)
        elif motion == M_UP:
            if level[player.x][player.y - 1] != '#':
                player.move_to(0, -STEP)
        elif motion == M_DOWN:
            if level[player.x][player.y + 1] != '#':
                player.move_to(0, STEP)

        if motion != M_STOP:
            time.sleep(0.15)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
main_game()
