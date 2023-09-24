from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver

options = Options()
# 去掉"chrome正受到自动化测试软件的控制"的提示条
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--no-sandbox")
options.add_argument("--lang=zh_CN")
browser = webdriver.Chrome(service=Service('/user/bin/chromedriver'), options=options)

# 发送 HTTP 请求
browser.get('https://v.douyin.com/ieG1jt5D/')

# 遍历请求列表
stream_url = ''
stream_is_get = False
while not stream_is_get:
    for request in browser.requests:
        if '.flv' in request.url:
            print("流"+request.url)
            stream_is_get = True
            break
