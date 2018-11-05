import CrawlingStrategy
import TextRank

class Bot():
    def __init__(self):
        # 셀러니움 봇 생성
        self.__strategy = CrawlingStrategy.CrawlingStrategy()
        self.__keyword = None
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword

    def start(self):
        if(self.__keyword == None):
            print('Not keyword, So Exit')
            return

        googleLinks = self.__strategy.getGoogleLinks()
        if(len(googleLinks)==0):
            self.__strategy.getGoogleBaseLinks(self.__keyword)
            googleLinks = self.__strategy.getGoogleLinks()

        for googleLink in googleLinks:
            self.__strategy.getInternalLinksFromUrl(googleLink)
            self.__strategy.getExternalLinksFromUrl(googleLink)

        internalLinks = self.__strategy.getInternalLinks()
        externalLinks = self.__strategy.getExternalLinks()
        totLinks = internalLinks + externalLinks
        
Bot = Bot()
Bot.setKeyword('C언어')
Bot.start()