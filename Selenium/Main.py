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
        # self.__bot.followExternalOnly(self.__startAddress)


# variable
address = "https://www.google.co.kr"
keyword = "C언어"

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
Bot.setKeyword(keyword)

# Bot start
Bot.bot_start()
