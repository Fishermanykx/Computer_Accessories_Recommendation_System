'''
Description: 电脑配置单爬虫，爬取站点如下
  http://zj.zol.com.cn/top_diy.html
Author: Fishermanykx
Date: 2020-12-16 10:41:16
LastEditors: Fishermanykx
LastEditTime: 2020-12-17 01:17:04
'''
import codecs
import sys

import re
import time
import lxml
import json
import requests
import pandas
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from pprint import pprint

f = codecs.open("out.txt", "w+", 'utf-8')
sys.stdout = f


class GetConfigLists:

  def __init__(self):
    self.root_url = 'http://zj.zol.com.cn/'

    self.chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    self.chrome_options.add_experimental_option("prefs", prefs)
    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    # self.chrome_options.add_argument('--headless')
    self.driver = webdriver.Chrome(options=self.chrome_options)

    self.configs = {}  # 按 tag 存配置
    self.categories = [
        '经济实惠型', '家用学习型', '网吧游戏型', '商务办公型', '疯狂游戏型', '图形音像型', '豪华发烧型'
    ]
    self.url_indexs = [1, 2, 21, 6, 5, 8, 3]
    self.delay_time = 0.3
    for i in range(1, 8):
      self.configs[self.url_indexs[i-1]] = []

  def __del__(self):
    self.driver.close()

  def testFunc(self):
    url = 'http://zj.zol.com.cn/diy/detail/9680358.html'
    page_resp = requests.get(url, timeout=10)
    page_resp.raise_for_status()
    page_resp.encoding = page_resp.apparent_encoding
    page = page_resp.text
    # Construct soup object
    soup = BeautifulSoup(page, features="lxml")
    cfg_table = soup.find_all('tr', class_='tr1')
    # pprint(cfg_table)
    item_dict = {}
    keys = ['CPU', '主板', '内存', '硬盘', '固态硬盘', '显卡', '机箱', '电源', '散热器']
    total_price = 0
    for item in cfg_table:
      info = item.find_all('td', limit=4)
      accessory_type = info[0].text
      name = info[1].text
      num = int(info[2].text)
      unit_price = int(info[3].text[1:])
      item_dict[accessory_type] = {
          'name': name,
          'number': num,
          'unit_price': unit_price,
          'percentage': 0
      }
      if accessory_type in keys:
        total_price += num * unit_price

    # 统计各配件价格比例
    for key in keys:
      if key in item_dict:
        item_dict[key]['percentage'] = item_dict[key]['number'] * item_dict[
            key]['unit_price'] / total_price
      else:
        item_dict[key] = {
            'name': "NULL",
            'number': 0,
            'unit_price': 0,
            'percentage': 0
        }
    pprint(item_dict)

  def parseSingleTypeURLS(self, conf_type):
    '''
    description: 拿到某个分类的前10页的URL
    param {*} conf_type: int类型，取值范围为 url_indexs， 分别对应7种类型
    '''
    page_num = 1
    sub_page_urls = []  # 每个页面的子页面的入口 url
    total_page_num = 10
    for page_num in range(1, total_page_num + 1):
      cur_url = 'http://zj.zol.com.cn/list_c' + str(conf_type) + '_l1_1_' + str(
          page_num) + '.html'
      # 先用 selenium 滚到底
      self.driver.get(cur_url)
      time.sleep(0.5)
      self.driver.execute_script(
          "window.scrollTo(0,document.body.scrollHeight)")
      time.sleep(0.5)
      start_resp = self.driver.page_source
      soup = BeautifulSoup(start_resp, "lxml")  # 拿到主页面
      # print(soup)
      # self.driver.quit()
      # exit(0)

      # 解析该页面的所有子页面链接
      cfg_lis = soup.find_all('li', class_='outli')
      for cfg in cfg_lis:
        # 解析价格
        price = int(cfg.find('font').text[:-1])
        if price > 100000:
          # print("You are thinking peach")
          continue
        # 解析子页面链接
        sub_page_link = cfg.find('a', class_='link')['href']
        sub_page_urls.append(self.root_url + sub_page_link)
    # pprint(sub_page_urls)
    return sub_page_urls

  def getSingleTypeInfo(self, conf_type, urls):
    '''
    description: 获取单个类型的信息
    param {*}
      conf_type : 配置单分类
      urls : 在函数 parseSingleTypeURLS 中获得的链接
    return {*}
    '''
    for url in urls:
      page_resp = requests.get(url, timeout=10)
      page_resp.raise_for_status()
      page_resp.encoding = page_resp.apparent_encoding
      page = page_resp.text
      # Construct soup object
      soup = BeautifulSoup(page, features="lxml")
      cfg_table = soup.find_all('tr', class_='tr1')
      # pprint(cfg_table)
      item_dict = {}
      keys = ['CPU', '主板', '内存', '硬盘', '固态硬盘', '显卡', '机箱', '电源', '散热器']
      total_price = 0
      for item in cfg_table:
        info = item.find_all('td', limit=4)
        accessory_type = info[0].text
        name = info[1].text
        num = int(info[2].text)
        # 匹配数字
        pat = r'\d+'
        try:
          unit_price = int(re.search(pat, info[3].text).group())
        except:
          print(url)
          print(info[3].text)
          exit(1)
        item_dict[accessory_type] = {
            'name': name,
            'number': num,
            'unit_price': unit_price,
            'percentage': 0
        }
        if accessory_type in keys:
          total_price += num * unit_price

      # 统计各配件价格比例
      for key in keys:
        if key in item_dict:
          item_dict[key]['percentage'] = item_dict[key]['number'] * item_dict[
              key]['unit_price'] / total_price
        else:
          item_dict[key] = {
              'name': "NULL",
              'number': 0,
              'unit_price': 0,
              'percentage': 0
          }
      self.configs[conf_type].append(item_dict)
      time.sleep(self.delay_time)
    # pprint(self.configs[conf_type])

  def getConfigInfo(self):
    # 获取配置信息
    for cat in range(1, 8):
      num = self.url_indexs[cat-1]
      urls = self.parseSingleTypeURLS(num)
      self.getSingleTypeInfo(num, urls)
    pprint(self.configs)


if __name__ == "__main__":
  get_config_list = GetConfigLists()
  # get_config_list.testFunc()
  # urls = get_config_list.parseSingleTypeURLS(1)
  # get_config_list.getSingleTypeInfo(1, urls)
  get_config_list.getConfigInfo()
