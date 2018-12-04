import re
import abc

class LinkFilter(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def _filter(self, link):
        pass

    def test(self):
        print(1)

class LinkFilterStrategyOne(LinkFilter):
    def __init__(self):
        self.__blackList = re.compile('youtube|facebook|www.google.co.kr/search?|mail:to|[a-z]{2}.wikipedia.org|wikimedia.org|wikidata.org|namu.live|downloads|instagram|imgurl|edit|aladin|shop')
        self.__blackListExtension = re.compile('^\S+.(?i)(txt|pdf|hwp|xls|svg|jpg|exe|ftp|tar|xz|pkg|zip)$')
        self.__blackKeywordList = ['로그인']
        self.__whiteList = re.compile('ko.wikipedia.org')

    def _filter(self, link):
        stlink = str(link)

        m = self.__whiteList.search(stlink)
        # 화이트 리스트에 있다면 필터하지 않기
        if(m != None):
            return False
            
        m = self.__blackListExtension.search(stlink)
        if(m != None):
            return True

        # 블랙 리스트에 있다면 필터하기
        m = self.__blackList.search(stlink)
        if(m != None):
            return True

        # 아무것도 포함되지 않는다면 필터하지 않기
        return False


# linkFilterStrategyOne = LinkFilterStrategyOne()
# linkFilterStrategyOne.test()
