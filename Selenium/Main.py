import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit
import threading
import logging
from time import sleep
import Document_similarity
import time
import math

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
random.seed(datetime.datetime.now())

class Bot():
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        self.__DS = Document_similarity.Document_similarity()
        pass

    def setIsDev(self, dev):
        self.__dev = dev

    def setAddress(self, address):
        self.__address = address
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword
        pass

    def setBaseKeywordsSet(self, baseKeywordsSet):
        self.__baseKeywordsSet = baseKeywordsSet
        pass

    def setNumThreads(self, numThreads):
        self.__numThreads = numThreads
        pass

    def createWorkerBot(self):
        self.__driverOfWorker = []

        for i in range(0, self.__numThreads):
            print ('workder bot create:', i)
            self.__driverOfWorker.append(CrawlerBot.Selenium())

    def removeWorkerBot(self):
        try:
            for i in range(0, self.__numThreads):
                print ('workder bot remove:', i)
                self.__driverOfWorker[i].quit()
        except:
            print('__numThreads not existed')

    def save_File(self, title, lists):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        #file open
        file = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + "_" + title + ".txt", "a", encoding='UTF-8')
        file.write("------------------------------------------------------------------------------------------------------------------------\n")
        for list in lists:
            try:
                file.write(list)
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
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
            if "search?" not in str(link):
                try:
                    # 해당 페이지의 page source get
                    self.__bot.go_page(link)

                    pageSource = self.__bot.get_page_source()
                    bsObj = self.__bot.get_bs_obj(pageSource)

                    # 외부 링크를 배제를 위한 host 부분 추출
                    excludeUrl = self.__bot.split_address(link)

                    for link in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                        if self.linkFilter(link) or link in externalLinks:
                            continue
                        externalLinks.append(link)
                    for link in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                        if self.linkFilter(link) or link in internalLinks:
                            continue
                        internalLinks.append(link)
                except:
                    # logger.info('google link travel error')
                    pass

        # 먼저, 구글 검색 리스트로부터 얻은 링크들을 TR 수행
        baseKeywordsList = []

        filelink = []
        filesentence = []
        for link in googleLinks:
            try:
                print('-----------------------------------------------------')
                print('link', link)
                self.__bot.go_page(link)
                pageSource = self.__bot.get_page_source()

                # TextRank의 url2sentences을 사용하기 위함. 전체 문장 가져오기
                # set_basepagesouce()를 이용해 각 문서의 모든 문장들을 하나의 배열에 append
                document = TextRank.SentenceTokenizer()
                sentences = document.url2sentences(pageSource)

                self.__DS.add_sentences_to_base(sentences)

                filelink.append("\n" + link + "\n\n")
                filesentence.append("\n" + link + "\n\n")

                for sentence in sentences:
                    filesentence.append(sentence + "\n")

                textrank = TextRank.TextRank(pageSource)

                for row in textrank.summarize(20):
                    filelink.append(row + "\n")
                    print(row)
                    print()

                filelink.append("\n")

                keywords = textrank.keywords()
                filelink.append(str(keywords)+"\n")

                for keyword in keywords:
                    baseKeywordsList.append(keyword)
                print(baseKeywordsList)

                filelink.append("\n\n")

                print('-----------------------------------------------------')
            except:
                print('error')
                # logger.info('google link TR error')
                continue

        self.save_File("구글링크_요약문", filelink)
        self.save_File("구글링크_문장", filesentence)

        self.__DS.base_vectorizing()

        # 중복 제거를 위해 set 으로 변경
        baseKeywordsSet = set(baseKeywordsList)
        self.setBaseKeywordsSet(baseKeywordsSet)

        # 외부, 내부 링크들에 대해 TR 수행
        allLinks = externalLinks + internalLinks
        countOfLink = len(allLinks)
        workAMountOfEachLink = int(float(countOfLink / self.__numThreads));

        workAmountList = []
        for i in range(0, self.__numThreads):
            workAmountList.append(workAMountOfEachLink);

        workAmountList[self.__numThreads-1] += countOfLink % self.__numThreads

        print('탐색할 링크의 개수', countOfLink)
        print('쓰레드 개수', self.__numThreads)

        threads = []

        # 쓰레드 개수만큼 봇 생성
        self.createWorkerBot()

        for i in range(0, self.__numThreads):
            print('쓰레드 ', i, ' 가 탐색할 링크의 개수: ', workAmountList[i])

            start = i * workAmountList[0]

            if(i == self.__numThreads-1):
                end = countOfLink
            else:
                end = (i + 1) * workAmountList[0]

            print(start, end)

            thread = threading.Thread(target=self.travelLink, args=(allLinks, start, end, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        self.removeWorkerBot()

        self.__bot.quit()
        pass

    def travelLink(self, links, start, end, threadNum):
        filelink = []
        filesentence = []
        filesuccesslink = []
        filefaillink = []
        filesimilarity = []

        print('Thread Num', threadNum, '실행')
        for i in range(start, end):
            try:
                print('-----------------------------------------------------')
                print('link', i, links[i])
                self.__driverOfWorker[threadNum].go_page(links[i])
                pageSource = self.__driverOfWorker[threadNum].get_page_source()

                document = TextRank.SentenceTokenizer()
                sentences = document.url2sentences(pageSource)

                self.__DS.set_target_sentence(sentences)
                self.__DS.target_vectorizing()

                # 벡터 사이의 거리를 구하기 위해서는 1차원 배열을 이용해야 하기 때문에 [0], 인덱스를 지정합니다.
                post_vec = self.__DS.get_post_vec().toarray()[0]
                new_post_vec = self.__DS.get_new_post_vec().toarray()[0]

                d = self.__DS.dist_norm(post_vec, new_post_vec)

                if math.isnan(d):
                    continue
                    
                print("=== link %i with dist = %.2f" % (i, d))

                if d < self.__DS.get_best_dist():
                    self.__DS.set_best_dist(d)
                    self.__DS.set_best_i(i)

                self.__DS.set_dic(i, d)

                filelink.append("\n" + links[i] + "\n\n")
                filesentence.append("\n" + links[i] + "\n\n")

                for sentence in sentences:
                    filesentence.append(sentence+"\n")

                textrank = TextRank.TextRank(pageSource)

                for row in textrank.summarize(3):
                    filelink.append(row + "\n")
                    print(row)
                    print()

                filelink.append("\n")

                keywords = textrank.keywords()
                keywordsSet = set(keywords)

                filelink.append(str(keywordsSet)+"\n")

                print('keywords :', keywordsSet)
                print('-----------------------------------------------------')

                filesuccesslink.append(links[i]+"\n")
            except:
                filefaillink.append(links[i]+"\n")
                continue

        if threadNum == 0:
            dic= self.__DS.get_dic()
            for i,d in sorted(dic.items(), key=lambda dic:dic[1]):
                filesimilarity.append(str(i) + " : " + str(d)+ "  " + links[i] + "\n")

        self.save_File("추출링크_요약문 threadNum: " + str(threadNum), filelink)
        self.save_File("추출링크_문장 threadNum: " + str(threadNum), filesentence)
        self.save_File("추출성공_링크 threadNum: " + str(threadNum), filesuccesslink)
        self.save_File("추출실패_링크 threadNum: " + str(threadNum), filefaillink)
        self.save_File("구글링크와의_연관도 threadNum: " + str(threadNum), filesimilarity)
        pass

    def getIntersection(self, keywords):
        intersection = baseKeywordsSet & set(keywords)
        if(len(intersection) >= 2):
            return True
        else:
            return False

    def linkFilter(self, link):
        #TODO: 유튜브 링크 거르기
        #TODO: mail:to 링크 거르기

        link = str(link)
        if "search" in link:
            return True

        if "facebook" in link:
            return True

        if "wikipedia.org" in link and "ko.wikipedia.org" not in link:
            return True

# variable
address = "https://www.google.co.kr"
# keyword = input("검색어를 입력하세요: ")

# Bot Setting
Bot = Bot()
Bot.setAddress(address)

Bot.setKeyword('c언어')
Bot.setIsDev(True)
Bot.setNumThreads(1)

# Bot start
start = timeit.default_timer()
Bot.bot_start()
stop = timeit.default_timer()
print(stop - start)
