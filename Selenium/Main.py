import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit
import threading
import logging
from time import sleep
import Validation
import time
import math

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
random.seed(datetime.datetime.now())

class Bot():
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        self.__validation = Validation.Validation()
        pass

    def setIsDev(self, dev):
        self.__dev = dev

    def setAddress(self, address):
        self.__address = address
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword
        pass

    def setBaseKeywordsSet(self, baseKeywordsSet):
        self.__baseKeywordsSet = baseKeywordsSet
        pass

    def save_File(self, title, lists):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')

        #file open
        file = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + "_" + title + ".txt", "a", encoding='UTF-8')
        file.write("------------------------------------------------------------------------------------------------------------------------\n")
        for list in lists:
            try:
                file.write(list)
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
            except:
                pass
        file.close()

    def bot_start(self):
        # Google 에 해당 키워드 검색 후 화면 이동
        self.__bot.search_keyword_based_on_google(self.__keyword)

        # Return Google Search List
        googleLinks = self.__bot.get_google_links()

        externalLinks = []
        internalLinks = []

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            if "search?" not in str(link):
                try:
                    # 해당 페이지의 page source get
                    self.__bot.go_page(link)

                    pageSource = self.__bot.get_page_source()
                    bsObj = self.__bot.get_bs_obj(pageSource)

                    # 외부 링크를 배제를 위한 host 부분 추출
                    excludeUrl = self.__bot.split_address(link)

                    # 외부 링크 흭득
                    for link in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                        if self.linkFilter(link) or link in externalLinks:
                            continue
                        externalLinks.append(link)

                    # 내부 링크 흭득
                    for link in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                        if self.linkFilter(link) or link in internalLinks:
                            continue
                        internalLinks.append(link)
                except:
                    pass

        ## 파일에 저장할 data 배열
        datas = []

        ## 구글 검색 리스트 첫 화면에서 요약문과 키워드, 그리고 문서 유사도를 위해 기준이 될 문장들을 추출
        for link in googleLinks:
            try:
                print('link', link)

                try:
                    self.__bot.go_page(link)
                    pageSource = self.__bot.get_page_source()
                except:
                    print('셀러니움 에러')
                    continue

                try:
                    # 요약문 구하기
                    textrank = TextRank.TextRank(pageSource)
                    summarizes = textrank.summarize(10)
                    keywords = textrank.keywords()
                except:
                    print('TextRank 에러')
                    continue

                try:
                    self.__validation.base_vectorizing(summarizes)
                except:
                    print('vectorizer 에러')
                    continue

                try:
                    self.printCommand(link, summarizes, keywords)
                except:
                    print('파일 입력 에러')
                    continue
            except Exception as ex:
                print('에러가 발생했습니다', ex)
                continue

        # 외부, 내부 링크들에 대해 TR 수행
        allLinks = externalLinks + internalLinks

        self.travelLink(allLinks)

        self.__bot.quit()
        pass

    def travelLink(self, links):
        for (index, link) in enumerate(links):
            try:
                print('link', link)

                # 페이지 이동
                try:
                    self.__bot.go_page(link)
                    pageSource = self.__bot.get_page_source()
                except:
                    print('셀러니움 에러')
                    continue

                try:
                    # 요약문 구하기
                    textrank = TextRank.TextRank(pageSource)
                    summarizes = textrank.summarize(10)
                    keywords = textrank.keywords()
                except:
                    print('TextRank 에러')
                    continue

                try:
                    self.__validation.target_vectorizing(summarizes)
                except:
                    print('vectorizer 에러')
                    continue

                # 유클리드 거리 구하기
                try:
                    # base와 target간에 유클리드 거리 구하기
                    distance = self.__validation.dist_norm()

                    if math.isnan(distance) == True:
                        raise ValueError

                    if distance < self.__validation.get_best_dist():
                        self.__validation.set_best_dist(d)
                        self.__validation.set_best_i(i)

                    self.__validation.set_dic(index, distance)
                except ValueError:
                    print('distance 이 nan입니다')
                    continue
                except:
                    print('유클리드 거리 구하기 에러')
                    continue

                # 파일 입력
                try:
                    self.printCommand(link, summarizes, keywords, distance)
                except:
                    print('파일 입력 에러')
                    continue

            except Exception as ex:
                print('에러가 발생했습니다', ex)
                continue

        dic = self.__validation.get_dic()

        for index, distance in sorted(dic.items(), key=lambda dic:dic[1]):
            # TODO: 최종적으로 파일 저장
            pass

        pass

    def getIntersection(self, keywords):
        intersection = baseKeywordsSet & set(keywords)
        if(len(intersection) >= 2):
            return True
        else:
            return False

    def linkFilter(self, link):
        blackList = ["search", "facebook", "wikipedia.org", "youtube", "mail:to"]
        whiteList = ["ko.wikipedia.org"]

        link = str(link)

        if link in blackList and link not in whiteList:
            return True

        return False

    def printCommand(self, link, summarizes, keywords, distance=None):
        print('----------------------------------')

        print('link: ', link)

        for summarize in summarizes:
            print(summarize)

        print(set(keywords))

        if distance is not None:
            print("distance: ", distance)

        print('----------------------------------')
        pass

# variable
address = "https://www.google.co.kr"
# keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)

Bot.setKeyword('c언어')
Bot.setIsDev(True)

# Bot start
start = timeit.default_timer()
Bot.bot_start()
stop = timeit.default_timer()
print(stop - start)
