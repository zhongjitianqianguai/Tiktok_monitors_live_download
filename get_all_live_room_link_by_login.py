import os
import random
import re
import time
from urllib.parse import unquote

import wget
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
browser = webdriver.Chrome(service=Service('webdriver/chromedriver.exe'), options=options)
browser.set_page_load_timeout(300)


def match(text, *patterns):
    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


user_list = []
try:
    browser.get("https://www.douyin.com/follow")
    input("请登录后按回车键继续...")
    browser.find_element(By.CLASS_NAME, '').click()  # 点击头像
    time.sleep(4)
    browser.find_element(By.CLASS_NAME, '').click()  # 点击关注
    time.sleep(4)
    end = False
    while not end:
        # 执行下滑操作
        js_code = """
            el = document.querySelector("div[data-name=]>div.panel-body");
            el.scrollTo(0, el.scrollHeight);
        """
        browser.execute_script(js_code)
        time.sleep(2)  # 等待页面加载
        # 检查是否存在特定的文本
        try:
            divs = browser.find_elements(By.CLASS_NAME, 'div')  # 直至暂时没有更多了
            for div in divs:
                if div.text == '暂时没有更多了':
                    end = True
                    break
        except NoSuchElementException:
            pass  # 如果没有找到特定元素，继续下滑
    follow_list = browser.find_element(By.CLASS_NAME, '')
    follow_list_users = follow_list.find_elements(By.TAG_NAME, 'a')

    for follow_user in follow_list_users:
        user_url = follow_user.get_attribute('href')
        user_name = follow_user.find_element(By.CLASS_NAME, '').text
        user_list.append({user_name: user_url})
    for user in user_list:
        for user_name, user_url in user.items():
            browser.get(user_url)
            time.sleep(random.randint(10, 20))
            live_room_id = \
                match(unquote(browser.page_source.split('<script id="RENDER_DATA" type="application/json">')[1].split(
                    '</script>')[0]), r'"web_rid":"([^"]+)"')
            print(user_name, 'https://live.douyin.com/' + live_room_id)
            with open("Tiktok_live_room_link_by_auto_get.txt", "a", encoding='utf-8') as file:
                file.write(str({user_name: 'https://live.douyin.com/' + live_room_id}) + '\n')
        time.sleep(random.randint(5, 10))
except NoSuchElementException:
    time.sleep(random.randint(5, 10))
