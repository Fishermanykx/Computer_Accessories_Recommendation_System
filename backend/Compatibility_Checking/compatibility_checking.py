'''
Description:
  问卷：json串，键值为 l1, ... , ln
  返回json串 {"flag": 1} 或 {"flag": 0, "errorList": ["xxxxxx", "xxxxxx"]}
Author: Fishermanykx
Date: 2021-01-07 21:31:08
LastEditors: Fishermanykx
LastEditTime: 2021-01-08 02:36:27
'''
import json
import pymysql

from pprint import pprint

MYSQL_HOSTS = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = "08239015"
MYSQL_PORT = 3306
MYSQL_DB = "computer_accessories"


class CompatibilityChecking:
  def __init__(self):
    # 是否成功
    self.flag = 1
    # 读入问卷
    with open("questionnaire.json", 'r', encoding='UTF-8') as f:
      data = json.load(f)
    self.questionnaire = data  # 问卷dict
    # pprint(data['l1'])
    # 数据库指针
    self.db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

  def parseQuestionnaire(self):
    """解析问卷并读入相关配件的参数"""
    accessories = ['cpu', 'motherboard', 'graphics_card', 'memory',
                   'ssd', 'hdd', 'cpu_radiator', 'power_supply', 'computer_case']
    accessories_data = []
    for i in range(len(accessories)):
      query = "select * from " + \
          accessories[i]+" where link = '" + \
          self.questionnaire['l'+str(i+1)] + "'"
      self.cursor.execute(query)
      tmp_data = self.cursor.fetchone()

      # 若不存在该商品，报错
      if not tmp_data:
        return [False, self.questionnaire['l'+str(i+1)]]

      accessories_data.append(tmp_data)

    self.cpu = accessories_data[0]
    self.motherboard = accessories_data[1]
    self.graphics_card = accessories_data[2]
    self.memory = accessories_data[3]
    self.ssd = accessories_data[4]
    self.hdd = accessories_data[5]
    self.cpu_radiator = accessories_data[6]
    self.power_supply = accessories_data[7]
    self.computer_case = accessories_data[8]
    # pprint(self.cpu)
    return [True]

  def check(self):
    """检测兼容性，若成功，返回[True]；否则返回[False, errorList]"""
    errorList = []

    # 检测 CPU 和 主板 的接口是否一致
    cpu_socket = self.cpu['socket']
    MB_socket = self.motherboard['cpu_socket']
    if cpu_socket != MB_socket:
      error = "主板与CPU接口不匹配"
      errorList.append(error)

    # 检测散热器接口是否与CPU一致
    radiator_sockets = self.cpu_radiator['socket']
    if cpu_socket not in radiator_sockets:
      error = "散热器支持接口与CPU接口不匹配"
      errorList.append(error)

    # 检测内存代数与主板是否匹配
    MB_ddr_gen = self.motherboard['ddr_gen']
    memory_ddr_gen = self.memory['ddr_gen']
    if MB_ddr_gen != memory_ddr_gen:
      error = "主板支持内存的代数与所选内存不匹配"
      errorList.append(error)

    # 机箱相关

    # 显卡长度
    card_len = self.graphics_card['card_length']
    max_card_len = self.computer_case['max_card_len']
    if card_len > max_card_len:
      error = "所选显卡长度大于所选机箱允许的最大卡长"
      errorList.append(error)

    # 主板大小
    max_form_factor = self.computer_case['max_form_factor']
    form_factor = self.motherboard['form_factor']
    fit = 1
    if max_form_factor == "MINI-ITX":
      if form_factor != "MINI-ITX":
        fit = 0
    elif max_form_factor == "M-ATX":
      if (form_factor == "ATX") or (form_factor == "E-ATX"):
        fit = 0
    elif max_form_factor == "ATX":
      if form_factor == "E-ATX":
        fit = 0
    if not fit:
      error = "所选主板板型大于所选机箱能容纳的最大主板大小"
      errorList.append(error)

    # 散热器相关
    # 机箱支持相关参数
    max_radiator_height = self.computer_case['max_radiator_height']
    max_water_cooling = 0  # 水冷尺寸限制
    case_radiators = self.computer_case['supported_radiator']
    if case_radiators == '0':
      max_water_cooling = 0
    else:
      case_radiators = case_radiators.split('~')
      max_water_cooling = int(case_radiators[0])
    # 散热器相关参数
    radiator_size = self.cpu_radiator['radiator_size']  # 散热器尺寸(若为 0 则是风冷)
    height = self.cpu_radiator['height']  # 散热器高度
    if not height:
      error = "散热器参数不足，无法判断"
      errorList.append(error)
    else:
      if not radiator_size:
        # 若散热器是风冷，检查风冷高度
        if height > max_radiator_height:
          error = "所选风冷散热器高度大于所选机箱散热器限高"
          errorList.append(error)
      else:
        # 若散热器是水冷，检查水冷大小
        if radiator_size > max_water_cooling:
          error = "所选水冷尺寸大于所选机箱支持的最大尺寸"
          errorList.append(error)

    # SSD接口
    m2_num = self.motherboard['m2_num']
    ssd_interface = self.ssd['interface']
    if (not m2_num) and (ssd_interface == 'M.2'):
      error = "所选主板上没有M.2接口，故不支持M.2接口的固态硬盘"
      errorList.append(error)

    # 电源大小
    power_size = self.power_supply['size']
    if max_form_factor == "MINI-ITX" and (power_size == "ATX" or power_size == "服务器电源"):
      error = "所选机箱无法容纳所选电源"
      errorList.append(error)

    if len(errorList):
      return [False, errorList]
    else:
      return [True]

  def main(self):
    errorList = []
    parse_res = self.parseQuestionnaire()
    if parse_res[0]:
      check_res = self.check()
      if not check_res[0]:
        errorList = check_res[1]
    else:
      error = "数据库中不存在链接 " + parse_res[1] + " 指向的商品"
      errorList.append(error)

    if len(errorList):
      self.flag = 0
      res = {"flag": self.flag, "errorList": errorList}
    else:
      res = {"flag": self.flag}
    res_json = json.dumps(res)

    # 写入文件
    with open("result.json", 'w', encoding='utf-8') as f:
      f.write(res_json)

    # for debugging
    print(res)


if __name__ == "__main__":
  check = CompatibilityChecking()
  check.main()
