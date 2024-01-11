import random
from numpy import floor
from perlin_noise import PerlinNoise
from pyeasyga.pyeasyga import GeneticAlgorithm
import sys

STEP = 1
MOVES = [[STEP, 0], [-STEP, 0], [0, STEP], [0, -STEP]]
SEED = 123
SEED2 = 4255
random.seed(SEED)
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


def generate_landscale(seed=SEED):
    noise = PerlinNoise(octaves=2, seed=seed)
    landscale = [[0 for i in range(terrain_width)] for i in range(terrain_width)]

    for position in range(terrain_width ** 2):
        x = floor(position / terrain_width)
        z = floor(position % terrain_width)
        y = floor(noise([x / period, z / period]) * amp)
        landscale[int(x)][int(z)] = int(y)
    return landscale


def generate_level(seed=SEED):
    level = generate_landscale(seed)
    lvl = [['.' for i in range(terrain_width)] for i in range(terrain_width)]
    for y in range(len(level)):
        for x in range(len(level[y])):
            if -1 <= level[y][x] < 1:
                lvl[x][y] = 's'
            elif -1 > level[y][x]:
                lvl[x][y] = 'r'
                if level[y][x] < -2:
                    lvl[x][y] = 'o'
            elif level[y][x] >= 1:
                lvl[x][y] = 'g'
                if level[y][x] > 1:
                    lvl[x][y] = 'e'
    return lvl


seed_data = []

for i in range(6):
    seed_data.append(0.0)
    seed_data.append(0.0)

ga = GeneticAlgorithm(
    seed_data,
    population_size=20,
    generations=50,
    crossover_probability=0.8,
    mutation_probability=0.5,
    elitism=True,
    maximise_fitness=True
)


def create_individual(data):
    individual = data[:]
    for i in range(len(individual)):
        individual[i] = random.randint(0, 1000) / 100.0
    return individual


ga.create_individual = create_individual


def crossover(parent_1, parent_2):
    index = random.randrange(0, len(parent_1))
    child_1 = parent_1[:index] + parent_2[index:]
    child_2 = parent_2[:index] + parent_1[index:]
    return child_1, child_2


ga.crossover_function = crossover


def mutate(individual):
    mutate_index1 = random.randrange(len(individual))
    mutate_index2 = random.randrange(len(individual))
    individual[mutate_index1] = individual[mutate_index1]*random.randint(0, 100000) / 10000.0
    individual[mutate_index2] = individual[mutate_index2]*random.randint(0, 100000) / 10000.0


ga.mutate_function = mutate


def get_elem_by_coord(lvl, x, y):
    if 0 <= x < len(lvl):
        if 0 <= y < len(lvl[x]):
            return lvl[x][y]
    return 0


def cycle_life(ind, x, y, attr, lvl, px, py):
    move = random.choice(MOVES)
    if get_elem_by_coord(lvl, px + m[0], py + m[0]):
        lvl[px][py] = tile_codes['s']
        lvl[px + m[0]][py + m[1]] = tile_codes['@']
        px += m[0]
        py += m[1]
    new_attr = attr[:]
    new_attr[0] -= 1
    max_res = -1
    max_move = MOVES[0]
    for m in MOVES:
        i = MOVES.index(m)
        xn = x + m[0]
        yn = y + m[1]
        elem = get_elem_by_coord(lvl, xn, yn)
        elem *= 100
        res = elem * ind[i * 3] + ind[i * 3 + 1] + attr[0] * ind[i * 3 + 2]
        if res > max_res and elem != 0:
            max_res = res
            max_move = m
        xn += m[0]
        yn += m[1]
        elem = get_elem_by_coord(lvl, xn, yn)
        elem *= 100
        res = elem * ind[i * 3] + ind[i * 3 + 1] + attr[0] * ind[i * 3 + 2]
        if res > max_res and elem != 0:
            max_res = res
            max_move = m
    if max_res == -1:
        new_attr[0] = 0
        return new_attr, x, y
    m = max_move
    xn = x + m[0]
    yn = y + m[1]
    elem = get_elem_by_coord(lvl, xn, yn)
    if elem == tile_codes['o']:
        lvl[xn][yn] = tile_codes['r']
        new_attr[1] += 10
    elif elem == tile_codes['e']:
        lvl[xn][yn] = tile_codes['g']
        new_attr[0] += 10
    elif elem == tile_codes['@']:
        lvl[xn][yn] = tile_codes['s']
        new_attr[0] += 1000
    return new_attr, xn, yn, px, py


