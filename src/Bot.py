import CrawlingBehavior
import LinkFilter
import Node
import TextRank
import Validation
import Timer

from enum import Enum
from time import sleep
import math
import abc

class SingletonInstane:
  __instance = None

  @classmethod
  def __getInstance(cls):
    return cls.__instance

  @classmethod
  def instance(cls, *args, **kargs):
    print('create instance')
    cls.__instance = cls(*args, **kargs)
    cls.instance = cls.__getInstance
    return cls.__instance

class Status(Enum):
    INITIAL = 0 # 초기상태
    RUNNING = 1 # 동작상태
    STOPING = 2 # 중지상태

class Subject(metaclass=abc.ABCMeta):
    def __init__(self):
        self._observer = None
    
    def register_observer(self, observer):
        self._observer = observer

class Bot(SingletonInstane, Subject):
    def __init__(self):
        self.__behavior = CrawlingBehavior.CrawlingBehavior(LinkFilter.LinkFilterStrategyOne())
        self.__status = Status.INITIAL
        self.__keyword = None
        self.__timer = Timer.Timer()

        self.init()
        pass
    
    def get_status(self):
        return self.__status

    def get_link_dict(self):
        return self.__linkDict

    def get_sentence_dict(self):
        return self.__sentenceDict

    def get_keyword_dict(self):
        return self.__keywordDict

    def get_distance_dict(self):
        return self.__distanceDict

    def get_keword(self):
        return self.__keyword
        
    def init(self):
        self.__linkDict = dict()
        self.__sentenceDict = dict()
        self.__keywordDict = dict()
        self.__distanceDict = dict()
        self.__validation = Validation.Validation()
        self.__validation.init_dic()
        self.__validation.init_base_normalized()
        self.__sentenceTokenizer = TextRank.SentenceTokenizer()

    def set_keyword(self, keyword):
        self.__keyword = keyword

    def base_vectorize(self, index, link):
        try:
            Basesummarizes = []

            textrank = TextRank.TextRank(link)
            if(textrank is None):
                return
            
            summarizes = textrank.summarize(10)
            keywords = textrank.keywords()

            for sentence in summarizes:
                Basesummarizes.append(sentence)

            for sentence in textrank.sentences:
                for word in sentence.split(" "):
                    if word in self.__keyword:
                        Basesummarizes.append(sentence)
                        break

            flag = 0
            for keyword in keywords:
                if keyword in self.__keyword:
                    flag = 1
                    break

            if flag == 0:
                print("검색어가 키워드에 없습니다.")
                return

            self.__validation.sum_str(self.__sentenceTokenizer.get_nouns(Basesummarizes))
            self.__validation.set_dic(index, 0)
        except Exception as e:
            print('textrank 가 불가능한 링크입니다.')
            return
        
        self.printCommand(index, link, summarizes, keywords)

        self.__linkDict[index] = link
        self.__sentenceDict[index] = summarizes
        self.__keywordDict[index] = keywords

        self.__distanceDict = self.__validation.get_dic()

        self._observer.resultToGui()

    def target_vectorize(self, targetIndex, targetLink):
        try:
            textrank = TextRank.TextRank(targetLink)
            if(textrank is None):
                return

            summarizes = textrank.summarize(10)
            keywords = textrank.keywords()

            flag = 0
            for keyword in keywords:
                if keyword in self.__keyword:
                    flag = 1
                    break

            if flag == 0:
                print("검색어가 키워드에 없습니다.")
                return

            self.__validation.target_vectorizing(self.__sentenceTokenizer.get_nouns(summarizes))

            distance = self.__validation.dist_norm()

            if math.isnan(distance) == True:
                raise ValueError

            self.__validation.set_dic(targetIndex, distance)
        except:
            print('textrank 가 불가능한 링크입니다.')
            return

        self.printCommand(targetIndex, targetLink, summarizes, keywords, distance)

        self.__linkDict[targetIndex] = targetLink
        self.__sentenceDict[targetIndex] = summarizes
        self.__keywordDict[targetIndex] = keywords
        self.__distanceDict = self.__validation.get_dic()

        self._observer.resultToGui()

    def start(self):
        if(self.__keyword == None):
            print('keyword 가 셋팅되지 않았습니다. 셋팅해주세요')
            return

        if(self.__status == Status.STOPING):
            self.init()

        self.__status = Status.RUNNING
        self.__timer.start()

        self._observer.set_progress_bar(1)

        self.__behavior.collect_google_base_links(self.__keyword)
        self.__behavior.collect_internal_links_from_url()
        self.__behavior.collect_external_links_from_url()

        googleLinkNodes = Node.GoogleLinkNode.get_nodes()

        internalLinks = []
        externalLinks = []

        for node in googleLinkNodes:
            internalLinks += node.get_internal_links()
            externalLinks += node.get_external_links()

        googleLinksCount = len(googleLinkNodes)
        targetLinks = internalLinks + externalLinks
        targetLinksCount = len(targetLinks)
        print('target count : ', targetLinksCount)

        for index, node in enumerate(googleLinkNodes):
            if(self._observer.stop_thread_check()):
                break

            self.base_vectorize(index, node.link)

        self.__validation.base_vectorizing()
        
        for index, targetLink in enumerate(targetLinks):
            if(self._observer.stop_thread_check()):
                break

            if index % 100 == 0:
                sleep(1)

            targetIndex = index + googleLinksCount

            # 프로그레스바 값 설정
            self._observer.set_progress_bar(int((targetIndex+1)/(targetLinksCount + googleLinksCount)*100))

            self.target_vectorize(targetIndex, targetLink)

        self.__timer.end()
        self.__status = Status.STOPING

        print("검색어: " + self.__keyword)
        print("running time: " + str(self.__timer.getTime()))
        print(targetIndex+1)

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

# bot = Bot.instance()
# bot = Bot.instance()
# bot = Bot.instance()

# bot.set_keyword('커피')
# bot.start()