import json
import random
import time
from threading import Thread

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver


def through_live_room(live_room_link, host):
    live_options = Options()
    # 去掉"chrome正受到自动化测试软件的控制"的提示条
    live_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    live_options.add_experimental_option('useAutomationExtension', False)
    live_options.add_argument("--lang=zh_CN")
    live_browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=live_options)
    flv_name = ""
    while True:
        live_browser.get(live_room_link)
        for request in live_browser.requests:
            if ".flv" in str(request):
                # 获取接口返回内容
                print(str(request))
                time.sleep(2)
                if flv_name is not str(request).split('.flv')[0]:
                    print(time.strftime('%Y-%m-%d_%H:%M:%S',
                                        time.localtime(time.time())) + "已获取" + host + "流媒体：")
                    flv_name = str(request).split('.flv')[0]
                    # live_thread = Thread(target=download, args=(str(request), host))
                    # live_thread.start()
                    time.sleep(random.randint(30, 90))
                break
            else:
                try:
                    # 校验是否下播了
                    if live_browser.find_element(By.CLASS_NAME, 'YQXSUEUr'):
                        print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播",
                              liver, "已下播")
                        time.sleep(random.randint(20, 60))
                        break
                except NoSuchElementException:
                    continue


options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links_dict = eval(file.read())
with open('Tiktok_live_room_link_by_auto_get.txt', encoding='utf-8') as f:
    live_room_dict = eval(f.read())
is_first_time = True
home_links_dict_tmp = home_links_dict.copy()
while True:
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
                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播", liver, "正在直播...")
                time.sleep(random.randint(2, 5))
                live_room_dict[actual_liver] = url.split("?")[0]
                home_links_dict_tmp.pop(actual_liver)
                with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                    file.write(json.dumps(live_room_dict, ensure_ascii=False))
                t = Thread(target=through_live_room, args=(url.split("?")[0], actual_liver))
                t.start()
            else:
                t = Thread(target=through_live_room, args=(live_room_dict[liver], liver))
                t.start()
        except NoSuchElementException:
            print("主播尚未开播,将在1分钟后重试...")
            time.sleep(random.randint(20, 60))
            continue
    home_links_dict = home_links_dict_tmp.copy()
