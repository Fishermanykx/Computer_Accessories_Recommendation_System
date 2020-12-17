'''
Description: 
  frequency ：内存频率 (单位：MHz)
  total_capacity ：总容量 (单位：G)
  memory_num ：内存数量 (单条 or 套条)
  appearance ：外观特征 (普条/马甲条/RGB灯条)
  ddr_gen ：DDR代数 (ddr4/ddr3)
  introduction ：商品介绍的 .json
  Ptable_params ：规格与包装的 .json
Author: Fishermanykx
Date: 2020-12-07 13:12:01
LastEditors: Fishermanykx
LastEditTime: 2020-12-11 23:39:17
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


class JDMemorySpider:

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

    query = "truncate table memory"
    cursor.execute(query)
    db.commit()
    print("原表已清空")
    cursor.close()
    db.close()

  def memorySpider(self):
    start_urls = []
    url_root = "https://list.jd.com/list.html?cat=670%2C677%2C680&ev=210_1558%5E&page="
    page_num = 20
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
      time.sleep(2 * self.delay_time)
      self.driver.execute_script(
          "window.scrollTo(0, 5 * document.body.scrollHeight / 6);"
      )  # 下拉页面，从而显示隐藏界面
      time.sleep(3 * self.delay_time)

      memory_urls = []
      memory_prices = []
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
          print("Error in getting product name in the main page")
          print(url_tmp)
          continue

        if ("笔记本" in name):
          print(name)
          continue

        if ("京东自营" not in shop_name):
          continue
        shop_names.append(shop_name)
        # print(url_tmp)
        # print(shop_name)
        # exit(0)
        memory_urls.append(url_tmp)
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
        memory_prices.append(price)
        # print(price)
        # exit(0)
      # print(len(memory_urls))
      # print(len(memory_prices))
      # print(len(shop_names))
      # pprint(memory_urls)
      # pprint(memory_prices)
      # pprint(shop_names)
      # exit(0)
      self.valid_urls.append(len(memory_urls))
      # 进入每个商品的页面，逐一访问
      for i in range(len(memory_urls)):
        time.sleep(self.delay_time)
        link = memory_urls[i]
        price = memory_prices[i]
        shop_name = shop_names[i]
        self.driver.get(link)
        time.sleep(self.delay_time)
        # 点击商品，获取详细信息
        try:
          name, comment_num, praise_rate, brand, frequency, total_capacity,\
              memory_num, appearance, ddr_gen, introduction, Ptable_params \
              = self.getGoodsInfo()
        except:
          print("Error in function getGoodsInfo!")
          print(link)
          continue

        # 写入数据库
        self.insertJDData(name, comment_num, praise_rate, shop_name, price,
                          link, brand, frequency, total_capacity, memory_num,
                          appearance, ddr_gen, introduction, Ptable_params)
        # exit(0)

  def getGoodsInfo(self):
    """
    返回值：
      name, comment_num, praise_rate, brand, frequency, total_capacity, 
      memory_num, appearance, ddr_gen, introduction, Ptable_params
      """
    name = ""
    comment_num = ""
    praise_rate = ""
    brand = ""
    frequency = ""
    total_capacity = ""
    memory_num = ""
    appearance = ""
    ddr_gen = ""
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

    try:
      name = self.driver.find_element_by_xpath(
          "/html/body/div[6]/div/div[2]/div[1]").text
    except:
      name = introduction["商品名称"]
      print("Error getting name in product page")

    frequency = introduction.get("频率", '2400/2666 (原链接没写)')
    total_capacity = introduction.get("总容量", "8GB (原链接没写)")
    memory_num = introduction.get("内存数量", "1条单条 (原链接没写)")
    appearance = introduction.get("外观特征", "没有写")
    ddr_gen = introduction.get("DDR代数", "没有写")
    introduction = json.dumps(introduction)  # 将 dict 转化为 json 字符串
    # pprint(introduction)
    # exit(0)

    # 点击进入 规格与包装 页面
    time.sleep(self.delay_time)
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
    comment_num, praise_rate = self.getCurrentCommentNumber()

    return name, comment_num, praise_rate, brand, frequency, total_capacity, memory_num, appearance, ddr_gen, introduction, Ptable_params

  def getCurrentCommentNumber(self):
    cnt = 1
    changed = 0
    comment_num = "100"
    praise_rate = "90%"
    while cnt < 5:
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
        time.sleep(self.delay_time)

        # self.driver.execute_script(
        #     "window.scrollTo(0, 5 * document.body.scrollHeight / 6);")  # 下拉页面，从而显示隐藏界面

      # 勾选 只看当前商品评价 选项
        self.driver.find_element_by_xpath(
            "/html/body/div[*]/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[9]/label"
        ).click()
        time.sleep(self.delay_time * 2)
        comment_num = self.driver.find_element_by_xpath(
            "/html/body/div[*]/div[2]/div[3]/div[2]/div[2]/div[1]/ul/li[1]/a/em").text
        comment_num = comment_num[1:-1]  # 去括号
        time.sleep(self.delay_time * 2)
        praise_rate = self.driver.find_element_by_xpath(
            "/html/body/*/div[2]/div[3]/div[2]/div[1]/div[1]/div").text
        changed = 1
        break
      except:
        self.driver.refresh()
        time.sleep(3*self.delay_time)
        cnt += 1

    if (not changed):
      print("Error! Cannot get comment number")
    return comment_num, praise_rate

  def insertJDData(self, name, comment_num, praise_rate, shop_name, price, link, brand, frequency, total_capacity, memory_num, appearance, ddr_gen,
                   introduction, Ptable_params):
    '''
    description: Insert data into table ** memory **
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

    sql_insert = "INSERT INTO memory (name, comment_num, praise_rate, shop_name, price, link,"\
        "brand, frequency, total_capacity, memory_num, appearance, ddr_gen, introduction, "\
        "Ptable_params) VALUES (%(name)s, %(comment_num)s, %(praise_rate)s, %(shop_name)s, %(price)s"\
        ", %(link)s, %(brand)s, %(frequency)s, %(total_capacity)s, %(memory_num)s, %(appearance)s, "\
        "%(ddr_gen)s, %(introduction)s, %(Ptable_params)s)"
    value = {
        "name": name,
        "comment_num": comment_num,
        "praise_rate": praise_rate,
        "shop_name": shop_name,
        "price": price,
        "link": link,
        "brand": brand,
        "frequency": frequency,
        "total_capacity": total_capacity,
        "memory_num": memory_num,
        "appearance": appearance,
        "ddr_gen": ddr_gen,
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
  memory_spider = JDMemorySpider()
  memory_spider.memorySpider()
  print(memory_spider.valid_urls)
