'''
Description: 电脑配置单爬虫，爬取站点如下
  http://zj.zol.com.cn/top_diy.html
Author: Fishermanykx
Date: 2020-12-16 10:41:16
LastEditors: Fishermanykx
LastEditTime: 2020-12-16 11:07:33
'''

import re
import sys
import lxml
import requests
from bs4 import BeautifulSoup

f = open("out.txt", "w+")
sys.stdout = f


class GetConfigLists:

  def __init__(self):
    self.start_url = 'http://zj.zol.com.cn/top_diy.html'
    self.urls = {}  # 按 tag 存配置

  def testFunc(self):
    response = requests.get(self.start_url, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    # print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup.prettify())

  def parseURLS(self):
    start_resp = requests.get(self.start_url, timeout=30)
    start_resp.raise_for_status()
    start_resp.encoding = start_resp.apparent_encoding
    soup = BeautifulSoup(start_resp.text, "html.parser")


if __name__ == "__main__":
  get_config_list = GetConfigLists()
  get_config_list.testFunc()