def fitness(individual, data):
    fit = 0
    attr = [100, 0]
    f_lvl = generate_level(SEED)
    lvl = [list(map(lambda x: tile_codes[x], l)) for l in f_lvl]
    x, y = len(lvl) // 2, len(lvl) // 2
    px, py = len(lvl) // 2, len(lvl) // 2 + 2
    lvl[px][py] = tile_codes['@']
    eat = 0
    while attr[0] > 0:
        laste = attr[0]
        attr, x, y, px, py = cycle_life(individual, x, y, attr, lvl, px, py)
        fit += 1
        if laste < attr[0]:
            eat += 1
    attr[0] = 100
    f_lvl = generate_level(SEED2)
    lvl = [list(map(lambda x: tile_codes[x], l)) for l in f_lvl]
    px, py = len(lvl) // 2, len(lvl) // 2 + 2
    lvl[px][py] = tile_codes['@']
    while attr[0] > 0:
        laste = attr[0]
        attr, x, y, px, py = cycle_life(individual, x, y, attr, lvl, px, py)
        fit += 1
        if laste < attr[0]:
            eat += 1
    fit += attr[1] * 500
    fit += eat * 500
    return fit


ga.fitness_function = fitness
ga.run()

f = open("best_pop.txt", "a")
real_stdout = sys.stdout
sys.stdout = f
for ind in ga.last_generation():
    print(ind)
sys.stdout = real_stdout
for ind in ga.last_generation():
    print(ind)
print(ga.best_individual())
# (3150, [95.26, 4.62, 87.16, 60.03, 55.89, 90.85, 93.19, 88.14, 87.52, 56.29, 75.33, 91.31])

# (184790, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 21.432317145200003, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])
# (184790, [15.51741, 0.0, 2.514816, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 12.237853089909201, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])
# (55200, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 3198.0962159807, 61.87340338025616, 7.82, 97.38863707395768, 188.5850342948])
# (53200, [15.51741, 0.0, 3.0364050000000002, 14.898136000000001, 2805.074917203738, 130.24637029430963, 18.3721539974, 691.8746920637984, 18.5884165656, 7.82, 77.95388068552501, 188.5850342948])
# (48200, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 116.62395374560582, 32.66259523520238, 7.82, 407.6302921665015, 188.5850342948])
# (45810, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 495.83655808317957, 61.87340338025616, 7.82, 18.0905444652, 188.5850342948])
# (45810, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 495.83655808317957, 61.87340338025616, 7.82, 18.0905444652, 188.5850342948])
# (43740, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 515.4486402518052, 112.16200015412701, 85.18703095702645, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])
# (42750, [15.51741, 0.0, 8.946822000000001, 14.898136000000001, 860.1997101592556, 85.356137022555, 18.3721539974, 495.83655808317957, 32.66259523520238, 7.82, 111.95696642216039, 68.51294295930084])
# (36700, [15.51741, 0.0, 1.11, 93.5945597928, 290.60801018893767, 85.356137022555, 112.16200015412701, 21.432317145200003, 32.66259523520238, 19.548436000000002, 10.9986286875, 188.5850342948])
# (35240, [15.51741, 0.0, 1.11, 14.898136000000001, 860.1997101592556, 85.356137022555, 18.3721539974, 3844.2704184746995, 32.66259523520238, 42.11539200000001, 111.95696642216039, 68.51294295930084])
# (33200, [15.51741, 0.0, 1.11, 21.036168032000003, 290.60801018893767, 85.356137022555, 112.16200015412701, 21.432317145200003, 32.66259523520238, 31.368366, 10.9986286875, 188.5850342948])
# (31730, [15.51741, 0.0, 2.06682, 116.99655182160002, 290.60801018893767, 92.09927184733684, 18.3721539974, 495.83655808317957, 149.71296586099896, 7.82, 55.18734578429003, 188.5850342948])
# (30200, [112.18466733599999, 0.0, 1.11, 37.270666831199996, 290.60801018893767, 85.356137022555, 18.3721539974, 21.432317145200003, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])
# (25200, [15.51741, 0.0, 2.06682, 116.99655182160002, 1291.9269700959412, 92.09927184733684, 18.3721539974, 495.83655808317957, 1185.0230386795652, 7.82, 10.9986286875, 188.5850342948])
# (20200, [15.51741, 0.0, 0.28848900000000005, 14.898136000000001, 290.60801018893767, 85.356137022555, 112.16200015412701, 21.432317145200003, 32.66259523520238, 7.82, 10.9986286875, 1581.7758336510644])
# (20200, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 21.432317145200003, 32.66259523520238, 27.515452000000003, 10.9986286875, 1088.2865159084317])
# (20200, [22.6613611473336, 0.0, 1.11, 34.422143228, 290.60801018893767, 92.09927184733684, 30.90380023902654, 1890.5752123153552, 149.71296586099896, 7.82, 55.18734578429003, 1302.4813978604657])
# (17340, [15.51741, 0.0, 1.11, 99.698326112, 290.60801018893767, 85.356137022555, 112.16200015412701, 193.908889371197, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])
# (15200, [15.51741, 0.0, 1.11, 21.036168032000003, 2549.5040733875503, 85.356137022555, 112.16200015412701, 39.058254765412485, 32.66259523520238, 31.368366, 10.9986286875, 188.5850342948])
# (184790, [15.51741, 0.0, 1.11, 14.898136000000001, 290.60801018893767, 85.356137022555, 18.3721539974, 21.432317145200003, 32.66259523520238, 7.82, 10.9986286875, 188.5850342948])