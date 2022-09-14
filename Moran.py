import xlrd


tmap_Result = xlrd.open_workbook('tmap_Result.xlsx')
Weight_Matrix = xlrd.open_workbook('Weight_Matrix.xlsx')
n = 20*20
S0 = 0
average = 0.0
numerator = 0.0
denominator = 0.0
mode = int(input('0:Treasure  1:Races'))
table1 = tmap_Result.sheets()[mode]

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
        denominator = denominator + (float(table1.cell_value(rowx=i, colx=j)) - average)*(float(table1.cell_value(rowx=i, colx=j)) - average)
        list.append(float(table1.cell_value(rowx=i, colx=j)))


for i in range(400):
    for j in range(400):
        if (int(table2.cell_value(rowx=i, colx=j)) == 1):
            numerator = numerator + (list[i] - average) * (list[j] - average)

print((n/S0)*(numerator/denominator))

