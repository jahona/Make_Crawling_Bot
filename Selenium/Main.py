import CrawlerBot

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

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            # 해당 페이지의 page source get
            self.__bot.go_page(link)
            pageSource = self.__bot.get_page_source()
            bsObj = self.__bot.get_bs_obj(pageSource)

            # 외부 링크를 배제를 위한 host 부분 추출
            excludeUrl = self.__bot.split_address(link)

            externalLinks = self.__bot.get_external_links(bsObj, excludeUrl)

            for i in externalLinks:
                print(i)

# variable
address = "https://www.google.co.kr"
keyword = "C언어"

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
Bot.setKeyword(keyword)

# Bot start
Bot.bot_start()
