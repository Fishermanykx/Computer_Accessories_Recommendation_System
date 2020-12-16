'''
Description: 
Author: Fishermanykx
Date: 2020-12-06 18:08:34
LastEditors: Fishermanykx
LastEditTime: 2020-12-11 22:32:09
'''

import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import numpy as np
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']


motherboard = [52, 51, 26, 22, 23, 23, 18,
               15, 14, 9, 8, 7, 10, 9, 6, 8, 2, 3, 7, 2]
video_card = [36, 46, 39, 24, 18, 15, 12,
              14, 3, 4, 3, 4, 1, 8, 3, 7, 2, 0, 6, 1]
ssd = [50, 52, 47, 50, 36, 36, 31, 26, 18, 22, 15, 16, 20, 9, 17, 13, 7, 4, 10, 6, 7,
       6, 2, 6, 2, 7, 3, 4, 1, 5, 0, 6, 4, 1, 5, 4, 0, 3, 4, 2, 3, 2, 1, 2, 1, 0, 3, 2, 0, 0]
board_u_suit = [38, 31, 32, 28, 31, 28, 30, 31, 31, 29, 25, 22, 17, 24, 15, 20, 21,
                22, 15, 16, 13, 17, 12, 11, 8, 10, 9, 10, 15, 15, 9, 12, 9, 15, 12, 6, 11, 11, 3, 6]
case_fan = [50, 55, 57, 52, 48, 38, 20, 19, 6, 6, 4, 3, 0, 1, 1, 1, 7, 0, 0, 0]
computer_case = [51, 48, 47, 47, 42, 45, 45, 40, 42, 35, 27, 28, 24, 22, 20,
                 15, 10, 14, 7, 9, 6, 8, 9, 9, 7, 5, 6, 8, 7, 3, 5, 6, 8, 5, 3, 1, 1, 1, 0, 0]
cpu_radiator = [51, 49, 44, 44, 37, 36, 26,
                26, 18, 13, 14, 6, 9, 8, 2, 2, 5, 1, 3, 2]
memory = [48, 53, 45, 40, 27, 23, 19, 25, 18,
          13, 11, 9, 13, 10, 15, 11, 13, 13, 12, 5]
hdd = [52, 39, 23, 16, 11, 9, 4, 5, 6, 5, 4, 4, 1, 4, 4, 1, 4, 2, 0, 0]
power_supply = [51, 49, 46, 45, 37, 41, 38, 36, 28, 28, 21, 21,
                21, 12, 12, 11, 8, 7, 8, 7, 7, 8, 4, 8, 1, 1, 3, 0, 0, 3]
# y = np.array(motherboard)
# y = np.array(video_card)
y = np.array(power_supply)
# y = np.array(ssd)
# y = np.array(computer_case)
# y = np.array(cpu_radiator)
# y = np.array(memory)
# y = np.array(hdd)
x = np.arange(len(y), dtype=int)
x = x + 1
# print(x)

plt.grid(True)
plt.plot(x, y, '-o')
# 图像设置
# plt.title("Board-U Suit")
# plt.title("Computer Case")
# plt.title("Case Fan")
# plt.title("CPU Radiator")
# plt.title("Memory")
# plt.title("HDD")
# plt.title("Video Card")
plt.title("Power Supply")
# plt.title("SSD")
# plt.title("Motherboard")
plt.xlabel("页数")
plt.ylabel("京东自营商品数(max=60)")

# 把x轴的刻度间隔设置为1，并存在变量里
x_major_locator = MultipleLocator(1)
# 把y轴的刻度间隔设置为1，并存在变量里
y_major_locator = MultipleLocator(1)

# ax为两条坐标轴的实例
ax = plt.gca()
# 把x轴的主刻度设置为1的倍数
ax.xaxis.set_major_locator(x_major_locator)
# 把y轴的主刻度设置为10的倍数
ax.yaxis.set_major_locator(y_major_locator)
# 把x轴的刻度范围设置为0到11，因为0.5不满一个刻度间隔，所以数字不会显示出来，但是能看到一点空白
plt.xlim(0, len(x)+1)
# 把y轴的刻度范围设置为0到60
plt.ylim(0, 60)

plt.show()
