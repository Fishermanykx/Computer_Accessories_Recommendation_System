'''
Description:
Author: Fishermanykx
Date: 2020-12-16 22:27:37
LastEditors: Fishermanykx
LastEditTime: 2020-12-17 02:23:28
'''
import codecs
import pandas as pd

with codecs.open('result.txt', 'r', 'utf-8') as f:
  res = f.read()
  res = eval(res)
  print(len(res))

url_indexs = [1, 2, 21, 6, 5, 8, 3]
key_in_consideration = ['CPU', '主板', '内存',
                        '硬盘', '固态硬盘', '显卡', '机箱', '电源', '散热器']
categories = [
    '经济实惠型', '家用学习型', '网吧游戏型', '商务办公型', '疯狂游戏型', '图形音像型', '豪华发烧型'
]
writer = pd.ExcelWriter('result.xlsx')

for i in range(1, 8):
  data = res[url_indexs[i-1]]
  # 重新洗一遍数据
  new_dict = {}

  for item in data:
    for key in item:
      if key not in key_in_consideration:
        continue
      if key not in new_dict:
        new_dict[key] = [item[key]['percentage']]
      else:
        new_dict[key].append(item[key]['percentage'])
    if 'Info' not in new_dict:
      new_dict['Info'] = [str(item)]
    else:
      new_dict['Info'].append(str(item))

  new_list = [new_dict]
  df = pd.DataFrame.from_dict(new_dict, orient='index').T

  # print(df)

  df.to_excel(writer, sheet_name=categories[i-1], index=False)
writer.save()
