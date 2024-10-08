import random
import warnings
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from browsermobproxy import Server
import time

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    # 开启代理
    server = Server(r'browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
    server.start()
    proxy = server.create_proxy()

    # 配置Proxy
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--proxy-server={}'.format(proxy.proxy))
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(executable_path='webdriver/chromedriver.exe', options=chrome_options)
    live_name = []
    need_not_to_get = ['沙子哥', 'TTing', '维密', '小乖乖', '安慧灵', '念念想吃', '蠢媛小宝贝', '楠楠不想',
                       '系阿布甜甜', '你好特别']
    with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
        home_links = eval(file.read())
    # with open('Tiktok_live_room_id.txt') as f:
    #     live_links = f.readlines()
    while True:
        for liver in home_links:
            # for live_link in live_links:
            try:
                if liver not in need_not_to_get:
                    driver.get(home_links[liver])
                    # driver.get('live.douyin.com/'+live_links)
                    url = driver.find_element(By.XPATH, "//div[@class='RPhIHafP']/a").get_attribute('href')
                    host = driver.find_element(By.CLASS_NAME, 'Nu66P_ba')
                    print("主播", host.text, "正在直播...")
                    proxy.new_har('fetch', options={'captureContent': True, 'captureContent': True})
                    driver.get(url)
                    time.sleep(3)
                    json_data = proxy.har
                    for entry in json_data['log']['entries']:
                        # 根据URL找到数据接口
                        entry_url = entry['request']['url']
                        if ".flv" in entry_url:
                            # 获取接口返回内容
                            time.sleep(2)
                            flv_name = entry_url.split('flv')[0]
                            if flv_name not in live_name:
                                print("已获取流媒体：", entry_url, '\n开始下载...')
                                driver.get(entry_url)
                                live_name.append(flv_name)
                            break
            except NoSuchElementException:
                print("主播尚未开播,将在1分钟后重试...")
                time.sleep(random.randint(20, 60))
            except WebDriverException:
                continue
