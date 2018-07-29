from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import ssl
from time import sleep
import random
import datetime
import os

random.seed(datetime.datetime.now())

class Selenium:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--disable-extensions')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')

        data=open(os.getcwd() + "/.env").read()
        selenium_path = data.split('\n')[0].split('=')[1]
        self.__driver = webdriver.Chrome(selenium_path, chrome_options=options)
        pass

    def split_address(self, fullAddress):
        hostParts = fullAddress.replace("http://", "").replace("https://", "").split("/")[0]
        return hostParts

    def search_keyword_based_on_google(self, keyword):
        self.go_page('https://www.google.co.kr')
        self.__driver.find_element_by_id('lst-ib').send_keys(keyword)
        self.__driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[3]/center/input[1]').click()
        pass

    def get_google_links(self):
        googleLinks = []

        gs = self.__driver.find_elements_by_class_name('g')

        for g in gs:
            href = g.find_element_by_tag_name('a').get_attribute('href')
            # print(href)
            googleLinks.append(href)

        return googleLinks

    def go_page(self, url):
        self.__driver.get(url)
        pass

    def get_current_url(self):
        return self.__driver.current_url

    def get_page_source(self):
        return self.__driver.page_source

    def get_bs_obj(self, pageSource):
        return BeautifulSoup(pageSource)

    def quit(self):
        self.__driver.quit()
        pass

    # 외부링크 리스트 얻기
    def get_external_links(self, bsObj, excludeUrl):
        externalLinks = []
        pattern = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")

        pageSource = self.__driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # 현재 URL을 포함하지 않으면서 http나 www로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll('a', href=pattern):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in externalLinks:
                    externalLinks.append(link.attrs['href'])

        return externalLinks

    # 내부링크 리스트 얻기
    def get_internal_links(self, bsObj, includeUrl):
        internalLinks = []
        pattern = re.compile("^(/|.*"+includeUrl+")")

        pageSource = self.__driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # /로 시작하거나 includeUrl이 들어있는 링크를 모두 찾습니다.
        for link in bsObj.findAll('a', href=pattern):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in internalLinks:
                    internalLinks.append(link.attrs['href'])

        return internalLinks