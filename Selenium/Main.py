import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit
import logging
from time import sleep
import time

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
random.seed(datetime.datetime.now())

class Bot():
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
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

    def save_File(self, title, link):
        now = datetime.datetime.now()
        date = now.strftime('%T%m%d_%H%M%S')
        file = open(os.getcwd()+"/"+str(date)+"_"+self.__keyword+"_"+title+".txt", 'w', encoding='UTF-8')
        for list in lists:
            try:
                file.write(list)
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
        baseKeywordsList = []
        KeywordsList = []
        count = 0
        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            try:
                # 해당 페이지의 page source get
                self.__bot.go_page(link)

                pageSource = self.__bot.get_page_source()
                bsObj = self.__bot.get_bs_obj(pageSource)

                # 외부 링크를 배제를 위한 host 부분 추출
                excludeUrl = self.__bot.split_address(link)

                for list in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                    if list not in externalLinks:
                        if 'search' not in str(list):
                            externalLinks.append(list)
                for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                    if list not in internalLinks:
                        if 'search' not in str(list):
                            internalLinks.append(list)
                try:
                    print('-----------------------------------------------------')
                    count = count + 1
                    print('link', count, link)
                    self.__bot.go_page(link)
                    pageSource = self.__bot.get_page_source()

                    textrank = TextRank.TextRank(pageSource)

                    for row in textrank.summarize(20):
                        print(row)
                        print()

                    keywords = textrank.keywords()
                    keywordslist = []
                    for keyword in keywords:
                        baseKeywordsList.append(keyword)
                        keywordslist.append(keyword)
                    print('keywords :', keywordslist)
                    print('-----------------------------------------------------')
                except:
                    # logger.info('google link TR error')
                    continue
            except:
                # logger.info('google link travel error')
                pass

        allLinks = externalLinks + internalLinks
        print("모든 링크 개수 : "+str(len(allLinks)))
        for link in allLinks:
            try:
                count = count + 1
                print("-----------------------------------------------------")
                print('link', count, link)
                self.__bot.go_page(link)
                pageSource = self.__bot.get_page_source()

                textrank = TextRank.TextRank(pageSource)

                for row in textrank.summarize(3):
                    print(row)
                    print()

                keywords = textrank.keywords()
                keywordsSet = set(keywords)

                print('keywords :', keywordsSet)
                if(self.getIntersection(keywordsSet)):
                    print('link', i, ': ', link, '완료')
                print("-----------------------------------------------------")
            except:
                # logger.info('travelLink error')
                pass

        # # 쓰레드 개수만큼 봇 생성
        # self.createWorkerBot()
        #
        # for i in range(0, self.__numThreads):
        #     print('쓰레드 ', i, ' 가 탐색할 링크의 개수: ', workAmountList[i])
        #     start = i * workAmountList[i]
        #     end = (i + 1) * workAmountList[i]
        #     thread = threading.Thread(target=self.travelLink, args=(allLinks, start, end, i))
        #     thread.start()
        #     threads.append(thread)
        #
        # for thread in threads:
        #     thread.join()
        #
        # self.removeWorkerBot()

        self.__bot.quit()
        pass

        # 유튜브 링크 거르기
        # mail:to 링크 거르기

    # def travelLink(self, links, start, end, threadNum):
    #     print('Thread Num', threadNum, '실행')
    #     for i in range(start, end):
    #         try:
    #             print('-----------------------------------------------------')
    #             print('link', links[i])
    #             self.__driverOfWorker[threadNum].go_page(links[i])
    #             pageSource = self.__driverOfWorker[threadNum].get_page_source()
    #
    #             textrank = TextRank.TextRank(pageSource)
    #
    #             for row in textrank.summarize(3):
    #                 print(row)
    #                 print()
    #
    #             keywords = textrank.keywords()
    #             keywordsSet = set(keywords)
    #
    #             print('keywords :', keywordsSet)
    #             if(self.getIntersection(keywordsSet)):
    #                 print('link', i, ': ', links[i], '완료')
    #             print('-----------------------------------------------------')
    #         except:
    #             # logger.info('travelLink error')
    #             continue
    #     pass

    def getIntersection(keywords):
        intersection = baseKeywordsSet & set(keywords)
        if(len(intersection) >= 2):
            return True
        else:
            return False

    def get_page(self):
        self.__bot.go_page("https://commons.wikimedia.org/wiki/File:The_C_Programming_Language_logo.svg")
        pageSource = self.__bot.get_page_source()
        print(pageSource)
# variable
address = "https://www.google.co.kr"
# keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)

Bot.setKeyword('c언어')
Bot.setIsDev(True)

# Bot.get_page()

# Bot start
start = timeit.default_timer()
Bot.bot_start()
stop = timeit.default_timer()
print(stop - start)
