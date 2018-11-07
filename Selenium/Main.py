import CrawlingStrategy
import TextRank
import Validation
import math

class Bot():
    def __init__(self):
        # 셀러니움 봇 생성
        self.__strategy = CrawlingStrategy.CrawlingStrategy()
        self.__validation = Validation.Validation()
        self.__validation.init_dic()
        self.__validation.init_base_normalized()
        self.__keyword = None
        self.__sentenceTokenizer = TextRank.SentenceTokenizer()
        
        pass

    def init(self):
        # 정상적으로 종료된 링크 저장
        
        self.__sentenceDict = dict()
        self.__distanceDict = dict()

    def setKeyword(self, keyword):
        self.__keyword = keyword
    
    def printCommand(self, index, googleLink, summarizes, keywords, distance=None):
        print('----------------------------------')

        print('url ', index, ' : ', googleLink)

        for i, summarize in enumerate(summarizes):
            if i<5:
                print(summarize)

        print(set(keywords))

        if distance is not None:
            print("distance: ", distance)

        print('----------------------------------')
        pass

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
        
        googleLinksCount = len(googleLinks)

        for index, googleLink in enumerate(googleLinks):
            try:
                Basesummarizes = []
                textrank = TextRank.TextRank(googleLink)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()

                for sentence in summarizes:
                    Basesummarizes.append(sentence)

                self.__validation.sum_str(self.__sentenceTokenizer.get_nouns(Basesummarizes))

                self.__validation.set_dic(index, 0)
            except:
                print('textrank not working')
                continue

            self.printCommand(index, googleLink, summarizes, keywords)
            self.__distanceDict = self.__validation.get_dic()

        # 비교 기준이 되는 문서들의 벡터 구하기
        self.__validation.base_vectorizing()

        for index, targetLink in enumerate(internalLinks + externalLinks):
            targetIndex = index + googleLinksCount

            try:
                textrank = TextRank.TextRank(targetLink)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()

                self.__validation.target_vectorizing(self.__sentenceTokenizer.get_nouns(summarizes))

                distance = self.__validation.dist_norm()

                if math.isnan(distance) == True:
                    raise ValueError
            except:
                print('textrank not working')
                continue
                
            self.__validation.set_dic(targetIndex, distance)
            self.printCommand(targetIndex, targetLink, summarizes, keywords, distance)
        pass
        
Bot = Bot()
Bot.setKeyword('C언어')
Bot.start()