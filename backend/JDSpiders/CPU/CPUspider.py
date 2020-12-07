'''
Description: 
Author: Fishermanykx
Date: 2020-12-06 16:13:56
LastEditors: Fishermanykx
LastEditTime: 2020-12-07 08:47:08
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


class JDVideoCardSpider:

  def __init__(self):
    self.delay_time = 0.5  # 休眠时间
    self.chrome_options = Options()
    self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

  def CPUSpider(self):
    start_urls = []
    url_root = "https://list.jd.com/list.html?cat=670%2C677%2C678&page="
    page_num = 1
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
      cpu_urls = []
      # 对每页商品，爬取商品链接
      for i in range(60):
        tmp = 1
        while tmp:
          try:
            tmp = 0
            url_tmp = self.driver.find_element_by_xpath(
                "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                str(i + 1) + "]/div/div[3]/a").get_attribute("href")
            cpu_urls.append(url_tmp)
          except NoSuchElementException:
            try:
              tmp = 0
              url_tmp = self.driver.find_element_by_xpath(
                  "/html/body/div[7]/div/div[2]/div[1]/div/div[2]/ul/li[" +
                  str(i + 1) +
                  "]/div/div/div[2]/div[1]/div[3]/a").get_attribute("href")
              cpu_urls.append(url_tmp)
            except NoSuchElementException:
              temp = 1
              self.driver.refresh()
              self.driver.execute_script(
                  "window.scrollTo(0, 3 * document.body.scrollHeight / 4);")
              time.sleep(2 * self.delay_time)
              self.driver.execute_script(
                  "window.scrollTo(0, 5 * document.body.scrollHeight / 6);")
              time.sleep(2 * self.delay_time)
      # print(cpu_urls)
      # 进入每个商品的页面，逐一访问
      for i in range(60):
        time.sleep(self.delay_time)
        cpu_url = cpu_urls[i]
        self.driver.get(cpu_url)
        time.sleep(self.delay_time)
        # 点击商品，获取详细信息


if __name__ == "__main__":
  cpu_spider = JDCPUSpider()
  cpu_spider.CPUSpider()
