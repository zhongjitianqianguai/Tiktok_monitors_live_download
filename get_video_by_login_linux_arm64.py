import os
import random
import time
from threading import Thread

import wget
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
live_name = []

browser.get('https://live.douyin.com/')
input("请登录后按回车键继续...")
browser.get("https://www.douyin.com/follow")
time.sleep(random.randint(5, 10))
follow_live_list = browser.find_element(By.CLASS_NAME, 'X5RsU67Q')
follow_live_lists = follow_live_list.find_elements(By.TAG_NAME, 'a')
for follow_live in follow_live_lists:
    live_room_url = follow_live.get_attribute('href')
    browser.get(live_room_url)

