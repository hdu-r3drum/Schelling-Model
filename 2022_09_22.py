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
wealth_map = []  # 财富
race_map = []  # 种族
unsatisfied = []  # 不满意率记录
sum_money = 0.0  # 总财富记录
save = 0.5  # 财富交交换中保留比率
exchange = 0.4  # 财富交换中交换比率
wealth_threshold = 6  # 财富满意门槛
race_threshold = 0.79  # 人种满意门槛


def initial():  # 20*20
    # 原地搅乱序列vector
    global sum_money
    global vector
    global wealth_map
    global race_map
    random.shuffle(vector)  # 打乱地图 同随机填入agent
    agent1 = vector[0:150]
    agent2 = vector[150:300]
    empty = vector[300:400]
    # 创建一个三维数组，以0填充，第一维62，第二维62，第三维3
    wealth_map = np.zeros((20, 20, 3))  # 财富
    race_map = np.zeros((20, 20, 3))  # 种族
    for i in range(400):
        if i in agent1:
            rnd = random.uniform(30.0, 20.0)  # 随机分配agent1财富 20-30
            wealth_map[i // 20][i % 20] = [rnd, 0, 0]
            race_map[i // 20][i % 20] = [0, 0, 1]
            sum_money = sum_money + rnd
        if i in agent2:
            rnd = random.uniform(30.0, 20.0)  # 随机分配agent2财富 20-30
            wealth_map[i // 20][i % 20] = [rnd, 0, 0]
            race_map[i // 20][i % 20] = [1, 165 / 255, 0]
            sum_money = sum_money + rnd
        elif i in empty:
            wealth_map[i // 20][i % 20] = [0.0, 0, 1]
            race_map[i // 20][i % 20] = [1, 1, 1]


def draw_race_map(name):  # maplotlib画图
    global race_map
    plt.cla()
    plt.ioff()
    plt.axis("off")
    plt.title(str(name))
    plt.imshow(race_map, interpolation="nearest")
    plt.show()


def draw_wealth_map(name):
    global wealth_map
    plt.cla()
    plt.ioff()
    plt.axis("off")
    plt.title(str(name))
    X = np.arange(20)  # X轴的坐标
    Y = np.arange(20)  # Y轴的坐标
    Z = np.zeros(shape=(20, 20))  # 设置每一个（X，Y）坐标所对应的Z轴的值
    for i in range(20):
        for j in range(20):
            Z[i, j] = wealth_map[i][j][0]
    xx, yy = np.meshgrid(X, Y)  # 网格化坐标
    X, Y = xx.ravel(), yy.ravel()  # 矩阵扁平化
    bottom = np.zeros_like(X)  # 设置柱状图的底端位值
    Z = Z.ravel()  # 扁平化矩阵
    print(Z)
    width = depth = 1  # 每一个柱子的长和宽
    height = 1
    fig = plt.figure()
    ax = fig.add_subplot(aspect='auto', projection='3d')  # 三维坐标轴
    ax.bar3d(X, Y, bottom, width, height, Z, shade=True)  #
    # 坐标轴设置
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z(value)')
    plt.show()


    # plt.cla()
    # plt.ioff()
    # plt.axis("off")
    # plt.title(str(name))
    # plt.imshow(wealth_map, interpolation="nearest")
    # plt.show()


def normalization():
    global wealth_map
    min = -10000
    max = 0.0
    for i in range(20):
        for j in range(20):
            if wealth_map[i][j][2] == 0:
                if wealth_map[i][j][0] > max:
                    max = wealth_map[i][j][0]
                if wealth_map[i][j][0] < max:
                    min = wealth_map[i][j][0]
    for i in range(20):
        for j in range(20):
            if wealth_map[i][j][2] == 0:
                # wealth_map[i][j][0] = (0.8 * (wealth_map[i][j][0] - min)/(max - min) + 0.2)
                wealth_map[i][j][0] = wealth_map[i][j][0] / max


def move(run_times):
    num_agent_nosat = 1  # 存在不满意的个体
    times = 0
    # 如果有节点不满意，那么就搬家，同时总循环次数小于2000次
    while num_agent_nosat and times < run_times:
        if times % 100 == 0:  # 每100次打印一次
            print(times)
        times = times + 1
        # 未定居个体个数
        num_agent_nosat = 0
        # 未定居节点位置
        nosat_v = []
        nosat_money = []
        empty_v = []

        for i in range(20):
            for j in range(20):
                if wealth_map[i][j][2] != 1:  # 非空节点
                    # 居住个数
                    n = 0.0
                    n1 = 0.0
                    area_same_class = 0  # 与邻居的种类差异个数
                    area_diff = 0  # 与邻居的财富差异

                    # 计算与邻居的种类差异
                    if (i - 1 >= 0) and (wealth_map[i - 1][j][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i - 1][j][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (wealth_map[i + 1][j][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i + 1][j][2]:
                            area_same_class = area_same_class + 1
                    if (j - 1 >= 0) and (wealth_map[i][j - 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (j + 1 <= 19) and (wealth_map[i][j + 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i][j + 1][2]:
                            area_same_class = area_same_class + 1
                    if (i - 1 >= 0) and (j - 1 >= 0) and (wealth_map[i - 1][j - 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i - 1][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (j - 1 >= 0) and (wealth_map[i + 1][j - 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i + 1][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (i - 1 >= 0) and (j + 1 <= 19) and (wealth_map[i - 1][j + 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i - 1][j + 1][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (j + 1 <= 19) and (wealth_map[i + 1][j + 1][0] != 0):
                        n = n + 1
                        if race_map[i][j][2] == race_map[i + 1][j + 1][2]:
                            area_same_class = area_same_class + 1
                    # 计算与邻居的财富差异总值
                    if (i - 1 >= 0) and (wealth_map[i - 1][j][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i - 1][j][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (i + 1 <= 19) and (wealth_map[i + 1][j][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i + 1][j][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (j - 1 >= 0) and (wealth_map[i][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i][j - 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (j + 1 <= 19) and (wealth_map[i][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i][j + 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (i - 1 >= 0) and (j - 1 >= 0) and (wealth_map[i - 1][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i - 1][j - 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (i + 1 <= 19) and (j - 1 >= 0) and (wealth_map[i + 1][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i + 1][j - 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (i - 1 >= 0) and (j + 1 <= 19) and (wealth_map[i - 1][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i - 1][j + 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1
                    if (i + 1 <= 19) and (j + 1 <= 19) and (wealth_map[i + 1][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(wealth_map[i][j][0]) - float(wealth_map[i + 1][j + 1][0])) < wealth_threshold:
                            area_diff = area_diff + 1

                    # 贫富差距大于阈值
                    if n1 == 0:
                        num_agent_nosat = num_agent_nosat  # 默认一个个体周围都是空位置时，这个个体满意
                    elif (0.6 * area_diff / n1) + (0.4 * area_same_class / n) < race_threshold:
                        # 那么未定居的人数加
                        num_agent_nosat = num_agent_nosat + 1
                        # 记录下当前未定居的节点位置
                        nosat_v.append([i, j])
                        nosat_money.append(wealth_map[i][j][0])
                    # # 种类差距大于阈值
                    # if n == 0:
                    #     num_agent_nosat = num_agent_nosat    # 默认一个个体周围都是空位置时，这个个体满意
                    # elif ((area_same_class / n) < thd_class):
                    #     # 那么未定居的人数加
                    #     num_agent_nosat = num_agent_nosat + 1
                    #     # 记录下当前未定居的节点位置
                    #     nosat_v.append([i, j])
                    #     nosat_money.append(wealth_map[i][j][0])
                    # 财富不满足or种类不满足
                    # if n1 == 0:
                    #     num_agent_nosat = num_agent_nosat    # 默认一个个体周围都是空位置时，这个个体满意
                    # elif (area_diff / n1) > thd or (area_same_class / n) < thd_class:
                    #     # 那么未定居的人数加
                    #     num_agent_nosat = num_agent_nosat + 1
                    #     # 记录下当前未定居的节点位置
                    #     nosat_v.append([i, j])
                    #     nosat_money.append(wealth_map[i][j][0])

        # 不满意率
        if times % 1000 == 0:
            print('不满意率:' + str(num_agent_nosat / 300.0 * 100) + '%')
            unsatisfied.append((num_agent_nosat / 300.0 * 100))
            # 计算总财富
            var1 = []
            final_sum = 0
            for i in range(20):
                for j in range(20):
                    final_sum = wealth_map[i][j][0] + final_sum
                    if wealth_map[i][j][0] != 0:
                        var1.append(wealth_map[i][j][0])
            print(final_sum)
        # print('方差： ', np.var(var1))

        # --------搬家---------
        for i in range(20):
            for j in range(20):
                if wealth_map[i][j][0] == 0:
                    empty_v.append([i, j])
        # print(num_agent_nosat, len(nosat_v))
        if times % 1 == 0 and len(nosat_v) >= 1:
            # 原地搅乱顺序,随机搬家
            for agent_a in range(num_agent_nosat):
                while (1):
                    agent_b = random.randint(0, len(nosat_v) - 1)
                    if (agent_a != agent_b):
                        break
                temp_a_0 = wealth_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][0]
                temp_a_1 = wealth_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][1]
                temp_a_2 = wealth_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][2]
                temp_b_0 = wealth_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][0]
                temp_b_1 = wealth_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][1]
                temp_b_2 = wealth_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][2]
                wealth_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]] = [temp_b_0, temp_b_1, temp_b_2]
                wealth_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]] = [temp_a_0, temp_a_1, temp_a_2]
                temp1_a_0 = race_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][0]
                temp1_a_1 = race_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][1]
                temp1_a_2 = race_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]][2]
                temp1_b_0 = race_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][0]
                temp1_b_1 = race_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][1]
                temp1_b_2 = race_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]][2]
                race_map[nosat_v[agent_a][0]][nosat_v[agent_a][1]] = [temp1_b_0, temp1_b_1, temp1_b_2]
                race_map[nosat_v[agent_b][0]][nosat_v[agent_b][1]] = [temp1_a_0, temp1_a_1, temp1_a_2]

        # 财富交换
        if times % 1000 == 0:
            for t in range(10):
                while (1):
                    agent_i0 = random.randint(0, 19)
                    agent_j0 = random.randint(0, 19)
                    if wealth_map[agent_i0][agent_j0][2] == 0:
                        break
                while (1):
                    agent_i1 = agent_i0 + random.randint(-1, 1)
                    agent_j1 = agent_j0 + random.randint(-1, 1)
                    if ((agent_i1 >= 0 and agent_i1 <= 19) and (agent_j1 >= 0 and agent_j1 <= 19)):
                        if (wealth_map[agent_i1][agent_j1][2] == 0) and (agent_i0 != agent_i1 or agent_j0 != agent_j1):
                            break
                money_a = wealth_map[agent_i0][agent_j0][0]
                money_b = wealth_map[agent_i1][agent_j1][0]
                wealth_map[agent_i0][agent_j0][0] = save * money_a + exchange * (1 - save) * (money_a + money_b)
                wealth_map[agent_i1][agent_j1][0] = (save * money_b) + (1 - exchange) * (1 - save) * (money_a + money_b)
        if times % 1000 == 0:
            for t in range(10):
                while (1):
                    agent_i0 = random.randint(0, 19)
                    agent_j0 = random.randint(0, 19)
                    if wealth_map[agent_i0][agent_j0][2] == 0:
                        break
                while (1):
                    agent_i1 = random.randint(0, 19)
                    agent_j1 = random.randint(0, 19)
                    if (wealth_map[agent_i1][agent_j1][2] == 0) and (agent_i0 != agent_i1 or agent_j0 != agent_j1):
                        break
                money_a = wealth_map[agent_i0][agent_j0][0]
                money_b = wealth_map[agent_i1][agent_j1][0]
                wealth_map[agent_i0][agent_j0][0] = save * money_a + exchange * (1 - save) * (money_a + money_b)
                wealth_map[agent_i1][agent_j1][0] = (save * money_b) + (1 - exchange) * (1 - save) * (money_a + money_b)
        # if times % 10 == 0:
        #     plt.cla()
        #     plt.ioff()
        #     plt.axis("off")
        #     plt.imshow(wealth_map, interpolation="nearest")
        #     plt.show()

        final_sum = 0
        for i in range(20):
            for j in range(20):
                final_sum = wealth_map[i][j][0] + final_sum
        # print("******", final_sum)


def writeExcel():
    workbook = xlsxwriter.Workbook('wealth_Result.xlsx')
    worksheet = workbook.add_worksheet('wealth_Matrix')
    for i in range(20):
        for j in range(20):
            worksheet.write(i, j, wealth_map[i][j][0])
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
    Wealth_Result = xlrd.open_workbook('wealth_Result.xlsx')
    Weight_Matrix = xlrd.open_workbook('Weight_Matrix.xlsx')
    n = 20 * 20
    S0 = 0
    average = 0.0
    numerator = 0.0
    denominator = 0.0
    mode = int(input('0:Treasure  1:Races'))
    table1 = Wealth_Result.sheets()[mode]

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
    Wealth_Result = xlrd.open_workbook('wealth_Result.xlsx')
    table1 = Wealth_Result.sheets()[1]
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


if __name__ == '__main__':
    initial()
    draw_wealth_map('Initial wealth distribution')
    draw_race_map('Initial race distribution')
    move(10000)
    writeExcel()
    Weight_Matrix()
    normalization()
    draw_wealth_map('Final wealth distribution')

    draw_race_map('Final race distribution')


    Moran()
