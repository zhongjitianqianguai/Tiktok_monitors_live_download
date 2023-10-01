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


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
options.add_argument("--shm-size=2048m")
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
browser.set_page_load_timeout(300)

with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    live_room_dict = eval(file.read())

is_first_time = True
live_name = []
while True:
    browser.get("https://www.douyin.com/follow")
    if is_first_time:
        input("请登录后按回车键继续...")
        is_first_time = False
    time.sleep(random.randint(5, 10))
    follow_live_list = browser.find_element(By.CLASS_NAME, 'X5RsU67Q')
    follow_live_link_lists = follow_live_list.find_elements(By.TAG_NAME, 'a')
    is_living_dict = {}
    for follow_live in follow_live_link_lists:
        live_room_url = follow_live.get_attribute('href').split("?")[0]
        liver = follow_live.find_element(By.CLASS_NAME, 'mY8V_PPX').text
        is_living_dict[liver] = live_room_url
    for liver in is_living_dict:
        if is_living_dict[liver] in live_room_dict.values() and liver not in live_room_dict.keys():
            live_room_dict[liver] = is_living_dict[liver]
            for old_liver in live_room_dict:
                if live_room_dict[old_liver] == is_living_dict[liver]:
                    live_room_dict.pop(old_liver)
            with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                file.write(json.dumps(live_room_dict, ensure_ascii=False))
    common_dict = {k: is_living_dict[k] for k in is_living_dict.keys() & live_room_dict.keys()
                   if is_living_dict[k] == live_room_dict[k]}
    for liver in common_dict:
        try:
            browser.get(common_dict[liver])
            stream_is_get = False
            is_living = True
            while not stream_is_get and is_living:
                for request in browser.requests:
                    # print(request)
                    if ".flv" in str(request):
                        # 获取接口返回内容
                        flv_name = str(request).split('.flv')[0].split('/')[-1]
                        stream_is_get = True
                        if flv_name not in live_name:
                            print("主播", liver, "正在直播...")
                            print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                                time.localtime(time.time())) + "已获取" + liver + "流媒体：")
                            print(str(request))
                            live_name.append(flv_name)
                            t = Thread(target=download, args=(str(request), liver))
                            t.start()
                            pre_live_stream = str(request).split('.flv')[0].split('/')[-1]
                            browser.quit()
                            browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                            break
                    else:
                        try:
                            # 校验是否下播了
                            if browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                                      liver, "下播了")
                                is_living = False
                                break
                        except NoSuchElementException:
                            continue
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

    time.sleep(random.randint(5, 10))
