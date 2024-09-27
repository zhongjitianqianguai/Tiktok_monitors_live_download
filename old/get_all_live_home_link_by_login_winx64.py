import os
import random
import time
from threading import Thread

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
live_name = []
liver_link = {}

browser.get('https://live.douyin.com/')
input("请登录后按回车键继续...")

browser.get("https://www.douyin.com/user/self")
browser.find_element(By.CLASS_NAME, 'Y150jDoF').click()
input("请手动下拉加载完所有关注后按回车键继续...")
follow_list = browser.find_element(By.CLASS_NAME, 'Pxf0E4cv')
follow_lists = follow_list.find_elements(By.CLASS_NAME, 'vcEWxPjN')
for follow in follow_lists:
    follow_link = follow.find_element(By.CLASS_NAME, 'dxFWVDGf').find_element(By.TAG_NAME, 'a').get_attribute('href')
    follow_name = follow.find_element(By.CLASS_NAME, 'Nu66P_ba').text
    liver_link[follow_name] = follow_link
print(liver_link)

