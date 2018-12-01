import BaseStrategy
import LinkFilter
import Node

from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup

import requests
import abc
import re

class CrawlingBehavior():
    def __init__(self, linkFilter):
        super(CrawlingBehavior, self).__init__()
        self.__linkFilter = linkFilter

    def __get_html(self, url):
        try:
            _html = ""
            resp = requests.get(url)
            if resp.status_code == 200:
                _html = resp.text
        except Exception:
            print('__get_html error')

        return _html

    def __split_address(self, fullAddress):
        googleAddress = 'https://www.google.co.kr/url?q='
        arr = fullAddress.replace("https://", "").split('/')
        host = ""

        if(googleAddress in fullAddress):
            host = (arr[1])[6:]
        else:
            host = arr[0]

        return host

    def __get_full_url(self, fullAddress):
        googleAddress = 'https://www.google.co.kr/url?q='

        if(googleAddress in fullAddress):
            return fullAddress[31:]

        return fullAddress

    def collect_google_base_links(self, keyword):
        google = 'https://www.google.co.kr'
        address = google + '/search?q=' + parse.quote(keyword)
        html = self.__get_html(address)
        bsObj = BeautifulSoup(html, "html.parser")

        gs = bsObj.findAll("div", class_="g")

        for g in gs:
            a = g.find("a")

            if a == None:
                continue

            href = a.get('href')
            href = google + href

            if self.__linkFilter._filter(href):
                continue

            node = Node.GoogleLinkNode(href)
            Node.GoogleLinkNode.add_to_google_link_node_storage(node)
        pass

    # 페이지에 발견된 내부 링크를 모두 목록으로 만듭니다.
    def collect_internal_links_from_url(self):
        googleLinkNodes = Node.GoogleLinkNode.get_nodes()
        
        for node in googleLinkNodes:
            html = self.__get_html(node.link)
            bsObj = BeautifulSoup(html, "html.parser")
            fullUrl = self.__get_full_url(node.link)
            includeUrl = self.__split_address(node.link)

            # /로 시작하는 링크를 모두 찾습니다.
            for link in bsObj.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
                if "http" in link.attrs['href']:
                    href = link.attrs['href']            
                else:
                    if "//" in link.attrs['href']:
                        href = fullUrl.split("/")[0]+link.attrs['href']
                    else:
                        href = fullUrl.split("/")[0]+"//"+includeUrl+link.attrs['href']

                if(self.__linkFilter._filter(href)):
                    continue
                
                node.add_to_internal_link(href)

                # print(href)

    # 페이지에서 발견된 외부 링크를 모두 목록으로 만듭니다.
    def collect_external_links_from_url(self):
        googleLinkNodes = Node.GoogleLinkNode.get_nodes()

        for node in googleLinkNodes:
            html = self.__get_html(node.link)
            bsObj = BeautifulSoup(html, "html.parser")

            excludeUrl = self.__split_address(node.link)
            fullUrl = self.__get_full_url(node.link)

            # /로 시작하는 링크를 모두 찾습니다.
            for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")):
                if "http" in link.attrs['href']:
                    href = link.attrs['href']
                else:
                    if "//" in link.attrs['href']:
                        href = fullUrl.split("/")[0]+link.attrs['href']
                    else:
                        href = fullUrl.split("/")[0]+"//"+excludeUrl+link.attrs['href']

                if(self.__linkFilter._filter(href)):
                    continue
                
                node.add_to_external_link(href)

                # print(href)

crawling = CrawlingBehavior(LinkFilter.LinkFilterStrategyOne())
crawling.collect_google_base_links('커피')

crawling.collect_internal_links_from_url()
crawling.collect_external_links_from_url()
# # # Crawler.getInternalLinksFromUrl('https://namu.wiki/w/C%EC%96%B8%EC%96%B4')
# CrawlingStrategy.getExternalLinksFromUrl('https://namu.wiki/w/C%EC%96%B8%EC%96%B4')