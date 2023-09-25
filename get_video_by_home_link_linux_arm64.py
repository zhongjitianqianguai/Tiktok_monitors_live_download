import os
import random
import time
from threading import Thread

import fake_useragent
import requests
import wget
from selenium.common import NoSuchElementException
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
with open('Tiktok_home_link.txt') as f:
    home_links = f.readlines()
with open('Tiktok_live_room_id.txt') as f:
    live_links = f.readlines()
while True:
    for home_link in home_links:
        # for live_link in live_links:
        try:
            browser.get(home_link)
            # driver.get('live.douyin.com/'+live_links)
            url = browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
            host = browser.find_element(By.CLASS_NAME, 'Nu66P_ba')
            liver = host.text
            print("主播", host.text, "正在直播...")
            time.sleep(random.randint(2, 5))
            driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
            driver.get(url)
            # 遍历请求列表
            stream_is_get = False
            while not stream_is_get:
                for request in driver.requests:
                    # print(request)
                    if ".flv" in request:
                        # 获取接口返回内容
                        time.sleep(2)
                        flv_name = str(request).split('flv')[0]
                        if flv_name not in live_name:
                            print("已获取流媒体：")
                            live_name.append(flv_name)
                            t = Thread(target=download, args=(request, liver))
                            t.start()
                            stream_is_get = True
                            break
        except NoSuchElementException:
            time.sleep(random.randint(20, 60))
