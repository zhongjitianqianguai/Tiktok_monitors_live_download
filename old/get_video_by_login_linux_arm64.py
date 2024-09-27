import os
import random
import re
import time
from threading import Thread
from urllib.error import HTTPError

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
    try:
        wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
    except HTTPError:
        print("下载失败，尝试重新下载...")
        try:
            wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
        except HTTPError:
            print("下载失败，尝试重新下载...")
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


def through_live_room(live_room_link, host):
    live_options = Options()
    # 去掉"chrome正受到自动化测试软件的控制"的提示条
    live_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    live_options.add_experimental_option('useAutomationExtension', False)
    live_options.add_argument("--no-sandbox")
    live_options.add_argument("--lang=zh_CN")
    live_options.add_argument("--headless")
    live_browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=live_options)
    live_browser.set_page_load_timeout(300)
    flv_name = ""
    while True:
        try:
            live_browser.get(live_room_link)
            for request in live_browser.requests:
                if ".flv" in str(request):
                    # 获取接口返回内容
                    print(str(request))
                    time.sleep(2)
                    if flv_name is not str(request).split('.flv')[0]:
                        print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                            time.localtime(time.time())), "已获取", host, "流媒体：")
                        flv_name = str(request).split('.flv')[0]
                        live_thread = Thread(target=download, args=(str(request), host))
                        live_thread.start()
                        time.sleep(random.randint(30, 90))
                    break
                else:
                    try:
                        # 校验是否下播了
                        if live_browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                            # print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                            #       host, "已下播")
                            time.sleep(random.randint(20, 60))
                            break
                    except NoSuchElementException:
                        continue
        except WebDriverException as live_e:
            print(live_e.msg)
            print(live_e.stacktrace)
            try:
                # 判断页面是否存在
                live_title = live_browser.title
                print("页面标题：", live_title)
            except WebDriverException as live_e:
                if isinstance(live_e, NoSuchWindowException):
                    print("页面已经关闭")
                    live_browser.quit()
                    live_browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=live_options)
                    continue
                else:
                    print("页面崩溃或无法访问")
                    continue


is_first_time = True

while True:
    browser.get("https://www.douyin.com/follow")
    if is_first_time:
        input("请登录后按回车键继续...")
        is_first_time = False
    time.sleep(random.randint(5, 10))
    follow_live_list = browser.find_element(By.CLASS_NAME, 'X5RsU67Q')
    follow_live_lists = follow_live_list.find_elements(By.TAG_NAME, 'a')
    for follow_live in follow_live_lists:
        live_room_url = follow_live.get_attribute('href')
        liver = follow_live.find_element(By.CLASS_NAME, 'mY8V_PPX').text
        through_live_room(live_room_url, liver)
    time.sleep(random.randint(5, 10))


