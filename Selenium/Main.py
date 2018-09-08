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
import re

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
random.seed(datetime.datetime.now())

class Bot():
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        self.__validation = Validation.Validation()
        self.__whiteList = re.compile('ko.wikipedia.org')
        self.__blackList = re.compile('youtube|facebook|www.google.co.kr/search?|mail:to|[a-z]{2}.wikipedia.org')
        self.__blackListExtension = re.compile('^\S+.(?i)(txt|pdf|hwp|xls|svg)$');

        self.__sentenceTokenizer = TextRank.SentenceTokenizer()

        # 정상적으로 종료된 링크 저장
        self.__linkDict = dict()
        self.__sentenceDict = dict()
        self.__keywordDict = dict()
        self.__distanceDict = dict()

        # 에러난 링크/메시지 저장
        self.__errorLinkDict = dict()
        self.__errorMessageDict = dict()
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

    def save_File(self, title):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')

        #file open
        file = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + "_" + title + ".txt", "w", encoding='UTF-8')
        file.write("------------------------------------------------------------------------------------------------------------------------\n")

        distanceDict = self.__distanceDict

        for i, distance in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
            try:
                file.write("link " + str(i) + ":" + str(self.__linkDict[i]) + "\n\n")
                file.write("sentence : " + str(self.__sentenceDict[i]) + "\n\n")
                file.write("keyword : " + str(self.__keywordDict[i]) + "\n\n")
                file.write("distance : " + str(distance) + "\n\n")
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
            except:
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
                pass

        errorFile = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + "_" + title + "_error.txt", "w", encoding='UTF-8')
        errorFile.write("------------------------------------------------------------------------------------------------------------------------\n")

        for i, link in self.__errorLinkDict.items():
            try:
                errorFile.write("link " + str(i) + ":" + link + "\n\n")
                errorFile.write("error message : " + str(self.__errorMessageDict[i]) + "\n\n")
                errorFile.write("------------------------------------------------------------------------------------------------------------------------\n")
            except:
                errorFile.write("------------------------------------------------------------------------------------------------------------------------\n")
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
        for index, link in enumerate(googleLinks):
            if self.linkFilter(link):
                continue

            try:
                # 해당 페이지의 page source get
                self.__bot.go_page(link)

                pageSource = self.__bot.get_page_source()
                bsObj = self.__bot.get_bs_obj(pageSource)
            except Exception as e:
                print(e)
                print('셀러니움 에러')
                continue

            try:
                # 외부 링크를 배제를 위한 host 부분 추출
                excludeUrl = self.__bot.split_address(link)

                # 외부 링크 흭득
                for externalLink in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                    if self.linkFilter(externalLink) or externalLink in externalLinks or externalLink in googleLinks:
                        continue
                    externalLinks.append(externalLink)

                # 내부 링크 흭득
                for internalLink in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                    if self.linkFilter(internalLink) or internalLink in internalLinks or internalLink in googleLinks:
                        continue
                    internalLinks.append(internalLink)

                # TODO: url 탐색 후 쿠키, 세션 삭제
            except Exception as e:
                print(e)
                print('외부/내부 링크 흭득 에러')
                continue

            try:
                textrank = TextRank.TextRank(pageSource)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()
                self.__validation.sum_str(self.__sentenceTokenizer.get_nouns(summarizes))
            except Exception as e:
                print(e)
                print('문서 요약 에러')
                continue

            self.printCommand(index, link, summarizes, keywords)

        # 전체 백터라이징
        self.__validation.base_vectorizing()

        ## 파일에 저장할 data 배열
        datas = []

        # 외부, 내부 링크들에 대해 TR 수행
        allLinks = externalLinks + internalLinks

        print("전체 링크수 : ", len(allLinks))

        self.travelLink(allLinks)

        self.__bot.quit()
        pass

    def travelLink(self, links):
        for (index, link) in enumerate(links):
            # 페이지 이동
            try:
                self.__bot.go_page(link)
                pageSource = self.__bot.get_page_source()
            except Exception as e:
                self.__errorLinkDict[index] = link
                self.__errorMessageDict[index] = e
                print(e)
                print('셀러니움 에러')
                continue

            try:
                # 요약문 구하기
                textrank = TextRank.TextRank(pageSource)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()
            except Exception as e:
                self.__errorLinkDict[index] = link
                self.__errorMessageDict[index] = e
                print(e)
                print('TextRank 에러')
                continue

            try:
                self.__validation.target_vectorizing(self.__sentenceTokenizer.get_nouns(summarizes))
            except Exception as e:
                self.__errorLinkDict[index] = link
                self.__errorMessageDict[index] = e
                print(e)
                print('vectorizer 에러')
                continue

            # 유클리드 거리 구하기
            try:
                # base와 target간에 유클리드 거리 구하기
                distance = self.__validation.dist_norm()

                if math.isnan(distance) == True:
                    raise ValueError

                self.__validation.set_dic(index, distance)
            except ValueError as e:
                self.__errorLinkDict[index] = link
                self.__errorMessageDict[index] = e
                print(e)
                print('distance가 nan입니다')
                continue
            except:
                self.__errorLinkDict[index] = link
                self.__errorMessageDict[index] = '유클리드 거리 구하기 에러'

                print('유클리드 거리 구하기 에러')
                continue

            self.printCommand(index, link, summarizes, keywords, distance)

            self.__linkDict[index] = link
            self.__sentenceDict[index] = summarizes
            self.__keywordDict[index] = keywords

        self.__distanceDict = self.__validation.get_dic()

        # for index, distance in sorted(dic.items(), key=lambda dic:dic[1]):
        #     if(index > 20):
        #         break
        #     alldistances[index] = distance

        self.save_File("요약문")

        pass

    def getIntersection(self, keywords):
        intersection = baseKeywordsSet & set(keywords)
        if(len(intersection) >= 2):
            return True
        else:
            return False

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

    def printCommand(self, index, link, summarizes, keywords, distance=None):
        print('----------------------------------')

        print('link', index, link)

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
