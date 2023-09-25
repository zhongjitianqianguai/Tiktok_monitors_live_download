import os
import random
import time
from threading import Thread
import json
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
    os.remove("/media/sd/Download/" + filename + ".flv")


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
live_name = []
# with open('Tiktok_home_link.txt') as f:
#     home_links = f.readlines()
with open('Tiktok_live_room_id.txt') as f:
    need_not_to_get = f.readlines()
with open('Tiktok_live_room_id.txt') as f:
    live_links = f.readlines()
with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links = eval(file.read())
while True:
    for liver in home_links:
        # for live_link in live_links:
        try:
            if liver not in need_not_to_get:
                browser.get(home_links[liver])
                # driver.get('live.douyin.com/'+live_links)
                url = browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
                host = browser.find_element(By.CLASS_NAME, 'Nu66P_ba')
                liver = host.text
                print("主播", host.text, "正在直播...")
                time.sleep(random.randint(2, 5))
                driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                driver.get(url.split("?")[0])
                # 遍历请求列表
                stream_is_get = False
                while not stream_is_get:
                    for request in driver.requests:
                        # print(request)
                        if ".flv" in str(request):
                            # 获取接口返回内容
                            print(str(request))
                            stream_is_get = True
                            time.sleep(2)
                            flv_name = str(request).split('flv')[0]
                            if flv_name not in live_name:
                                print("已获取流媒体：")
                                live_name.append(flv_name)
                                t = Thread(target=download, args=(str(request), time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+liver))
                                t.start()
                            driver.quit()
                            break
        except NoSuchElementException:
            time.sleep(random.randint(5, 20))
