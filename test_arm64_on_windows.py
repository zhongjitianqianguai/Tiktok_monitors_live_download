import os
import random
import re
import time
from threading import Thread
import json
import wget
from selenium.common import NoSuchElementException, WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver


def download(live_url, filename):
    print('开始下载', filename)
    # 过滤英文和汉字以外的字符
    filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', filename)
    wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
    print(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '下载完成', filename)
    cmd = ("ffmpeg -i /media/sd/Download/" + filename + ".flv -vcodec copy -acodec "
                                                        "copy /media/sd/Download/" + time.strftime('%Y-%m-%d-%H-%M-%S',
                                                                                                   time.localtime(
                                                                                                       time.time())) +
           filename + ".mp4")
    os.system(cmd)
    os.remove("/media/sd/Download/" + filename + ".flv")
    print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + '转码完成', filename)


def only_live(live_dict):
    live_browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
    live_browser.set_page_load_timeout(300)

    for liver in live_dict:
        live_browser.get(live_dict[liver])
        stream_is_get = False
        is_living = True
        while not stream_is_get and is_living:
            for request in live_browser.requests:
                # print(request)
                if ".flv" in str(request):
                    # 获取接口返回内容
                    print(str(request))
                    stream_is_get = True
                    time.sleep(2)
                    flv_name = str(request).split('.flv')[0]
                    if flv_name not in live_name:
                        print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                            time.localtime(time.time())) + "已获取" + liver + "流媒体：")
                        live_name.append(flv_name)
                        t = Thread(target=download, args=(str(request), liver))
                        t.start()
                    break
                else:
                    try:
                        # 校验是否下播了
                        if live_browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                            print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                                  liver, "已下播")
                            is_living = False
                            break
                    except NoSuchElementException:
                        continue


def only_home(home_dict):
    home_browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
    home_browser.set_page_load_timeout(300)
    for liver in home_dict:
        try:
            # if liver not in need_not_to_get:
            #     browser.get(home_links[liver])
            home_browser.get(home_dict[liver])
            # driver.get('live.douyin.com/'+live_links)
            liver = home_browser.find_element(By.CLASS_NAME, 'Nu66P_ba').text
            url = home_browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
            print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播", liver, "正在直播...")
            time.sleep(random.randint(2, 5))
            driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
            driver.get(url.split("?")[0])
            if liver not in live_room_dict:
                live_room_dict[liver] = url.split("?")[0]
            # 遍历请求列表
            stream_is_get = False
            is_living = True
            while not stream_is_get and is_living:
                for request in driver.requests:
                    # print(request)
                    if ".flv" in str(request):
                        # 获取接口返回内容
                        print(str(request))
                        stream_is_get = True
                        time.sleep(2)
                        flv_name = str(request).split('.flv')[0]
                        if flv_name not in live_name:
                            print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                                time.localtime(time.time())) + "已获取" + liver + "流媒体：")
                            live_name.append(flv_name)
                            t = Thread(target=download, args=(str(request), liver))
                            t.start()
                        driver.quit()
                        break
                    else:
                        try:
                            # 校验是否下播了
                            if driver.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                                      liver, "已下播")
                                driver.quit()
                                is_living = False
                                break
                        except NoSuchElementException:
                            continue
        except NoSuchElementException:
            time.sleep(random.randint(5, 20))
        except WebDriverException as e:
            print(e.msg)
            try:
                # 判断页面是否存在
                title = home_browser.title
                print("页面标题：", title)
            except WebDriverException as e:
                if isinstance(e, NoSuchWindowException):
                    print("页面已经关闭")
                    home_browser.quit()
                    browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                    continue
                else:
                    print("页面崩溃或无法访问")
                    home_browser.quit()
                    browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                    continue


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")

with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    live_room_dict = eval(file.read())

with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links_dict = eval(file.read())
live_name = []
home_links_dict_after_filter = {}
for home_link in home_links_dict:
    if home_link not in live_room_dict:
        home_links_dict_after_filter[home_link] = home_links_dict[home_link]
