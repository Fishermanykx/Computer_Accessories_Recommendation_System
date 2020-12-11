'''
Description: 
Author: Fishermanykx
Date: 2020-12-11 16:18:16
LastEditors: Fishermanykx
LastEditTime: 2020-12-11 16:25:24
'''

import re
s = "\n 技嘉（GIGABYTE）X570 AORUS PRO WIFI 主板+ AMD 锐龙 9 3900X 板U套装/主板+CPU套装   \n"
s = s.strip().split('+')
board = s[0]
s2 = s[1]
index = s2.rfind("板U套装")
s2 = s2[:index].strip()
print(s2)