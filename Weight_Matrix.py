import numpy as np
import xlsxwriter
import xlrd

tmap_Result = xlrd.open_workbook('tmap_Result.xlsx')
table1 = tmap_Result.sheets()[1]
weight_matrix = np.zeros((400, 400))

workbook = xlsxwriter.Workbook('Weight_Matrix.xlsx')
worksheet = workbook.add_worksheet('sheet1')
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
