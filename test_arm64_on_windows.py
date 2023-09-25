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
    wget.download(live_url, filename + '.flv')
    print('下载完成', filename)
    cmd = "ffmpeg -i " + filename + ".flv -vcodec copy -acodec copy " + filename + ".mp4"
    os.system(cmd)
    os.remove("/media/sd/Download/" + filename + ".flv")


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
while True:
    browser.get("https://www.douyin.com/follow")
    time.sleep(random.randint(5, 10))
    follow_live_list = browser.find_element(By.CLASS_NAME, 'X5RsU67Q')
    follow_live_lists = follow_live_list.find_elements(By.TAG_NAME, 'a')
    for follow_live in follow_live_lists:
        live_room_url = follow_live.get_attribute('href')
        liver = follow_live.find_element(By.CLASS_NAME, 'mY8V_PPX').text
        liver_link[liver] = live_room_url
    time.sleep(1)
    for liver in liver_link:
        browser.get(liver_link[liver])
        time.sleep(1)
        stream_is_get = False
        while not stream_is_get:
            #校验是否关播了
            for request in browser.requests:
                # print(request)
                if ".flv" in str(request):
                    # 获取接口返回内容
                    print(str(request))
                    time.sleep(2)
                    flv_name = str(request).split('flv')[0]
                    if flv_name not in live_name:
                        print("已获取流媒体")
                        live_name.append(flv_name)
                        t = Thread(target=download, args=(
                            str(request), time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())) + liver))
                        t.start()
                        stream_is_get = True
                    browser.close()
                    break
