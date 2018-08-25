import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit
import time

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

    def save_File(self, title, lists):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d_%H%M%S')
        # file open
        file = open(os.getcwd()+"/"+str(date)+"_"+self.__keyword+"_"+title+".txt", 'w', encoding='UTF-8')
        for list in lists:
            try:
                file.write(list)
            except:
                pass
        file.close()

    def bot_start(self):
        # Google 에 해당 키워드 검색 후 화면 이동
        self.__bot.search_keyword_based_on_google(self.__keyword)

        # Return Google Search List
        googleLinks = self.__bot.get_google_links()

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
                    if 'search' not in str(list):
                        externalLinks.append(list)
            for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                if list not in internalLinks:
                    if 'search' not in str(list):
                        internalLinks.append(list)

        # 링크들에 대해 TR 수행
        allLinks = googleLinks + externalLinks + internalLinks
        for i in googleLinks:
            print(i+"\n")
        count = 0

        print('탐색할 링크의 개수', len(allLinks))
        alllist = []
        sentencelist = []
        suclink = []
        faillink = []
        succount=0
        failcount=0
        for link in allLinks:
            if count == 2:
                break
            try:
                self.__bot.go_page(link)
                pageSource = self.__bot.get_page_source()

                alllist.append("--------------------------------------------------------------------------------------------------------------------\n")
                alllist.append(link+"\n\n")
                print('-----------------------------------------------------')
                count = count + 1
                print('link ' + str(count) + ' : ' + link)

                sentence = TextRank.SentenceTokenizer()
                sentencelist.append("--------------------------------------------------------------------------------------------------------------------\n")
                sentencelist.append(link+"\n")
                sentencelist.append("--------------------------------------------------------------------------------------------------------------------\n")

                for list in sentence.url2sentences(pageSource):
                    sentencelist.append(list+"\n")
                sentencelist.append("\n")

                textrank = TextRank.TextRank(pageSource)
        
                for row in textrank.summarize(3):
                    alllist.append(row+"\n")
                    print(row)
                    print()
                alllist.append("\n")

                alllist.append("[")
                for keyword in textrank.keywords():
                    alllist.append("\'"+keyword+"\', ")
                alllist.append("]\n\n")
                print('keywords :', textrank.keywords())
                print()
                print('-----------------------------------------------------')
                suclink.append(link+"\n")
                succount = succount + 1
            except:
                faillink.append(link+"\n")
                failcount = failcount + 1
                print('TR 중 Error 발생')
                continue

        print('Success... Good')
        self.save_File("TR결과", alllist)
        self.save_File("문장", sentencelist)
        suclink.append("\n\n"+str(succount))
        faillink.append("\n\n"+str(failcount))
        self.save_File("성공링크", suclink)
        self.save_File("실패링크", faillink)

        # 외부링크에 대해서 필터를 거친다.
        ## 내용 부분을 뽑아낸다.
        ###
        ## 내용 부분에 있는 링크들만을 get 한다.

        # 내부링크에 대해서 필터를 거친다.

        # 걸러진 링크들에 한해서 TR 알고리즘을 돌린다.

        # 키워드와 요약된 문장을 출력한다.


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
