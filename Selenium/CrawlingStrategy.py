from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup
import re
import datetime
import random
import ssl
from time import sleep
import requests

class CrawlingStrategy:
    def __init__(self):
        self.__googleLinks = []
        self.__internalLinks = []
        self.__externalLinks = []
        pass

    def get_html(self, url):
        _html = ""
        resp = requests.get(url)
        if resp.status_code == 200:
            _html = resp.text
        return _html

    def getGoogleLinks(self):
        return self.__googleLinks

    def getInternalLinks(self):
        return self.__internalLinks

    def getExternalLinks(self):
        return self.__externalLinks

    def getGoogleBaseLinks(self, keyword):
        self.__googleLinks = []
        self.__internalLinks = []
        self.__externalLinks = []

        google = 'https://www.google.co.kr'
        address = google + '/search?q=' + parse.quote(keyword)
        html = self.get_html(address)
        bsObj = BeautifulSoup(html, "html.parser")

        gs = bsObj.findAll("div", class_="g")

        for g in gs:
            a = g.find("a")

            if a == None:
                continue

            href = a.get('href')
            self.__googleLinks.append(google + href)
            # print(google + href)

        pass

    # 페이지에 발견된 내부 링크를 모두 목록으로 만듭니다.
    def getInternalLinksFromUrl(self, url):
        html = self.get_html(url)
        bsObj = BeautifulSoup(html, "html.parser")

        fullUrl = self.getFullUrl(url)
        includeUrl = self.splitAddress(url)

        # /로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
            if "http" in link.attrs['href']:
                if link.attrs['href'] not in self.__internalLinks:
                    self.__internalLinks.append(link.attrs['href'])
            else:
                if link.attrs['href'] not in self.__internalLinks:
                    if "//" in link.attrs['href']:
                        self.__internalLinks.append(fullUrl.split("/")[0]+link.attrs['href'])
                    else:
                        self.__internalLinks.append(fullUrl.split("/")[0]+"//"+includeUrl+link.attrs['href'])

        # for i in range(0, len(self.__internalLinks)):
        #     print(self.__internalLinks[i])

    # 페이지에서 발견된 외부 링크를 모두 목록으로 만듭니다.
    def getExternalLinksFromUrl(self, url):
        html = self.get_html(url)
        bsObj = BeautifulSoup(html, "html.parser")

        excludeUrl = self.splitAddress(url)
        fullUrl = self.getFullUrl(url)

        # /로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")):
            if "http" in link.attrs['href']:
                if link.attrs['href'] not in self.__externalLinks:
                    self.__externalLinks.append(link.attrs['href'])
            else:
                if link.attrs['href'] not in self.__externalLinks:
                    if "//" in link.attrs['href']:
                        self.__externalLinks.append(fullUrl.split("/")[0]+link.attrs['href'])
                    else:
                        self.__externalLinks.append(fullUrl.split("/")[0]+"//"+excludeUrl+link.attrs['href'])

        # for i in range(0, len(self.__externalLinks)):
        #     print(self.__externalLinks[i])

    def splitAddress(self, fullAddress):
        googleAddress = 'https://www.google.co.kr/url?q='
        arr = fullAddress.replace("https://", "").split('/')
        host = ""

        if(googleAddress in fullAddress):
            host = (arr[1])[6:]
        else:
            host = arr[0]

        return host

    def getFullUrl(self, fullAddress):
        googleAddress = 'https://www.google.co.kr/url?q='

        if(googleAddress in fullAddress):
            return fullAddress[31:]

        return fullAddress

# CrawlingStrategy = CrawlingStrategy()
# CrawlingStrategy.getGoogleBaseLinks('커피')
# CrawlingStrategy.getInternalLinksFromUrl('https://www.google.co.kr/url?q=https://namu.wiki/w/C%25EC%2596%25B8%25EC%2596%25B4&sa=U&ved=0ahUKEwj9qMX33areAhVFwbwKHeiKAEAQFggTMAA&usg=AOvVaw35MOt_h_jTe8RBzmUaFCsU')
# # # Crawler.getInternalLinksFromUrl('https://namu.wiki/w/C%EC%96%B8%EC%96%B4')
# CrawlingStrategy.getExternalLinksFromUrl('https://namu.wiki/w/C%EC%96%B8%EC%96%B4')
