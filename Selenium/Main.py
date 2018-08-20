import CrawlerBot
import datetime
import random
import os

from PyQt4.QtGui import *
import MainWindow
import sys
import pickle

random.seed(datetime.datetime.now())

class Bot(QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        self.__bot = CrawlerBot.Selenium()
        self.__depth = 0
        #GUI 추가
        QMainWindow.__init__(self)
        self.setupUi(self)

        # 검색 버튼 이벤트 핸들링
        self.btnSearch.clicked.connect(self.search)
        self.btnSearch.setAutoDefault(True)
        # 저장 버튼 이벤트 핸들링
        self.btnSave.clicked.connect(self.saveData)

        # 메인윈도우 보이기
        self.show()
        pass

    def setAddress(self, address):
        self.__address = address
        pass

    def setKeyword(self, keyword):
        self.__keyword = keyword
        pass

    def setLink(self, links):
        self.__link = []
        for link in links:
            self.__link.append(str(link))
        pass

    #GUI 검색
    def search(self):
        keyword = self.lineEdit.text()
        Bot.setKeyword(keyword)

        self.__bot.search_keyword_based_on_google(self.__keyword)

        # Return Google Search List
        googleLinks = self.__bot.get_google_links()

        externalLinks = []
        internalLinks = []
        keywordLinks = []

        # googleLinks에 있는 link들을 탐색
        for link in googleLinks:
            # 해당 페이지의 page source get
            if(self.__bot.go_page(link)):
                pageSource = self.__bot.get_page_source()
                bsObj = self.__bot.get_bs_obj(pageSource)

                # 외부 링크를 배제를 위한 host 부분 추출
                excludeUrl = self.__bot.split_address(link)
                # 추출한 내부, 외부, 링크들 키워드들 통합
                for list in self.__bot.get_external_links(bsObj, excludeUrl, keyword):
                    if list not in externalLinks:
                        externalLinks.append(list)
                for list in self.__bot.get_internal_links(bsObj, excludeUrl, link, keyword):
                    if list not in internalLinks:
                        internalLinks.append(list)
                for list in self.__bot.get_keyword_text(bsObj, link, keyword):
                    if list not in keywordLinks:
                        keywordLinks.append(list)
            else:
                continue

        Bot.setLink(externalLinks)
        Bot.setLink(internalLinks)

        self.tableWidget.setRowCount(len(self.__link))
        row = 0
        for link in self.__link:
            self.tableWidget.setItem(row, 0, QTableWidgetItem(keyword))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(link))
            row += 1

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        file = open(os.getcwd()+"/_"+self.__keyword+"_문장.txt", 'w', encoding='UTF-8')
        for link in keywordLinks:
            file.write(link+"\n")
        file.close()

    def saveData(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d_%H%M%S')
        linkfile = open(os.getcwd()+"/"+str(date)+"_"+self.__keyword+"_링크.txt", 'w', encoding='UTF-8')
        for link in self.__link:
            linkfile.write(link+"\n")
        linkfile.close()
        QMessageBox.information(self, "저장", "데이타 저장됨")

# variable
address = "https://www.google.co.kr"

# Bot Setting
app = QApplication(sys.argv)
Bot = Bot()
Bot.setAddress(address)
Bot.search()

app.exec_()
