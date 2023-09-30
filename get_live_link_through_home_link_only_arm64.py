import random
import time
import json
from selenium.common import NoSuchElementException, WebDriverException, NoSuchWindowException
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
home_browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
home_browser.set_page_load_timeout(300)

with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links_dict = eval(file.read())
live_name = []
home_browser.get("https://v.douyin.com/ienMvGbo/")
input("请在页面中完成人机验证后按回车键继续...")
while True:
    start_time = time.time()
    with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
        live_room_dict = eval(file.read())
    home_links_only_keys = home_links_dict.keys() - live_room_dict.keys()
    print("home_links_dict 中独有的键名：", home_links_only_keys)
    with open("home_link_need_to_get.txt", "r", encoding='utf-8') as file:
        home_links_need_to_get = file.readlines()
    try:
        if len(home_links_need_to_get) > 0:
            for home_link in home_links_need_to_get:
                home_browser.get(home_link)
                liver = home_browser.find_element(By.CLASS_NAME, 'Nu66P_ba').text
                if home_browser.current_url not in home_links_dict.values():
                    home_links_dict[liver] = home_browser.current_url
            with open("home_link_need_to_get.txt", "w", encoding='utf-8'):
                pass
            with open("Tiktok_home_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                file.write(json.dumps(home_links_dict, ensure_ascii=False))

        for liver in home_links_only_keys:
            try:
                home_browser.get(home_links_dict[liver])
                actual_liver = home_browser.find_element(By.CLASS_NAME, 'Nu66P_ba').text
                if liver != actual_liver:
                    home_links_dict[actual_liver] = home_links_dict[liver]
                    del home_links_dict[liver]
                    with open("Tiktok_home_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                        file.write(json.dumps(home_links_dict, ensure_ascii=False))
                url = home_browser.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
                print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) + "主播", actual_liver, "正在直播...")
                time.sleep(random.randint(2, 5))
                if actual_liver not in live_room_dict:
                    live_room_dict[actual_liver] = url.split("?")[0]
                with open("Tiktok_live_room_link_by_auto_get.txt", "w", encoding='utf-8') as file:
                    file.write(json.dumps(live_room_dict, ensure_ascii=False))
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
    end_time = time.time()
    print("本次爬取", len(home_links_only_keys), "个主播主页耗时：", (end_time - start_time)/60, "分钟还有",
          len(home_links_dict) - len(live_room_dict), "个主播直播间未爬取")
