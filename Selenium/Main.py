import CrawlerBot
import datetime
import random
import os

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
        keywordLinks = []

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            # 해당 페이지의 page source get
            if(self.__bot.go_page(link)):
                pass
            else:
                continue
            pageSource = self.__bot.get_page_source()
            bsObj = self.__bot.get_bs_obj(pageSource)

            # 외부 링크를 배제를 위한 host 부분 추출
            excludeUrl = self.__bot.split_address(link)

            for list in self.__bot.get_external_links(bsObj, excludeUrl, keyword):
                if list not in externalLinks:
                    externalLinks.append(list)
            for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, keyword):
                if list not in internalLinks:
                    internalLinks.append(list)
            for list in self.__bot.get_keyword_text(bsObj, link, keyword):
                if list not in keywordLinks:
                    keywordLinks.append(list)

        exfile = open(os.getcwd()+"/"+str(date)+"_"+keyword+"_외부링크.txt", 'w', encoding='UTF-8')
        infile = open(os.getcwd()+"/"+str(date)+"_"+keyword+"_내부링크.txt", 'w', encoding='UTF-8')
        keyfile = open(os.getcwd()+"/"+str(date)+"_"+keyword+"_태그별문장.txt", 'w', encoding='UTF-8')

        for list in externalLinks:
            exfile.write(str(list)+"\n")
        for list in internalLinks:
            infile.write(str(list)+"\n")
        for list in keywordLinks:
            keyfile.write(str(list)+"\n\n")

        exfile.close()
        infile.close()
        keyfile.close()

# variable
address = "https://www.google.co.kr"
keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
Bot.setKeyword(keyword)

# Bot start
Bot.bot_start()
