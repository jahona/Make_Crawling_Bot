import CrawlerBot
import datetime
import random
import os
import TextRank
import sys
import timeit
import logging
from time import sleep
import Validation
import time
import math
import re

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import MainWindow
import pickle

import webbrowser

import threading

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
random.seed(datetime.datetime.now())

class Timer():
    def __self__(self):
        self.__start = None
        self.__end = None

    def start(self):
        self.__start = timeit.default_timer()

    def end(self):
        self.__end = timeit.default_timer()

    def getTime(self):
        return self.__end - self.__start

class Bot(QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        # 셀러니움 봇 생성
        self.__bot = CrawlerBot.Selenium()

        # 유사도 검증 클래스
        self.__validation = Validation.Validation()

        # 문서 필터링
        self.__whiteList = re.compile('ko.wikipedia.org')
        self.__blackList = re.compile('youtube|facebook|www.google.co.kr/search?|mail:to|[a-z]{2}.wikipedia.org|wikimedia.org|wikidata.org|namu.live|downloads|instagram|imgurl')
        self.__blackListExtension = re.compile('^\S+.(?i)(txt|pdf|hwp|xls|svg|jpg|exe|ftp|tar|xz|pkg|zip)$');
        self.__blackKeywordList = ['로그인']
        # 문장 분리기
        self.__sentenceTokenizer = TextRank.SentenceTokenizer()

        # GUI 셋팅
        self.guiInit()

        pass

    def get_CrawlerBot(self):
        return self.__bot

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

    def save_File(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')

        #file open
        file = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + ".txt", "w", encoding='UTF-8')
        file.write("------------------------------------------------------------------------------------------------------------------------\n")

        distanceDict = self.__distanceDict
        row = 0
        for i, distance in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
            try:
                row += 1
                file.write("link " + str(row) + " : " + str(self.__linkDict[i]) + "\n\n")
                file.write("key sentence\n")
                for j, sentence in enumerate(self.__sentenceDict[i]):
                    if j<5:
                        file.write(sentence + "\n")
                file.write("\nkeyword\n" + str(self.__keywordDict[i]) + "\n")
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
            except:
                file.write("------------------------------------------------------------------------------------------------------------------------\n")
                pass

        file.close()

    def resultToGui(self):
        self.tableWidget.setRowCount(0)
        row = 0
        distanceDict = self.__distanceDict

        self.tableWidget.setRowCount(len(distanceDict))

        for i, distance in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
            contents = ""
            contents += "key sentence\n"

            for j, sentence in enumerate(self.__sentenceDict[i]):
                if j<5:
                    if len(sentence) > 100:
                        contents += sentence[0:97]
                        contents += "...\n"
                    else:
                        contents += str(sentence) + "\n"

            contents += "\n"
            contents += "keyword\n"

            for k, keyword in enumerate(self.__keywordDict[i]):
                if k+1 == len(self.__keywordDict[i]):
                    contents += keyword
                else:
                    contents += keyword + ", "

            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(self.__linkDict[i])))
            self.tableWidget.item(row, 0).setForeground(Qt.blue)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(contents))
            row += 1

        self.tableWidget.resizeColumnToContents(1)
        self.tableWidget.resizeRowsToContents()

    def OpenLink(self, item):
        if item.column() == 0:
            webbrowser.open(self.tableWidget.item(item.row(), item.column()).text())

    def init(self):
        # 정상적으로 종료된 링크 저장
        self.__linkDict = dict()
        self.__sentenceDict = dict()
        self.__keywordDict = dict()
        self.__distanceDict = dict()
        self.__validation.init_dic()
        self.__validation.init_base_normalized()

    def guiInit(self):
        #GUI 추가
        QMainWindow.__init__(self)
        self.setupUi(self)

        # 검색 버튼 이벤트 핸들링
        self.btnSearch.clicked.connect(self.btnSearchClickEvent)
        self.btnSearch.setAutoDefault(True)

        # 중지 버튼 이벤트 핸들링
        self.btnStop.clicked.connect(self.stop_thread)

        # 저장 버튼 이벤트 핸들링
        self.btnSave.clicked.connect(self.save_File)

        self.tableWidget.itemDoubleClicked.connect(self.OpenLink)

        # 메인윈도우 보이기
        self.show()

        # progress bar thread start
        self.get_progressbar_thread.start()

    def btnSearchClickEvent(self):
        keyword = self.lineEdit.text()

        self.setKeyword(keyword)

        self.__t = threading.Thread(target=self.botStart)
        self.get_progressbar_thread.setValue(0)
        self.__threadStopFlag = False
        self.__t.start()

    def botStart(self):
        # dic() clean
        t = Timer()
        t.start()

        self.init()

        # Google 에 해당 키워드 검색 후 화면 이동
        self.__bot.search_keyword_based_on_google(self.__keyword)

        self.__keyword = self.__keyword.replace(" ", "")

        # Return Google Search List
        googleLinks = self.__bot.get_google_links()

        externalLinks = []
        internalLinks = []

        # googleLinks에 있는 link들을 탐색
        for index, link in enumerate(googleLinks):
            if(self.stop_thread_check()):
                break

            if self.linkFilter(link):
                del googleLinks[index]
                continue

            try:
                # 해당 페이지의 page source get
                self.__bot.go_page(link)

                pageSource = self.__bot.get_page_source()
                bsObj = self.__bot.get_bs_obj(pageSource)
            except Exception as e:
                print(e)
                print('셀러니움 에러')
                continue

            try:
                # 외부 링크를 배제를 위한 host 부분 추출
                excludeUrl = self.__bot.split_address(link)

                # 외부 링크 흭득
                for externalLink in self.__bot.get_external_links(bsObj, excludeUrl, self.__keyword):
                    if self.linkFilter(externalLink) or externalLink in externalLinks or externalLink in googleLinks:
                        continue
                    externalLinks.append(externalLink)

                # 내부 링크 흭득
                for internalLink in self.__bot.get_internal_links(bsObj, excludeUrl, link, self.__keyword):
                    if self.linkFilter(internalLink) or internalLink in internalLinks or internalLink in googleLinks:
                        continue
                    internalLinks.append(internalLink)

                # TODO: url 탐색 후 쿠키, 세션 삭제
            except Exception as e:
                print(e)
                print('외부/내부 링크 흭득 에러')
                continue

            try:
                Basesummarizes = []
                textrank = TextRank.TextRank(pageSource)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()

                # 구글 링크 문서의 키워드에 __keyword가 포함되어 있지 않다면 예외처리
                if(self.keywordFilter(keywords) == True):
                    continue

                for sentence in summarizes:
                    Basesummarizes.append(sentence)

                for sentence in textrank.sentences:
                    if self.__keyword in sentence:
                        Basesummarizes.append(sentence)

                self.__validation.sum_str(self.__sentenceTokenizer.get_nouns(Basesummarizes))

                self.__validation.set_dic(index, 0)
            except Exception as e:
                print(e)
                print('문서 요약 에러')
                continue

            self.printCommand(index, link, summarizes, keywords)

            self.__linkDict[index] = link
            self.__sentenceDict[index] = summarizes
            self.__keywordDict[index] = keywords

            self.__distanceDict = self.__validation.get_dic()

            self.resultToGui()

        # 비교 기준이 되는 문서들의 벡터 구하기
        self.__validation.base_vectorizing()

        # 외부, 내부 링크들에 대해 TR 수행
        allLinks = externalLinks + internalLinks

        print("전체 링크수 : ", len(allLinks))

        # 외부/내부 링크 탐색 시작
        self.travelLink(allLinks, len(googleLinks))

        t.end()

        print('running time: ', t.getTime())
        pass

    def travelLink(self, links, baselength):
        for (index, link) in enumerate(links):
            if(self.stop_thread_check()):
                break
            Dictindex = index + baselength

            # 프로그레스바 값 설정
            self.get_progressbar_thread.setValue(int((Dictindex+1)/(len(links)+baselength)*100))

            #페이지 이동
            try:
                self.__bot.go_page(link)
                pageSource = self.__bot.get_page_source()
            except Exception as e:
                print(e)
                print('셀러니움 에러')
                continue

            try:
                # 요약문 구하기
                textrank = TextRank.TextRank(pageSource)
                summarizes = textrank.summarize(10)
                keywords = textrank.keywords()

                if(self.keywordFilter(keywords) == True):
                    continue
            except Exception as e:
                print(e)
                print('TextRank 에러')
                continue

            try:
                self.__validation.target_vectorizing(self.__sentenceTokenizer.get_nouns(summarizes))
            except Exception as e:
                print(e)
                print('vectorizer 에러')
                continue

            # 유클리드 거리 구하기
            try:
                # base와 target간에 유클리드 거리 구하기
                distance = self.__validation.dist_norm()

                if math.isnan(distance) == True:
                    raise ValueError

                self.__validation.set_dic(Dictindex, distance)
            except ValueError as e:
                print(e)
                print('distance가 nan입니다')
                continue
            except:
                print('유클리드 거리 구하기 에러')
                continue

            self.printCommand(Dictindex, link, summarizes, keywords, distance)

            self.__linkDict[Dictindex] = link
            self.__sentenceDict[Dictindex] = summarizes
            self.__keywordDict[Dictindex] = keywords

            self.__distanceDict = self.__validation.get_dic()

            self.resultToGui()

        pass

    def keywordFilter(self, keywords):
        flag = False
        for keyword in keywords:
            if keyword in self.__blackKeywordList:
                return True

            if keyword in self.__keyword:
                flag = True
                break

        if(flag == False):
            print('검색어가 키워드에 없습니다.')
            return True

        return False

    def linkFilter(self, link):
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

    def printCommand(self, index, link, summarizes, keywords, distance=None):
        print('----------------------------------')

        print('link', index, link)

        for i, summarize in enumerate(summarizes):
            if i<5:
                print(summarize)

        print(set(keywords))

        if distance is not None:
            print("distance: ", distance)

        print('----------------------------------')
        pass

    def stop_thread(self):
        self.__threadStopFlag = True
        self.__t.join()

    def stop_thread_check(self):
        if(self.__threadStopFlag == True):
            return True

        return False

# variable
address = "https://www.google.co.kr"

app = QApplication(sys.argv)

# Bot Setting
Bot = Bot()
Bot.setAddress(address)
app.exec_()
Bot.get_CrawlerBot().quit()

# Bot start
# start = timeit.default_timer()
# Bot.bot_start()
# stop = timeit.default_timer()
# print(stop - start)