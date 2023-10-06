import json
import os
import random
import re
import time
import traceback
from threading import Thread
from urllib.error import HTTPError

import wget
from selenium.common import NoSuchElementException, WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as ec
import subprocess


def download(live_url, filename):
    live = filename
    print('开始下载', filename)
    # 过滤英文和汉字以外的字符
    filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', filename)
    try:
        wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
        print(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '下载完成', filename)
        cmd = ["ffmpeg", "-i", "/media/sd/Download/" + filename + ".flv", "-vcodec", "copy", "-acodec", "copy",
               "/media/sd/Download/" + time.strftime('%Y-%m-%d-%H-%M-%S',
                                                     time.localtime(time.time())) + filename + ".mp4"]
        with open("output.log", "w") as log:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
        os.remove("/media/sd/Download/" + filename + ".flv")
        print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + '转码完成', filename)
    except HTTPError as e:
        account_404 = 0
        if "404" in str(e):
            account_404 += 1
            print(e)
            print(traceback.format_exc())
            while True:
                try:
                    wget.download(live_url, '/media/sd/Download/' + filename + '.flv')
                    break
                except HTTPError as e:
                    if "404" in str(e):
                        account_404 += 1
                        print(e)
                        print(traceback.format_exc())
                        if account_404 > 10:
                            break
                        continue
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        live_downloading.pop(live)


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
options.add_argument("--shm-size=2048m")
# options.add_argument('--headless')
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
browser.set_page_load_timeout(300)
browser.scopes = [
    '.*stream-.*.flv.*',
]
live_downloading = {}
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
                WebDriverWait(browser, 20, 0.5).until(ec.presence_of_element_located((By.CLASS_NAME, 'st8eGKi4')))
                liver = browser.find_element(By.CLASS_NAME, 'st8eGKi4').text
                if browser.current_url not in live_room_dict.values():
                    live_room_dict[liver] = browser.current_url
            with open('live_link_need_to_get.txt', "w"):
                pass
            with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                file.write(json.dumps(live_room_dict, ensure_ascii=False))
            browser.quit()
            browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
            browser.set_page_load_timeout(300)
            browser.scopes = [
                '.*stream-.*.flv.*',
            ]
        live_room_dict_tmp = live_room_dict.copy()
        with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
            file.write(json.dumps(live_room_dict, ensure_ascii=False))
        for_start_time = time.time()
        for liver in live_room_dict:
            if liver in live_downloading:
                print(liver, "正在下载中...", "跳过爬取")
                continue
            browser.get(live_room_dict[liver])
            stream_is_get = False
            is_living = True
            stream_start_time = time.time()
            while not stream_is_get and is_living:
                if time.time() - for_start_time > 60 * 2:
                    browser.refresh()
                    for_start_time = time.time()
                    continue
                for request in browser.requests:
                    # print(request)
                    if ".flv" in str(request):
                        # 获取接口返回内容
                        flv_name = str(request).split('.flv')[0].split('/')[-1]
                        if flv_name not in live_downloading.values():
                            stream_is_get = True
                            actual_liver = browser.find_element(By.CLASS_NAME, 'st8eGKi4').text
                            print("主播", actual_liver, "正在直播...")
                            if actual_liver != liver:
                                live_room_dict_tmp.pop(liver)
                                live_room_dict_tmp[actual_liver] = browser.current_url
                                with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                                    file.write(json.dumps(live_room_dict_tmp, ensure_ascii=False))
                            print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                                time.localtime(time.time())) + "已获取" + actual_liver + "流媒体：")
                            print(str(request))
                            live_downloading[actual_liver] = flv_name
                            t = Thread(target=download, args=(str(request), actual_liver))
                            t.start()
                            pre_live_stream = str(request).split('.flv')[0].split('/')[-1]
                            browser.quit()
                            browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                            browser.set_page_load_timeout(300)
                            browser.scopes = [
                                '.*stream-.*.flv.*',
                            ]
                            stream_end_time = time.time()
                            print("本次抓取", actual_liver, "流媒体耗时：", (stream_end_time - stream_start_time) / 60,
                                  "分钟")
                            break
                try:
                    # 校验是否下播了
                    if browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):  # 直播已结束显示在中间
                        print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                              liver, "未开播")
                        is_living = False
                        break
                except NoSuchElementException:
                    try:
                        if browser.find_element(By.CLASS_NAME, 'JbEIkuHq'):  # 寻找点赞数量按钮
                            print("通过寻找点赞数量发现主播", liver, "正在直播...")
                            if not stream_is_get and liver not in live_downloading:
                                continue
                            else:
                                break
                    except NoSuchElementException:
                        print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())), "主播", liver, "未开播")
                        is_living = False
                        break
            if not stream_is_get:
                try:
                    actual_liver = browser.find_element(By.CLASS_NAME, 'st8eGKi4').text
                    if actual_liver != liver:
                        live_room_dict_tmp.pop(liver)
                    live_room_dict_tmp[actual_liver] = browser.current_url
                    with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                        file.write(json.dumps(live_room_dict_tmp, ensure_ascii=False))
                except NoSuchElementException:
                    try:
                        if browser.find_element(By.CLASS_NAME, 'P6wJrwQ6'):
                            print("因主播的设置，您不能观看此内容。")
                            continue
                    except NoSuchElementException:
                        print("网页加载异常")
                        if 4 < time.localtime(time.time()).tm_hour.real < 7:
                            print("凌晨4点到7点，且网页加载异常，降低爬取频率")
                            time.sleep(random.randint(60 * 5, 60 * 10))
                        browser.refresh()
                        continue

    except TimeoutError:
        print("网页加载超时")
        browser.quit()
        browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
        browser.set_page_load_timeout(300)
        browser.scopes = [
            '.*stream-.*.flv.*',
        ]
        continue
    except WebDriverException as e:
        print(e.msg)
        print(traceback.format_exc())
        try:
            # 判断页面是否存在
            title = browser.title
            print("页面标题：", title)
        except WebDriverException as e:
            if isinstance(e, NoSuchWindowException):
                print("页面已经关闭")
                browser.quit()
                browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                browser.set_page_load_timeout(300)
                browser.scopes = [
                    '.*stream-.*.flv.*',
                ]
                continue
            else:
                print("页面崩溃或无法访问")
                browser.quit()
                browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
                browser.set_page_load_timeout(300)
                browser.scopes = [
                    '.*stream-.*.flv.*',
                ]
                continue
    finally:
        time.sleep(random.randint(1, 3))
    end_time = time.time()
    print("本次通过直播间爬取", len(live_room_dict), "个主播耗时：", "共有", len(live_downloading), "个主播直播",
          (end_time - start_time) / 60, "分钟 平均耗时：", (end_time - start_time) / 60 / len(live_room_dict), "分钟")
