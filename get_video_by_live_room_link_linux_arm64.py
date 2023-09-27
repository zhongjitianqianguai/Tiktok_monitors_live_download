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


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
browser.set_page_load_timeout(300)
with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links_dict = eval(file.read())
with open('Tiktok_live_room_link_by_auto_get.txt', encoding='utf-8') as f:
    live_room_dict = eval(f.read())
is_first_time = True
home_links_dict_tmp = home_links_dict.copy()
while True:
    start_time = time.time()
    for liver in home_links_dict:
        try:
            if liver not in live_room_dict:
                browser.get(home_links_dict[liver])
                if len(live_room_dict) is not len(home_links_dict) and is_first_time:
                    input("请在浏览器中完成人机验证后，按回车键继续...")
                    is_first_time = False
                actual_liver = browser.find_element(By.CLASS_NAME, 'Nu66P_ba').text
                if actual_liver is not liver:
                    home_links_dict_tmp[actual_liver] = home_links_dict_tmp[liver]
                    home_links_dict_tmp.pop(liver)
                    with open("Tiktok_home_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                        file.write(json.dumps(home_links_dict_tmp, ensure_ascii=False))
                    file.close()
                url = browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())), "主播", liver, "正在直播...")
                time.sleep(random.randint(2, 5))
                live_room_dict[actual_liver] = url.split("?")[0]
                home_links_dict_tmp.pop(actual_liver)
                with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                    file.write(json.dumps(live_room_dict, ensure_ascii=False))
                # t = Thread(target=through_live_room, args=(url.split("?")[0], actual_liver))
                # t.start()
            else:
                t = Thread(target=through_live_room, args=(live_room_dict[liver], liver))
                t.start()
        except NoSuchElementException:
            # print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())), "主播", liver,
            #       "尚未开播,将在1分钟后重试...")
            time.sleep(random.randint(20, 60))
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
                    continue
    home_links_dict = home_links_dict_tmp.copy()
    end_time = time.time()
    print("本次爬取列表中所有主播花费时间：", (end_time - start_time) / 60, "分钟")
