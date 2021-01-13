'''
Description:
Author: Fishermanykx
Date: 2020-12-29 08:21:41
LastEditors: Fishermanykx
LastEditTime: 2021-01-13 17:05:44
'''

import re
import json
import time
import pymysql

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from pprint import pprint

from DBConfig import *

# from dataCleaning import *

MYSQL_DB = "computer_accessories"


class JDSpider:
  """
    爬虫类的父类\n
    实现了基本项的爬取，以及基本筛选规则的设定\n
    爬取的基本项： name, comment_num, praise_rate, shop_name, price, link, brand, introduction, Ptable_params\n
    基本筛选规则：过滤非京东自营的商品\n
    数据库更新规则：若存在则更新，否则插入
  """

  def __init__(self, accessory_type):
    self.accessory_type = accessory_type
    self.delay_time = 0.5  # 休眠时间

    self.chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    self.chrome_options.add_experimental_option("prefs", prefs)
    self.driver = webdriver.Chrome(options=self.chrome_options)

    self.id = 1

    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")

    # for data analysis
    self.valid_urls = []

  def __del__(self):
    # 析构函数
    print(self.valid_urls)
    self.driver.close()

  def validData(self, name, shop_name):
    '''
    description: 函数接口，判定该条数据是否有效，由子类实现
    param {*} 相关参数
    return {bool} 若有效，返回True；否则返回False
    '''
    if ("京东自营" not in shop_name):
      return False
    return True

  def productSpider(self, url_root, page_num, start_page):
    start_urls = []
    delta_page = 2
    for i in range(start_page, page_num + start_page):
      url = url_root + str((i - 1) * delta_page + 1)
      start_urls.append(url)

    for url in start_urls:
      self.driver.get(url)
      time.sleep(self.delay_time)
      self.driver.execute_script(
          "window.scrollTo(0, 3 * document.body.scrollHeight / 4);")
      time.sleep(2 * self.delay_time)
      self.driver.execute_script(
          "window.scrollTo(0, 5 * document.body.scrollHeight / 6);"
      )  # 下拉页面，从而显示隐藏界面
      time.sleep(2 * self.delay_time)

      product_urls = []
      product_prices = []
      shop_names = []

      # 对每页商品，爬取商品链接
      for i in range(60):
        # 获取商品链接
        tmp = 1
        while tmp:
          try:
            tmp = 0
            try:
              url_tmp = self.driver.find_element_by_xpath(
                  "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                  str(i + 1) + "]/div/div[3]/a").get_attribute("href")
            except:
              url_tmp = self.driver.find_element_by_xpath(
                  "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                  str(i + 1) +
                  "]/div/div/div[2]/div[1]/div[3]/a").get_attribute("href")

          except NoSuchElementException:
            temp = 1
            self.driver.refresh()
            self.driver.execute_script(
                "window.scrollTo(0, 3 * document.body.scrollHeight / 4);")
            time.sleep(2 * self.delay_time)
            self.driver.execute_script(
                "window.scrollTo(0, 5 * document.body.scrollHeight / 6);")
            time.sleep(2 * self.delay_time)
        # 判断链接长度是否超标
        if len(url_tmp) > 3 * len("https://item.jd.com/100003815425.html"):
          continue
        # 获得店铺，判断是否为京东自营
        try:
          try:
            shop_name = self.driver.find_element_by_xpath(
                "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                str(i + 1) + "]/div/div[5]/span/a").get_attribute("title")
          except:
            shop_name = self.driver.find_element_by_xpath(
                "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                str(i + 1) +
                "]/div/div/div[2]/div[1]/div[5]/span/a").get_attribute("title")
        except:
          print("Error in getting shop name, the url is:", end=" ")
          print(url_tmp)
          continue

        try:
          try:
            name = self.driver.find_element_by_xpath(
                "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                str(i+1) + "]/div/div[3]/a/em"
            ).text
          except:
            name = self.driver.find_element_by_xpath(
                "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                str(i+1) + "]/div/div/div[2]/div[1]/div[3]/a/em"
            ).text
        except:
          print(
              "Error in getting product name in the main page, the product url is", end=" ")
          print(url_tmp)
          continue

        if not self.validData(name, shop_name):
          continue
        shop_names.append(shop_name)
        # print(url_tmp)
        # print(shop_name)
        # exit(0)
        product_urls.append(url_tmp)
        # 获得 price
        try:
          price = self.driver.find_element_by_xpath(
              "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
              str(i + 1) + "]/div/div[2]/strong/i").text
        except:
          price = self.driver.find_element_by_xpath(
              "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
              str(i + 1) + "]/div/div/div[2]/div[1]/div[2]/strong/i").text

        # time.sleep(self.delay_time)
        try:
          price = float(price)
        except:
          print(
              "Error in converting price to float type, the url is:", end=" ")
          print(price)
          continue
        product_prices.append(price)

      self.valid_urls.append(len(product_urls))
      # 进入每个商品的页面，逐一访问
      for i in range(len(product_urls)):
        link = product_urls[i]
        price = product_prices[i]
        shop_name = shop_names[i]
        self.driver.get(link)
        # 点击商品，获取详细信息
        try:
          name, comment_num, praise_rate, brand, introduction, Ptable_params, title_name = self.getGoodsInfo()
        except:
          print(
              "Error in function getGoodsInfo, the url of the product is:", end=" ")
          print(link)
          continue

        # 写入数据库
        self.insertJDData(name, comment_num, praise_rate, shop_name, price,
                          link, brand, introduction, Ptable_params, title_name)
      # exit(0)

  def getGoodsInfo(self):
    """
    返回值：
      name, comment_num, praise_rate, brand, introduction, Ptable_params
      """
    name = ""  # introduction 中的 name
    comment_num = ""
    praise_rate = ""
    brand = ""
    tags = ""
    power = ""
    size = ""
    transfer_efficiency = ""
    introduction = {}  # dict类型，会转成 json 字符串
    Ptable_params = {}  # dict类型，会转成 json 字符串
    title_name = ""  # 商品标题中的名字

    # 获取 brand
    brand = self.driver.find_element_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[2]/div[1]/div[1]/ul[1]/li/a").text
    # print(brand)
    brand = self.cleanBrand(brand)

    # 获取 introduction 页面
    front_str = "/html/body/div[*]/div[2]/div[1]/div[2]/div[1]/div[1]/ul[2]/li["
    back_str = "]"
    introd_index = 1
    while True:
      try:
        key_val_str = self.driver.find_element_by_xpath(front_str +
                                                        str(introd_index) +
                                                        back_str).text

        # 分割键值对
        key_val = key_val_str.split("：")
        introduction[key_val[0]] = key_val[1]

        introd_index += 1
      except:
        break
    # 获取商品名称
    try:  # /html/body/div[8]/div/div[2]/div[1]/text()
      name = self.driver.find_element_by_xpath(
          "/html/body/div[8]/div/div[2]/div[1]").text
      if (name == ""):
        name = self.driver.find_element_by_xpath(
            "/html/body/div[6]/div/div[2]/div[1]").text
    except:
      name = introduction["商品名称"]
    if (name == "" or "加入PLUS会员" in name):
      name = introduction["商品名称"]
    title_name = name
    name = introduction["商品名称"]

    introduction = json.dumps(introduction)  # 将 dict 转化为 json 字符串
    # pprint(introduction)
    # exit(0)

    # 点击进入 规格与包装 页面
    time.sleep(self.delay_time * 2)
    self.driver.find_element_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[2]").click()
    time.sleep(self.delay_time * 2)
    # 获取页面的 html 文本
    Ptable_items = self.driver.find_elements_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[2]/div[2]/div[1]/*"
    )  # 拿到了所有的 Ptable-item 标签下的内容
    # print(type(Ptable_items))
    len_Ptable_items = len(Ptable_items)
    for i in range(len_Ptable_items):
      params = Ptable_items[i]
      key_i = params.find_element_by_xpath(
          '//*[@id="detail"]/div[2]/div[2]/div[1]/div[' + str(i + 1) +
          ']/h3').text
      p_index = 1
      Ptable_params[key_i] = {}
      while True:
        try:
          sub_key = params.find_element_by_xpath(
              '//*[@id="detail"]/div[2]/div[2]/div[1]/div[' + str(i + 1) +
              ']/dl/dl[' + str(p_index) + ']/dt').text
          sub_val = params.find_element_by_xpath(
              '//*[@id="detail"]/div[2]/div[2]/div[1]/div[' + str(i + 1) +
              ']/dl/dl[' + str(p_index) + ']/dd').text
          Ptable_params[key_i][sub_key] = sub_val
          p_index += 1
        except:
          break
    Ptable_params = json.dumps(Ptable_params)  # 将 dict 转化为 json 字符串
    # pprint(Ptable_params)
    # exit(0)

    # 点击进入评论页面
    time.sleep(self.delay_time)
    comment_num, praise_rate = self.getCurrentCommentNumber()
    time.sleep(self.delay_time)

    return name, comment_num, praise_rate, brand, introduction, Ptable_params, title_name

  def getCurrentCommentNumber(self):
    cnt = 1
    comment_num = "100"
    praise_rate = "90%"
    while cnt < 3:
      try:
        # 转到 商品评价 页面
        label = self.driver.find_element_by_xpath(
            "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[4]"
        ).text
        if (label[:4] == "商品评价"):
          self.driver.find_element_by_xpath(
              "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[4]").click()
        else:
          self.driver.find_element_by_xpath(
              "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[5]").click()
        time.sleep(self.delay_time*3)

      # 勾选 只看当前商品评价 选项
        self.driver.find_element_by_xpath(
            "/html/body/div[*]/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[9]/label"
        ).click()
        time.sleep(self.delay_time)
        comment_num = self.driver.find_element_by_xpath(
            "/html/body/div[*]/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[1]/a/em").text
        comment_num = comment_num[1:-1]  # 去括号
        time.sleep(self.delay_time)
        praise_rate = self.driver.find_element_by_xpath(
            "/html/body/*/div[2]/div[3]/div[2]/div[1]/div[1]/div").text
        break
      except:
        self.driver.refresh()
        time.sleep(cnt*self.delay_time)
        cnt += 1

    return self.cleanComments(comment_num, praise_rate)

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    # engine = sqlalchemy.create_engine(
    #     "mysql+pymysql://root:08239015@localhost:3306/jd_test")
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO "+self.accessory_type+" (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, "\
        "%(shop_name)s, %(price)s, %(link)s, %(brand)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }
    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def cleanComments(self, comment_num, praise_rate):
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

  def cleanBrand(self, brand):
    if "Intel" in brand:
      return "INTEL"
    elif 'AMD' in brand:
      return "AMD"

    index = brand.find('（')
    if brand == 'Thermaltake（Tt）':
      return "TT"
    if brand == '玩家国度':
      return '华硕'

    if index != -1:
      brand = brand[:index]
    else:
      # Special cases
      if brand == 'Crucial':
        brand = '英睿达'
      elif brand == 'HP':
        brand = '惠普'
      elif brand == 'uFound' or brand == 'ifound':
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
        brand = '联力'
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
      elif brand == 'JUHOR':
        brand = '玖合'
      elif brand == 'GEIL':
        brand = '金邦'
      elif brand == 'G.SKILL':
        brand = '芝奇'

    # 注意：没被处理的有：EVGA, zero zone(这TM还是家国内公司。。。), ID_COOLING

    return brand


