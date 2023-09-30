import json
import os
import random
import re
import time
from threading import Thread
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


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
browser.set_page_load_timeout(300)
live_name = []

while True:
    start_time = time.time()
    with open('live_link_need_to_get.txt', "r") as f:
        live_links_need_to_get = f.readlines()
    try:
        with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
            live_room_dict = eval(file.read())
        if len(live_links_need_to_get) > 0:
            for live_link in live_links_need_to_get:
                browser.get(live_link)
                liver = browser.find_element(By.CLASS_NAME, 'st8eGKi4').text
                if browser.current_url not in live_room_dict.values():
                    live_room_dict[liver] = browser.current_url
            with open('live_link_need_to_get.txt', "w"):
                pass
            with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                file.write(json.dumps(live_room_dict, ensure_ascii=False))
        live_room_dict_tmp = live_room_dict.copy()
        with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
            file.write(json.dumps(live_room_dict, ensure_ascii=False))
        for liver in live_room_dict:
            browser.get(live_room_dict[liver])
            stream_is_get = False
            is_living = True
            while not stream_is_get and is_living:
                for request in browser.requests:
                    # print(request)
                    if ".flv" in str(request):
                        # 获取接口返回内容
                        print(str(request))
                        print("主播", liver, "正在直播...")
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
                            if browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                                      liver, "已下播")
                                is_living = False
                                break
                        except NoSuchElementException:
                            continue
            if not stream_is_get:
                actual_liver = browser.find_element(By.CLASS_NAME, 'st8eGKi4').tex
                if actual_liver != liver:
                    live_room_dict_tmp.pop(liver)
                    live_room_dict_tmp[actual_liver] = browser.current_url
                    with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                        file.write(json.dumps(live_room_dict_tmp, ensure_ascii=False))
    except WebDriverException as e:
        print(e.msg)
        try:
            # 判断页面是否存在
            title = browser.title
            print("页面标题：", title)
        except WebDriverException as e:
            if isinstance(e, NoSuchWindowException):
                print("页面已经关闭")
                browser.quit()
                browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                continue
            else:
                print("页面崩溃或无法访问")
                browser.quit()
                browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                continue
    finally:
        time.sleep(random.randint(1, 3))
    end_time = time.time()
    print("本次通过直播间爬取", len(live_room_dict), "个主播耗时：", (end_time - start_time)/60, "分钟")
