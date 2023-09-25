import os
import random
import time
from threading import Thread

import wget
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver


def download(live_url, filename):
    print('开始下载', filename)
    wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
    print('下载完成', filename)
    cmd = "ffmpeg -i /media/sd/Download/" + filename + ".flv -vcodec copy -acodec copy /media/sd/Download/" + filename + ".mp4"
    os.system(cmd)


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
follow_window = browser.current_window_handle
for follow_live in follow_live_lists:
    live_room_url = follow_live.get_attribute('href')
    liver = follow_live.find_element(By.CLASS_NAME, 'mY8V_PPX').text
    browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
    browser.get(live_room_url)
    time.sleep(1)
    stream_is_get = False
    while not stream_is_get:
        for request in browser.requests:
            # print(request)
            if ".flv" in str(request):
                # 获取接口返回内容
                print(str(request))
                time.sleep(2)
                flv_name = str(request).split('flv')[0]
                if flv_name not in live_name:
                    print("已获取流媒体：")
                    live_name.append(flv_name)
                    t = Thread(target=download, args=(str(request), liver))
                    t.start()
                    stream_is_get = True
                break
