import CrawlingStrategy
import TextRank
import Validation
import math
import timeit

# Gui 환경 Set
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import MainWindow
import webbrowser
import threading
import sys
import os

import datetime
import random
random.seed(datetime.datetime.now())

from time import sleep

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

class Bot(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        # 셀러니움 봇 생성
        self.__strategy = CrawlingStrategy.CrawlingStrategy()
        self.__validation = Validation.Validation()
        self.__validation.init_dic()
        self.__validation.init_base_normalized()
        self.__keyword = None
        self.__sentenceTokenizer = TextRank.SentenceTokenizer()
        
        # GUI 셋팅
        self.guiInit()
        pass

    def guiInit(self):
        #GUI 추가
        QtWidgets.QMainWindow.__init__(self)
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
    
    def stop_thread(self):
        self.__threadStopFlag = True
        self.__t.join()

    def stop_thread_check(self):
        if(self.__threadStopFlag == True):
            return True

        return False
        
    def resultToGui(self):
        self.tableWidget.setRowCount(0)
        row = 0
        distanceDict = self.__distanceDict

        self.tableWidget.setRowCount(len(distanceDict))

        for i in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
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

            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.__linkDict[i])))
            self.tableWidget.item(row, 0).setForeground(QtWidgets.blue)
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(contents))
            row += 1

        self.tableWidget.resizeColumnToContents(1)
        self.tableWidget.resizeRowsToContents()
    
    def OpenLink(self, item):
        if item.column() == 0:
            webbrowser.open(self.tableWidget.item(item.row(), item.column()).text())
    
    def btnSearchClickEvent(self):
        keyword = self.lineEdit.text()

        self.setKeyword(keyword)

        self.__t = threading.Thread(target=self.start)
        self.get_progressbar_thread.setValue(0)
        self.__threadStopFlag = False
        self.__t.start()

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
        targetLinks = internalLinks + externalLinks
        targetLinksCount = len(targetLinks)

        for index, googleLink in enumerate(googleLinks):
            if(self.stop_thread_check()):
                break

            # 프로그레스바 값 설정
            self.get_progressbar_thread.setValue(int((index+1)/(targetLinksCount + googleLinksCount)*100))

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
        
        for index, targetLink in enumerate(targetLinks):
            if(self.stop_thread_check()):
                break

            targetIndex = index + googleLinksCount

            # 프로그레스바 값 설정
            self.get_progressbar_thread.setValue(int((targetIndex+1)/(targetLinksCount + googleLinksCount)*100))

            try:
                sleep(2)
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

    def save_File(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')

        #file open
        file = open(os.getcwd() + "/" + str(date) + "_" + self.__keyword + ".txt", "w", encoding='UTF-8')
        file.write("------------------------------------------------------------------------------------------------------------------------\n")

        distanceDict = self.__distanceDict
        row = 0
        for i in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
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
        
app = QApplication(sys.argv)
Bot = Bot()
sys.exit(app.exec_())