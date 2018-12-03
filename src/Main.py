# Gui 환경 Set
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import Bot
import MainWindow
import webbrowser
import threading
import sys
import os

import datetime
import random
random.seed(datetime.datetime.now())

from time import sleep
from enum import Enum

class Main(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        # GUI 셋팅
        self.bot = Bot.Bot.instance()
        self.bot.register_observer(self)
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

        # 키워드 검색 버튼 이벤트 핸들링
        self.btnFind.clicked.connect(self.btnFindClickEvent)
        self.btnFind.setAutoDefault(True)

        self.tableWidget.itemDoubleClicked.connect(self.OpenLink)

        # 메인윈도우 보이기
        self.show()

        # progress bar thread start
        self.get_progressbar_thread.start()

        # exit button
        self.finishButton.triggered.connect(self.closeEvent)

    def stop_thread(self):
        if not self.bot.is_bot_status_running():
            QMessageBox.information(self, 'ALARM', "검색 중 상태가 아닙니다.", QMessageBox.Ok, QMessageBox.Ok)
            return

        reply = QMessageBox.question(self, 'STOP', "검색을 중지하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.__threadStopFlag = True
            self.__t.join()
            self.bot.set_bot_status_stopping()
        else:
            return

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                     "QUIT",
                                     "Sure?",
                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            if self.bot.is_bot_status_running():
                self.__threadStopFlag = True
                self.__t.join()

            event.accept()
        else:
            event.ignore()

    def stop_thread_check(self):
        if(self.__threadStopFlag == True):
            return True

        return False

    def items_clear(self):
        self.tableWidget.setRowCount(0)

    def resultToGui(self, findkeyword=None):
        self.items_clear()

        row = 0
        distanceDict = self.bot.get_distance_dict()
        keywordDict = self.bot.get_keyword_dict()
        sentenceDict = self.bot.get_sentence_dict()
        linkDict = self.bot.get_link_dict()

        # TODO: distanceDict만큼 생성하는게 너무 불필요해보임
        self.tableWidget.setRowCount(len(distanceDict))

        # TODO: 한 행마다 출력문들을 객체화 시켜서 깔끔하게 유지하기
        for i, distance in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
            contents = ""
            contents += "keyword\n"

            if(self.bot.is_bot_status_stopping() and findkeyword is not None and findkeyword is not ''):
                if findkeyword not in keywordDict[i]:
                    continue

            for k, keyword in enumerate(keywordDict[i]):
                if k+1 == len(keywordDict[i]):
                    contents += keyword
                else:
                    contents += keyword + ", "

            contents += "\n\n"

            for j, sentence in enumerate(sentenceDict[i]):
                if j<5:
                    if len(sentence) > 100:
                        contents += str(j+1) + ". " + sentence[0:100]
                        contents += "...\n"
                    else:
                        contents += str(j+1) + ". " + str(sentence) + "\n"

            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(linkDict[i])))
            self.tableWidget.item(row, 0).setForeground(Qt.blue)
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(contents))
            self.tableWidget.item(row, 1).setFlags(QtCore.Qt.ItemIsEnabled)

            row += 1

        if len(distanceDict) > row:
            for ri in range(row, len(distanceDict)):
                self.tableWidget.removeRow(row)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnToContents(1)


    def OpenLink(self, item):
        if item.column() == 0:
            webbrowser.open(self.tableWidget.item(item.row(), item.column()).text())

    def btnSearchClickEvent(self):
        if self.bot.is_bot_status_running():
            QMessageBox.information(self, 'ALARM', "이미 검색 중입니다.", QMessageBox.Ok, QMessageBox.Ok)
            return

        keyword = self.lineEdit.text()

        self.bot.set_keyword(keyword)

        reply = QMessageBox.question(self, 'Search', "검색을 시작하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.__t = threading.Thread(target=self.bot.start)
            self.get_progressbar_thread.setValue(0)
            self.__threadStopFlag = False
            self.bot.init()
            self.items_clear()
            self.__t.start()
        else:
            return

    def btnFindClickEvent(self):
        if not self.bot.is_bot_status_stopping():
            QMessageBox.information(self, 'ALARM', "검색 중입니다. 중지 후 눌러주세요", QMessageBox.Ok, QMessageBox.Ok)
            return False

        findkeyword = self.lineEdit_2.text()

        # '' 입력시 메시지 박스 출력 없이 다시 전체 데이터을 보여주기 위해 예외처리
        if(findkeyword == ''):
            self.resultToGui()
            return

        reply = QMessageBox.question(self, 'Find Keyword', "키워드를 찾으시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.resultToGui(findkeyword)

            print(findkeyword)
        else:
            return

    def set_progress_bar(self, percent):
        if(percent <= 1):
            self.get_progressbar_thread.setValue(1)
            return

        self.get_progressbar_thread.setValue(percent)

    def save_File(self):
        if self.bot.is_bot_status_running():
            QMessageBox.information(self, 'ALARM', "검색 중입니다. 중지 후 저장을 눌러주세요", QMessageBox.Ok, QMessageBox.Ok)
            return

        reply = QMessageBox.question(self, 'SAVE', "결과를 저장하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            now = datetime.datetime.now()
            date = now.strftime('%Y%m%d')

            #file open
            file = open(os.getcwd() + "/" + str(date) + "_" + self.bot.get_keword() + ".txt", "w", encoding='UTF-8')
            file.write("------------------------------------------------------------------------------------------------------------------------\n")

            distanceDict = self.bot.get_distance_dict()
            keywordDict = self.bot.get_keyword_dict()
            sentenceDict = self.bot.get_sentence_dict()
            linkDict = self.bot.get_link_dict()

            row = 0
            for i, distance in sorted(distanceDict.items(), key=lambda distanceDict:distanceDict[1]):
                try:
                    row += 1
                    file.write("link " + str(row) + " : " + str(linkDict[i]) + "\n\n")
                    file.write("keywords\n")

                    for k, keyword in enumerate(keywordDict[i]):
                        if k+1 == len(keywordDict[i]):
                            file.write(str(keyword) + "\n\n")
                        else:
                            file.write(str(keyword+', '))

                    for j, sentence in enumerate(sentenceDict[i]):
                        if j<5:
                            if len(sentence) > 100:
                                file.write(str(j+1) + ". ")
                                for l in range(0, int(len(sentence)/100)+1):
                                    if l == 0:
                                        file.write(sentence[l*100:(l+1)*100] + "\n")
                                    else:
                                        if(sentence[l*100] == " "):
                                            file.write("  " + sentence[l*100:(l+1)*100] + "\n")
                                        else:
                                            file.write("   " + sentence[l*100:(l+1)*100] + "\n")
                            else:
                                file.write(str(j+1) + ". " + sentence + "\n")
                    file.write("------------------------------------------------------------------------------------------------------------------------\n")
                except:
                    file.write("------------------------------------------------------------------------------------------------------------------------\n")
                    pass

            file.close()
        else:
            return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ## !!테스트 용으로 사용할 때는 아래 주석 지우지 말고, 실제 기능으로 테스트해보고 싶을 때 아래 주석 제거해서 사용하셈.
    # ex.setIsTest(False)
    sys.exit(app.exec_())
