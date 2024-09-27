from selenium.webdriver.chrome.service import Service
from undetected_chromedriver import Chrome

browser = Chrome()
browser.set_page_load_timeout(300)
while True:
    with open('flv_link_need_to_download.txt', "r") as f:
        flv_links_need_to_download = f.readlines()
    if len(flv_links_need_to_download) > 0:
        browser.get(flv_links_need_to_download[0])
