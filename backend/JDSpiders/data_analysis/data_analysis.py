'''
Description: 
Author: Fishermanykx
Date: 2020-12-06 18:08:34
LastEditors: Fishermanykx
LastEditTime: 2020-12-08 10:45:49
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
y = np.array(motherboard)
# y = np.array(video_card)
# y = np.array(ssd)
x = np.arange(len(y), dtype=int)
x = x + 1
y = y / 60
# print(x)

plt.grid(True)
plt.plot(x, y, '-o')
# 图像设置
plt.title("Motherboard")
# plt.title("Video Card")
# plt.title("SSD")
plt.xlabel("页数")
plt.ylabel("京东自营商品比例")

# 把x轴的刻度间隔设置为1，并存在变量里
x_major_locator = MultipleLocator(1)
# 把y轴的刻度间隔设置为0.05，并存在变量里
y_major_locator = MultipleLocator(0.05)

# ax为两条坐标轴的实例
ax = plt.gca()
# 把x轴的主刻度设置为1的倍数
ax.xaxis.set_major_locator(x_major_locator)
# 把y轴的主刻度设置为10的倍数
ax.yaxis.set_major_locator(y_major_locator)
# 把x轴的刻度范围设置为0到11，因为0.5不满一个刻度间隔，所以数字不会显示出来，但是能看到一点空白
plt.xlim(0, len(x)+1)
# 把y轴的刻度范围设置为0到60
plt.ylim(0, 1)

plt.show()
