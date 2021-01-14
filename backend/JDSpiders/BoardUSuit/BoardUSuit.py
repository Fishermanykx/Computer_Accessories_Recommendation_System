'''
Description: 
  name ：商品名
  board ：主板名
  cpu ：cpu名
  shop_name ：店铺名
  评论数和好评率不爬，因为都是0
Author: Fishermanykx
Date: 2020-12-11 14:25:04
LastEditors: Fishermanykx
LastEditTime: 2020-12-11 17:07:22
'''
import re
import json
from pprint import pprint
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import pymysql
import sqlalchemy
MYSQL_HOSTS = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = "08239015"
MYSQL_PORT = 3306
MYSQL_DB = "computer_accessories"


class JDBoardUSuitSpider:

  def __init__(self):
    self.delay_time = 0.5  # 休眠时间
    self.chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    self.chrome_options.add_experimental_option("prefs", prefs)
    self.driver = webdriver.Chrome(options=self.chrome_options)
    db = pymysql.connect(
        host=MYSQL_HOSTS,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset="utf8")
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()
    # for data analysis
    self.valid_urls = []

    query = "truncate table board_u_suit"
    cursor.execute(query)
    db.commit()
    print("原表已清空")
    cursor.close()
    db.close()

  def boardUSuitSpider(self):
    start_urls = []
    url_root = "https://list.jd.com/list.html?cat=670%2C677%2C17466&psort=3&psort=3&page="
    page_num = 18
    delta_page = 2
    for i in range(1, page_num + 1):
      url = url_root + str((i - 1) * delta_page + 1)
      start_urls.append(url)
    # print(start_urls)
    for url in start_urls:
      self.driver.get(url)
      time.sleep(self.delay_time)
      self.driver.execute_script(
          "window.scrollTo(0, 3 * document.body.scrollHeight / 4);")
      time.sleep(3 * self.delay_time)
      self.driver.execute_script(
          "window.scrollTo(0, 5 * document.body.scrollHeight / 6);"
      )  # 下拉页面，从而显示隐藏界面
      time.sleep(3 * self.delay_time)

      board_u_suit_urls = []
      board_u_suit_prices = []
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
        if len(url_tmp) > 3 * len("https://item.jd.com/100011256960.html"):
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
          print("Error in getting shop name in main page")
          print(url_tmp)
          continue

        if ("京东自营" not in shop_name):
          continue
        shop_names.append(shop_name)
        # print(url_tmp)
        # print(shop_name)
        # exit(0)
        board_u_suit_urls.append(url_tmp)
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
          print("Error in converting price to float type")
          print(price)
          continue
        board_u_suit_prices.append(price)

      # print(len(board_u_suit_urls))
      # print(len(board_u_suit_prices))
      # print(len(shop_names))
      # pprint(board_u_suit_urls)
      # pprint(board_u_suit_prices)
      # pprint(shop_names)
      # exit(0)
      self.valid_urls.append(len(board_u_suit_urls))
      # 进入每个商品的页面，逐一访问
      for i in range(len(board_u_suit_urls)):
        link = board_u_suit_urls[i]
        price = board_u_suit_prices[i]
        shop_name = shop_names[i]
        self.driver.get(link)
        # 点击商品，获取详细信息
        try:
          name, board, cpu, introduction, Ptable_params\
              = self.getGoodsInfo()
        except:
          print("Error in function getGoodsInfo")
          print(link)
          continue

        if (name == ""):
          print("Name is NULL")
          print(link)
          continue

        # 写入数据库
        self.insertJDData(name, board, cpu, shop_name, price, link,
                          introduction, Ptable_params)
        # exit(0)

  def getGoodsInfo(self):
    """
    返回值：
      name, brand, introduction, Ptable_params
      """
    name = ""
    brand = ""
    board = ""
    cpu = ""
    introduction = {}  # dict类型，会转成 json 字符串
    Ptable_params = {}  # dict类型，会转成 json 字符串

    # 获取并分析出板、U名
    try:
      name, board, cpu = self.getSpecificNames()
    except:
      print("Error in function getSpecificNames, skip this product!")

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
    introduction = json.dumps(introduction)  # 将 dict 转化为 json 字符串
    # pprint(introduction)
    # exit(0)

    # 点击进入 规格与包装 页面
    time.sleep(self.delay_time * 2)
    self.driver.find_element_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[2]").click()
    time.sleep(self.delay_time)
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

    return name, board, cpu, introduction, Ptable_params

  def getSpecificNames(self):
    name = ""
    board = ""
    cpu = ""

    name = self.driver.find_element_by_xpath(
        "/html/body/div[6]/div/div[2]/div[1]").text

    # 分析
    name_lis = name.strip().split('+')
    board = name_lis[0]
    ss = name_lis[1]
    # 过滤无关词
    indexs = []
    index = -1
    # 过滤规则
    indexs.append(ss.find("酷睿"))
    indexs.append(ss.find("CPU"))
    indexs.append(ss.find("处理器"))
    indexs.append(ss.find("盒装"))
    indexs.append(ss.find("板"))
    pat = r"\d*核\d*线程"
    result = re.search(pat, ss)
    if (result):
      result = result.span()[0]
      indexs.append(result)
    indexs.sort()
    # print(indexs)
    for item in indexs:
      if (item != -1):
        index = item
        break
    cpu = ss[:index].strip()

    return name, board, cpu

  def insertJDData(self, name, board, cpu, shop_name, price, link, introduction,
                   Ptable_params):
    '''
    description: Insert data into table ** board_u_suit **
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

    sql_insert = "INSERT INTO board_u_suit (name, board, cpu, shop_name, price, link,"\
        "introduction, Ptable_params) VALUES (%(name)s, %(board)s, %(cpu)s,"\
        "%(shop_name)s, %(price)s, %(link)s, %(introduction)s, %(Ptable_params)s)"
    value = {
        "name": name,
        "board": board,
        "cpu": cpu,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "introduction": introduction,
        "Ptable_params": Ptable_params
    }
    try:
      cursor.execute(sql_insert, value)
      db.commit()
      # for debugging
      print('成功插入', cursor.rowcount, '条数据')
    except:
      print("插入数据失败!")
      print(link)
    cursor.close()
    db.close()


if __name__ == "__main__":
  board_u_suit_spider = JDBoardUSuitSpider()
  board_u_suit_spider.boardUSuitSpider()
  # print(board_u_suit_spider.valid_urls)
