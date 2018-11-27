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

        # 문서 필터링
        self.__whiteList = re.compile('ko.wikipedia.org')
        self.__blackList = re.compile('youtube|facebook|www.google.co.kr/search?|mail:to|[a-z]{2}.wikipedia.org|wikimedia.org|wikidata.org|namu.live|downloads|instagram|imgurl|edit')
        self.__blackListExtension = re.compile('^\S+.(?i)(txt|pdf|hwp|xls|svg|jpg|exe|ftp|tar|xz|pkg|zip)$');
        self.__blackKeywordList = ['로그인']
        pass

    def linkFilter(self, link):
        stlink = str(link)
        m = self.__whiteList.search(stlink)
        # 화이트 리스트에 있다면 필터하지 않기
        if(m != None):
            return False

        m = self.__blackListExtension.search(stlink)
        if(m != None):
            return True

        # 블랙 리스트에 있다면 필터하기
        m = self.__blackList.search(stlink)
        if(m != None):
            return True

        # 아무것도 포함되지 않는다면 필터하지 않기
        return False

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

    def collectGoogleBaseLinks(self, keyword):
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
            googleLink = google + href

            if self.linkFilter(googleLink):
                continue

            self.__googleLinks.append(googleLink)

        pass

    # 페이지에 발견된 내부 링크를 모두 목록으로 만듭니다.
    def collectInternalLinksFromUrl(self, url):
        html = self.get_html(url)
        bsObj = BeautifulSoup(html, "html.parser")

        fullUrl = self.getFullUrl(url)
        includeUrl = self.splitAddress(url)

        # /로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
            if "http" in link.attrs['href']:
                if link.attrs['href'] not in self.__internalLinks:
                    href = link.attrs['href']
                    
            else:
                if link.attrs['href'] not in self.__internalLinks:
                    if "//" in link.attrs['href']:
                        href = fullUrl.split("/")[0]+link.attrs['href']
                    else:
                        href = fullUrl.split("/")[0]+"//"+includeUrl+link.attrs['href']

            if(self.linkFilter(href) == False):
                self.__internalLinks.append(href)
                
        # for i in range(0, len(self.__internalLinks)):
        #     print(self.__internalLinks[i])

    # 페이지에서 발견된 외부 링크를 모두 목록으로 만듭니다.
    def collectExternalLinksFromUrl(self, url):
        html = self.get_html(url)
        bsObj = BeautifulSoup(html, "html.parser")

        excludeUrl = self.splitAddress(url)
        fullUrl = self.getFullUrl(url)

        # /로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")):
            if "http" in link.attrs['href']:
                if link.attrs['href'] not in self.__externalLinks:
                    href = link.attrs['href']
            else:
                if link.attrs['href'] not in self.__externalLinks:
                    if "//" in link.attrs['href']:
                        href = fullUrl.split("/")[0]+link.attrs['href']
                    else:
                        href = fullUrl.split("/")[0]+"//"+excludeUrl+link.attrs['href']

            if(self.linkFilter(href) == False):
                self.__externalLinks.append(href)

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
