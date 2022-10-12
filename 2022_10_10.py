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
vector = list(range(400))  # 20*20
agent1 = []  # 人种1
agent2 = []  # 人种2
empty = []  # 空节点
strategy_map = []  # 策略
race_map = []  # 种族
wealth_threshold = 6  # 财富满意门槛
race_threshold = 0.79  # 人种满意门槛
t = 1.2  # 参数t
a = 0  # 搬家策略收益权重
b = 1  # 搬家同质性权重
plt.ion()


def initial():  # 20*20
    # 原地搅乱序列vector
    global vector
    global strategy_map
    global race_map
    global agent1
    global agent2
    global empty
    random.shuffle(vector)  # 打乱地图 同随机填入agent
    agent1 = vector[0:150]
    agent2 = vector[150:300]
    empty = vector[300:400]
    # 创建一个三维数组，以0填充，第一维62，第二维62，第三维3
    strategy_map = np.zeros((20, 20, 3))  # 策略
    race_map = np.zeros((20, 20, 3))  # 种族
    for i in range(400):
        if i in agent1:
            rnd = random.randint(0, 1)  # 随机分配agent1策略
            strategy_map[i // 20][i % 20] = [rnd, 0, 0]
            race_map[i // 20][i % 20] = [0, 0, 1]
        if i in agent2:
            rnd = random.randint(0, 1)  # 随机分配agent2策略
            strategy_map[i // 20][i % 20] = [rnd, 0, 0]
            race_map[i // 20][i % 20] = [1, 165 / 255, 0]
        elif i in empty:
            strategy_map[i // 20][i % 20] = [0, 0, 1]
            race_map[i // 20][i % 20] = [1, 1, 1]


def draw_race_map(name):  # matplotlib画图
    global race_map
    plt.subplot(2, 1, 2)
    plt.axis("off")
    plt.title(str(name))
    plt.imshow(race_map, interpolation="nearest")
    plt.pause(0.1)
    plt.ioff()


def draw_strategy_map(name):
    # global strategy_map
    # plt.cla()
    # plt.ioff()
    # plt.axis("off")
    # plt.title(str(name))
    # X = np.arange(20)  # X轴的坐标
    # Y = np.arange(20)  # Y轴的坐标
    # Z = np.zeros(shape=(20, 20))  # 设置每一个（X，Y）坐标所对应的Z轴的值
    # for i in range(20):
    #     for j in range(20):
    #         Z[i, j] = strategy_map[i][j][0]
    # xx, yy = np.meshgrid(X, Y)  # 网格化坐标
    # X, Y = xx.ravel(), yy.ravel()  # 矩阵扁平化
    # bottom = np.zeros_like(X)  # 设置柱状图的底端位值
    # Z = Z.ravel()  # 扁平化矩阵
    # print(Z)
    # width = depth = 1  # 每一个柱子的长和宽
    # height = 1
    # fig = plt.figure()
    # ax = fig.add_subplot(aspect='auto', projection='3d')  # 三维坐标轴
    # ax.bar3d(X, Y, bottom, width, height, Z, shade=True)  #
    # # 坐标轴设置
    # ax.set_xlabel('X')
    # ax.set_ylabel('Y')
    # ax.set_zlabel('Z(value)')
    # plt.show()
    strategy_map1 = np.zeros((20, 20, 3))
    for i in range(20):
        for j in range(20):
            if strategy_map[i][j][2] == 1:
                strategy_map1[i][j] = [1, 1, 1]
            elif strategy_map[i][j][0] == 1:
                strategy_map1[i][j] = strategy_map[i][j]
            else:
                strategy_map1[i][j] = [0, 1, 0]

    plt.subplot(2, 1, 1)
    plt.axis("off")
    plt.title(str(name))
    plt.imshow(strategy_map1, interpolation="nearest")
    plt.pause(0.1)
    plt.ioff()


def writeExcel():
    workbook = xlsxwriter.Workbook('strategy_Result.xlsx')
    worksheet = workbook.add_worksheet('strategy_Matrix')
    for i in range(20):
        for j in range(20):
            if strategy_map[i][j][2] != 1:
                worksheet.write(i, j, 1)
            else:
                worksheet.write(i, j, 0)
    worksheet = workbook.add_worksheet('race_Matrix')
    for i in range(20):
        for j in range(20):
            if race_map[i][j][1] == 0:
                worksheet.write(i, j, 1)
            elif race_map[i][j][1] == 1:
                worksheet.write(i, j, 0)
            else:
                worksheet.write(i, j, -1)
    workbook.close()


def Moran():
    strategy_Result = xlrd.open_workbook('strategy_Result.xlsx')
    Weight_Matrix = xlrd.open_workbook('Weight_Matrix.xlsx')
    n = 20 * 20
    S0 = 0
    average = 0.0
    numerator = 0.0
    denominator = 0.0
    mode = int(input('0:Strategy  1:Races'))
    table1 = strategy_Result.sheets()[mode]

    table2 = Weight_Matrix.sheets()[0]

    list = []

    for i in range(400):
        for j in range(400):
            S0 = S0 + int(table2.cell_value(rowx=i, colx=j))

    for i in range(20):
        for j in range(20):
            average = average + float(table1.cell_value(rowx=i, colx=j))

    average = average / 400.0

    for i in range(20):
        for j in range(20):
            denominator = denominator + (float(table1.cell_value(rowx=i, colx=j)) - average) * (
                    float(table1.cell_value(rowx=i, colx=j)) - average)
            list.append(float(table1.cell_value(rowx=i, colx=j)))

    for i in range(400):
        for j in range(400):
            if int(table2.cell_value(rowx=i, colx=j)) == 1:
                numerator = numerator + (list[i] - average) * (list[j] - average)

    print((n / S0) * (numerator / denominator))


def Weight_Matrix():
    strategy_Result = xlrd.open_workbook('strategy_Result.xlsx')
    table1 = strategy_Result.sheets()[1]
    weight_matrix = np.zeros((400, 400))

    workbook = xlsxwriter.Workbook('Weight_Matrix.xlsx')
    worksheet = workbook.add_worksheet('Weight_Matrix')
    list = []
    for i in range(20):
        for j in range(20):
            list.append(float(table1.cell_value(rowx=i, colx=j)))

    for i in range(400):
        temp = np.zeros(400)
        if list[i] != 0:
            if (i < 20) and (i == 0):
                temp[i + 1] = abs(list[i + 1])
                temp[i + 20] = abs(list[i + 20])

            elif (i < 20) and (i != 19):
                temp[i - 1] = abs(list[i - 1])
                temp[i + 1] = abs(list[i + 1])
                temp[i + 20] = abs(list[i + 20])

            elif (i < 20) and (i == 19):
                temp[i - 1] = abs(list[i - 1])
                temp[i + 20] = abs(list[i + 20])

            elif (i >= 20) and (i < 380) and (i % 20 == 0):
                temp[i - 20] = abs(list[i - 20])
                temp[i + 1] = abs(list[i + 1])
                temp[i + 20] = abs(list[i + 20])

            elif (i >= 20) and (i < 380) and ((i - 19) % 20 != 0):
                temp[i - 1] = abs(list[i - 1])
                temp[i + 1] = abs(list[i + 1])
                temp[i + 20] = abs(list[i + 20])
                temp[i - 20] = abs(list[i - 20])

            elif (i >= 20) and (i < 380) and ((i - 19) % 20 == 0):
                temp[i - 1] = abs(list[i - 1])
                temp[i + 20] = abs(list[i + 20])
                temp[i - 20] = abs(list[i - 20])

            elif (i >= 380) and (i == 380):
                temp[i + 1] = abs(list[i + 1])
                temp[i - 20] = abs(list[i - 20])

            elif (i >= 380) and (i != 399):
                temp[i - 1] = abs(list[i - 1])
                temp[i + 1] = abs(list[i + 1])
                temp[i - 20] = abs(list[i - 20])

            elif (i >= 380) and (i == 399):
                temp[i - 1] = abs(list[i - 1])
                temp[i - 20] = abs(list[i - 20])

            for j in range(400):
                worksheet.write(i, j, temp[j])
        else:
            for j in range(400):
                worksheet.write(i, j, 0)

    workbook.close()


def calculate_payload(i, j):
    payload0 = 0
    payload1 = 0
    payload = 0
    global strategy_map
    global t
    strategy = strategy_map[i][j][0]
    if strategy_map[(i - 1) % 20][j][2] == 0:
        if strategy_map[(i - 1) % 20][j][0] == 1:
            payload0 = payload0 + t
            payload1 = payload1 + 1
        else:
            payload0 = payload0 + 0
            payload1 = payload1 + 0

    if strategy_map[i][(j - 1) % 20][2] == 0:
        if strategy_map[i][(j - 1) % 20][0] == 1:
            payload0 = payload0 + t
            payload1 = payload1 + 1
        else:
            payload0 = payload0 + 0
            payload1 = payload1 + 0

    if strategy_map[i][(j + 1) % 20][2] == 0:
        if strategy_map[i][(j + 1) % 20][0] == 1:
            payload0 = payload0 + t
            payload1 = payload1 + 1
        else:
            payload0 = payload0 + 0
            payload1 = payload1 + 0

    if strategy_map[(i + 1) % 20][j][2] == 0:
        if strategy_map[(i + 1) % 20][j][0] == 1:
            payload0 = payload0 + t
            payload1 = payload1 + 1
        else:
            payload0 = payload0 + 0
            payload1 = payload1 + 0

    if payload1 > payload0:
        strategy = 1
        payload = payload1
    elif payload1 == payload0:
        payload = payload0
    else:
        payload = payload0
        strategy = 0
    return payload, strategy


def move(run_times):
    global strategy_map
    global race_map
    global agent1
    global agent2
    global empty
    count = 0
    agent = agent1 + agent2
    while count <= run_times:
        old_payload = 0
        new_payload = 0
        coordinate1 = int(random.choice(agent))
        coordinate2 = int(random.choice(empty))
        i1 = coordinate1 // 20
        j1 = coordinate1 % 20
        i2 = coordinate2 // 20
        j2 = coordinate2 % 20
        strategy = strategy_map[i1][j1][0]
        old_payload = calculate_payload(i1, j1)[0]
        new_payload, strategy = calculate_payload(i2, j2)
        old_race_satisfy = race_satisfy(i1, j1, check_race(i1, j1))
        new_race_satisfy = race_satisfy(i2, j2, check_race(i1, j1))
        if a * new_payload + b * new_race_satisfy > a * old_payload + b * old_race_satisfy:
            temp_a_0 = strategy
            temp_a_1 = strategy_map[i1][j1][1]
            temp_a_2 = strategy_map[i1][j1][2]
            temp_b_0 = strategy_map[i2][j2][0]
            temp_b_1 = strategy_map[i2][j2][1]
            temp_b_2 = strategy_map[i2][j2][2]

            strategy_map[i1][j1] = [temp_b_0, temp_b_1, temp_b_2]
            strategy_map[i2][j2] = [temp_a_0, temp_a_1, temp_a_2]

            temp_a_0 = race_map[i1][j1][0]
            temp_a_1 = race_map[i1][j1][1]
            temp_a_2 = race_map[i1][j1][2]
            temp_b_0 = race_map[i2][j2][0]
            temp_b_1 = race_map[i2][j2][1]
            temp_b_2 = race_map[i2][j2][2]

            race_map[i1][j1] = [temp_b_0, temp_b_1, temp_b_2]
            race_map[i2][j2] = [temp_a_0, temp_a_1, temp_a_2]

            agent.remove(coordinate1)
            agent.append(coordinate2)
            empty.remove(coordinate2)
            empty.append(coordinate1)

            draw_race_map('Race distribution (Round: ' + str(count) + ')')
            draw_strategy_map('Strategy distribution (Round: ' + str(count) + ')')

        count = count + 1
        print(count)


def move2(run_times):
    global strategy_map
    global race_map
    global agent1
    global agent2
    global empty
    count = 0
    agent = agent1 + agent2
    while count <= run_times:
        old_payload = 0
        new_payload = 0
        coordinate1 = int(random.choice(agent))
        coordinate2 = int(random.choice(empty))
        i1 = coordinate1 // 20
        j1 = coordinate1 % 20
        i2 = coordinate2 // 20
        j2 = coordinate2 % 20
        strategy = strategy_map[i1][j1][0]
        old_payload = calculate_payload(i1, j1)[0]
        new_payload, strategy = calculate_payload(i2, j2)
        if new_payload > old_payload:
            temp_a_0 = strategy_map[i1][j1][0]
            temp_a_1 = strategy_map[i1][j1][1]
            temp_a_2 = strategy_map[i1][j1][2]
            temp_b_0 = strategy_map[i2][j2][0]
            temp_b_1 = strategy_map[i2][j2][1]
            temp_b_2 = strategy_map[i2][j2][2]

            strategy_map[i1][j1] = [temp_b_0, temp_b_1, temp_b_2]
            strategy_map[i2][j2] = [temp_a_0, temp_a_1, temp_a_2]

            temp_a_0 = race_map[i1][j1][0]
            temp_a_1 = race_map[i1][j1][1]
            temp_a_2 = race_map[i1][j1][2]
            temp_b_0 = race_map[i2][j2][0]
            temp_b_1 = race_map[i2][j2][1]
            temp_b_2 = race_map[i2][j2][2]

            race_map[i1][j1] = [temp_b_0, temp_b_1, temp_b_2]
            race_map[i2][j2] = [temp_a_0, temp_a_1, temp_a_2]

            agent.remove(coordinate1)
            agent.append(coordinate2)
            empty.remove(coordinate2)
            empty.append(coordinate1)

        count = count + 1


def check():
    race_total = 0
    strategy_total = 0
    cooperate = 0
    defect = 0
    for i in range(20):
        for j in range(20):
            if strategy_map[i][j][2] != 1:
                strategy_total = strategy_total + 1
                if strategy_map[i][j][0] == 0:
                    defect = defect + 1
                else:
                    cooperate = cooperate + 1
            if race_map[i][j][1] != 1:
                race_total = race_total + 1
    print('race total:' + str(race_total))
    print('strategy total:' + str(strategy_total))
    print('cooperate:' + str(cooperate))
    print('defect:' + str(defect))


def race_satisfy(x, y, center_race):
    population = 0.0
    homogeneity = 0.0
    if check_race((x - 1) % 20, y) != 'empty':
        population = population + 1
        if check_race((x - 1) % 20, y) == center_race:
            homogeneity = homogeneity + 1
    if check_race(x, (y - 1) % 20) != 'empty':
        population = population + 1
        if check_race(x, (y - 1) % 20) == center_race:
            homogeneity = homogeneity + 1
    if check_race(x, (y + 1) % 20) != 'empty':
        population = population + 1
        if check_race(x, (y + 1) % 20) == center_race:
            homogeneity = homogeneity + 1
    if check_race((x + 1) % 20, y) != 'empty':
        population = population + 1
        if check_race((x + 1) % 20, y) == center_race:
            homogeneity = homogeneity + 1
    if population == 0:
        return 0
    return homogeneity / population


def check_race(x, y):
    if race_map[x][y][1] == 0:
        race = 'agent1'
    elif race_map[x][y][1] < 1:
        race = 'agent2'
    else:
        race = 'empty'
    return race


if __name__ == '__main__':
    initial()
    draw_strategy_map('Initial strategy distribution')
    draw_race_map('Initial race distribution')
    check()
    writeExcel()
    #Moran()
    move(1000)
    writeExcel()
    Weight_Matrix()
    # normalization()
    draw_strategy_map('Final strategy distribution')
    draw_race_map('Final race distribution')
    check()
    Moran()