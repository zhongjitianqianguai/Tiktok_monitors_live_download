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
browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
browser.set_page_load_timeout(180)
live_name = []
home_link_dict = {}

# with open('Tiktok_live_room_id.txt') as f:
#     need_not_to_get = f.readlines()
with open('Tiktok_live_room_id.txt') as f:
    live_links = f.readlines()
# with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
#     home_links = eval(file.read())
with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    live_room_dict = eval(file.read())
while True:
    # for liver in home_links:
    start_time = time.time()
    with open('Tiktok_home_link.txt') as f:
        home_links = f.readlines()
    for home_link in home_links:
        # for live_link in live_links:
        try:
            # if liver not in need_not_to_get:
            #     browser.get(home_links[liver])
            browser.get(home_link)
            # driver.get('live.douyin.com/'+live_links)
            liver = browser.find_element(By.CLASS_NAME, 'Nu66P_ba').text
            if liver not in home_link_dict:
                home_link_dict[liver] = home_link
            url = browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
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

    end_time = time.time()
    print("本次爬取列表中所有主播花费时间：", (end_time - start_time) / 60, "分钟")
    if len(home_link_dict) == len(home_links):
        print('所有主播的直播间链接已获取完毕，可以考虑切换为直接访问直播间的模式')
    with open("Tiktok_home_link_by_auto_get.txt", "w", encoding='utf-8') as file:
        file.write(json.dumps(home_link_dict, ensure_ascii=False))
    with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
        file.write(json.dumps(live_room_dict, ensure_ascii=False))
