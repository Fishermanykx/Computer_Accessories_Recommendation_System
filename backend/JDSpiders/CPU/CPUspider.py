'''
Description: 
  clock_speed ：CPU 主频 (单位：GHz)
  core_num ：核心数量 (单核/双核/六核/八核/三十二核)
  have_core_graphics_card ：是否支持核显
  have_cpu_fan ：是否自带风扇
  introduction ：商品介绍的 .json
  Ptable_params ：规格与包装的 .json
Author: Fishermanykx
Date: 2020-12-06 16:13:56
LastEditors: Fishermanykx
LastEditTime: 2020-12-07 16:14:14
'''
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


class JDMotherboardSpider:

  def __init__(self):
    self.delay_time = 0.5  # 休眠时间
    self.chrome_options = Options()
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

    query = "truncate table motherboard"
    cursor.execute(query)
    db.commit()
    print("原表已清空")
    cursor.close()
    db.close()

  def motherboardSpider(self):
    start_urls = []
    # 按 综合 抓，否则抓到的全是板U套装。。。
    url_root = "https://list.jd.com/list.html?cat=670%2C677%2C678&page="

    page_num = 1  # 1页就够了，没那么多CPU
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

      motherboard_urls = []
      motherboard_prices = []
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
        if len(url_tmp) > 3 * len("https://item.jd.com/100006773296.html"):
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
          print(url_tmp)
          continue

        if ("NUC" in shop_name):  # 不要 Intel 自己配的 NUC 主机
          continue
        if ("京东自营" not in shop_name):
          continue
        shop_names.append(shop_name)
        # print(url_tmp)
        # print(shop_name)
        # exit(0)
        motherboard_urls.append(url_tmp)
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
          print(price)
          # exit(1)
          continue
        motherboard_prices.append(price)
        # print(price)
        # exit(0)
      # print(len(motherboard_urls))
      # print(len(motherboard_prices))
      # print(len(shop_names))
      # pprint(motherboard_urls)
      # pprint(motherboard_prices)
      # pprint(shop_names)
      # exit(0)

      # 进入每个商品的页面，逐一访问
      for i in range(len(motherboard_urls)):
        time.sleep(self.delay_time)
        link = motherboard_urls[i]
        price = motherboard_prices[i]
        shop_name = shop_names[i]
        self.driver.get(link)
        time.sleep(self.delay_time)
        # 点击商品，获取详细信息
        try:
          name, comment_num, praise_rate, brand, tags, form_factor, platform, introduction, Ptable_params\
              = self.getGoodsInfo()
        except:
          print(link)
          continue

        # 写入数据库
        self.insertJDData(name, comment_num, praise_rate, shop_name, price,
                          link, brand, tags, form_factor, platform,
                          introduction, Ptable_params)
        # exit(0)

  def getGoodsInfo(self):
    """
    返回值：
      name, comment_num, praise_rate, brand, tags, form_factor, platform, introduction, Ptable_params
      """
    name = ""
    comment_num = ""
    brand = ""
    tags = ""
    form_factor = ""
    platform = ""
    praise_rate = ""
    introduction = {}  # dict类型，会转成 json 字符串
    Ptable_params = {}  # dict类型，会转成 json 字符串

    # 获取 brand
    brand = self.driver.find_element_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[2]/div[1]/div[1]/ul[1]/li/a").text
    # print(brand)

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
    name = introduction["商品名称"]
    core_num = introduction.get("核心数量", '没有写，不讲武德')
    have_core_graphics_card = introduction.get("是否支持核显", "没有写，不讲武德")
    have_cpu_fan = introduction.get("是否自带风扇", "不带风扇")  # 如果没写，默认不带风扇
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
    platform = Ptable_params["主体"].get("平台类型", "没有写，不讲武德")
    Ptable_params = json.dumps(Ptable_params)  # 将 dict 转化为 json 字符串
    # pprint(Ptable_params)
    # exit(0)

    # 点击进入评论页面
    time.sleep(self.delay_time)
    comment_num, praise_rate = self.getCurrentCommentNumber()
    time.sleep(self.delay_time)

    return name, comment_num, praise_rate, brand, tags, form_factor, platform, introduction, Ptable_params

  def getCurrentCommentNumber(self):
    # 转到 商品评价 页面
    self.driver.find_element_by_xpath(
        "/html/body/div[*]/div[2]/div[1]/div[1]/ul/li[5]").click()
    time.sleep(self.delay_time * 2)

    # self.driver.execute_script(
    #     "window.scrollTo(0, 5 * document.body.scrollHeight / 6);")  # 下拉页面，从而显示隐藏界面
    # time.sleep(3 * self.delay_time)

    # 勾选 只看当前商品评价 选项
    try:
      self.driver.find_element_by_xpath(
          "/html/body/*/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[9]/label"
      ).click()
      time.sleep(self.delay_time * 2)
      comment_num = self.driver.find_element_by_xpath(
          "/html/body/*/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[1]/a/em").text
      comment_num = comment_num[1:-1]  # 去括号
      time.sleep(self.delay_time * 2)
      praise_rate = self.driver.find_element_by_xpath(
          "/html/body/*/div[2]/div[3]/div[2]/div[1]/div[1]/div").text
    except:
      print("Error!")
      comment_num = "100"
      praise_rate = "90%"

    return comment_num, praise_rate

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link,
                   brand, tags, form_factor, platform, introduction,
                   Ptable_params):
    '''
    description: Insert data into table ** motherboard **
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

    sql_insert = "INSERT INTO motherboard (name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, tags, form_factor, platform, introduction, Ptable_params) VALUES (%(name)s, %(comment_num)s,"\
        "%(praise_rate)s, %(shop_name)s, %(price)s, %(link)s, %(brand)s, %(tags)s, %(form_factor)s, "\
        "%(platform)s, %(introduction)s, %(Ptable_params)s)"
    value = {
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "tags": tags,
        "form_factor": form_factor,
        "platform": platform,
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
      # pprint(value)
    cursor.close()
    db.close()


if __name__ == "__main__":
  motherboard_spider = JDMotherboardSpider()
  motherboard_spider.motherboardSpider()
