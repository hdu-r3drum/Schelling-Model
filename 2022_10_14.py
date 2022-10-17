"""
策略改变+人种
"""

from operator import truediv
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import importlib
import sys
import xlsxwriter
import xlrd

importlib.reload(sys)

# 打开交互模式
plt.ion()
plt.figure()

# 变量声明
vector = list(range(10000))  # 100*100
strategy_map = []  # 策略
race_map = []  # 种族
wealth_threshold = 6  # 财富满意门槛
race_threshold = 0.5  # 人种满意门槛
strategy_threshold = 0.6  # 博弈满意门槛

# 博弈收益矩阵
T = 1.2
R = 1
P = 0
S = 0


def initial():  # 初始化 100*100
    global strategy_map
    global race_map

    # 初始化策略集
    strategy_all = []
    for i in range(2500):
        strategy_all.append([165 / 255, 165 / 255, 0])  # 背叛
        strategy_all.append([165 / 255, 0, 165 / 255])  # 合作
    random.shuffle(strategy_all)

    # 初始化种族集
    race_all = []
    for i in range(2500):
        race_all.append([0, 0, 1])  # 种族1
        race_all.append([1, 165 / 255, 0])  # 种族2
    for i in range(5000):
        race_all.append([1, 1, 1])  # 空
    random.shuffle(race_all)

    # 一起打乱
    # 创建一个三维数组，以0填充，第一维62，第二维62，第三维3
    strategy_map = np.zeros((100, 100, 3))  # 策略
    race_map = np.zeros((100, 100, 3))  # 种族
    j = 0
    for i in range(10000):  # 种族1
        race_map[i // 100][i % 100] = race_all[i]
        if race_all[i] == [1, 1, 1]:
            strategy_map[i // 100][i % 100] = [1, 1, 1]
        else:
            strategy_map[i // 100][i % 100] = strategy_all[j]
            j = j + 1


def draw_race_map(name):  # maplotlib画图
    global race_map
    plt.cla()
    plt.ioff()
    plt.axis("off")
    plt.title(str(name))
    plt.imshow(race_map, interpolation="nearest")
    plt.show()


def draw_strategy_map(name):  # matplotlib画图
    global strategy_map
    plt.cla()
    plt.ioff()
    plt.axis("off")
    plt.title(str(name))
    plt.imshow(strategy_map, interpolation="nearest")
    # plt.show()
    plt.savefig(f'.\OUT\{str(name)}', bbox_inches='tight')


def gambling_score(x, y):  # 两两博弈得分
    score = 0
    if x[1] == 0 and y[2] == 0:  # 合作VS背叛
        score = score + S

    if x[1] == 0 and y[1] == 0:  # 合作VS合作
        score = score + R

    if x[2] == 0 and y[2] == 0:  # 背叛VS背叛
        score = score + P

    if x[2] == 0 and y[1] == 0:  # 背叛VS合作
        score = score + T
    # print(x, y)
    # print(score)
    return score


def exchange(a, b):
    temp_strategy_0 = strategy_map[a[0]][a[1]][0]
    temp_strategy_1 = strategy_map[a[0]][a[1]][1]
    temp_strategy_2 = strategy_map[a[0]][a[1]][2]
    temp_race_0 = race_map[a[0]][a[1]][0]
    temp_race_1 = race_map[a[0]][a[1]][1]
    temp_race_2 = race_map[a[0]][a[1]][2]

    strategy_map[a[0]][a[1]] = strategy_map[b[0]][b[1]]
    race_map[a[0]][a[1]] = race_map[b[0]][b[1]]

    strategy_map[b[0]][b[1]] = [temp_strategy_0, temp_strategy_1, temp_strategy_2]
    race_map[b[0]][b[1]] = [temp_race_0, temp_race_1, temp_race_2]


def satisfied_or_not(x, y):  # 邻居满意计算
    race_all = 0
    race_score = 0
    strategy_score = 0
    # 邻居1
    if sum(race_map[(x + 1 + 100) % 100][y]) != 3:  # 邻居不为空
        race_all = race_all + 1
        if race_map[(x + 1 + 100) % 100][y][1] == race_map[x][y][1]:
            race_score = race_score + 1
        strategy_score = strategy_score + gambling_score(strategy_map[x][y], strategy_map[(x + 1 + 100) % 100][y])
    # 邻居2
    if sum(race_map[(x - 1 + 100) % 100][y]) != 3:
        race_all = race_all + 1
        if race_map[(x - 1 + 100) % 100][y][1] == race_map[x][y][1]:
            race_score = race_score + 1
        strategy_score = strategy_score + gambling_score(strategy_map[x][y], strategy_map[(x - 1 + 100) % 100][y])
    # 邻居3
    if sum(race_map[x][(y + 1 + 100) % 100]) != 3:
        race_all = race_all + 1
        if race_map[x][(y + 1 + 100) % 100][1] == race_map[x][y][1]:
            race_score = race_score + 1
        strategy_score = strategy_score + gambling_score(strategy_map[x][y], strategy_map[x][(y + 1 + 100) % 100])
    # 邻居4
    if sum(race_map[x][(y - 1 + 100) % 100]) != 3:
        race_all = race_all + 1
        if race_map[x][(y - 1 + 100) % 100][1] == race_map[x][y][1]:
            race_score = race_score + 1
        strategy_score = strategy_score + gambling_score(strategy_map[x][y], strategy_map[x][(y - 1 + 100) % 100])

    if race_all == 0:
        return 0, 0

    race_score = race_score / race_all
    # print("race_all:", race_all)
    # print("race_score:", race_score)
    # print("strategy_score:", strategy_score)

    if strategy_score >= strategy_threshold * race_all:
        return 1, strategy_score
    else:
        return 0, 0


def move(run_times):
    # neighbor = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [0, -1], [1, -1], [1, 0], [1, 1]]
    neighbor = [[-1, 0], [0, 1], [0, -1], [1, 0]]
    times = 0
    while times < run_times:
        if times % 1000 == 0:
            print(times)
            draw_strategy_map(f'Initial {times}  strategy distribution----------------')
            # draw_race_map(f'Initial {times} race distribution----------------')

        while True:
            i = random.randint(0, 99)
            j = random.randint(0, 99)
            if sum(race_map[i][j]) != 3:
                break

        # 判断空邻居
        neighbor_empty = []
        neighbor_not_empty = []
        for neig in neighbor:
            new_i = (i + neig[0] + 100) % 100
            new_j = (j + neig[1] + 100) % 100
            if sum(race_map[new_i][new_j]) == 3:
                neighbor_empty.append([new_i, new_j])
            else:
                neighbor_not_empty.append([new_i, new_j])

        # 跟随邻居策略，寻找邻居最优策略，学习邻居最优策略(得分按照个体各自博弈）
        if len(neighbor_not_empty) != 0:
            score_all = []
            for nei in neighbor_not_empty:
                flag_satisfied_or_not, score = satisfied_or_not(nei[0], nei[1])
                score_all.append(score)
            max_score = max(score_all)
            flag_satisfied_or_not, mine_score = satisfied_or_not(i, j)
            Index_max_score = score_all.index(max_score)  # 只选取了第一个最大值
            # 改变自身策略
            if max_score > mine_score:
                strategy_map[i][j] = strategy_map[neighbor_not_empty[Index_max_score][0]][neighbor_not_empty[Index_max_score][1]]

        flag_satisfied_or_not, mine_score = satisfied_or_not(i, j)
        # 邻居为满
        if len(neighbor_empty) == 0:
            continue
        # 邻居为空  邻居位置随意移动
        elif flag_satisfied_or_not == 0:
            # 随机寻找一个邻居
            a = random.random()
            Rand = int(a / (1 / len(neighbor_empty)))
            exchange(neighbor_empty[Rand], [i, j])
        times += 1


if __name__ == '__main__':
    initial()
    draw_race_map('Initial race distribution')
    draw_strategy_map('Initial strategy distribution')
    move(100000000)
