import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit

random.seed(datetime.datetime.now())

class Bot:
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        self.__depth = 0
        pass

    def setAddress(self, address):
        self.__address = address
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword
        pass

    def bot_start(self):
        # Google 에 해당 키워드 검색 후 화면 이동
        self.__bot.search_keyword_based_on_google(self.__keyword)

        # Return Google Search List
        googleLinks = self.__bot.get_google_links()

        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d_%H%M%S')

        externalLinks = []
        internalLinks = []

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            # 해당 페이지의 page source get
            self.__bot.go_page(link)

            pageSource = self.__bot.get_page_source()
            bsObj = self.__bot.get_bs_obj(pageSource)

            # 외부 링크를 배제를 위한 host 부분 추출
            excludeUrl = self.__bot.split_address(link)

            for list in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                if list not in externalLinks:
                    externalLinks.append(list)
            for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                if list not in internalLinks:
                    internalLinks.append(list)

        # file open
        exfile = open(os.getcwd()+"/"+str(date)+"_"+self.__keyword+"_TR결과.txt", 'w', encoding='UTF-8')

        count = 0

        # 먼저, 구글 검색 리스트로부터 얻은 링크들을 TR 수행
        baseKeywordsList = []

        print('구글 리스트에서 탐색할 링크의 개수', len(googleLinks))
        for link in googleLinks:
            try:
                print('-----------------------------------------------------')
                count = count + 1
                print('link ' + str(count) + ' : ' + link)

                textrank = TextRank.TextRank(link)

                for row in textrank.summarize(3):
                    print(row)
                    print()

                keywords = textrank.keywords()

                for keyword in keywords:
                    baseKeywordsList.append(keyword)

                print('keywords :', keywords)
                print()

                print('-----------------------------------------------------')
            except:
                print('TR 중 Error 발생')
                continue

        baseKeywordsSet = set(baseKeywordsList)

        # 외부, 내부 링크들에 대해 TR 수행
        allLinks = externalLinks + internalLinks

        print('탐색할 링크의 개수', len(allLinks))
        for link in allLinks:
            try:
                print('-----------------------------------------------------')
                count = count + 1
                print('link ' + str(count) + ' : ' + link)

                textrank = TextRank.TextRank(link)

                for row in textrank.summarize(3):
                    print(row)
                    print()

                keywords = textrank.keywords()

                print('keywords :', keywords)
                print()

                intersection = baseKeywordsSet & set(keywords)
                print(intersection)
                print('-----------------------------------------------------')
            except:
                print('TR 중 Error 발생')
                continue

        print('Success... Good')
        exfile.close()

        # 문서랑 검색어와의 연관도를 판단함
        ## 문서 TR 산출물인 키워드랑 검색어랑 비교를 해야함
        ### 구글 링크 리스트에서 얻은 키워드들을 기준으로 하여 외부링크, 내부링크로부터 얻는 문서의 키워드랑 비교

        # 쓰레드 해서 속도 향상

# variable
address = "https://www.google.co.kr"
# keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
Bot.setKeyword('c언어')

# Bot start
start = timeit.default_timer()
Bot.bot_start()
stop = timeit.default_timer()
print(stop - start)
