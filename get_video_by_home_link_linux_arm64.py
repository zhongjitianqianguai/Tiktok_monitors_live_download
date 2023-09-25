import os
import random
import time
from threading import Thread

import fake_useragent
import requests
import wget
from fake_useragent import UserAgent
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver


def download(live_url, filename):
    print('开始下载', filename)
    wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
    print('下载完成', filename)
    cmd = "ffmpeg -i " + filename + ".flv -vcodec copy -acodec copy " + filename + ".mp4"
    os.system(cmd)
    os.remove(filename + '.flv')


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
            json_data = requests.get(url, headers=UserAgent().random).json()
            stream_url = ''
            stream_is_get = False
            while not stream_is_get:
                for entry in json_data['log']['entries']:
                    # 根据URL找到数据接口
                    entry_url = entry['request']['url']
                    if ".flv" in entry_url:
                        # 获取接口返回内容
                        stream_is_get = True
                        flv_name = entry_url.split('flv')[0]
                        if flv_name not in live_name:
                            t = Thread(target=download, args=(
                                entry_url,
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ":" +
                                liver))
                            t.start()
                            print("已获取流媒体")
                            live_name.append(flv_name)
                        break

        except NoSuchElementException:
            time.sleep(random.randint(20, 60))
