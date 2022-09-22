#   说明：
#   1 移动策略：逐个选取不满意的个体与空位置进行重排；
#   2 财富交换策略：个体随机挑选任意个体进行财富交换；
#coding=utf-8
from operator import truediv
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import importlib
import sys
import xlsxwriter
importlib.reload(sys)
# 打开交互模式，好让我画动态图
plt.ion()
plt.figure()
vector = list(range(400))    # 20*20
# 原地搅乱序列vector
random.shuffle(vector)  #打乱地图 同随机填入agent
agent1 = vector[0:150]
agent2 = vector[150:300]
empty = vector[300:400]
# 创建一个三维数组，以0填充，第一维62，第二维62，第三维3
tmap = np.zeros((20, 20, 3))  # 财富
tmap1 = np.zeros((20, 20, 3))  # 种族
# 创建数组，记录每一轮不满意比率
Unsatisfied = []
num_sa = []
# init
sum_money = 0.0
save = 0.5
exchange = 0.4

# 财富赋值 and 种族赋值
for i in range(400):
    if i in agent1:
        rnd = random.uniform(30.0, 20.0)    #随机分配agent1财富 20-30
        tmap[i // 20][i % 20] = [rnd, 0, 0]
        tmap1[i // 20][i % 20] = [0, 0, 1]
        sum_money = sum_money + rnd
    if i in agent2:
        rnd = random.uniform(30.0, 20.0)    #随机分配agent2财富 20-30
        tmap[i // 20][i % 20] = [rnd, 0, 0]
        tmap1[i // 20][i % 20] = [1, 165 / 255, 0]
        sum_money = sum_money + rnd
    elif i in empty:
        tmap[i // 20][i % 20] = [0.0, 0, 1]
        tmap1[i // 20][i % 20] = [1, 1, 1]
print(sum_money)

# 初始图像
plt.cla()
plt.ioff()
plt.axis("off")
plt.imshow(tmap, interpolation="nearest")
plt.show()

plt.cla()
plt.ioff()
plt.axis("off")
plt.imshow(tmap1, interpolation="nearest")
plt.show()


for a in range(1):
    thd = 6   # 阈值
    thd_class = 0.79   # 种类阈值
    num_agent_nosat = 1    # 存在不满意的个体
    times = 0
    # 如果有节点不满意，那么就搬家，同时总循环次数小于2000次
    while num_agent_nosat and times < 50000:
        if times % 100 == 0:    #每100次打印一次
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
                if(tmap[i][j][2] != 1): #非空节点
                    # 居住个数
                    n = 0.0
                    n1 = 0.0
                    area_same_class = 0    # 与邻居的种类差异个数
                    area_diff = 0    # 与邻居的财富差异

                    # 计算与邻居的种类差异
                    if (i - 1 >= 0) and (tmap[i - 1][j][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i - 1][j][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (tmap[i + 1][j][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i + 1][j][2]:
                            area_same_class = area_same_class + 1
                    if (j - 1 >= 0) and (tmap[i][j - 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (j + 1 <= 19) and (tmap[i][j + 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i][j + 1][2]:
                            area_same_class = area_same_class + 1
                    if (i - 1 >= 0) and (j - 1 >= 0) and (tmap[i - 1][j - 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i - 1][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (j - 1 >= 0) and (tmap[i + 1][j - 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i + 1][j - 1][2]:
                            area_same_class = area_same_class + 1
                    if (i - 1 >= 0) and (j + 1 <= 19) and (tmap[i - 1][j + 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i - 1][j + 1][2]:
                            area_same_class = area_same_class + 1
                    if (i + 1 <= 19) and (j + 1 <= 19) and (tmap[i + 1][j + 1][0] != 0):
                        n = n + 1
                        if tmap1[i][j][2] == tmap1[i + 1][j + 1][2]:
                            area_same_class = area_same_class + 1
                    # 计算与邻居的财富差异总值
                    if(i - 1 >= 0) and (tmap[i - 1][j][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i - 1][j][0])) < thd:
                            area_diff = area_diff + 1
                    if(i + 1 <= 19) and (tmap[i + 1][j][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i + 1][j][0])) < thd:
                            area_diff = area_diff + 1
                    if(j - 1 >= 0) and (tmap[i][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i][j - 1][0])) < thd:
                            area_diff = area_diff + 1
                    if(j + 1 <= 19) and (tmap[i][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i][j + 1][0])) < thd:
                            area_diff = area_diff + 1
                    if (i - 1 >= 0) and (j - 1 >= 0) and (tmap[i - 1][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i - 1][j - 1][0])) < thd:
                            area_diff = area_diff + 1
                    if (i + 1 <= 19) and (j - 1 >= 0) and (tmap[i + 1][j - 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i + 1][j - 1][0])) < thd:
                            area_diff = area_diff + 1
                    if (i - 1 >= 0) and (j + 1 <= 19) and (tmap[i - 1][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i - 1][j + 1][0])) < thd:
                            area_diff = area_diff + 1
                    if (i + 1 <= 19) and (j + 1 <= 19) and (tmap[i + 1][j + 1][0] != 0):
                        n1 = n1 + 1
                        if abs(float(tmap[i][j][0]) - float(tmap[i + 1][j + 1][0])) < thd:
                            area_diff = area_diff + 1

                    # 贫富差距大于阈值
                    if n1 == 0:
                        num_agent_nosat = num_agent_nosat    # 默认一个个体周围都是空位置时，这个个体满意
                    elif (0.6 * area_diff / n1) + (0.4 * area_same_class / n) < thd_class:
                        # 那么未定居的人数加
                        num_agent_nosat = num_agent_nosat + 1
                        # 记录下当前未定居的节点位置
                        nosat_v.append([i, j])
                        nosat_money.append(tmap[i][j][0])
                    # # 种类差距大于阈值
                    # if n == 0:
                    #     num_agent_nosat = num_agent_nosat    # 默认一个个体周围都是空位置时，这个个体满意
                    # elif ((area_same_class / n) < thd_class):
                    #     # 那么未定居的人数加
                    #     num_agent_nosat = num_agent_nosat + 1
                    #     # 记录下当前未定居的节点位置
                    #     nosat_v.append([i, j])
                    #     nosat_money.append(tmap[i][j][0])
                    # 财富不满足or种类不满足
                    # if n1 == 0:
                    #     num_agent_nosat = num_agent_nosat    # 默认一个个体周围都是空位置时，这个个体满意
                    # elif (area_diff / n1) > thd or (area_same_class / n) < thd_class:
                    #     # 那么未定居的人数加
                    #     num_agent_nosat = num_agent_nosat + 1
                    #     # 记录下当前未定居的节点位置
                    #     nosat_v.append([i, j])
                    #     nosat_money.append(tmap[i][j][0])

        # 不满意率
        if times % 1000 == 0:
            num_sa.append(num_agent_nosat)
            print('不满意率:' + str(num_agent_nosat / 300.0 * 100) + '%')
            Unsatisfied.append((num_agent_nosat / 300.0 * 100))
            # 计算总财富
            var1 = []
            final_sum = 0
            for i in range(20):
                for j in range(20):
                    final_sum = tmap[i][j][0] + final_sum
                    if tmap[i][j][0] != 0:
                        var1.append(tmap[i][j][0])
            print(final_sum)
        # print('方差： ', np.var(var1))

        # --------搬家---------
        for i in range(20):
            for j in range(20):
                if (tmap[i][j][0] == 0):
                    empty_v.append([i, j])
        # print(num_agent_nosat, len(nosat_v))
        if times % 1 == 0 and len(nosat_v) >= 1:
            # 原地搅乱顺序,随机搬家
            for agent_a in range(num_agent_nosat):
                while (1):
                    agent_b = random.randint(0, len(nosat_v) - 1)
                    if (agent_a != agent_b):
                        break
                temp_a_0 = tmap[nosat_v[agent_a][0]][nosat_v[agent_a][1]][0]
                temp_a_1 = tmap[nosat_v[agent_a][0]][nosat_v[agent_a][1]][1]
                temp_a_2 = tmap[nosat_v[agent_a][0]][nosat_v[agent_a][1]][2]
                temp_b_0 = tmap[nosat_v[agent_b][0]][nosat_v[agent_b][1]][0]
                temp_b_1 = tmap[nosat_v[agent_b][0]][nosat_v[agent_b][1]][1]
                temp_b_2 = tmap[nosat_v[agent_b][0]][nosat_v[agent_b][1]][2]
                tmap[nosat_v[agent_a][0]][nosat_v[agent_a][1]] = [temp_b_0, temp_b_1, temp_b_2]
                tmap[nosat_v[agent_b][0]][nosat_v[agent_b][1]] = [temp_a_0, temp_a_1, temp_a_2]
                temp1_a_0 = tmap1[nosat_v[agent_a][0]][nosat_v[agent_a][1]][0]
                temp1_a_1 = tmap1[nosat_v[agent_a][0]][nosat_v[agent_a][1]][1]
                temp1_a_2 = tmap1[nosat_v[agent_a][0]][nosat_v[agent_a][1]][2]
                temp1_b_0 = tmap1[nosat_v[agent_b][0]][nosat_v[agent_b][1]][0]
                temp1_b_1 = tmap1[nosat_v[agent_b][0]][nosat_v[agent_b][1]][1]
                temp1_b_2 = tmap1[nosat_v[agent_b][0]][nosat_v[agent_b][1]][2]
                tmap1[nosat_v[agent_a][0]][nosat_v[agent_a][1]] = [temp1_b_0, temp1_b_1, temp1_b_2]
                tmap1[nosat_v[agent_b][0]][nosat_v[agent_b][1]] = [temp1_a_0, temp1_a_1, temp1_a_2]

        # 财富交换
        if times % 1000 == 0:
            for t in range(10):
                while (1):
                    agent_i0 = random.randint(0, 19)
                    agent_j0 = random.randint(0, 19)
                    if tmap[agent_i0][agent_j0][2] == 0:
                        break
                while (1):
                    agent_i1 = agent_i0 + random.randint(-1,1)
                    agent_j1 = agent_j0 + random.randint(-1,1)
                    if ((agent_i1 >= 0 and agent_i1 <= 19) and (agent_j1 >=0 and agent_j1 <= 19)):
                        if(tmap[agent_i1][agent_j1][2] == 0) and (agent_i0 != agent_i1 or agent_j0 != agent_j1):
                            break
                money_a = tmap[agent_i0][agent_j0][0]
                money_b = tmap[agent_i1][agent_j1][0]
                tmap[agent_i0][agent_j0][0] = save * money_a + exchange * (1 - save) * (money_a + money_b)
                tmap[agent_i1][agent_j1][0] = (save * money_b) + (1 - exchange) * (1 - save) * (money_a + money_b)

        # if times % 10 == 0:
        #     plt.cla()
        #     plt.ioff()
        #     plt.axis("off")
        #     plt.imshow(tmap, interpolation="nearest")
        #     plt.show()

        final_sum = 0
        for i in range(20):
            for j in range(20):
                final_sum = tmap[i][j][0] + final_sum
        # print("******", final_sum)


min = -10000
max = 0.0
for i in range(20):
    for j in range(20):
        if tmap[i][j][2] == 0:
            if tmap[i][j][0] > max:
                max = tmap[i][j][0]
            if tmap[i][j][0] < max:
                min = tmap[i][j][0]
for i in range(20):
    for j in range(20):
        if tmap[i][j][2] == 0:
            # tmap[i][j][0] = (0.8 * (tmap[i][j][0] - min)/(max - min) + 0.2)
            tmap[i][j][0] = tmap[i][j][0]/max
plt.cla()
plt.ioff()
plt.axis("off")
plt.imshow(tmap, interpolation="nearest")
plt.show()

plt.cla()
plt.ioff()
plt.axis("off")
plt.imshow(tmap1, interpolation="nearest")
plt.show()

# plt.imshow(Unsatisfied, interpolation="nearest")
plt.plot([i for i in range(len(Unsatisfied))], Unsatisfied, '-')
plt.show()



# output = open('满意度.xls', 'w', encoding='gbk')
# for j in range(len(num_sa)):
#     output.write(str(num_sa[j]))  # write函数不能写int类型的参数，所以使用str()转化
#     output.write('\t')  # 相当于Tab一下，换一个单元格
# output.close()
# print(num_sa)
workbook = xlsxwriter.Workbook('tmap_Result.xlsx')
worksheet = workbook.add_worksheet('sheet1')
for i in range(20):
    for j in range(20):
        worksheet.write(i, j, tmap[i][j][0])
worksheet = workbook.add_worksheet('sheet2')
for i in range(20):
    for j in range(20):
        if tmap1[i][j][1] == 0:
            worksheet.write(i, j, 1)
        elif tmap1[i][j][1] == 1:
            worksheet.write(i, j, 0)
        else:
            worksheet.write(i, j, -1)
workbook.close()