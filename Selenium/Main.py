import CrawlerBot

class Bot:
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        pass

    def setStartAddress(self, startAddress):
        self.__startAddress = startAddress
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword
        pass

    def bot_start(self):
        # Google 에 해당 키워드 검색
        self.__bot.search_keyword_based_on_google(self.__keyword)

        # self.__bot.followExternalOnly(self.__startAddress)

startAddress = "https://www.google.co.kr"
keyword = "C언어"

# Bot Setting
Bot = Bot()
Bot.setStartAddress(startAddress)
Bot.setKeyword(keyword)

# Bot start
Bot.bot_start()
