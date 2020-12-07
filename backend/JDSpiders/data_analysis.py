'''
Description: 
Author: Fishermanykx
Date: 2020-12-06 18:08:34
LastEditors: Fishermanykx
LastEditTime: 2020-12-07 11:23:26
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

y = [49, 46, 38, 23, 19, 16, 13, 13, 8, 9]
x = np.arange(len(y), dtype=int)
x = x + 1
# print(x)

plt.grid(True)
plt.plot(x, y)

x_major_locator = MultipleLocator(1)
y_major_locator = MultipleLocator(5)

#ax为两条坐标轴的实例
ax = plt.gca()
#把x轴的主刻度设置为1的倍数
ax.xaxis.set_major_locator(x_major_locator)
#把y轴的主刻度设置为10的倍数
ax.yaxis.set_major_locator(y_major_locator)
#把x轴的刻度范围设置为-0.5到11，因为0.5不满一个刻度间隔，所以数字不会显示出来，但是能看到一点空白
plt.xlim(0, 11)
#把y轴的刻度范围设置为-5到110
plt.ylim(0, 50)

plt.show()