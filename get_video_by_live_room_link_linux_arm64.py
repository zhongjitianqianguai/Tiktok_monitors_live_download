import random
import time
import urllib

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
            print("主播", host.text, "正在直播...")
            browser.get(url)
            # 遍历请求列表
            stream_url = ''
            stream_is_get = False
            while not stream_is_get:
                for request in browser.requests:
                    if '.flv' in request.url:
                        stream_is_get = True
                        stream_url = request.url
                        flv_name = stream_url.split('flv')[0].split('/')[-1]
                        if flv_name not in live_name:
                            print("已获取流媒体：", host.text, '的直播, \n开始下载...')
                            live_name.append(flv_name)
                        break
        except NoSuchElementException:
            print("主播尚未开播,将在1分钟后重试...")
            time.sleep(random.randint(20, 60))
            continue
