import CrawlerBot
import datetime
import random
import os
import TextRank

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
        keywords = []

        count = 0

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            # 해당 페이지의 page source get
            try:
                if(self.__bot.go_page(link)):
                    pageSource = self.__bot.get_page_source()
                    bsObj = self.__bot.get_bs_obj(pageSource)

                    count = count + 1
                    print('link ' + str(count) + ' : ' + link)

                    textrank = TextRank.TextRank(link)
                    for row in textrank.summarize(3):
                        print(row)
                        print()

                    print('keywords :', textrank.keywords())
                    print()
                    # # 외부 링크를 배제를 위한 host 부분 추출
                    # excludeUrl = self.__bot.split_address(link)
                    #
                    # for list in self.__bot.get_external_links(bsObj, excludeUrl, keyword):
                    #     if list not in externalLinks:
                    #         externalLinks.append(list)
                    # for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, keyword):
                    #     if list not in internalLinks:
                    #         internalLinks.append(list)
                else:
                    continue
            except:
                pass

        # 외부링크에 대해서 필터를 거친다.
        ## 내용 부분을 뽑아낸다.
        ###
        ## 내용 부분에 있는 링크들만을 get 한다.

        # 내부링크에 대해서 필터를 거친다.

        # 걸러진 링크들에 한해서 TR 알고리즘을 돌린다.

        # 키워드와 요약된 문장을 출력한다.


# variable
address = "https://www.google.co.kr"
keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
Bot.setKeyword(keyword)

# Bot start
Bot.bot_start()