########## 以下均为子类，负责设置过滤规则，以及数据清洗 ##########
class CPUSpider(JDSpider):
  def validData(self, name, shop_name):
    if ("京东自营" not in shop_name) or ("NUC" in shop_name) or ('蓝牙' in name) or ('套装' in name):
      return False
    return True

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO cpu (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, clock_speed, core_num, TDP, socket, have_core_graphics_card, have_cpu_fan, generation, "\
        "introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, "\
        "%(price)s, %(link)s, %(brand)s, %(tags)s, %(clock_speed)s, %(core_num)s, %(TDP)s, %(socket)s, "\
        "%(have_core_graphics_card)s, %(have_cpu_fan)s, %(generation)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "tags": "",
        "clock_speed": "",
        "core_num": "",
        "TDP": 0,
        "socket": "",
        "have_core_graphics_card": "",
        "have_cpu_fan": "",
        "generation": 1,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleCPURecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 类别
    record['tags'] = introd.get("类别", "无")
    # 时钟频率
    record['clock_speed'] = p_table['规格']['主频']
    # 内核数
    record['core_num'] = introd['核心数量']
    # 是否支持核显
    record['have_core_graphics_card'] = introd.get('是否支持核显', '不支持核显')
    # 是否自带风扇
    record['have_cpu_fan'] = introd.get('是否自带风扇', '不带风扇')
    # TDP
    record['TDP'] = int(p_table['规格']['功率'][:-1])
    # 处理接口
    socket = introd["接口"]
    if "1151" in socket:
      socket = "INTEL LGA1151"
    elif "其他" in socket:
      socket = "INTEL LGA1151"
    record["socket"] = socket

    # CPU 代数
    # 分类标准：锐龙5000系和酷睿10代为最新代；锐龙3000和酷睿9代为上代；其余为上古版本
    # 提取代数
    name = record['name']
    pat = r"\d+\w"
    res = re.search(pat, name)
    res = res.group()
    if record['brand'] == 'INTEL':
      if res[:2] == "10":
        record['generation'] = 3
      elif res[0] == '9':
        record['generation'] = 2
      else:
        record['generation'] = 1
    else:
      ch = res[0]
      if ch == '5':
        record['generation'] = 3
      elif ch == '3' or ch == '4':
        record['generation'] = 2
      else:
        record['generation'] = 1

    return record

  def cleanCPU(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    cnt = 1
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      # 判定是否为板-U套装
      record = data[i]
      try:
        if '套装' in record['title_name']:
          continue
      except:
        if '套装' in record['name']:
          continue
      # 清洗数据
      new_data.append(self.handleSingleCPURecord(record))
      new_data[index]['id'] = cnt
      index += 1
      cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO cpu (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, clock_speed, core_num, TDP, socket, have_core_graphics_card, have_cpu_fan, generation, "\
        "introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, "\
        "%(price)s, %(link)s, %(brand)s, %(tags)s, %(clock_speed)s, %(core_num)s, %(TDP)s, %(socket)s, "\
        "%(have_core_graphics_card)s, %(have_cpu_fan)s, %(generation)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    cpu_link = "https://list.jd.com/list.html?cat=670%2C677%2C678&page="
    cpu_link = "https://list.jd.com/list.html?cat=670%2C677%2C678&psort=3&psort=3&page="

    page_num = 3
    start_page = 1
    self.productSpider(cpu_link, page_num, start_page)

    self.cleanCPU()
    print("Successfully get CPU data!")


class MotherboardSpider(JDSpider):
  def validData(self, name, shop_name):
    res = True
    if ("ROG" not in shop_name):
      if ("京东自营" not in shop_name):
        res = False
    return res

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO motherboard (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, form_factor, platform, cpu_socket, m2_num, slot_num, ddr_gen, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s,"\
        " %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(form_factor)s, "\
        "%(platform)s, %(cpu_socket)s, %(m2_num)s, %(slot_num)s, %(ddr_gen)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "tags": "",
        "form_factor": "",
        "platform": "",
        "cpu_socket": "",
        "m2_num": 0,
        "slot_num": 0,
        "ddr_gen": "",
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleMotherboardRecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # tags
    tags = introd.get("应用场景", "无")
    record['tags'] = tags
    # ROG
    if record['brand'] == '玩家国度':
      record['brand'] = '华硕'
    # form_factor
    s = introd.get("板型", '没有写')
    record['form_factor'] = s[:s.find('（')]  # form_factor 去中文
    # platform
    platform = p_table["主体"].get("平台类型", "没有写")
    record['platform'] = self.cleanBrand(platform[:-2])
    # 加入 CPU 接口列
    try:
      ss = introd.get('适用CPU接口', "")
      if not ss:
        ss = p_table['支持CPU'].get("接口类型", "")
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
    # 插槽数目
    slot_num = p_table['内存'].get("内存插槽", 0)
    try:
      if slot_num[0].isdigit():
        slot_num = int(slot_num[0])
      else:
        slot_num = int(slot_num[0][-1])
    except:
      slot_num = 0
    record['slot_num'] = slot_num

    # 支持的内存代数
    ddr_gen = p_table['内存'].get('DDR代数')
    record['ddr_gen'] = ddr_gen

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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    cnt = 1
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      # 判定是否为板-U套装
      record = data[i]
      if record['comment_num'] == 100:  # 抓到板-U套装了
        continue
      if '套装' in record['title_name']:
        continue
      # 清洗数据
      new_data.append(self.handleSingleMotherboardRecord(record))
      new_data[index]['id'] = cnt
      index += 1
      cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO motherboard (id, name, comment_num, praise_rate, shop_name, price, link, brand, tags, "\
        "form_factor, platform, cpu_socket, m2_num, slot_num, ddr_gen, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s,"\
        " %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(form_factor)s, "\
        "%(platform)s, %(cpu_socket)s, %(m2_num)s, %(slot_num)s, %(ddr_gen)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    motherboard_link = "https://list.jd.com/list.html?cat=670%2C677%2C681&psort=3&psort=3&page="
    # 爬取数据
    page_num = 26  # 一共爬了26页
    # page_num = 1  # for testing
    start_page = 1
    self.productSpider(motherboard_link, page_num, start_page)
    # 清洗数据
    self.cleanMotherboard()
    print("Successfully get Motherboard data!")


class GraphicsCardSpider(JDSpider):
  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO "+self.accessory_type+" (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, card_length, rgb, card_type, generation, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, "\
        "%(card_length)s, %(rgb)s, %(card_type)s, %(generation)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "tags": "",
        "card_length": 0,
        "rgb": "",
        "card_type": "NVIDIA",
        "generation": 1,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }
    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleGraphicsCard(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # tags
    tags = introd.get("性能", "无")
    record['tags'] = tags
    # 显卡类别
    amd = introd.get('AMD芯片', "其他")
    nv = introd.get('NVIDIA芯片', "其他")
    if nv == '其他':
      record['card_type'] = 'AMD'
    else:
      record['card_type'] = 'NVIDIA'
    # 修正卡长
    card_length = p_table["特性"].get("显卡长度", "没有写")
    if (card_length != "没有写"):
      card_length = card_length[:-2]
    record['card_length'] = eval(card_length)
    # 修正 RGB 列
    rgb = introd.get("灯效", '无')
    if rgb == '单色':
      rgb = '支持RGB'
    record['rgb'] = rgb

    # 显卡代数
    # 分类标准：
    #   对 N卡 ： 按30系，20系等进行分类，其中 Quardo 系列统一属于类别2
    #   对 A卡 ：
    name = record['name']
    generation = 1
    if record['card_type'] == 'NVIDIA':
      if ('3090' in name) or ('3080' in name) or ('3070' in name) or ('3060' in name):
        generation = 3
      elif ('2080' in name) or ('2070' in name) or ('2060' in name):
        generation = 2
      else:
        generation = 1
    else:
      if ('6900' in name) or ('6800' in name):
        generation = 3
      elif ('5700' in name) or ('5600' in name) or ('5500' in name):
        generation = 2
      else:
        generation = 1
    record['generation'] = generation

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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    cnt = 1
    new_data = []
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      if '支架' in record['name']:
        continue
      # 清洗数据
      new_data.append(self.handleSingleGraphicsCard(record))
      new_data[index]['id'] = cnt
      cnt += 1
      index += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO "+self.accessory_type+" (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, card_length, rgb, card_type, generation, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, "\
        "%(card_length)s, %(rgb)s, %(card_type)s, %(generation)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    graphics_card_link = "https://list.jd.com/list.html?cat=670%2C677%2C679&psort=3&psort=3&page="
    # 爬取数据
    page_num = 30
    start_page = 1
    # self.productSpider(graphics_card_link, page_num, start_page)
    # 清洗数据
    self.cleanGraphicsCard()
    print("Successfully get Graphics Card data!")


class MemorySpider(JDSpider):
  def validData(self, name, shop_name):
    res = True
    if ("笔记本" in name):
      res = False
      print(name)
    elif ("京东自营" not in shop_name):
      res = False
    else:
      res = True
    return res

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO memory (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, frequency, total_capacity, memory_num, appearance, ddr_gen, introduction, "\
        "Ptable_params, title_name) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s"\
        ", %(link)s, %(brand)s, %(frequency)s, %(total_capacity)s, %(memory_num)s, %(appearance)s, "\
        "%(ddr_gen)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "frequency": "",
        "total_capacity": 0,
        "memory_num": "",
        "appearance": "",
        "ddr_gen": "",
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleMemory(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])
    record['brand'] = self.cleanBrand(record['brand'])

    record['frequency'] = introd.get("频率", '2400/2666 (原链接没写)')
    record['memory_num'] = introd.get("内存数量", "1条单条 (原链接没写)")
    record['appearance'] = introd.get("外观特征", "没有写")
    record['ddr_gen'] = introd.get("DDR代数", "没有写")

    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = introd.get("总容量", "8GB (原链接没写)")
    if '及' not in capacity and '没' not in capacity:
      capacity = int(capacity[:-2])
    else:
      pat = r'\d+G'
      name = record['title_name']
      if not name:
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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    cnt = 1
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      name = record['title_name']
      if not name:
        name = record['name']

      if '内存发光套件' in name:
        continue

      # 清洗数据
      new_data.append(self.handleSingleMemory(record))
      new_data[index]['id'] = cnt
      cnt += 1
      index += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 重新写入
    sql_insert = "INSERT INTO memory (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, frequency, total_capacity, memory_num, appearance, ddr_gen, introduction, "\
        "Ptable_params, title_name) VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s"\
        ", %(link)s, %(brand)s, %(frequency)s, %(total_capacity)s, %(memory_num)s, %(appearance)s, "\
        "%(ddr_gen)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    sql_insert = pymysql.escape_string(sql_insert)
    cursor.executemany(sql_insert, new_data)
    # for i in range(len(new_data)):
    #   cursor.execute(sql_insert, new_data[i])

    connection.commit()

  def main(self):
    memory_link = "https://list.jd.com/list.html?cat=670%2C677%2C680&psort=3&ev=210_1558%5E&psort=3&page="
    # 爬取数据
    page_num = 40
    start_page = 1
    # self.productSpider(memory_link, page_num, start_page)
    # 清洗数据
    self.cleanMemory()
    print("Successfully get Memory data!")


class CPURadiatorSpider(JDSpider):
  def validData(self, name, shop_name):
    res = True
    if ("笔记本" in name):
      res = False
      print(name)
    elif ("京东自营" not in shop_name):
      res = False
    else:
      res = True
    return res

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO cpu_radiator (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, height, socket, radiator_size, rgb, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(height)s, "\
        "%(socket)s, %(radiator_size)s, %(rgb)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "height": 0,
        "socket": "",
        "radiator_size": 0,
        "rgb": "",
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

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
    cooling_size = introd.get('水冷类型', '风冷')
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

    return record

  def cleanCPURadiator(self):
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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    new_data = []
    cnt = 1
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      name = record['title_name']
      if not name:
        name = record['name']
      if ('套装' in name) or ('机箱风扇' in name) or ('套装' in record['name']):
        continue
      if ('+' in record['name']):
        continue
      introd = eval(record['introduction'])
      cate = introd.get('产品类型', "无")
      if (cate == '分体式水冷配件'):
        continue
      # 清洗数据
      new_data.append(self.handleSingleCPURadiator(record))
      new_data[index]['id'] = cnt
      index += 1
      cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)
    # 重新写入
    sql_insert = "INSERT INTO cpu_radiator (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, height, socket, radiator_size, rgb, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(height)s, "\
        "%(socket)s, %(radiator_size)s, %(rgb)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    sql_insert = pymysql.escape_string(sql_insert)
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    radiator_link = "https://list.jd.com/list.html?cat=670%2C677%2C682&psort=3&ev=3680_97402%7C%7C97403%7C%7C106254%7C%7C106255%5E&psort=3&page="
    # 爬取数据
    page_num = 27
    start_page = 1
    # self.productSpider(radiator_link, page_num, start_page)
    # 清洗数据
    self.cleanCPURadiator()
    print("Successfully get CPU Radiator data!")


class SSDSpider(JDSpider):
  def validData(self, name, shop_name):
    if ("京东自营" not in shop_name):
      return False
    return True

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO ssd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, interface, total_capacity, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, "\
        "%(interface)s, %(total_capacity)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "interface": "",
        "total_capacity": 0,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleSSDRecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 清洗接口
    s = introd.get("接口", '没有写')
    index = s.find('接口')
    record['interface'] = s[:index]

    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = introd.get("容量", "没有写")
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
      name = record['title_name']
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

    return record

  def cleanSSD(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    cnt = 1
    new_data = []
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      if ('支架' in record['name']) or ('套装' in record['name']) or ('固态硬盘散热器' in record['name']):
        continue
      if 'HDMI' in record['interface']:
        continue
      # 清洗数据
      new_data.append(self.handleSingleSSDRecord(record))
      new_data[index]['id'] = cnt
      cnt += 1
      index += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO ssd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, interface, total_capacity, introduction, Ptable_params, title_name) VALUES (%(id)s, %(name)s, "\
        "%(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, "\
        "%(interface)s, %(total_capacity)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    ssd_link = "https://list.jd.com/list.html?cat=670%2C677%2C11303&psort=3&psort=3&page="
    page_num = 36  # 一共爬了36页
    start_page = 1
    # self.productSpider(ssd_link, page_num, start_page)

    self.cleanSSD()
    print("Successfully get SSD data!")


class HDDSpider(JDSpider):
  def validData(self, name, shop_name):
    if ("京东自营" not in shop_name):
      return False
    return True

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO hdd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, size, rotating_speed, total_capacity, introduction, Ptable_params, title_name) VALUES (%(id)s, "\
        "%(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(size)s, "\
        "%(rotating_speed)s, %(total_capacity)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "size": "",
        "rotating_speed": "",
        "total_capacity": 0,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleHDDRecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    # 转速
    record['rotating_speed'] = introd.get("转速", '没有写')
    # 清洗容量 (以TB为单位的0.25的倍数的浮点数)
    capacity = introd.get("容量", "没有写")
    dig = capacity[:-2]
    if dig != '12' and dig.isdigit():
      capacity = dig
    else:
      name = record['title_name']
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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    cnt = 1
    new_data = []
    index = 0

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      if ('套装' in record['title_name']) or ('解决方案' in record['title_name']) \
              or ('解决方案' in record['name']) or ('笔记本' in record['title_name']) or ('套装' in record['name']) \
              or ('移动硬盘' in record['title_name']) or ('固态硬盘' in record['title_name']):
        continue
      # 清洗数据
      new_data.append(self.handleSingleHDDRecord(record))
      new_data[index]['id'] = cnt
      index += 1
      cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO hdd (id, name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, size, rotating_speed, total_capacity, introduction, Ptable_params, title_name) VALUES (%(id)s, "\
        "%(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(size)s, "\
        "%(rotating_speed)s, %(total_capacity)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    hdd_link = "https://list.jd.com/list.html?cat=670%2C677%2C683&psort=3&psort=3&page="
    page_num = 11
    start_page = 1
    # self.productSpider(hdd_link, page_num, start_page)

    self.cleanHDD()
    print("Successfully get HDD data!")


class PowerSupplySpider(JDSpider):
  def validData(self, name, shop_name):
    if ("京东自营" not in shop_name) or ('套装' in name):
      return False
    return True

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO power_supply (id, name, comment_num, praise_rate, shop_name, price, link, brand, tags, "\
        "power, size, modularization, transfer_efficiency, introduction, Ptable_params, title_name) VALUES (%(id)s, "\
        "%(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(power)s, "\
        "%(size)s, %(modularization)s, %(transfer_efficiency)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "tags": "",
        "power": 0,
        "size": "",
        "modularization": "",
        "transfer_efficiency": "",
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSinglePowerRecord(self, record):
    record['price'] = int(record['price'])
    introd = eval(record['introduction'])
    p_table = eval(record['Ptable_params'])

    record['tags'] = introd.get("使用场景", "无")
    record['power'] = introd.get("电源功率", '没有写')
    record['size'] = introd.get("电源尺寸", "无")
    record['transfer_efficiency'] = introd.get("转换效率", "无")

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

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    cnt = 1
    index = 0
    new_data = []

    for i in range(data_len):
      # 逐条数据处理
      record = data[i]
      size = record['size']
      if size == '无':
        continue
      name = record['title_name']
      if '套装' in name:
        continue
      if '接线类型' not in record['introduction']:
        continue
      # 清洗数据
      new_data.append(self.handleSinglePowerRecord(record))
      new_data[index]['id'] = cnt
      index += 1
      cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO power_supply (id, name, comment_num, praise_rate, shop_name, price, link, brand, tags, "\
        "power, size, modularization, transfer_efficiency, introduction, Ptable_params, title_name) VALUES (%(id)s, "\
        "%(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(power)s, "\
        "%(size)s, %(modularization)s, %(transfer_efficiency)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    power_supply_link = "https://list.jd.com/list.html?cat=670%2C677%2C691&psort=3&psort=3&page="
    page_num = 25  # 抓25页
    start_page = 1
    # self.productSpider(power_supply_link, page_num, start_page)

    self.cleanPowerSupply()
    print("Successfully get Power Supply data!")


class CaseSpider(JDSpider):
  def validData(self, name, shop_name):
    if ("京东自营" not in shop_name) or ('套装' in name):
      return False
    return True

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, introduction, Ptable_params, title_name):
    '''
    description: Insert data into table
    '''
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()

    sql_insert = "INSERT INTO computer_case (id, name, comment_num, praise_rate, shop_name, price, "\
        "link, brand, max_form_factor, max_card_len, max_radiator_height, supported_radiator, "\
        "has_transparent_side_panel, introduction, Ptable_params, title_name)"\
        " VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, "\
        "%(brand)s, %(max_form_factor)s, %(max_card_len)s, %(max_radiator_height)s, %(supported_radiator)s, "\
        "%(has_transparent_side_panel)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
        "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
        "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    # sql_insert = "INSERT INTO computer_case (id, name, comment_num, praise_rate, shop_name, price, "\
    #     "link, brand, max_form_factor, max_card_len, max_radiator_height, supported_radiator, "\
    #     "has_transparent_side_panel, is_water_cooling, introduction, Ptable_params, title_name)"\
    #     " VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, "\
    #     "%(brand)s, %(max_form_factor)s, %(max_card_len)s, %(max_radiator_height)s, %(supported_radiator)s, "\
    #     "%(has_transparent_side_panel)s, %(is_water_cooling)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"\
    #     "ON DUPLICATE KEY UPDATE id=VALUES(id), name=VALUES(name), comment_num=VALUES(comment_num), praise_rate=VALUES(praise_rate), "\
    #     "price=VALUES(price), introduction=VALUES(introduction), Ptable_params=VALUES(Ptable_params), title_name=VALUES(title_name)"
    value = {
        "id": self.id,
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "max_form_factor": "",
        "max_card_len": 0,
        "max_radiator_height": 0,
        "supported_radiator": "",
        "has_transparent_side_panel": 0,
        "introduction": introduction,
        "Ptable_params": Ptable_params,
        "title_name": title_name
    }

    try:
      cursor.execute(sql_insert, value)
      db.commit()
      self.id += 1
      # for debugging
      changed_num = cursor.rowcount
      if changed_num == 1:
        print('成功插入1条数据')
      elif changed_num == 2:
        print('成功更新1条数据')
      else:
        print("未修改任何数据")
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()

  def handleSingleCaseRecord(self, record):
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

    # 侧透
    side_panel = 0
    name = record['title_name']
    category = introd.get('机箱类型', "")
    if ('侧透' in name) or ('侧透' in category):
      side_panel = 1
    record['has_transparent_side_panel'] = side_panel

    return record

  def cleanCase(self):
    connection = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 获取游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    cursor.execute("select * from " + self.accessory_type)
    data = cursor.fetchall()  # 以字典列表的形式读出表中所有数据

    # 数据清洗
    data_len = len(data)
    # print(data_len)
    cnt = 1
    new_data = []
    index = 0

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
        new_data.append(self.handleSingleCaseRecord(record))
        new_data[index]['id'] = cnt
        index += 1
        cnt += 1

    # 清空表
    cursor.execute("truncate table " + self.accessory_type)

    # 重新写入
    sql_insert = "INSERT INTO computer_case (id, name, comment_num, praise_rate, shop_name, price, "\
        "link, brand, max_form_factor, max_card_len, max_radiator_height, supported_radiator, "\
        "has_transparent_side_panel, introduction, Ptable_params, title_name)"\
        " VALUES (%(id)s, %(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, "\
        "%(max_form_factor)s, %(max_card_len)s, %(max_radiator_height)s, %(supported_radiator)s, "\
        "%(has_transparent_side_panel)s, %(introduction)s, %(Ptable_params)s, %(title_name)s)"
    cursor.executemany(sql_insert, new_data)

    connection.commit()

  def main(self):
    case_link = "https://list.jd.com/list.html?cat=670%2C677%2C687&psort=3&psort=3&page="
    page_num = 36
    start_page = 1
    self.productSpider(case_link, page_num, start_page)

    self.cleanCase()
    print("Successfully get Computer Case data!")


if __name__ == "__main__":
  accessory_type = 'ssd'
  # accessory_type = 'motherboard'
  if accessory_type == 'cpu':
    cpu_spider = CPUSpider('cpu')
    cpu_spider.main()
  elif accessory_type == 'motherboard':
    motherboard_spider = MotherboardSpider('motherboard')
    motherboard_spider.main()
  elif accessory_type == 'graphics_card':
    graphics_card_spider = GraphicsCardSpider('graphics_card')
    graphics_card_spider.main()
  elif accessory_type == 'memory':
    memory_spider = MemorySpider('memory')
    memory_spider.main()
  elif accessory_type == 'cpu_radiator':
    cpu_radiator_spider = CPURadiatorSpider('cpu_radiator')
    cpu_radiator_spider.main()
  elif accessory_type == 'ssd':
    ssd_spider = SSDSpider('ssd')
    ssd_spider.main()
  elif accessory_type == 'hdd':
    hdd_spider = HDDSpider('hdd')
    hdd_spider.main()
  elif accessory_type == 'power_supply':
    power_supply_spider = PowerSupplySpider('power_supply')
    power_supply_spider.main()
  elif accessory_type == 'computer_case':
    case_spider = CaseSpider('computer_case')
    case_spider.main()
  elif accessory_type == 'all':
    cpu_spider = CPUSpider('cpu')
    cpu_spider.main()
    motherboard_spider = MotherboardSpider('motherboard')
    motherboard_spider.main()
    graphics_card_spider = GraphicsCardSpider('graphics_card')
    graphics_card_spider.main()
    memory_spider = MemorySpider('memory')
    memory_spider.main()
    cpu_radiator_spider = CPURadiatorSpider('cpu_radiator')
    cpu_radiator_spider.main()
    ssd_spider = SSDSpider('ssd')
    ssd_spider.main()
    hdd_spider = HDDSpider('hdd')
    hdd_spider.main()
    power_supply_spider = PowerSupplySpider('power_supply')
    power_supply_spider.main()
    case_spider = CaseSpider('computer_case')
    case_spider.main()
  else:
    print("输入的配件类型名有误！请重新输入")
