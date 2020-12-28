'''
Description:
Author: Fishermanykx
Date: 2020-12-21 12:08:22
LastEditors: Fishermanykx
LastEditTime: 2020-12-28 12:07:42
'''
import re
import pymysql

MYSQL_HOSTS = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = "08239015"
MYSQL_PORT = 3306
MYSQL_DB = "test"
# MYSQL_DB = "computer_accessories"


class DataCleaning:
  def __init__(self, accessory_type):
    self.accessory_type = accessory_type

  def washComments(self, comment_num, praise_rate):
    # 清洗好评率
    praise_rate = int(praise_rate[:-1])
    # 清洗评论数
    pat = r'\d*(\.)?\d*'
    base = 1
    try:
      if '万' in comment_num:
        base *= 10**4
      res = re.match(pat, comment_num)
      comment_num = eval(res.group()) * base
    except:
      comment_num = 100
    return int(comment_num), praise_rate

  def handleSingleCPURecrod(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # TDP
    record['TDP'] = int(p_table['规格']['功率'][:-1])
    # 处理接口
    socket = introd["接口"]
    if "1151" in socket:
      socket = "INTEL LGA1151"
    elif "其他" in socket:
      socket = "INTEL LGA1151"
    record["socket"] = socket
    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanCPU(self):
    '''
    description: 清洗 CPU 数据
    '''
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 增加列
    add_col = "alter table cpu add column TDP int NOT NULL default 0 AFTER core_num "
    cursor.execute(add_col)
    add_col = "alter table cpu add column socket VARCHAR(255) default NULL AFTER TDP"
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    for i in range(data_len):
      # 逐条数据处理
      data[i] = self.handleSingleCPURecrod(data[i])

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO cpu (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, clock_speed, core_num, TDP, socket, have_core_graphics_card, have_cpu_fan, introduction, "\
        "Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, "\
        "%(link)s, %(brand)s, %(tags)s, %(clock_speed)s, %(core_num)s, %(TDP)s, %(socket)s, "\
        "%(have_core_graphics_card)s, %(have_cpu_fan)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, data)

    connection.commit()

  def washBrand(self, brand):
    if "Intel" in brand:
      return "INTEL"
    elif 'AMD' in brand:
      return "AMD"

    index = brand.find('（')
    if brand == 'Thermaltake（Tt）':
      return "TT"

    if index != -1:
      brand = brand[:index]
    else:
      # Special cases
      if brand == 'Crucial':
        brand = '英睿达'
      elif brand == 'HP':
        brand = '惠普'
      elif brand == 'uFound':
        brand = '方正'
      elif brand == 'pioneer':
        brand = '先锋'
      elif brand == 'HIKVISION':
        brand = '海康威视'
      elif brand == 'dahua':
        brand = '大华'
      elif brand == 'SEASONIC':
        brand = '海韵'
      elif brand == 'SUPER FLOWER':
        brand = '振华'
      elif brand == 'INWIN':
        brand = '迎广'
      elif brand == 'NZXT':
        brand = '恩杰'
      elif brand == 'be quiet':
        brand = '德商必酷'
      elif brand == 'XPG':
        brand = '威刚'
      elif brand == 'LIANLI':
        brand = '联立'
      elif brand == 'BitFenix':
        brand = '火鸟'
      elif brand == 'Fractal Design':
        brand = '分形工艺'
      elif brand == 'METALLICGEAR':
        brand = '普力魔'
      elif brand == 'Thermalright':
        brand = '利民'
      elif brand == 'noctua':
        brand = '猫头鹰'
      elif brand == 'PHANTEKS':
        brand = '追风者'

    # 注意：没被处理的有：EVGA, zero zone(这TM还是家国内公司。。。), ID_COOLING

    return brand

  def handleSingleMotherboardRecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])
    # form_factor 去中文
    s = record['form_factor']
    record['form_factor'] = s[:s.find('（')]
    # platform
    record['platform'] = self.washBrand(record['platform'][:-2])
    # 加入 CPU 接口列
    try:
      ss = introd['适用CPU接口']
      index = ss.find('（')
      if (index != -1):
        ss = ss[:index]
      ss = ss.split("，")[0]
      if ss == 'INTEL1151':
        ss = 'INTEL LGA1151'
      record['cpu_socket'] = ss
    except:
      print(introd)
      exit(1)
    # 加入 m2 接口数 列
    record['m2_num'] = int(introd.get('M.2接口数量', 0))
    # 清洗品牌
    record['brand'] = self.washBrand(record['brand'])
    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])

    return record

  def cleanMotherboard(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 插入 CPU 接口列和 m.2 接口数
    add_col = "alter table " + self.accessory_type + \
        " add column cpu_socket VARCHAR(255) default NULL AFTER platform "
    cursor.execute(add_col)
    add_col = "alter table " + self.accessory_type + \
        " add column m2_num int NOT NULL default 0 AFTER cpu_socket"
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    for i in range(data_len):
      # 逐条数据处理
      # 判定是否为板-U套装
      record = data[i]
      if record['comment_num'] == '100':  # 抓到板-U套装了
        continue
      if '板U套装' in record['name']:
        continue
      # 清洗数据
      new_data.append(self.handleSingleMotherboardRecord(record))

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table motherboard modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table motherboard modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO motherboard (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, form_factor, platform, cpu_socket, m2_num, introduction, Ptable_params) VALUES (%(id)s, %(name)s,"\
        " %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(form_factor)s, "\
        "%(platform)s, %(cpu_socket)s, %(m2_num)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def handleSingleGraphicsCard(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 显卡类别
    amd = introd.get('AMD芯片', "其他")
    nv = introd.get('NVIDIA芯片', "其他")
    if nv == '其他':
      record['card_type'] = 'AMD'
    else:
      record['card_type'] = 'NVIDIA'
    # 修正卡长
    record['card_length'] = eval(record['card_length'])
    # 修正 RGB 列
    rgb = record['rgb']
    if rgb == '单色':
      record['rgb'] = '支持RGB'
    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanGraphicsCard(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 插入 显卡类别列 (AMD/NVIDIA)
    add_col = "alter table " + self.accessory_type + \
        " add column card_type VARCHAR(255) default NULL AFTER rgb "
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      # 清洗数据
      data[i] = self.handleSingleGraphicsCard(record)

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type + \
        " modify card_length float default 0.0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO video_card (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, card_length, rgb, card_type, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(card_length)s, "\
        "%(rgb)s, %(card_type)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, data)

    connection.commit()

  def handleSingleCPURadiator(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 散热器高度
    try:
      h = p_table['规格']['散热器高度']
      h = int(h[:-2])
    except:
      h = 0
    record['height'] = h

    # 冷排大小
    cooling_size = introd.get('水冷类型', '0风冷')
    cooling_size = cooling_size[:-2]
    try:
      record['radiator_size'] = int(cooling_size)
    except:
      record['radiator_size'] = 0

    # RGB
    rgb = introd.get('发光类型', '无')
    if '无' in rgb:
      rgb = '无'
    elif 'RGB' not in rgb:
      rgb = 'RGB'
    record['rgb'] = rgb

    # 兼容接口
    try:
      socket_str = introd.get('兼容接口', "")
      socket_str = socket_str.split('，')
      res_socket = ""
      for item in socket_str:
        index = item.find('（')
        if index != -1:
          item = item[:index]
        item = item.strip()
        if item == "INTEL1151":
          item = 'INTEL LGA1151'
        res_socket += item
        res_socket += '~'
      res_socket = res_socket[:-1]
    except:
      print(record)
      exit(1)
    record['socket'] = res_socket

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanCPURadiator(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 插入 散热器高度 (mm)
    add_col = "alter table " + self.accessory_type + \
        " add column height int default NULL AFTER brand "
    cursor.execute(add_col)
    # 插入 兼容接口 列
    add_col = "alter table " + self.accessory_type + \
        " add column socket VARCHAR(255) default NULL AFTER height "
    cursor.execute(add_col)
    # 插入 冷排 列
    add_col = "alter table " + self.accessory_type + \
        " add column radiator_size int default NULL AFTER socket "
    cursor.execute(add_col)
    # 插入 RGB 列
    add_col = "alter table " + self.accessory_type + \
        " add column rgb VARCHAR(255) default NULL AFTER radiator_size "
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      # 清洗数据
      data[i] = self.handleSingleCPURadiator(record)

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数

    # 重新写入
    sql_insert = "INSERT INTO cpu_radiator (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, height, socket, radiator_size, rgb, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(height)s, %(socket)s, "\
        "%(radiator_size)s, %(rgb)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, data)

    connection.commit()

  def handleSingleCase(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 最大板型
    boards = introd.get('支持主板', '')
    if boards:
      boards = boards.split('，')[0]
      boards = boards[:boards.find('（')]
    record['max_form_factor'] = boards

    # 最大卡长
    max_l = p_table['规格'].get('显卡（连供电头总长度）限长', 0)
    if max_l:
      max_l = int(max_l[1:-2])
    record['max_card_len'] = max_l

    # 散热器限高
    max_h = p_table['规格'].get('CPU散热器限高', 0)
    if max_h:
      pat = r'\d*'
      max_h = re.match(pat, max_h).group()
    record['max_radiator_height'] = int(max_h)

    # 支持的冷排
    sup_rad = introd.get('支持水冷', '0')
    res = sup_rad

    if sup_rad != '0':
      sup_rad = sup_rad.split('，')
      res = ""
      for i in range(len(sup_rad)):
        sup_rad[i] = sup_rad[i][:-2]
        res = res + sup_rad[i] + '~'
      res = res[:-1]
    if res == '不':
      res = '0'
    record["supported_radiator"] = res

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanCase(self):
    # TODO: 侧透
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 插入 最大板型
    add_col = "alter table " + self.accessory_type + \
        " add column max_form_factor VARCHAR(255) default NULL AFTER brand "
    cursor.execute(add_col)
    # 插入 最大显卡长度 列
    add_col = "alter table " + self.accessory_type + \
        " add column max_card_len int default NULL AFTER max_form_factor "
    cursor.execute(add_col)
    # 插入 散热器限高 列
    add_col = "alter table " + self.accessory_type + \
        " add column max_radiator_height int default NULL AFTER max_card_len "
    cursor.execute(add_col)
    # 插入 散热器规格支持 列
    add_col = "alter table " + self.accessory_type + \
        " add column supported_radiator VARCHAR(255) default NULL AFTER max_radiator_height "
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      p_table = eval(record['Ptable_params'])
      max_l = p_table['规格'].get('显卡（连供电头总长度）限长', 0)
      max_h = p_table['规格'].get('CPU散热器限高', 0)
      name = record['name']
      if '套装' in name:
        continue
      # 清洗数据
      if max_h and max_l:
        new_data.append(self.handleSingleCase(record))

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数

    # 重新写入
    sql_insert = "INSERT INTO computer_case (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, max_form_factor, max_card_len, max_radiator_height, supported_radiator, introduction, Ptable_params)"\
        " VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, "\
        "%(max_form_factor)s, %(max_card_len)s, %(max_radiator_height)s, %(supported_radiator)s, %(introduction)s, %(Ptable_params)s)"

    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def handleSingleHDD(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = record['total_capacity']
    dig = capacity[:-2]
    if dig != '12' and dig.isdigit():
      capacity = dig
    else:
      name = record['name']
      pat = r'\d+T|\d+G|\d*\.\d*T'
      res = re.search(pat, name)
      if res:
        res = res.group()
      else:
        res = '0T'
      if res and res[-1] == 'T':
        capacity = round(eval(res[:-1]))
      elif res and res[-1] == 'G':
        capacity = eval(res[:-1]) // 250 * 0.25
      else:
        print("Error in converting capacity")
        print(res)
        print(record)
        exit(1)
    record['total_capacity'] = capacity

    # 清洗 尺寸
    try:
      size = p_table['特性'].get('产品尺寸（mm）', '0x0x0')
    except:
      size = '0x0x0'
    if '×' in size:
      size = size.replace('×', '*')
    if 'x' in size:
      size = size.replace('x', '*')
    if 'X' in size:
      size = size.replace('X', '*')
    new_size = ""
    if len(size) > 9:
      lis = size.split('*')
      pat = r'\d*\.\d*|\d*'
      for item in lis:
        res = re.findall(pat, item)
        res = list(filter(None, res))[0]
        new_size = new_size + (res + '*')
      new_size = new_size[:-1]
    else:
      pat = r'\d*\.\d*|\d*'
      res = re.search(pat, size.strip()).group()
      new_size = res + ' inches'
    record['size'] = new_size

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanHDD(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 插入 尺寸 列
    add_col = "alter table " + self.accessory_type + \
        " add column size VARCHAR(255) default NULL AFTER brand "
    cursor.execute(add_col)

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    for i in range(data_len):
      # 逐条数据处理
      # 判定是否为 SSD
      record = data[i]
      name = record['name']
      if ('SSD' in name) or ('固态' in name):
        continue
      if '笔记本' in name:
        continue
      # 清洗数据
      new_data.append(self.handleSingleHDD(record))

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type + \
        " modify total_capacity float default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO hdd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, size,rotating_speed, total_capacity, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(size)s, %(rotating_speed)s, "\
        "%(total_capacity)s, %(introduction)s, %(Ptable_params)s)"
    for i in range(len(new_data)):
      try:
        cursor.execute(sql_insert, new_data[i])
      except:
        print(new_data[i])
        exit(1)
    # sql_insert = "INSERT INTO hdd (id, name, comment_num, praise_rate, shop_name, price, link,"\
    #     "brand, size,rotating_speed, total_capacity, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
    #     "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(size)s, %(rotating_speed)s, "\
    #     "%(total_capacity)s, %(introduction)s, %(Ptable_params)s)"
    # cursor.executemany(sql_insert, new_data)

    connection.commit()

  def handleSingleSSD(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 清洗接口
    s = record['interface']
    index = s.find('接口')
    record['interface'] = s[:index]

    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = record['total_capacity']
    if capacity == '960GB-1TB':
      capacity = 1.0
    elif capacity == '(480-512)GB':
      capacity = 0.5
    elif capacity == '(240-256)GB':
      capacity = 0.25
    elif capacity == '(120-128)GB':
      capacity = 0.125
    elif capacity == '2TB及以上':
      pat = r'\dT|\d+G|\d\.\d*T'
      res = re.search(pat, capacity)
      if res:
        res = res.group()
      if res and res[-1] == 'T':
        capacity = round(eval(res[:-1]))
      elif res and res[-1] == 'G':
        capacity = eval(res[:-1]) // 250 * 0.25
      else:
        print("Error in converting capacity")
        print(res)
        print(record)
        exit(1)
    else:
      name = record['name']
      pat = r'\dT|\d+G|\d\.\d*T'
      res = re.search(pat, name)
      if res:
        res = res.group()
      else:
        res = '0T'
      if res and res[-1] == 'T':
        capacity = round(eval(res[:-1]))
      elif res and res[-1] == 'G':
        capacity = eval(res[:-1]) // 250 * 0.25
      else:
        print("Error in converting capacity")
        print(res)
        print(record)
        exit(1)
    record['total_capacity'] = capacity

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanSSD(self):
    '''
    description: 清洗 CPU 数据
    '''
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      # 清洗数据
      data[i] = self.handleSingleSSD(record)

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type + \
        " modify total_capacity float default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO ssd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, interface, total_capacity, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(interface)s, "\
        "%(total_capacity)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, data)

    connection.commit()

  def handleSingleMemory(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = record['total_capacity']
    if '及' not in capacity and '没' not in capacity:
      capacity = int(capacity[:-2])
    else:
      pat = r'\d+G'
      name = record['name']
      res = re.search(pat, name)
      if res:
        res = res.group()

      if res and res[-1] == 'G':
        capacity = eval(res[:-1])
      else:
        print("Error in converting capacity")
        print(res)
        print(record)
        exit(1)

    record['total_capacity'] = capacity

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanMemory(self):
    '''
    description: 清洗 内存 数据
    '''
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      name = record['name']
      if '套装' in name:
        continue
      # 清洗数据
      new_data.append(self.handleSingleMemory(record))

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type + \
        " modify total_capacity int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    # 重新写入
    sql_insert = "INSERT INTO memory (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, frequency, total_capacity, memory_num, appearance, ddr_gen, introduction, "\
        "Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s"\
        ", %(link)s, %(brand)s, %(frequency)s, %(total_capacity)s, %(memory_num)s, %(appearance)s, "\
        "%(ddr_gen)s, %(introduction)s, %(Ptable_params)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def handleSinglePow(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 接线类型
    record['modularization'] = introd['接线类型']

    # 清洗 size
    pat = r'[A-Z]+'
    size = record['size']
    res = re.search(pat, size)
    if res:
      size = res.group()
    else:
      print("No size info")
    record['size'] = size

    # 明确功率
    ss = p_table['规格'].get('额定功率', 0)
    if ss:
      record['power'] = int(ss[:-1])
    else:
      record['power'] = ss

    # 清洗评论和好评率
    record['comment_num'], record['praise_rate'] = self.washComments(
        record['comment_num'], record['praise_rate'])
    # 清洗 brand
    record['brand'] = self.washBrand(record['brand'])

    return record

  def cleanPowerSupply(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("drop table " + self.accessory_type)
    cursor.execute(
        "create table test."+self.accessory_type+" as select * from computer_accessories."+self.accessory_type)

    add_col = "alter table "+self.accessory_type + \
        " add column modularization VARCHAR(255) default NULL AFTER size "
    cursor.execute(add_col)

    instruct = "alter table " + self.accessory_type + " modify price int default NULL"
    row = cursor.execute(instruct)  # 返回被影响的行数
    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      size = record['size']
      if size == '无':
        continue
      name = record['name']
      if '套装' in name:
        continue
      # 清洗数据
      new_data.append(self.handleSinglePow(record))

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 将评论数和好评率修改为 int 类型
    instruct = "alter table "+self.accessory_type+" modify comment_num int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify praise_rate int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数
    instruct = "alter table "+self.accessory_type+" modify power int default 0"
    row = cursor.execute(instruct)  # 返回被影响的行数

    # 重新写入
    sql_insert = "INSERT INTO power_supply (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, power, size, modularization, transfer_efficiency, introduction, Ptable_params) VALUES (%(id)s, %(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(power)s, "\
        "%(size)s, %(modularization)s, %(transfer_efficiency)s, %(introduction)s, %(Ptable_params)s)"
    # cursor.executemany(sql_insert, new_data)

    for i in range(len(new_data)):
      try:
        cursor.execute(sql_insert, new_data[i])
      except:
        print(new_data[i])
        exit(1)

    connection.commit()

  def main(self):
    t = self.accessory_type
    if t == 'all':
      self.cleanCPU()
      self.cleanMotherboard()
      self.cleanGraphicsCard()
      self.cleanCPURadiator()
      self.cleanCase()
      self.cleanHDD()
      self.cleanSSD()
      self.cleanMemory()
      self.cleanPowerSupply()
    elif t == 'cpu':
      self.cleanCPU()
    elif t == 'motherboard':
      self.cleanMotherboard()
    elif t == 'video_card':
      self.cleanGraphicsCard()
    elif t == 'cpu_radiator':
      self.cleanCPURadiator()
    elif t == 'computer_case':
      self.cleanCase()
    elif t == 'hdd':
      self.cleanHDD()
    elif t == 'ssd':
      self.cleanSSD()
    elif t == 'memory':
      self.cleanMemory()
    elif t == 'power_supply':
      self.cleanPowerSupply()
    else:
      print(self.accessory_type)
      print("Wrong name!")


if __name__ == "__main__":
  # washer = DataCleaning('power_supply')
  washer = DataCleaning('cpu_radiator')
  # washer = DataCleaning('motherboard')
  washer.main()
