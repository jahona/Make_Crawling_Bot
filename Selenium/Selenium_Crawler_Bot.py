from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
import ssl
import json
import os
from time import sleep

pages = set()
random.seed(datetime.datetime.now())

class Selenium_Scraping:
    def __init__(self, selenium_path):
        options = webdriver.ChromeOptions()
        # options.add_argument('--disable-extensions')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(selenium_path, chrome_options=options)
        pass

    def getInternalLinks(self, bsObj, includeUrl):
        internalLinks = []
        pattern = re.compile("^(/|.*"+includeUrl+")")

        pageSource = self.driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # /로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll("a", href=pattern):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in internalLinks:
                    internalLinks.append(link.attrs['href'])

        return internalLinks

    def getExternalLinks(self, bsObj, excludeUrl):
        externalLinks = []
        pattern = re.compile("^(http|www)((?!"+excludeUrl+").)*$")

        pageSource = self.driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # 현재 URL을 포함하지 않으면서 http나 www로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll('a', href=pattern):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in externalLinks:
                    externalLinks.append(link.attrs['href'])

        return externalLinks

    def splitAddress(self, fullAddress):
        hostParts = fullAddress.replace("http://", "").split("/")
        return hostParts

    def getRandomExternalLink(self, startingAddress):
        self.driver.get(startingAddress)
        sleep(1)

        pageSource = self.driver.page_source
        bsObj = BeautifulSoup(pageSource)

        externalLinks = self.getExternalLinks(bsObj, self.splitAddress(startingAddress)[0])

        if len(externalLinks) == 0:
            # internalLinks = self.getInternalLinks(bsObj, startingAddress)
            # return self.getNextExternalLInk(internalLinks[random.randint(0, len(internalLinks)-1)])
            pass
        else:
            return externalLinks[random.randint(0, len(externalLinks)-1)]

    def followExternalOnly(self, startingAddress):
        externalLink = self.getRandomExternalLink(startingAddress)
        print("Random external link is: "+externalLink)
        self.followExternalOnly(externalLink)
        pass

    def quit(self):
        self.driver.quit()
        pass


data=open(os.getcwd() + "/.env").read()

selenium_path = data.split('\n')[0].split('=')[1]

selenium_ins = Selenium_Scraping(selenium_path)
selenium_ins.followExternalOnly("http://oreilly.com")
